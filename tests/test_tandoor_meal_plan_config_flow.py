"""Tests for the Tandoor Meal Plan config flow.

These instantiate TandoorMealPlanConfigFlow directly rather than going
through hass.config_entries.flow.async_init(). That entry point requires
Home Assistant's real component loader to find this integration via a
literal `import custom_components` statement (hardcoded in
homeassistant/loader.py as PACKAGE_CUSTOM_COMPONENTS) - it can't be pointed
at an arbitrarily-named package directory (this repo uses `integrations/`).
Calling the flow's own methods tests the same validation/error-handling
logic without that constraint.
"""
from homeassistant.data_entry_flow import FlowResultType

from integrations.tandoor_meal_plan.config_flow import TandoorMealPlanConfigFlow
from integrations.tandoor_meal_plan.const import DOMAIN

MEAL_PLAN_URL = "http://tandoor.local:8002/api/meal-plan/"
USER_INPUT = {"url": "http://tandoor.local:8002", "api_token": "tok123"}


def _new_flow(hass):
    flow = TandoorMealPlanConfigFlow()
    flow.hass = hass
    flow.handler = DOMAIN
    flow.context = {}
    return flow


async def test_user_flow_shows_form_with_no_input(hass) -> None:
    flow = _new_flow(hass)

    result = await flow.async_step_user(None)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_user_flow_success(hass, aioclient_mock) -> None:
    aioclient_mock.get(MEAL_PLAN_URL, json={"results": []})
    flow = _new_flow(hass)

    result = await flow.async_step_user(USER_INPUT)

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Tandoor Meal Plan"
    assert result["data"] == USER_INPUT


async def test_user_flow_invalid_auth(hass, aioclient_mock) -> None:
    aioclient_mock.get(MEAL_PLAN_URL, status=401)
    flow = _new_flow(hass)

    result = await flow.async_step_user(USER_INPUT)

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_user_flow_cannot_connect(hass, aioclient_mock) -> None:
    import aiohttp

    aioclient_mock.get(MEAL_PLAN_URL, exc=aiohttp.ClientConnectionError())
    flow = _new_flow(hass)

    result = await flow.async_step_user(USER_INPUT)

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
