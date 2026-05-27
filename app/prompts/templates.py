"""Prompt assembly templates."""


def build_scripture_prompt(query: str, context: str, correction_hints: list[str] | None = None) -> str:
    base = f"User question: {query}\n\nRETRIEVED_CONTEXT:\n{context}"
    if correction_hints:
        base += "\n\nIMPORTANT CORRECTIONS:\n" + "\n".join(correction_hints)
    return base
