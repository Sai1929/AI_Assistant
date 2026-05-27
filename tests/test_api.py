"""Tests for the FastAPI REST API (app/main.py) — Phase 8."""
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Health check
# ---------------------------------------------------------------------------

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert data["model"] == "llama-3.3-70b-versatile"


# ---------------------------------------------------------------------------
# 2. Chat — successful text response
# ---------------------------------------------------------------------------

def test_chat_success():
    mock_result = {
        "response": "Jesus said 'I am the way, the truth, and the life.' (John 14:6)",
        "image_result": None,
        "intent": "scripture_qa",
        "denomination": "Protestant",
        "toxicity_ok": True,
    }
    with patch("app.main.run_assistant", return_value=mock_result) as mock_ra:
        response = client.post(
            "/chat",
            json={"session_id": "sess-abc", "message": "Who is Jesus?"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "sess-abc"
    assert data["response"] == mock_result["response"]
    assert data["intent"] == "scripture_qa"
    assert data["denomination"] == "Protestant"
    assert data["toxicity_ok"] is True
    assert data["image_b64"] is None
    mock_ra.assert_called_once_with("sess-abc", "Who is Jesus?")


# ---------------------------------------------------------------------------
# 3. Chat — response includes image_result with success=True
# ---------------------------------------------------------------------------

def test_chat_with_image():
    fake_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    mock_result = {
        "response": "Here is your generated image.",
        "image_result": {
            "success": True,
            "image_b64": fake_b64,
        },
        "intent": "image_generation",
        "denomination": None,
        "toxicity_ok": True,
    }
    with patch("app.main.run_assistant", return_value=mock_result):
        response = client.post(
            "/chat",
            json={"session_id": "sess-img", "message": "Generate a nativity scene"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["image_b64"] == fake_b64
    assert data["intent"] == "image_generation"


# ---------------------------------------------------------------------------
# 4. Chat — run_assistant raises an exception → 500
# ---------------------------------------------------------------------------

def test_chat_exception():
    with patch("app.main.run_assistant", side_effect=RuntimeError("LLM unavailable")):
        response = client.post(
            "/chat",
            json={"session_id": "sess-err", "message": "Hello"},
        )
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "LLM unavailable" in data["detail"]


# ---------------------------------------------------------------------------
# 5. DELETE /session/{session_id}
# ---------------------------------------------------------------------------

def test_clear_session():
    with patch("app.main.clear_session") as mock_cs:
        response = client.delete("/session/test123")
    assert response.status_code == 200
    data = response.json()
    assert data == {"cleared": "test123"}
    mock_cs.assert_called_once_with("test123")


# ---------------------------------------------------------------------------
# 6. GET /session/{session_id}/history
# ---------------------------------------------------------------------------

def test_get_history():
    fake_history = [
        {"role": "user", "content": "What is grace?"},
        {"role": "assistant", "content": "Grace is the unmerited favour of God."},
    ]
    with patch("app.main.get_history", return_value=fake_history):
        response = client.get("/session/test123/history")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test123"
    assert data["history"] == fake_history
