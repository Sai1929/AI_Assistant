# app/retrieval/hybrid_retriever.py
import pickle
from pathlib import Path


def reciprocal_rank_fusion(
    result_lists: list[list[dict]], top_k: int = 3, k: int = 60
) -> list[dict]:
    """RRF: score(doc) = sum(1 / (k + rank)) across all lists. Parameter-free."""
    scores: dict[str, float] = {}
    doc_map: dict[str, dict] = {}
    for result_list in result_lists:
        for rank, doc in enumerate(result_list, start=1):
            doc_id = doc["id"]
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            if doc_id not in doc_map:
                doc_map[doc_id] = doc
    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
    return [doc_map[i] for i in sorted_ids[:top_k]]


class HybridRetriever:
    """BM25 + Jina dense + RRF fusion retriever over dual-chunked Bible corpus."""

    def __init__(self):
        import chromadb
        from app.core.embeddings import embed_query as _embed_query
        from app.config import CHROMA_DB_PATH, BM25_INDEX_PATH, BM25_TOP_K, DENSE_TOP_K, FUSED_TOP_K

        self._embed_query = _embed_query
        self._bm25_top_k = BM25_TOP_K
        self._dense_top_k = DENSE_TOP_K
        self._fused_top_k = FUSED_TOP_K

        self._chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self._collection = self._chroma_client.get_collection("bible_verses")
        index_path = Path(BM25_INDEX_PATH)
        if not index_path.exists():
            raise FileNotFoundError(
                f"BM25 index not found at {BM25_INDEX_PATH}. Run scripts/build_index.py first."
            )
        with open(BM25_INDEX_PATH, "rb") as f:
            data = pickle.load(f)
        self._bm25 = data["bm25"]
        self._bm25_meta = data["metadata"]
        self._bm25_texts = data["texts"]

    def _dense_search(self, query: str, top_k: int | None = None) -> list[dict]:
        if top_k is None:
            top_k = self._dense_top_k
        vector = self._embed_query(query)
        results = self._collection.query(query_embeddings=[vector], n_results=top_k)
        docs = []
        for i, doc_id in enumerate(results["ids"][0]):
            docs.append({
                "id": doc_id,
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": results["distances"][0][i] if results.get("distances") else 0.0,
            })
        return docs

    def _bm25_search(self, query: str, top_k: int | None = None) -> list[dict]:
        if top_k is None:
            top_k = self._bm25_top_k
        tokens = query.lower().split()
        bm25_scores = self._bm25.get_scores(tokens)
        top_indices = sorted(
            range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True
        )[:top_k]
        return [
            {
                "id": f"bm25_{i}",
                "text": self._bm25_texts[i],
                "metadata": self._bm25_meta[i],
                "score": float(bm25_scores[i]),
            }
            for i in top_indices
        ]

    def search(
        self,
        query: str,
        top_k: int | None = None,
        translation: str | None = None,
    ) -> list[dict]:
        if top_k is None:
            top_k = self._fused_top_k
        dense = self._dense_search(query)
        bm25 = self._bm25_search(query)
        if translation:
            t = translation.lower()
            dense = [d for d in dense if d["metadata"].get("translation") == t]
            bm25 = [d for d in bm25 if d["metadata"].get("translation") == t]
        return reciprocal_rank_fusion([bm25, dense], top_k=top_k)
