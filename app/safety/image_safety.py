# app/safety/image_safety.py
import base64
from app.schemas import ImagePromptSafety


def check_prompt_safety(prompt: str) -> ImagePromptSafety:
    """Pre-generation image safety check + prompt rewrite via Groq."""
    from app.core.llm_client import chat_structured
    from app.prompts.system_prompts import IMAGE_SAFETY

    messages = [{"role": "user", "content": f"Image prompt to evaluate: {prompt}"}]
    return chat_structured(
        messages=messages,
        schema=ImagePromptSafety,
        system=IMAGE_SAFETY,
    )


def generate_safe_image(prompt: str) -> dict:
    """
    Two-gate image safety pipeline.
    Gate 1 (pre-gen): Groq llama-guard prompt safety check + rewrite
    Gate 2 (post-gen): Groq vision policy violation check
    Returns: {success, image_b64, original_prompt, rewritten_prompt, refusal_reason}
    """
    from app.core.llm_client import generate_image, analyze_image_safety

    safety = check_prompt_safety(prompt)
    if not safety.is_safe:
        return {
            "success": False,
            "image_b64": None,
            "original_prompt": prompt,
            "rewritten_prompt": None,
            "refusal_reason": safety.refusal_reason or "image_policy_violation",
        }

    image_bytes = generate_image(safety.rewritten_prompt)
    if image_bytes is None:
        return {
            "success": False,
            "image_b64": None,
            "original_prompt": prompt,
            "rewritten_prompt": safety.rewritten_prompt,
            "refusal_reason": "image_generation_failed",
        }

    image_b64 = base64.b64encode(image_bytes).decode()

    vision_result = analyze_image_safety(image_b64)
    if vision_result.get("violates"):
        return {
            "success": False,
            "image_b64": None,
            "original_prompt": prompt,
            "rewritten_prompt": safety.rewritten_prompt,
            "refusal_reason": vision_result.get("reason", "post_gen_policy_violation"),
        }

    return {
        "success": True,
        "image_b64": image_b64,
        "original_prompt": prompt,
        "rewritten_prompt": safety.rewritten_prompt,
        "refusal_reason": None,
    }
