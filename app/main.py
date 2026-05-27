"""FastAPI REST API — Phase 8."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import GROQ_PRIMARY_MODEL
from app.agents.graph import run_assistant
from app.core.memory import clear_session, get_history


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str | None
    image_b64: str | None = None
    intent: str | None
    denomination: str | None = None
    toxicity_ok: bool = True


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
        raise HTTPException(status_code=500, detail=str(e))

    image_b64: str | None = None
    if result.get("image_result") and result["image_result"].get("success"):
        image_b64 = result["image_result"].get("image_b64")

    return ChatResponse(
        session_id=request.session_id,
        response=result.get("response"),
        image_b64=image_b64,
        intent=result.get("intent"),
        denomination=result.get("denomination"),
        toxicity_ok=result.get("toxicity_ok", True),
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
