"""Hybrid retriever tests. RED phase — implemented in Phase 3 Task 8."""
import pytest
import sys
sys.path.insert(0, ".")


def test_placeholder_fails():
    from app.retrieval.hybrid_retriever import reciprocal_rank_fusion
    with pytest.raises(NotImplementedError):
        reciprocal_rank_fusion([[], []])
