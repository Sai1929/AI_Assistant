# app/safety/output_moderation.py
from app.schemas import ToxicityCheck


def moderate_output(response_text: str) -> ToxicityCheck:
    """Post-generation toxicity + heresy check via Groq."""
    from app.core.llm_client import chat_structured
    from app.prompts.system_prompts import OUTPUT_MODERATION

    messages = [{"role": "user", "content": f"Response to evaluate:\n{response_text}"}]
    return chat_structured(
        messages=messages,
        schema=ToxicityCheck,
        system=OUTPUT_MODERATION,
    )
