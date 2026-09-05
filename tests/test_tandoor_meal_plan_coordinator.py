"""Tests for pure coordinator helper logic."""
from integrations.tandoor_meal_plan.coordinator import _trim_recipe_detail


def test_trim_recipe_detail_keeps_only_rendered_fields() -> None:
    full = {
        "id": 1,
        "name": "Tacos",
        "image": "http://tandoor.local/media/tacos.jpg",
        "servings": 4,
        "working_time": 10,
        "waiting_time": 5,
        "description": "a long description we don't need",
        "nutrition": {"calories": 500},
        "steps": [
            {
                "name": "Prep",
                "instruction": "Chop everything",
                "ingredients": [
                    {
                        "amount": 2.0,
                        "unit": {"id": 1, "name": "cups", "plural_name": None},
                        "food": {"id": 5, "name": "Lettuce", "supermarket_category": None},
                        "note": "",
                    }
                ],
            }
        ],
    }

    trimmed = _trim_recipe_detail(full)

    assert trimmed == {
        "image": "http://tandoor.local/media/tacos.jpg",
        "servings": 4,
        "working_time": 10,
        "waiting_time": 5,
        "steps": [
            {
                "name": "Prep",
                "instruction": "Chop everything",
                "ingredients": [{"amount": 2.0, "unit": "cups", "food": "Lettuce"}],
            }
        ],
    }
    # explicitly not carried over
    assert "description" not in trimmed
    assert "nutrition" not in trimmed


def test_trim_recipe_detail_handles_missing_unit_and_food() -> None:
    full = {"steps": [{"ingredients": [{"amount": 1, "unit": None, "food": None}]}]}

    trimmed = _trim_recipe_detail(full)

    assert trimmed["steps"][0]["ingredients"][0] == {"amount": 1, "unit": None, "food": None}
