"""BM25 + Jina dense + RRF hybrid retriever. Stub — implemented in Phase 3 Task 8."""


def reciprocal_rank_fusion(result_lists: list[list[dict]], top_k: int = 3, k: int = 60) -> list[dict]:
    raise NotImplementedError("Implement in Phase 3 Task 8")


class HybridRetriever:
    def __init__(self):
        pass

    def search(self, query: str, top_k: int = 3, translation: str | None = None) -> list[dict]:
        raise NotImplementedError("Implement in Phase 3 Task 8")
