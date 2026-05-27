"""Historical claims validator. Stub — implemented in Phase 2 Task 6."""
from dataclasses import dataclass, field


@dataclass
class HistoricalClaim:
    raw_text: str
    extracted_year: int | None = None
    matched_fact: dict | None = None


@dataclass
class HistoricalValidationResult:
    verified: list[HistoricalClaim] = field(default_factory=list)
    unverified: list[HistoricalClaim] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.unverified) == 0

    @property
    def uncertainty_notes(self) -> list[str]:
        return [
            f"Cannot verify: '{c.raw_text}'. Please confirm."
            for c in self.unverified
        ]


class HistoricalValidator:
    def __init__(self, facts_path: str):
        self.facts_path = facts_path

    def validate(self, text: str) -> HistoricalValidationResult:
        raise NotImplementedError("Implement in Phase 2 Task 6")
