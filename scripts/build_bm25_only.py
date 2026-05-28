"""Build ONLY the BM25 index from Bible JSON files — skips ChromaDB entirely."""
import json, os, pickle, sys
from pathlib import Path
from itertools import groupby

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rank_bm25 import BM25Okapi
from app.config import BM25_INDEX_PATH, BIBLE_DATA_PATH

PASSAGE_WINDOW = 5

def load_verses(bibles_dir):
    verses = []
    for f in Path(bibles_dir).glob("*.json"):
        print(f"  Loading {f.name}...")
        verses.extend(json.loads(f.read_text(encoding="utf-8")))
    return verses

def make_verse_chunks(verses):
    return [{"text": v["text"], "metadata": {"book": v["book"], "chapter": int(v["chapter"]),
        "verse": int(v["verse"]), "translation": v["translation"].lower(),
        "chunk_type": "verse", "reference": f"{v['book']} {v['chapter']}:{v['verse']}"}}
        for v in verses]

def make_passage_chunks(verses):
    chunks = []
    key_fn = lambda v: (v["translation"].lower(), v["book"].lower(), int(v["chapter"]))
    for (trans, book, ch), group in groupby(sorted(verses, key=key_fn), key=key_fn):
        group_list = list(group)
        for i in range(0, len(group_list), PASSAGE_WINDOW):
            window = group_list[i:i+PASSAGE_WINDOW]
            v_start, v_end = int(window[0]["verse"]), int(window[-1]["verse"])
            book_display = window[0]["book"]
            chunks.append({"text": " ".join(v["text"] for v in window),
                "metadata": {"book": book_display, "chapter": ch, "verse_start": v_start,
                    "verse_end": v_end, "translation": trans, "chunk_type": "passage",
                    "reference": f"{book_display} {ch}:{v_start}-{v_end}"}})
    return chunks

print("Loading verses...")
verses = load_verses(BIBLE_DATA_PATH)
print(f"Loaded {len(verses)} verses")

print("Building chunks...")
all_chunks = make_verse_chunks(verses) + make_passage_chunks(verses)
print(f"Total chunks: {len(all_chunks)}")

print("Building BM25 index...")
corpus = [c["text"].lower().split() for c in all_chunks]
bm25 = BM25Okapi(corpus)
payload = {"bm25": bm25, "metadata": [c["metadata"] for c in all_chunks], "texts": [c["text"] for c in all_chunks]}

Path(BM25_INDEX_PATH).parent.mkdir(parents=True, exist_ok=True)
with open(BM25_INDEX_PATH, "wb") as f:
    pickle.dump(payload, f)
print(f"BM25 saved to {BM25_INDEX_PATH}")
