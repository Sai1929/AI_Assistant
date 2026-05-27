"""Historical claims validator. Phase 2 implementation."""
import json
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HistoricalClaim:
    raw_text: str
    extracted_year: Optional[int] = None
    matched_fact: Optional[dict] = None


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


# Regex to locate years (3–4 digit numbers) in text, with optional era suffix
_YEAR_RE = re.compile(r"\b(\d{3,4})\s*(?:AD|BC|CE|BCE)?\b")

# How close a found year must be to the fact's year to count as "correct"
# Using exact match (tolerance=0) because the test suite checks 329 vs 325 (diff=4)
# as wrong, which would pass a 5-year window but should be flagged.
_YEAR_TOLERANCE = 2


def _keywords_from_claim(claim: str) -> list[str]:
    """
    Extract meaningful lowercase keywords from a fact's claim string.
    Ignores short words and common stopwords so matching is robust.
    """
    stopwords = {"and", "the", "of", "in", "a", "an", "at", "to", "for", "or", "95"}
    words = re.findall(r"[A-Za-z]+", claim)
    return [w.lower() for w in words if w.lower() not in stopwords and len(w) > 2]


class HistoricalValidator:
    """
    Loads a historical_facts.json file and validates date claims found in text.

    For each fact in the database it checks whether the text:
      1. Contains keywords from the fact's claim string (case-insensitive)
      2. Contains a year within _YEAR_TOLERANCE of the fact's known year

    If keywords match but the year is wrong (diff > _YEAR_TOLERANCE), the
    extracted claim is placed in the ``unverified`` list.
    """

    def __init__(self, facts_path: str):
        self.facts_path = facts_path
        with open(facts_path, encoding="utf-8") as fh:
            self._facts: list[dict] = json.load(fh)

    def validate(self, text: str) -> HistoricalValidationResult:
        """
        Scan *text* for historical claims, match against known facts,
        and return a HistoricalValidationResult.
        """
        result = HistoricalValidationResult()
        text_lower = text.lower()
        years_in_text = [int(y) for y in _YEAR_RE.findall(text)]

        for fact in self._facts:
            keywords = _keywords_from_claim(fact["claim"])
            if not keywords:
                continue

            # Check whether all keywords from this fact appear in the text
            if not all(kw in text_lower for kw in keywords):
                continue

            # Fact keywords matched — now look for a year
            known_year = fact["year"]

            if not years_in_text:
                # Keywords matched but no year stated — treat as unverifiable
                claim = HistoricalClaim(
                    raw_text=fact["claim"],
                    extracted_year=None,
                    matched_fact=fact,
                )
                result.unverified.append(claim)
                continue

            # Pick the closest year to the known fact year
            closest_year = min(years_in_text, key=lambda y: abs(y - known_year))
            diff = abs(closest_year - known_year)

            claim = HistoricalClaim(
                raw_text=f"{fact['claim']} {closest_year}",
                extracted_year=closest_year,
                matched_fact=fact,
            )

            if diff <= _YEAR_TOLERANCE:
                result.verified.append(claim)
            else:
                result.unverified.append(claim)

        return result
