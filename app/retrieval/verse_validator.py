"""Hallucination prevention — verse citation extractor and validator. Phase 2."""
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Citation:
    reference: str
    book: str
    chapter: int
    verse_start: int
    verse_end: Optional[int]
    verified_text: Optional[str] = None


@dataclass
class ValidationResult:
    valid_citations: list[Citation] = field(default_factory=list)
    invalid_citations: list[Citation] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.invalid_citations) == 0

    @property
    def correction_hints(self) -> list[str]:
        return [
            f"Citation '{c.reference}' does not exist. Remove or correct it."
            for c in self.invalid_citations
        ]


# Pattern: optional leading number (1/2/3), book name, chapter:verse[-verse_end]
_CITATION_RE = re.compile(
    r"\b((?:[123]\s?)?[A-Z][a-zA-Z]+)\s+(\d+):(\d+)(?:-(\d+))?\b"
)


class VerseValidator:
    def __init__(self, store, translation: str = "kjv"):
        self.store = store
        self.translation = translation

    def extract_citations(self, text: str) -> list[Citation]:
        """
        Scan *text* for Bible references using the pattern:
            <Book> <chapter>:<verse_start>[-verse_end]
        Book may have an optional leading digit (1 John, 2 Kings, etc.).
        Returns a list of Citation objects (not yet verified).
        """
        citations: list[Citation] = []
        for match in _CITATION_RE.finditer(text):
            book_raw = match.group(1)
            chapter = int(match.group(2))
            verse_start = int(match.group(3))
            verse_end = int(match.group(4)) if match.group(4) else None
            reference = match.group(0)
            citations.append(Citation(
                reference=reference,
                book=book_raw,
                chapter=chapter,
                verse_start=verse_start,
                verse_end=verse_end,
            ))
        return citations

    def validate(self, text: str) -> ValidationResult:
        """
        Extract all Bible citations from *text*, look each one up in the
        BibleStore, and return a ValidationResult separating valid from invalid.
        """
        result = ValidationResult()
        citations = self.extract_citations(text)

        for citation in citations:
            text_found = self.store.exact_lookup(
                citation.book,
                citation.chapter,
                citation.verse_start,
                self.translation,
            )
            if text_found is not None:
                citation.verified_text = text_found
                result.valid_citations.append(citation)
            else:
                result.invalid_citations.append(citation)

        return result
