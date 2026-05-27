"""Intent router: regex pre-screen + Groq classification. Stub — implemented in Phase 5."""
from app.schemas import IntentClassification


def pre_screen(text: str) -> str | None:
    raise NotImplementedError("Implement in Phase 5 Task 11")


def classify_intent(user_message: str, conversation_history: list[dict]) -> IntentClassification:
    raise NotImplementedError("Implement in Phase 5 Task 11")
