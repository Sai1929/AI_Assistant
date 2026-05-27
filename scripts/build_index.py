"""Build ChromaDB vector index + BM25 index from Bible corpus."""
import json
import os
import pickle
import sys
import time
from itertools import groupby
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from rank_bm25 import BM25Okapi

from app.config import CHROMA_DB_PATH, BM25_INDEX_PATH, BIBLE_DATA_PATH
from app.core.embeddings import embed_texts

BATCH_SIZE = 50
PASSAGE_WINDOW = 5


def load_verses(bibles_dir: str) -> list[dict]:
    verses = []
    for f in Path(bibles_dir).glob("*.json"):
        verses.extend(json.loads(f.read_text(encoding="utf-8")))
    return verses


def make_verse_chunks(verses: list[dict]) -> list[dict]:
    return [
        {
            "id": f"{v['translation'].lower()}_{v['book'].lower().replace(' ', '_')}_{v['chapter']}_{v['verse']}",
            "text": v["text"],
            "metadata": {
                "book": v["book"],
                "chapter": int(v["chapter"]),
                "verse": int(v["verse"]),
                "translation": v["translation"].lower(),
                "chunk_type": "verse",
                "reference": f"{v['book']} {v['chapter']}:{v['verse']}",
            },
        }
        for v in verses
    ]


def make_passage_chunks(verses: list[dict]) -> list[dict]:
    chunks = []
    key_fn = lambda v: (v["translation"].lower(), v["book"].lower(), int(v["chapter"]))
    sorted_verses = sorted(verses, key=key_fn)
    for (trans, book, ch), group in groupby(sorted_verses, key=key_fn):
        group_list = list(group)
        for i in range(0, len(group_list), PASSAGE_WINDOW):
            window = group_list[i : i + PASSAGE_WINDOW]
            combined = " ".join(v["text"] for v in window)
            v_start = int(window[0]["verse"])
            v_end = int(window[-1]["verse"])
            book_display = window[0]["book"]
            chunks.append({
                "id": f"passage_{trans}_{book}_{ch}_{v_start}_{v_end}",
                "text": combined,
                "metadata": {
                    "book": book_display,
                    "chapter": ch,
                    "verse_start": v_start,
                    "verse_end": v_end,
                    "translation": trans,
                    "chunk_type": "passage",
                    "reference": f"{book_display} {ch}:{v_start}-{v_end}",
                },
            })
    return chunks


def index_to_chroma(chunks: list[dict], client: chromadb.Client) -> None:
    collection = client.get_or_create_collection("bible_verses")
    total = len(chunks)
    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        embeddings = embed_texts(texts)
        collection.add(
            ids=[c["id"] for c in batch],
            embeddings=embeddings,
            documents=texts,
            metadatas=[c["metadata"] for c in batch],
        )
        print(f"  ChromaDB: {min(i + BATCH_SIZE, total)}/{total}")
        time.sleep(0.5)


def build_bm25(chunks: list[dict]) -> None:
    corpus = [c["text"].lower().split() for c in chunks]
    bm25 = BM25Okapi(corpus)
    payload = {
        "bm25": bm25,
        "metadata": [c["metadata"] for c in chunks],
        "texts": [c["text"] for c in chunks],
    }
    Path(BM25_INDEX_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump(payload, f)
    print(f"BM25 saved to {BM25_INDEX_PATH}")


if __name__ == "__main__":
    print("Loading verses...")
    verses = load_verses(BIBLE_DATA_PATH)
    print(f"Loaded {len(verses)} verses")

    print("Building verse chunks...")
    verse_chunks = make_verse_chunks(verses)

    print("Building passage chunks...")
    passage_chunks = make_passage_chunks(verses)

    all_chunks = verse_chunks + passage_chunks
    print(f"Total: {len(all_chunks)} chunks ({len(verse_chunks)} verse, {len(passage_chunks)} passage)")

    print("Indexing to ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    index_to_chroma(all_chunks, client)

    print("Building BM25 index...")
    build_bm25(all_chunks)
    print("Done.")
