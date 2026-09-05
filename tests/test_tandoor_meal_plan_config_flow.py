"""Tests for the Tandoor Meal Plan config flow."""
from homeassistant import config_entries, data_entry_flow

from custom_components.tandoor_meal_plan.const import DOMAIN

MEAL_PLAN_URL = "http://tandoor.local:8002/api/meal-plan/"
USER_INPUT = {"url": "http://tandoor.local:8002", "api_token": "tok123"}


async def test_user_flow_success(hass, aioclient_mock) -> None:
    aioclient_mock.get(MEAL_PLAN_URL, json={"results": []})

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Tandoor Meal Plan"
    assert result["data"] == USER_INPUT


async def test_user_flow_invalid_auth(hass, aioclient_mock) -> None:
    aioclient_mock.get(MEAL_PLAN_URL, status=401)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_user_flow_cannot_connect(hass, aioclient_mock) -> None:
    import aiohttp

    aioclient_mock.get(MEAL_PLAN_URL, exc=aiohttp.ClientConnectionError())

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
