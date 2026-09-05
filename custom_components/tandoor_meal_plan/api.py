"""Minimal client for the Tandoor API."""
from __future__ import annotations

import datetime
import logging
from typing import Any

import aiohttp

from homeassistant.util import dt as dt_util

from .const import (
    DAYS_AHEAD,
    MEAL_PLAN_ENDPOINT,
    RECIPE_ENDPOINT,
    RECIPE_PAGE_SIZE,
    SHOPPING_LIST_ENTRY_ENDPOINT,
)

_LOGGER = logging.getLogger(__name__)


class TandoorAuthError(Exception):
    """Raised when the API token is rejected."""


class TandoorConnectionError(Exception):
    """Raised when the Tandoor server can't be reached."""


async def _request(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    api_token: str,
    *,
    params: dict | None = None,
    json: dict | None = None,
) -> Any:
    """Make an authenticated request to Tandoor and return the parsed JSON body.

    Raises TandoorAuthError or TandoorConnectionError on failure.
    """
    headers = {"Authorization": f"Bearer {api_token}"}
    try:
        async with session.request(
            method,
            url,
            params=params,
            json=json,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as response:
            if response.status in (401, 403):
                body = await response.text()
                _LOGGER.warning(
                    "Tandoor rejected the API token (HTTP %s) for %s %s: %s",
                    response.status,
                    method,
                    response.url.with_query(None),
                    body,
                )
                raise TandoorAuthError(f"Tandoor rejected the API token ({response.status})")
            response.raise_for_status()
            if response.status == 204 or not await response.read():
                return None
            return await response.json()
    except aiohttp.ClientError as err:
        raise TandoorConnectionError(str(err)) from err


def _endpoint(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


async def async_fetch_meal_plan(
    session: aiohttp.ClientSession, url: str, api_token: str
) -> list[dict]:
    """Fetch the upcoming meal plan from Tandoor and normalize its dates."""
    today = dt_util.now().date()
    to_date = today + datetime.timedelta(days=DAYS_AHEAD)
    params = {"from_date": today.isoformat(), "to_date": to_date.isoformat()}

    data = await _request(
        session, "GET", _endpoint(url, MEAL_PLAN_ENDPOINT), api_token, params=params
    )
    meals = data.get("results", data) if isinstance(data, dict) else data
    return [_normalize_meal_dates(meal) for meal in meals]


def _normalize_meal_dates(meal: dict) -> dict:
    """Convert from_date/to_date to local YYYY-MM-DD strings.

    Tandoor returns timestamps with a UTC offset; without this, meals can
    land on the wrong local day depending on the time of day they were
    scheduled.
    """
    for field in ("from_date", "to_date"):
        value = meal.get(field)
        if not value:
            continue
        try:
            parsed = datetime.datetime.fromisoformat(value)
        except ValueError:
            continue
        meal[field] = dt_util.as_local(parsed).strftime("%Y-%m-%d")
    return meal


async def async_fetch_shopping_list(
    session: aiohttp.ClientSession, url: str, api_token: str
) -> list[dict]:
    """Fetch all shopping list entries."""
    data = await _request(
        session,
        "GET",
        _endpoint(url, SHOPPING_LIST_ENTRY_ENDPOINT),
        api_token,
        params={"page_size": 200},
    )
    return data.get("results", data) if isinstance(data, dict) else data


async def async_create_shopping_list_item(
    session: aiohttp.ClientSession, url: str, api_token: str, name: str
) -> dict:
    """Add a new item to the shopping list, creating the underlying food if needed."""
    return await _request(
        session,
        "POST",
        _endpoint(url, SHOPPING_LIST_ENTRY_ENDPOINT),
        api_token,
        json={"food": {"name": name}, "amount": 1},
    )


async def async_set_shopping_list_item_checked(
    session: aiohttp.ClientSession, url: str, api_token: str, entry_id: str, checked: bool
) -> dict:
    """Mark a shopping list entry as checked/unchecked."""
    return await _request(
        session,
        "PATCH",
        _endpoint(url, f"{SHOPPING_LIST_ENTRY_ENDPOINT}{entry_id}/"),
        api_token,
        json={"checked": checked},
    )


async def async_delete_shopping_list_item(
    session: aiohttp.ClientSession, url: str, api_token: str, entry_id: str
) -> None:
    """Delete a shopping list entry."""
    await _request(
        session, "DELETE", _endpoint(url, f"{SHOPPING_LIST_ENTRY_ENDPOINT}{entry_id}/"), api_token
    )


async def async_fetch_recipes(
    session: aiohttp.ClientSession,
    url: str,
    api_token: str,
    *,
    query: str | None = None,
    page_size: int = RECIPE_PAGE_SIZE,
) -> dict:
    """Search/list recipes. Returns {'count': int, 'results': [...]}."""
    params: dict[str, Any] = {"page_size": page_size}
    if query:
        params["query"] = query

    return await _request(
        session, "GET", _endpoint(url, RECIPE_ENDPOINT), api_token, params=params
    )


async def async_fetch_recipe_detail(
    session: aiohttp.ClientSession, url: str, api_token: str, recipe_id: int
) -> dict:
    """Fetch full recipe detail (steps, ingredients, image) for one recipe."""
    return await _request(
        session, "GET", _endpoint(url, f"{RECIPE_ENDPOINT}{recipe_id}/"), api_token
    )
