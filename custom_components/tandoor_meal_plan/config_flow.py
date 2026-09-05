"""Config flow for the Tandoor Meal Plan integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TandoorAuthError, TandoorConnectionError, async_fetch_meal_plan
from .const import CONF_API_TOKEN, CONF_URL, DOMAIN

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
        vol.Required(CONF_API_TOKEN): str,
    }
)


class TandoorMealPlanConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            try:
                await async_fetch_meal_plan(
                    session, user_input[CONF_URL], user_input[CONF_API_TOKEN]
                )
            except TandoorAuthError:
                errors["base"] = "invalid_auth"
            except TandoorConnectionError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input[CONF_URL])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Tandoor Meal Plan", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )
