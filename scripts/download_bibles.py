"""
Download KJV, WEB (NHEB), and DRA Bible JSON from scrollmapper GitHub,
normalize to a flat list of verse dicts, and save to data/bibles/.

Scrollmapper moved translations to:
  https://raw.githubusercontent.com/scrollmapper/bible_databases/master/formats/json/<NAME>.json

Each file has the structure:
  {
    "translation": "...",
    "books": [
      {
        "name": "Genesis",
        "chapters": [
          {
            "chapter": 1,
            "verses": [
              {"verse": 1, "text": "..."},
              ...
            ]
          }
        ]
      }
    ]
  }

This script also handles the legacy scrollmapper format:
  {"resultset": {"row": [{"field": [b, c, v, "text"]}, ...]}}

Output format per verse:
  {
    "book_num":    int,   # 1-66
    "book":        str,   # e.g. "Genesis"
    "chapter":     int,
    "verse":       int,
    "text":        str,
    "translation": str    # "KJV" | "WEB" | "DRA"
  }
"""

import json
import os
import urllib.request

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = (
    "https://raw.githubusercontent.com/scrollmapper/"
    "bible_databases/master/formats/json/{filename}"
)

TRANSLATIONS = [
    # (short_key, remote_filename, output_filename)
    ("KJV", "KJV.json",  "kjv.json"),
    ("WEB", "NHEB.json", "web.json"),   # NHEB is the open WEB successor
    ("DRA", "DRC.json",  "dra.json"),   # DRC = Douay-Rheims Challoner
]

BOOK_NAMES = {
    1: "Genesis", 2: "Exodus", 3: "Leviticus", 4: "Numbers", 5: "Deuteronomy",
    6: "Joshua", 7: "Judges", 8: "Ruth", 9: "1 Samuel", 10: "2 Samuel",
    11: "1 Kings", 12: "2 Kings", 13: "1 Chronicles", 14: "2 Chronicles",
    15: "Ezra", 16: "Nehemiah", 17: "Esther", 18: "Job", 19: "Psalms",
    20: "Proverbs", 21: "Ecclesiastes", 22: "Song of Solomon", 23: "Isaiah",
    24: "Jeremiah", 25: "Lamentations", 26: "Ezekiel", 27: "Daniel",
    28: "Hosea", 29: "Joel", 30: "Amos", 31: "Obadiah", 32: "Jonah",
    33: "Micah", 34: "Nahum", 35: "Habakkuk", 36: "Zephaniah", 37: "Haggai",
    38: "Zechariah", 39: "Malachi", 40: "Matthew", 41: "Mark", 42: "Luke",
    43: "John", 44: "Acts", 45: "Romans", 46: "1 Corinthians", 47: "2 Corinthians",
    48: "Galatians", 49: "Ephesians", 50: "Philippians", 51: "Colossians",
    52: "1 Thessalonians", 53: "2 Thessalonians", 54: "1 Timothy", 55: "2 Timothy",
    56: "Titus", 57: "Philemon", 58: "Hebrews", 59: "James", 60: "1 Peter",
    61: "2 Peter", 62: "1 John", 63: "2 John", 64: "3 John", 65: "Jude",
    66: "Revelation",
}

# Reverse map: canonical name -> book_num (for nested format, which uses book names)
_NAME_TO_NUM = {v: k for k, v in BOOK_NAMES.items()}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_json(url: str) -> dict | list:
    """Download JSON from *url* and return the parsed object."""
    print(f"  Fetching {url} …")
    with urllib.request.urlopen(url, timeout=60) as resp:
        raw = resp.read()
    return json.loads(raw)


def _normalize_nested(data: dict, translation: str) -> list[dict]:
    """
    Parse the current scrollmapper nested format:
      {translation: str, books: [{name, chapters: [{chapter, verses: [{verse, text}]}]}]}
    """
    verses = []
    for book_obj in data.get("books", []):
        book_name = book_obj["name"]
        book_num = _NAME_TO_NUM.get(book_name)
        if book_num is None:
            # Try a fuzzy match (some translations use slight name variants)
            for num, canonical in BOOK_NAMES.items():
                if canonical.lower() == book_name.lower():
                    book_num = num
                    break
        if book_num is None:
            print(f"    WARNING: unknown book name '{book_name}', skipping.")
            continue
        for chap_obj in book_obj.get("chapters", []):
            chapter = int(chap_obj["chapter"])
            for v_obj in chap_obj.get("verses", []):
                verses.append({
                    "book_num":    book_num,
                    "book":        BOOK_NAMES[book_num],
                    "chapter":     chapter,
                    "verse":       int(v_obj["verse"]),
                    "text":        v_obj["text"].strip(),
                    "translation": translation,
                })
    return verses


def _normalize_resultset(data: dict, translation: str) -> list[dict]:
    """
    Parse the legacy scrollmapper resultset format:
      {resultset: {row: [{field: [book_num, chapter, verse, text]}, ...]}}
    """
    verses = []
    rows = data["resultset"]["row"]
    for row in rows:
        fields = row["field"]          # [book_num, chapter, verse, text]
        book_num = int(fields[0])
        chapter  = int(fields[1])
        verse    = int(fields[2])
        text     = str(fields[3]).strip()
        book_name = BOOK_NAMES.get(book_num, f"Book{book_num}")
        verses.append({
            "book_num":    book_num,
            "book":        book_name,
            "chapter":     chapter,
            "verse":       verse,
            "text":        text,
            "translation": translation,
        })
    return verses


def _normalize_flat(data: list, translation: str) -> list[dict]:
    """
    Parse a flat-list format where each element is already a verse dict.
    Expected keys: b/book_num, c/chapter, v/verse, t/text.
    """
    verses = []
    for item in data:
        book_num = int(item.get("b") or item.get("book_num", 0))
        chapter  = int(item.get("c") or item.get("chapter", 0))
        verse    = int(item.get("v") or item.get("verse", 0))
        text     = str(item.get("t") or item.get("text", "")).strip()
        book_name = BOOK_NAMES.get(book_num, f"Book{book_num}")
        verses.append({
            "book_num":    book_num,
            "book":        book_name,
            "chapter":     chapter,
            "verse":       verse,
            "text":        text,
            "translation": translation,
        })
    return verses


def normalize(data: dict | list, translation: str) -> list[dict]:
    """Dispatch to the correct normalizer based on JSON shape."""
    if isinstance(data, list):
        return _normalize_flat(data, translation)
    if "resultset" in data:
        return _normalize_resultset(data, translation)
    if "books" in data:
        return _normalize_nested(data, translation)
    raise ValueError(f"Unrecognized JSON format for translation '{translation}'")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    out_dir = os.path.join(project_root, "data", "bibles")
    os.makedirs(out_dir, exist_ok=True)

    for translation, remote_file, output_file in TRANSLATIONS:
        out_path = os.path.join(out_dir, output_file)

        if os.path.exists(out_path):
            size = os.path.getsize(out_path)
            print(f"[{translation}] Already exists ({size:,} bytes) — skipping.")
            continue

        url = BASE_URL.format(filename=remote_file)
        print(f"[{translation}] Downloading from {url}")

        try:
            raw_data = _fetch_json(url)
        except Exception as exc:
            print(f"  ERROR fetching {url}: {exc}")
            continue

        print(f"  Normalizing …")
        try:
            verses = normalize(raw_data, translation)
        except Exception as exc:
            print(f"  ERROR normalizing: {exc}")
            continue

        print(f"  Writing {len(verses):,} verses to {out_path} …")
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(verses, fh, ensure_ascii=False, indent=2)

        print(f"  Done — {os.path.getsize(out_path):,} bytes written.")

    print("\nAll downloads complete.")


if __name__ == "__main__":
    main()
