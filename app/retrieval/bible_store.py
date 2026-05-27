"""O(1) verse hashmap store. Phase 2 implementation."""
import json
import os
from typing import Optional


class BibleStore:
    """
    Loads Bible JSON files and provides O(1) verse lookups via a hashmap.

    Key: (book_lower, chapter: int, verse: int, translation_lower) -> text: str
    JSON format (per verse dict):
        {"book": str, "chapter": int, "verse": int, "text": str, "translation": str, ...}
    """

    def __init__(self):
        self._hashmap: dict[tuple, str] = {}
        self._loaded = False

    def load_from_files(self, bibles_dir: str) -> None:
        """
        Read all *.json files in bibles_dir, parse each verse, and build
        the O(1) hashmap keyed by (book_lower, chapter, verse, translation_lower).
        """
        self._hashmap.clear()

        for filename in os.listdir(bibles_dir):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(bibles_dir, filename)
            with open(filepath, encoding="utf-8") as fh:
                verses = json.load(fh)

            for entry in verses:
                book = entry.get("book", "")
                chapter = int(entry.get("chapter", 0))
                verse = int(entry.get("verse", 0))
                text = entry.get("text", "")
                translation = entry.get("translation", "")

                key = (book.lower(), chapter, verse, translation.lower())
                self._hashmap[key] = text

        self._loaded = True

    def exact_lookup(
        self,
        book: str,
        chapter: int,
        verse: int,
        translation: str = "kjv",
    ) -> Optional[str]:
        """Return verse text for (book, chapter, verse, translation), or None if not found."""
        key = (book.lower(), chapter, verse, translation.lower())
        return self._hashmap.get(key)

    def verse_exists(
        self,
        book: str,
        chapter: int,
        verse: int,
        translation: str = "kjv",
    ) -> bool:
        """Return True if the verse exists in the hashmap."""
        return self.exact_lookup(book, chapter, verse, translation) is not None

    def get_all_verses(self, translation: str = "kjv") -> list[dict]:
        """Return all verses for the given translation as a list of dicts."""
        tl = translation.lower()
        results = []
        for (book, chapter, verse, trans), text in self._hashmap.items():
            if trans == tl:
                results.append({
                    "book": book,
                    "chapter": chapter,
                    "verse": verse,
                    "translation": trans,
                    "text": text,
                })
        return results
