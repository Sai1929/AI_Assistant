# app/core/memory.py
"""
Two-tier conversation memory: sliding window (6 turns) + Groq summarization overflow.

Session structure:
    {
        "history": list[dict],   # recent turns {"role": "user"|"assistant", "content": str}
        "summary": str | None,   # Groq-generated summary of older turns
        "denomination": str | None,  # detected denomination preference
    }
"""
import json

from app.config import MEMORY_WINDOW_SIZE
from app.core.llm_client import chat_structured
from app.schemas import ConversationSummary
from app.prompts.system_prompts import CONVERSATION_SUMMARIZER

_sessions: dict[str, dict] = {}
WINDOW_SIZE = MEMORY_WINDOW_SIZE  # 6


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _default_session() -> dict:
    return {"history": [], "summary": None, "denomination": None}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_session(session_id: str) -> dict:
    """Return the session dict, creating it with defaults if it doesn't exist."""
    if session_id not in _sessions:
        _sessions[session_id] = _default_session()
    return _sessions[session_id]


def add_turn(session_id: str, role: str, content: str) -> None:
    """
    Append a turn to the session history.

    If len(history) exceeds WINDOW_SIZE * 2 (i.e. > 12 messages):
      - Summarize the OLDEST half via Groq (chat_structured with ConversationSummary)
      - Replace history with the NEWER half
      - Merge denomination_preference from summary if set
    """
    session = get_session(session_id)
    session["history"].append({"role": role, "content": content})

    if len(session["history"]) > WINDOW_SIZE * 2:
        midpoint = len(session["history"]) // 2
        oldest_half = session["history"][:midpoint]
        newer_half = session["history"][midpoint:]

        # Summarize oldest half via Groq
        try:
            summary_obj: ConversationSummary = chat_structured(
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize this conversation:\n{json.dumps(oldest_half)}",
                    }
                ],
                schema=ConversationSummary,
                system=CONVERSATION_SUMMARIZER,
            )
            # Merge summaries: prepend old summary if it existed
            if session["summary"]:
                merged_text = f"{session['summary']} | {summary_obj.summary}"
            else:
                merged_text = summary_obj.summary
            session["summary"] = merged_text

            # Update denomination from summary if newly detected
            if summary_obj.denomination_preference:
                session["denomination"] = summary_obj.denomination_preference

        except Exception:
            # If summarization fails, just trim to newer half without summary update
            pass

        session["history"] = newer_half


def get_history(session_id: str) -> list[dict]:
    """
    Return the conversation history for the session.

    If a summary exists, prepend two synthetic messages so the LLM is aware of
    earlier context without seeing the full transcript:
        {"role": "user",      "content": "[Conversation context: <summary>]"}
        {"role": "assistant", "content": "Understood. I'll keep that context in mind."}
    Then append the actual recent history turns.
    """
    session = get_session(session_id)
    messages: list[dict] = []

    if session["summary"]:
        messages.append(
            {
                "role": "user",
                "content": f"[Conversation context: {session['summary']}]",
            }
        )
        messages.append(
            {
                "role": "assistant",
                "content": "Understood. I'll keep that context in mind.",
            }
        )

    messages.extend(session["history"])
    return messages


def clear_session(session_id: str) -> None:
    """Remove session data entirely."""
    _sessions.pop(session_id, None)


def update_denomination(session_id: str, denomination: str | None) -> None:
    """Update the detected denomination for the session."""
    session = get_session(session_id)
    session["denomination"] = denomination
