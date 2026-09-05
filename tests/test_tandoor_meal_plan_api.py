"""Tests for the Tandoor meal-plan API client."""
import aiohttp
import pytest

from custom_components.tandoor_meal_plan.api import (
    TandoorAuthError,
    TandoorConnectionError,
    _normalize_meal_dates,
    async_fetch_meal_plan,
)

MEAL_PLAN_URL = "http://tandoor.local:8002/api/meal-plan/"


def test_normalize_meal_dates_converts_utc_offset_to_local_date() -> None:
    # 2026-01-05T23:30:00+05:00 is 2026-01-05T18:30:00 UTC; with HA's default
    # time zone (UTC) that should stay on the same local calendar day.
    meal = {"from_date": "2026-01-05T23:30:00+05:00", "to_date": None, "title": "Dinner"}

    normalized = _normalize_meal_dates(meal)

    assert normalized["from_date"] == "2026-01-05"
    assert normalized["to_date"] is None
    assert normalized["title"] == "Dinner"


def test_normalize_meal_dates_ignores_unparseable_values() -> None:
    meal = {"from_date": "not-a-date"}

    normalized = _normalize_meal_dates(meal)

    assert normalized["from_date"] == "not-a-date"


async def test_async_fetch_meal_plan_returns_normalized_meals(aioclient_mock) -> None:
    aioclient_mock.get(
        MEAL_PLAN_URL,
        json={"results": [{"from_date": "2026-01-05T12:00:00+00:00", "title": "Tacos"}]},
    )

    async with aiohttp.ClientSession() as session:
        meals = await async_fetch_meal_plan(session, "http://tandoor.local:8002", "tok123")

    assert meals == [{"from_date": "2026-01-05", "title": "Tacos"}]


async def test_async_fetch_meal_plan_raises_on_401(aioclient_mock) -> None:
    aioclient_mock.get(MEAL_PLAN_URL, status=401)

    async with aiohttp.ClientSession() as session:
        with pytest.raises(TandoorAuthError):
            await async_fetch_meal_plan(session, "http://tandoor.local:8002", "bad-token")


async def test_async_fetch_meal_plan_raises_on_403(aioclient_mock) -> None:
    # Tandoor's own DRF-based API returns 403 (not 401) for a missing/invalid token.
    aioclient_mock.get(MEAL_PLAN_URL, status=403)

    async with aiohttp.ClientSession() as session:
        with pytest.raises(TandoorAuthError):
            await async_fetch_meal_plan(session, "http://tandoor.local:8002", "bad-token")


async def test_async_fetch_meal_plan_raises_on_connection_error(aioclient_mock) -> None:
    aioclient_mock.get(MEAL_PLAN_URL, exc=aiohttp.ClientConnectionError())

    async with aiohttp.ClientSession() as session:
        with pytest.raises(TandoorConnectionError):
            await async_fetch_meal_plan(session, "http://tandoor.local:8002", "tok123")
