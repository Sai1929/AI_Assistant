# tests/test_retrieval.py
import pytest
import sys
sys.path.insert(0, ".")

def test_rrf_combines_two_lists():
    from app.retrieval.hybrid_retriever import reciprocal_rank_fusion
    list1 = [{"id": "a", "text": "foo", "metadata": {}}, {"id": "b", "text": "bar", "metadata": {}}]
    list2 = [{"id": "b", "text": "bar", "metadata": {}}, {"id": "a", "text": "foo", "metadata": {}}]
    fused = reciprocal_rank_fusion([list1, list2], top_k=2)
    ids = [r["id"] for r in fused]
    assert "a" in ids and "b" in ids
    assert len(fused) == 2

def test_rrf_handles_empty_lists():
    from app.retrieval.hybrid_retriever import reciprocal_rank_fusion
    result = reciprocal_rank_fusion([[], []], top_k=3)
    assert result == []

def test_rrf_deduplicates():
    from app.retrieval.hybrid_retriever import reciprocal_rank_fusion
    results = [{"id": "a", "text": "x", "metadata": {}}, {"id": "a", "text": "x", "metadata": {}}]
    fused = reciprocal_rank_fusion([results, results], top_k=5)
    ids = [r["id"] for r in fused]
    assert ids.count("a") == 1

def test_rrf_top_k_limits_results():
    from app.retrieval.hybrid_retriever import reciprocal_rank_fusion
    items = [{"id": str(i), "text": f"t{i}", "metadata": {}} for i in range(10)]
    fused = reciprocal_rank_fusion([items, items], top_k=3)
    assert len(fused) == 3

def test_rrf_higher_rank_scores_higher():
    from app.retrieval.hybrid_retriever import reciprocal_rank_fusion
    # "a" is rank 1 in both lists, "b" is rank 2 in both — "a" should appear first
    list1 = [{"id": "a", "text": "x", "metadata": {}}, {"id": "b", "text": "y", "metadata": {}}]
    list2 = [{"id": "a", "text": "x", "metadata": {}}, {"id": "b", "text": "y", "metadata": {}}]
    fused = reciprocal_rank_fusion([list1, list2], top_k=2)
    assert fused[0]["id"] == "a"
