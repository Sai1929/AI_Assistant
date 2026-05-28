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


def analyze_image_safety(image_b64: str, mime_type: str = "image/jpeg") -> dict:
    """Post-generation image safety check via Groq vision model."""
    try:
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
                        "image_url": {"url": f"data:{mime_type};base64,{image_b64}"},
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
    except Exception as e:
        print(f"[vision_safety] Error: {e} — defaulting to safe")
        return {"violates": False, "reason": None}


def _generate_image_gemini(prompt: str) -> bytes | None:
    """Generate image via new google-genai SDK. Returns bytes or None."""
    try:
        from google import genai as google_genai
        from google.genai import types as google_types
        # Short timeout to fail fast when quota is exhausted
        client = google_genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=google_types.HttpOptions(timeout=8000),
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=google_types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                return part.inline_data.data
    except Exception as e:
        print(f"[image_gen/gemini] {str(e)[:120]}")
    return None


def _generate_image_pollinations(prompt: str) -> bytes | None:
    """Generate image via Pollinations.AI (free, no API key). Returns bytes or None."""
    import urllib.parse, time
    encoded = urllib.parse.quote(prompt, safe="")
    headers = {"User-Agent": "curl/7.88.1", "Accept": "image/jpeg,image/*"}
    url = f"https://image.pollinations.ai/prompt/{encoded}"
    # Retry up to 3 times — 402 means queue full, wait and retry
    for attempt in range(3):
        try:
            r = httpx.get(url, headers=headers, timeout=55, follow_redirects=True)
            ct = r.headers.get("content-type", "")
            if r.status_code == 200 and ct.startswith("image/"):
                return r.content
            if r.status_code in (402, 429):
                print(f"[image_gen/pollinations] queue full (attempt {attempt+1}), retrying in 5s")
                time.sleep(5)
                continue
            print(f"[image_gen/pollinations] {r.status_code}: {r.text[:80]}")
            return None
        except Exception as e:
            print(f"[image_gen/pollinations] attempt {attempt+1}: {e}")
            if attempt < 2:
                time.sleep(3)
    return None


def generate_image(prompt: str) -> bytes | None:
    """Generate image: Pollinations.AI primary (Gemini as future upgrade when quota available)."""
    # Skip Gemini — daily free-tier quota is exhausted; go straight to Pollinations
    result = _generate_image_pollinations(prompt)
    if result:
        return result
    # Gemini as last resort (will likely fail if quota exhausted)
    print("[image_gen] Pollinations failed, trying Gemini")
    return _generate_image_gemini(prompt)
