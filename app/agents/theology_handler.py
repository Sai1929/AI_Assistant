# app/agents/theology_handler.py
from pathlib import Path
from app.config import DENOM_DATA_PATH


def _load_denom_context(denomination: str | None) -> str:
    denom_path = Path(DENOM_DATA_PATH)
    if denomination:
        fp = denom_path / f"{denomination}.md"
        if fp.exists():
            return fp.read_text(encoding="utf-8")
    parts = []
    for name in ["catholic", "protestant", "orthodox"]:
        fp = denom_path / f"{name}.md"
        if fp.exists():
            parts.append(f"## {name.title()} Tradition\n{fp.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def answer_theology_query(
    query: str,
    conversation_history: list[dict],
    denomination: str | None = None,
) -> str:
    from app.core.llm_client import chat
    from app.prompts.system_prompts import THEOLOGY_HANDLER

    denom_context = _load_denom_context(denomination)
    messages = conversation_history[-6:] + [
        {
            "role": "user",
            "content": f"Theological question: {query}\n\nDENOMINATION KNOWLEDGE BASE:\n{denom_context}",
        }
    ]
    return chat(messages=messages, system=THEOLOGY_HANDLER)
