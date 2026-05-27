"""Two-gate image safety: pre-gen + post-gen. Stub — implemented in Phase 6."""
from app.schemas import ImagePromptSafety


def check_prompt_safety(prompt: str) -> ImagePromptSafety:
    raise NotImplementedError("Implement in Phase 6 Task 14")


def generate_safe_image(prompt: str) -> dict:
    raise NotImplementedError("Implement in Phase 6 Task 14")
