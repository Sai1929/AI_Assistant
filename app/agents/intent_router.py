# app/agents/intent_router.py
import re
from app.schemas import IntentClassification

ADVERSARIAL_PATTERNS = [
    re.compile(r"rewrite.{0,30}(verse|scripture|bible).{0,30}(support|justify|defend|endorse)", re.I),
    # Also catch "rewrite <Book Chapter:Verse> to support/justify/..."
    re.compile(r"rewrite.{0,50}\d+:\d+.{0,30}(support|justify|defend|endorse)", re.I),
    re.compile(r"(generate|write|create).{0,30}(hateful|extremist|racist|violent).{0,30}(sermon|message|content|prayer)", re.I),
    re.compile(r"(prove|show|demonstrate).{0,30}(religion|denomination|faith|christianity).{0,30}(false|fake|wrong|evil)", re.I),
    re.compile(r"ignore.{0,20}(previous|above|prior|all).{0,20}(instructions|prompt|system|rules)", re.I),
    re.compile(r"(jailbreak|bypass|override|disable|remove).{0,20}(filter|safety|moderation|restriction|guard)", re.I),
    re.compile(r"(act as|pretend|roleplay|you are now).{0,30}(no restriction|no limit|unrestricted|evil|different ai)", re.I),
]


def pre_screen(text: str) -> str | None:
    """Zero-LLM regex pre-screen. Returns refusal type or None if clean."""
    if not text or not text.strip():
        return "empty_input"
    if len(text) > 2000:
        return "input_too_long"
    for pattern in ADVERSARIAL_PATTERNS:
        if pattern.search(text):
            return "adversarial_intent"
    return None


def classify_intent(
    user_message: str,
    conversation_history: list[dict],
) -> IntentClassification:
    """Classify intent via Groq fast model with structured output."""
    from app.core.llm_client import chat_structured
    from app.prompts.system_prompts import INTENT_CLASSIFIER

    messages = conversation_history[-4:] + [{"role": "user", "content": user_message}]
    return chat_structured(
        messages=messages,
        schema=IntentClassification,
        system=INTENT_CLASSIFIER,
    )
