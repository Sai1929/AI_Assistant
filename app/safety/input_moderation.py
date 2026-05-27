# app/safety/input_moderation.py
from app.agents.intent_router import pre_screen, classify_intent
from app.safety.refusal_templates import get_refusal
from app.schemas import IntentClassification


def moderate_input(
    user_message: str,
    conversation_history: list[dict],
) -> tuple[bool, str | None, IntentClassification | None]:
    """
    Returns: (is_allowed, refusal_message_or_none, classification_or_none)
    Stage 1: regex pre-screen (zero LLM calls)
    Stage 2: LLM intent classification
    """
    pre = pre_screen(user_message)
    if pre:
        return False, get_refusal(pre), None

    classification = classify_intent(user_message, conversation_history)

    if classification.intent == "refuse":
        return False, get_refusal("adversarial_intent"), classification
    if classification.safety_flag == "manipulation_attempt":
        return False, get_refusal("verse_manipulation"), classification
    if classification.safety_flag == "hateful":
        return False, get_refusal("hateful_content"), classification

    return True, None, classification
