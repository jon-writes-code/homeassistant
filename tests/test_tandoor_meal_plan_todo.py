"""Tests for the shopping-list item summary formatting."""
from custom_components.tandoor_meal_plan.todo import _format_summary


def test_format_summary_plain_item_no_amount() -> None:
    assert _format_summary({"food": {"name": "Milk"}, "amount": 1, "unit": None}) == "Milk"


def test_format_summary_missing_amount() -> None:
    assert _format_summary({"food": {"name": "Eggs"}, "amount": None, "unit": None}) == "Eggs"


def test_format_summary_amount_with_unit() -> None:
    result = _format_summary({"food": {"name": "Flour"}, "amount": 2, "unit": {"name": "kg"}})
    assert result == "2 kg Flour"


def test_format_summary_fractional_amount_no_unit() -> None:
    result = _format_summary({"food": {"name": "Lemon"}, "amount": 0.5, "unit": None})
    assert result == "0.5 Lemon"
