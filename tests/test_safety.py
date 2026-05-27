"""Safety tests. RED phase — implemented in Phase 6 Task 14."""
import pytest
import sys
sys.path.insert(0, ".")


def test_placeholder_fails():
    from app.agents.intent_router import pre_screen
    with pytest.raises(NotImplementedError):
        pre_screen("test")
