"""Input moderation: regex pre-screen + Groq intent classifier. Stub — implemented in Phase 6."""
from app.schemas import IntentClassification


def moderate_input(
    user_message: str,
    conversation_history: list[dict],
) -> tuple[bool, str | None, IntentClassification | None]:
    raise NotImplementedError("Implement in Phase 6 Task 14")
