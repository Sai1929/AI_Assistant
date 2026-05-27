"""Verse validator tests. Phase 2 — BibleStore + VerseValidator TDD."""
import pytest
import sys
sys.path.insert(0, ".")


# ---------------------------------------------------------------------------
# BibleStore tests
# ---------------------------------------------------------------------------

def test_exact_lookup_returns_known_verse():
    from app.retrieval.bible_store import BibleStore
    store = BibleStore()
    store.load_from_files("data/bibles")
    result = store.exact_lookup("John", 3, 16, "kjv")
    assert result is not None
    assert "God so loved" in result or "god so loved" in result.lower()


def test_exact_lookup_returns_none_for_fake_book():
    from app.retrieval.bible_store import BibleStore
    store = BibleStore()
    store.load_from_files("data/bibles")
    result = store.exact_lookup("Hezekiah", 4, 12, "kjv")
    assert result is None


def test_exact_lookup_returns_none_for_out_of_range_chapter():
    from app.retrieval.bible_store import BibleStore
    store = BibleStore()
    store.load_from_files("data/bibles")
    result = store.exact_lookup("Romans", 30, 5, "kjv")
    assert result is None


def test_verse_exists_true_for_real():
    from app.retrieval.bible_store import BibleStore
    store = BibleStore()
    store.load_from_files("data/bibles")
    assert store.verse_exists("Genesis", 1, 1, "kjv") is True


def test_verse_exists_false_for_fake():
    from app.retrieval.bible_store import BibleStore
    store = BibleStore()
    store.load_from_files("data/bibles")
    assert store.verse_exists("Hezekiah", 4, 12, "kjv") is False


# ---------------------------------------------------------------------------
# VerseValidator tests
# ---------------------------------------------------------------------------

def test_validator_flags_fake_book():
    from app.retrieval.bible_store import BibleStore
    from app.retrieval.verse_validator import VerseValidator
    store = BibleStore()
    store.load_from_files("data/bibles")
    validator = VerseValidator(store)
    result = validator.validate("As Hezekiah 4:12 says, blessed are the meek.")
    assert len(result.invalid_citations) == 1
    assert "Hezekiah" in result.invalid_citations[0].reference


def test_validator_passes_real_verse():
    from app.retrieval.bible_store import BibleStore
    from app.retrieval.verse_validator import VerseValidator
    store = BibleStore()
    store.load_from_files("data/bibles")
    validator = VerseValidator(store)
    result = validator.validate("For God so loved the world (John 3:16).")
    assert result.is_valid
    assert len(result.valid_citations) == 1


def test_validator_flags_out_of_range_chapter():
    from app.retrieval.bible_store import BibleStore
    from app.retrieval.verse_validator import VerseValidator
    store = BibleStore()
    store.load_from_files("data/bibles")
    validator = VerseValidator(store)
    result = validator.validate("See Romans 30:5 for reference.")
    assert len(result.invalid_citations) == 1


def test_validator_mixed_valid_and_invalid():
    from app.retrieval.bible_store import BibleStore
    from app.retrieval.verse_validator import VerseValidator
    store = BibleStore()
    store.load_from_files("data/bibles")
    validator = VerseValidator(store)
    result = validator.validate("John 3:16 and Romans 8:28 are real. Hezekiah 4:12 is fake.")
    assert len(result.valid_citations) == 2
    assert len(result.invalid_citations) == 1
    assert not result.is_valid


def test_correction_hints_contain_bad_reference():
    from app.retrieval.bible_store import BibleStore
    from app.retrieval.verse_validator import VerseValidator
    store = BibleStore()
    store.load_from_files("data/bibles")
    validator = VerseValidator(store)
    result = validator.validate("Hezekiah 4:12 says something.")
    hints = result.correction_hints
    assert len(hints) == 1
    assert "Hezekiah" in hints[0]
