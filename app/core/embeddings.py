# app/core/embeddings.py
import httpx
from app.config import JINA_API_KEY, JINA_EMBED_MODEL

JINA_API_URL = "https://api.jina.ai/v1/embeddings"

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed batch of texts via Jina API. Returns list of float vectors."""
    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"model": JINA_EMBED_MODEL, "input": texts}
    resp = httpx.post(JINA_API_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return [item["embedding"] for item in data["data"]]

def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
