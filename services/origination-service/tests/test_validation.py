"""Request-validation tests for the application schema (these PASS)."""
import pytest
from pydantic import ValidationError

from app.schemas import ApplicationIn


def test_valid_application():
    a = ApplicationIn(name="Test Borrower", amount=10000, term_months=36)
    assert a.amount == 10000
    assert a.term_months == 36


def test_amount_over_cap_rejected():
    with pytest.raises(ValidationError):
        ApplicationIn(name="Test", amount=75000, term_months=36)


def test_term_out_of_range_rejected():
    with pytest.raises(ValidationError):
        ApplicationIn(name="Test", amount=10000, term_months=6)


def test_name_required():
    with pytest.raises(ValidationError):
        ApplicationIn(name="", amount=10000)
