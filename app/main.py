"""FastAPI REST API — Phase 8."""
import logging
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any

from app.config import GROQ_PRIMARY_MODEL
from app.agents.graph import run_assistant
from app.core.memory import clear_session, get_history

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str


class Citation(BaseModel):
    reference: str
    verse_text: str | None = None
    translation: str | None = None
    verified: bool = True


class ChatResponse(BaseModel):
    session_id: str
    response: str | None
    image_b64: str | None = None
    image_mime_type: str = "image/jpeg"
    intent: str | None
    denomination: str | None = None
    toxicity_ok: bool = True
    citations: list[Citation] = []
    cross_references: list[dict] = []
    reading_plan: dict | None = None
    alternatives: list[dict] = []


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Christianity AI Assistant",
    description="Scripture-grounded AI with hallucination prevention",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Liveness check."""
    return {"status": "ok", "model": GROQ_PRIMARY_MODEL}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Send a message and get a theology / scripture / image response."""
    try:
        result = run_assistant(request.session_id, request.message)
    except Exception as e:
        logger.error("run_assistant failed: %s\n%s", e, traceback.format_exc())
        # Return a graceful error response instead of 500
        return ChatResponse(
            session_id=request.session_id,
            response=(
                "I encountered an issue processing your request. "
                "Please check that the API keys are configured correctly and try again."
            ),
            intent="general_chat",
            toxicity_ok=True,
        )

    image_b64: str | None = None
    image_mime_type: str = "image/jpeg"
    if result.get("image_result") and result["image_result"].get("success"):
        image_b64 = result["image_result"].get("image_b64")
        image_mime_type = result["image_result"].get("mime_type", "image/jpeg")

    # Build citations from valid_citations in result
    # valid_citations are Citation dataclass objects from verse_validator
    citations: list[Citation] = []
    for c in result.get("valid_citations", []):
        if isinstance(c, dict):
            ref = c.get("reference", "")
            verse_text = c.get("verse_text") or c.get("verified_text")
            translation = c.get("translation")
        else:
            ref = getattr(c, "reference", "")
            verse_text = getattr(c, "verified_text", None)
            translation = getattr(c, "translation", None)
        citations.append(Citation(
            reference=ref,
            verse_text=verse_text,
            translation=translation,
            verified=True,
        ))

    return ChatResponse(
        session_id=request.session_id,
        response=result.get("response"),
        image_b64=image_b64,
        image_mime_type=image_mime_type,
        intent=result.get("intent"),
        denomination=result.get("denomination"),
        toxicity_ok=result.get("toxicity_ok", True),
        citations=citations,
        cross_references=result.get("cross_references", []),
        reading_plan=result.get("reading_plan"),
        alternatives=result.get("alternatives", []),
    )


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    """Clear conversation memory for a session."""
    clear_session(session_id)
    return {"cleared": session_id}


@app.get("/session/{session_id}/history")
def session_history(session_id: str):
    """Return conversation history for a session."""
    return {"session_id": session_id, "history": get_history(session_id)}
