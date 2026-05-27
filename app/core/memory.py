"""Two-tier conversation memory. Stub — implemented in Phase 7."""

_sessions: dict[str, dict] = {}


def get_session(session_id: str) -> dict:
    raise NotImplementedError("Implement in Phase 7")


def add_turn(session_id: str, role: str, content: str) -> None:
    raise NotImplementedError("Implement in Phase 7")


def get_history(session_id: str) -> list[dict]:
    raise NotImplementedError("Implement in Phase 7")


def clear_session(session_id: str) -> None:
    _sessions.pop(session_id, None)
