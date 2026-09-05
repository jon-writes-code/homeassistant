"""The Tandoor Meal Plan integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TandoorAuthError, TandoorConnectionError, async_fetch_recipes
from .const import ATTR_QUERY, DOMAIN, SERVICE_SEARCH_RECIPES
from .coordinator import (
    TandoorMealPlanCoordinator,
    TandoorRecipeCoordinator,
    TandoorShoppingListCoordinator,
)

PLATFORMS: list[str] = ["sensor", "todo"]

SEARCH_RECIPES_SCHEMA = vol.Schema({vol.Required(ATTR_QUERY): str})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    meal_plan_coordinator = TandoorMealPlanCoordinator(hass, entry)
    shopping_list_coordinator = TandoorShoppingListCoordinator(hass, entry)
    recipe_coordinator = TandoorRecipeCoordinator(hass, entry)

    await meal_plan_coordinator.async_config_entry_first_refresh()
    await shopping_list_coordinator.async_config_entry_first_refresh()
    await recipe_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "meal_plan": meal_plan_coordinator,
        "shopping_list": shopping_list_coordinator,
        "recipes": recipe_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _async_register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


def _async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_SEARCH_RECIPES):
        return

    async def async_search_recipes(call: ServiceCall) -> ServiceResponse:
        # Multiple Tandoor servers aren't a realistic setup here; use whichever
        # config entry was set up first.
        entry_data = next(iter(hass.data[DOMAIN].values()))
        coordinator = entry_data["recipes"]
        session = async_get_clientsession(hass)
        try:
            data = await async_fetch_recipes(
                session, coordinator.url, coordinator.api_token, query=call.data[ATTR_QUERY]
            )
        except (TandoorAuthError, TandoorConnectionError) as err:
            return {"recipes": [], "error": str(err)}

        return {
            "recipes": [
                {
                    "id": recipe.get("id"),
                    "name": recipe.get("name"),
                    "rating": recipe.get("rating"),
                    "last_cooked": recipe.get("last_cooked"),
                }
                for recipe in data.get("results", [])
            ]
        }

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEARCH_RECIPES,
        async_search_recipes,
        schema=SEARCH_RECIPES_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
