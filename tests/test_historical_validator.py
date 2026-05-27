"""Historical validator tests. RED phase — implemented in Phase 2 Task 6."""
import pytest
import sys
sys.path.insert(0, ".")


def test_placeholder_fails():
    from app.retrieval.historical_validator import HistoricalValidator
    v = HistoricalValidator("data/historical_facts.json")
    with pytest.raises(NotImplementedError):
        v.validate("test")
