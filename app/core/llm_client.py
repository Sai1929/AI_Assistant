# app/core/llm_client.py
"""Groq + Gemini LLM wrapper."""
import base64
import json
from typing import Type, TypeVar
import httpx
from groq import Groq
from pydantic import BaseModel
from app.config import (
    GROQ_API_KEY, GEMINI_API_KEY,
    GROQ_PRIMARY_MODEL, GROQ_FAST_MODEL, GROQ_VISION_MODEL,
    GEMINI_IMAGE_MODEL,
)

T = TypeVar("T", bound=BaseModel)

_groq = Groq(api_key=GROQ_API_KEY)


def chat(
    messages: list[dict],
    model: str | None = None,
    system: str | None = None,
) -> str:
    """Plain text generation via Groq."""
    all_messages: list[dict] = []
    if system:
        all_messages.append({"role": "system", "content": system})
    all_messages.extend(messages)
    response = _groq.chat.completions.create(
        model=model or GROQ_PRIMARY_MODEL,
        messages=all_messages,
        temperature=0.3,
        max_tokens=2048,
    )
    return response.choices[0].message.content


def chat_structured(
    messages: list[dict],
    schema: Type[T],
    model: str | None = None,
    system: str | None = None,
) -> T:
    """Structured JSON output via Groq, validated into Pydantic model."""
    all_messages: list[dict] = []
    if system:
        all_messages.append({"role": "system", "content": system})
    all_messages.extend(messages)
    response = _groq.chat.completions.create(
        model=model or GROQ_FAST_MODEL,
        messages=all_messages,
        response_format={"type": "json_object"},
        temperature=0.1,
        max_tokens=1024,
    )
    raw = response.choices[0].message.content
    return schema.model_validate_json(raw)


def analyze_image_safety(image_b64: str) -> dict:
    """Post-generation image safety check via Groq vision model."""
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Does this image violate any of these policies? "
                        "1) Photorealistic face of God the Father, "
                        "2) Mocking/sexualized depiction of Christ, Mary, or saints, "
                        "3) Religious violence imagery, "
                        "4) Syncretism blending Christ with other-religion deities. "
                        'Reply with valid JSON only: {"violates": true/false, "reason": "string or null"}'
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                },
            ],
        }
    ]
    response = _groq.chat.completions.create(
        model=GROQ_VISION_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    return json.loads(response.choices[0].message.content)


def generate_image(prompt: str) -> bytes | None:
    """Generate image via Gemini. Returns raw PNG bytes or None on failure."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_IMAGE_MODEL)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_modalities=["IMAGE"],
            ),
        )
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                return part.inline_data.data
    except Exception as e:
        print(f"[image_gen] Error: {e}")
    return None
