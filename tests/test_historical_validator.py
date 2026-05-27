"""Historical validator tests. Phase 2 TDD."""
import pytest
import sys
sys.path.insert(0, ".")


def test_correct_nicaea_date_passes():
    from app.retrieval.historical_validator import HistoricalValidator
    v = HistoricalValidator("data/historical_facts.json")
    result = v.validate("The Council of Nicaea in 325 AD established Trinity doctrine.")
    assert result.is_clean


def test_wrong_nicaea_date_flagged():
    from app.retrieval.historical_validator import HistoricalValidator
    v = HistoricalValidator("data/historical_facts.json")
    result = v.validate("The Council of Nicaea was held in 329 AD.")
    assert not result.is_clean
    assert len(result.unverified) >= 1


def test_no_claims_returns_clean():
    from app.retrieval.historical_validator import HistoricalValidator
    v = HistoricalValidator("data/historical_facts.json")
    result = v.validate("Jesus loves us. God is good.")
    assert result.is_clean


def test_correct_luther_date_passes():
    from app.retrieval.historical_validator import HistoricalValidator
    v = HistoricalValidator("data/historical_facts.json")
    result = v.validate("Martin Luther posted his theses in 1517.")
    assert result.is_clean
