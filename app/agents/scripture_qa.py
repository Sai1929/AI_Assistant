# app/agents/scripture_qa.py
from app.config import MAX_REGEN_ATTEMPTS, HISTORICAL_FACTS_PATH


def _denom_to_translation(denomination: str | None) -> str | None:
    return {"catholic": "dra", "protestant": "kjv", "orthodox": "web"}.get(denomination or "")


def _build_context(retrieved: list[dict]) -> str:
    lines = []
    for doc in retrieved:
        m = doc.get("metadata", {})
        ref = m.get("reference", "unknown")
        trans = m.get("translation", "").upper()
        lines.append(f"[{ref} {trans}]: {doc['text']}")
    return "\n".join(lines)


def answer_scripture_query(
    query: str,
    conversation_history: list[dict],
    retriever,
    validator,
    hist_validator,
    denomination: str | None = None,
) -> dict:
    """
    5-gate hallucination prevention pipeline:
    Gate 1: retrieval-grounded generation
    Gate 2: regex citation extraction (inside validator)
    Gate 3: O(1) deterministic lookup (inside validator)
    Gate 4: regen-or-refuse loop
    Gate 4.5: historical claims check
    Gate 5: handled by output_moderation in graph
    """
    from app.core.llm_client import chat
    from app.prompts.system_prompts import SCRIPTURE_QA
    from app.prompts.templates import build_scripture_prompt

    translation = _denom_to_translation(denomination)

    # Pre-check: detect noncanonical books in the user's query itself
    query_check = validator.validate(query)
    if query_check.noncanonical_books:
        books = ", ".join(query_check.noncanonical_books)
        return {
            "answer": (
                f"'{books}' is not a book in the canonical Bible "
                f"(Catholic, Protestant, or Orthodox traditions). "
                f"It may be apocryphal, pseudepigraphal, or simply not a biblical text. "
                f"I can only reference scripture from the recognized biblical canon. "
                f"If you're looking for a similar topic, I'd be happy to suggest canonical passages."
            ),
            "valid_citations": [],
            "invalid_citations": [],
            "hist_issues": [],
            "attempts": 0,
            "status": "noncanonical_book",
        }

    retrieved = retriever.search(query, translation=translation)
    context = _build_context(retrieved)

    messages = conversation_history[-6:] + [
        {"role": "user", "content": build_scripture_prompt(query, context)}
    ]

    attempt = 0
    correction_hints: list[str] = []
    verse_result = None

    while attempt < MAX_REGEN_ATTEMPTS:
        system = SCRIPTURE_QA
        if correction_hints:
            system += "\n\nIMPORTANT CORRECTIONS REQUIRED:\n" + "\n".join(correction_hints)

        answer = chat(messages=messages, system=system)

        verse_result = validator.validate(answer)
        hist_result = hist_validator.validate(answer)

        if verse_result.is_valid and hist_result.is_clean:
            for c in verse_result.valid_citations:
                if not getattr(c, "translation", None):
                    c.translation = validator.translation
            return {
                "answer": answer,
                "valid_citations": verse_result.valid_citations,
                "invalid_citations": [],
                "hist_issues": [],
                "attempts": attempt + 1,
                "status": "ok",
            }

        correction_hints = verse_result.correction_hints + hist_result.uncertainty_notes
        attempt += 1

    return {
        "answer": (
            "I couldn't verify some scripture references reliably. "
            "Could you confirm the book and verse you're looking for? "
            "I want to give you accurate citations rather than risk an error."
        ),
        "valid_citations": [],
        "invalid_citations": verse_result.invalid_citations if verse_result else [],
        "hist_issues": [],
        "attempts": attempt,
        "status": "refused_unverified",
    }
