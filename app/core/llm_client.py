"""Groq + Gemini LLM wrapper. Stub — implemented in Phase 4."""
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def chat(messages: list[dict], model: str | None = None, system: str | None = None) -> str:
    raise NotImplementedError("Implement in Phase 4")


def chat_structured(
    messages: list[dict],
    schema: Type[T],
    model: str | None = None,
    system: str | None = None,
) -> T:
    raise NotImplementedError("Implement in Phase 4")


def analyze_image_safety(image_b64: str) -> dict:
    raise NotImplementedError("Implement in Phase 4")


def generate_image(prompt: str) -> bytes | None:
    raise NotImplementedError("Implement in Phase 4")
