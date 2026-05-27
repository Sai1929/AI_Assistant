"""Hallucination prevention core. Stub — implemented in Phase 2 Task 5."""
from dataclasses import dataclass, field


@dataclass
class Citation:
    reference: str
    book: str
    chapter: int
    verse_start: int
    verse_end: int | None
    verified_text: str | None = None


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


class VerseValidator:
    def __init__(self, store, translation: str = "kjv"):
        self.store = store
        self.translation = translation

    def extract_citations(self, text: str) -> list[Citation]:
        raise NotImplementedError("Implement in Phase 2 Task 5")

    def validate(self, text: str) -> ValidationResult:
        raise NotImplementedError("Implement in Phase 2 Task 5")
