"""Tests for the Tandoor shopping-list and recipe API client functions."""
import aiohttp
import pytest

from custom_components.tandoor_meal_plan.api import (
    TandoorAuthError,
    async_create_shopping_list_item,
    async_delete_shopping_list_item,
    async_fetch_recipe_detail,
    async_fetch_recipes,
    async_fetch_shopping_list,
    async_set_shopping_list_item_checked,
)

BASE_URL = "http://tandoor.local:8002"
SHOPPING_LIST_URL = f"{BASE_URL}/api/shopping-list-entry/"
RECIPE_URL = f"{BASE_URL}/api/recipe/"


async def test_async_fetch_shopping_list_returns_entries(aioclient_mock) -> None:
    aioclient_mock.get(
        SHOPPING_LIST_URL,
        json={"results": [{"id": 1, "food": {"name": "Milk"}, "amount": 1, "checked": False}]},
    )

    async with aiohttp.ClientSession() as session:
        entries = await async_fetch_shopping_list(session, BASE_URL, "tok123")

    assert entries == [{"id": 1, "food": {"name": "Milk"}, "amount": 1, "checked": False}]


async def test_async_create_shopping_list_item_sends_food_name(aioclient_mock) -> None:
    aioclient_mock.post(SHOPPING_LIST_URL, json={"id": 2})

    async with aiohttp.ClientSession() as session:
        await async_create_shopping_list_item(session, BASE_URL, "tok123", "Eggs")

    method, url, data, _headers = aioclient_mock.mock_calls[-1]
    assert method == "post"
    assert data == {"food": {"name": "Eggs"}, "amount": 1}


async def test_async_set_shopping_list_item_checked_sends_patch(aioclient_mock) -> None:
    aioclient_mock.patch(f"{SHOPPING_LIST_URL}5/", json={"id": 5, "checked": True})

    async with aiohttp.ClientSession() as session:
        await async_set_shopping_list_item_checked(session, BASE_URL, "tok123", "5", True)

    method, url, data, _headers = aioclient_mock.mock_calls[-1]
    assert method == "patch"
    assert data == {"checked": True}


async def test_async_delete_shopping_list_item_calls_delete(aioclient_mock) -> None:
    aioclient_mock.delete(f"{SHOPPING_LIST_URL}5/", status=204)

    async with aiohttp.ClientSession() as session:
        await async_delete_shopping_list_item(session, BASE_URL, "tok123", "5")

    method, url, _data, _headers = aioclient_mock.mock_calls[-1]
    assert method == "delete"


async def test_async_fetch_recipes_returns_count_and_results(aioclient_mock) -> None:
    aioclient_mock.get(
        RECIPE_URL,
        json={"count": 2, "results": [{"id": 1, "name": "Tacos"}, {"id": 2, "name": "Chili"}]},
    )

    async with aiohttp.ClientSession() as session:
        data = await async_fetch_recipes(session, BASE_URL, "tok123")

    assert data["count"] == 2
    assert [r["name"] for r in data["results"]] == ["Tacos", "Chili"]


async def test_async_fetch_recipe_detail_returns_full_recipe(aioclient_mock) -> None:
    aioclient_mock.get(
        f"{RECIPE_URL}42/",
        json={"id": 42, "name": "Tacos", "steps": [{"instruction": "Cook it", "ingredients": []}]},
    )

    async with aiohttp.ClientSession() as session:
        recipe = await async_fetch_recipe_detail(session, BASE_URL, "tok123", 42)

    assert recipe["name"] == "Tacos"
    assert recipe["steps"][0]["instruction"] == "Cook it"


async def test_async_fetch_recipes_raises_on_auth_error(aioclient_mock) -> None:
    aioclient_mock.get(RECIPE_URL, status=403)

    async with aiohttp.ClientSession() as session:
        with pytest.raises(TandoorAuthError):
            await async_fetch_recipes(session, BASE_URL, "bad-token")
