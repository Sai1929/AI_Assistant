"""Verse validator tests. RED phase — implemented in Phase 2 Tasks 4+5."""
import pytest
import sys
sys.path.insert(0, ".")


def test_placeholder_fails():
    """Placeholder: remove once real tests written in Phase 2."""
    from app.retrieval.bible_store import BibleStore
    store = BibleStore()
    with pytest.raises(NotImplementedError):
        store.load_from_files("data/bibles")
