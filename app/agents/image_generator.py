# app/agents/image_generator.py
"""
Image generation agent. Delegates to the two-gate safety pipeline in
app.safety.image_safety so prompt checking and post-generation vision
review are always applied.
"""
from app.safety.image_safety import generate_safe_image


def generate_christian_image(prompt: str) -> dict:
    """
    Generate a Christian-themed image with full safety pipeline.

    Returns: {
        "success": bool,
        "image_b64": str | None,
        "original_prompt": str,
        "rewritten_prompt": str | None,
        "refusal_reason": str | None,
    }
    """
    return generate_safe_image(prompt)
