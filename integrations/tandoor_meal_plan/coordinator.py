"""Data update coordinators for the Tandoor Meal Plan integration."""
from __future__ import annotations

import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    TandoorAuthError,
    TandoorConnectionError,
    async_fetch_meal_plan,
    async_fetch_recipe_detail,
    async_fetch_recipes,
    async_fetch_shopping_list,
)
from .const import (
    CONF_API_TOKEN,
    CONF_URL,
    DOMAIN,
    MEAL_PLAN_SCAN_INTERVAL_SECONDS,
    RECIPE_SCAN_INTERVAL_SECONDS,
    SHOPPING_LIST_SCAN_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


class _TandoorCoordinator(DataUpdateCoordinator):
    """Shared setup for coordinators that poll a Tandoor endpoint."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, name: str, interval_seconds: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{name}",
            update_interval=datetime.timedelta(seconds=interval_seconds),
        )
        self._url = entry.data[CONF_URL]
        self._api_token = entry.data[CONF_API_TOKEN]

    @property
    def session(self):
        return async_get_clientsession(self.hass)

    @property
    def url(self) -> str:
        return self._url

    @property
    def api_token(self) -> str:
        return self._api_token


class TandoorMealPlanCoordinator(_TandoorCoordinator):
    """Polls Tandoor for the upcoming meal plan."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, entry, "meal_plan", MEAL_PLAN_SCAN_INTERVAL_SECONDS)

    async def _async_update_data(self) -> list[dict]:
        try:
            meals = await async_fetch_meal_plan(self.session, self._url, self._api_token)
            await self._async_enrich_with_recipe_detail(meals)
            return meals
        except TandoorAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except TandoorConnectionError as err:
            raise UpdateFailed(f"Could not reach Tandoor: {err}") from err

    async def _async_enrich_with_recipe_detail(self, meals: list[dict]) -> None:
        """Add steps/ingredients to each meal's recipe, fetching each recipe once.

        Tandoor's full recipe response nests large Food objects (a dozen+
        fields we don't use) inside every ingredient of every step. Merging
        that verbatim across a week of meals easily blows past HA's 16KB
        recorder limit for state attributes, silently disabling history for
        this entity. Trim to just what the dashboard actually renders.
        """
        recipe_ids = {m["recipe"]["id"] for m in meals if m.get("recipe")}
        details: dict[int, dict] = {}
        for recipe_id in recipe_ids:
            try:
                detail = await async_fetch_recipe_detail(
                    self.session, self._url, self._api_token, recipe_id
                )
                details[recipe_id] = _trim_recipe_detail(detail)
            except (TandoorAuthError, TandoorConnectionError) as err:
                _LOGGER.warning("Could not fetch detail for recipe %s: %s", recipe_id, err)

        for meal in meals:
            recipe = meal.get("recipe")
            if recipe and recipe["id"] in details:
                recipe.update(details[recipe["id"]])


def _trim_recipe_detail(detail: dict) -> dict:
    """Keep only the fields the dashboard popup actually renders."""
    return {
        "image": detail.get("image"),
        "servings": detail.get("servings"),
        "working_time": detail.get("working_time"),
        "waiting_time": detail.get("waiting_time"),
        "steps": [
            {
                "name": step.get("name"),
                "instruction": step.get("instruction"),
                "ingredients": [
                    {
                        "amount": ingredient.get("amount"),
                        "unit": (ingredient.get("unit") or {}).get("name"),
                        "food": (ingredient.get("food") or {}).get("name"),
                    }
                    for ingredient in step.get("ingredients") or []
                ],
            }
            for step in detail.get("steps") or []
        ],
    }


class TandoorShoppingListCoordinator(_TandoorCoordinator):
    """Polls Tandoor for the shopping list."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, entry, "shopping_list", SHOPPING_LIST_SCAN_INTERVAL_SECONDS)

    async def _async_update_data(self) -> list[dict]:
        try:
            return await async_fetch_shopping_list(self.session, self._url, self._api_token)
        except TandoorAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except TandoorConnectionError as err:
            raise UpdateFailed(f"Could not reach Tandoor: {err}") from err


class TandoorRecipeCoordinator(_TandoorCoordinator):
    """Polls Tandoor for the recipe collection."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, entry, "recipes", RECIPE_SCAN_INTERVAL_SECONDS)

    async def _async_update_data(self) -> dict:
        try:
            return await async_fetch_recipes(self.session, self._url, self._api_token)
        except TandoorAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except TandoorConnectionError as err:
            raise UpdateFailed(f"Could not reach Tandoor: {err}") from err
