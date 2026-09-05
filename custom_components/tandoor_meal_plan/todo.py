"""Todo platform for the Tandoor Meal Plan integration (shopping list)."""
from __future__ import annotations

from homeassistant.components.todo import TodoItem, TodoItemStatus, TodoListEntity, TodoListEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import (
    async_create_shopping_list_item,
    async_delete_shopping_list_item,
    async_set_shopping_list_item_checked,
)
from .const import CONF_API_TOKEN, CONF_URL, DOMAIN
from .coordinator import TandoorShoppingListCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinators = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TandoorShoppingListEntity(coordinators["shopping_list"], entry)])


def _format_summary(entry: dict) -> str:
    food = entry.get("food") or {}
    name = food.get("name", "")
    amount = entry.get("amount")
    unit = ((entry.get("unit") or {}).get("name") or "").strip()

    if not amount or amount == 1:
        return name

    amount_str = str(int(amount)) if amount == int(amount) else str(amount)
    return f"{amount_str} {unit} {name}".strip() if unit else f"{amount_str} {name}"


class TandoorShoppingListEntity(
    CoordinatorEntity[TandoorShoppingListCoordinator], TodoListEntity
):
    """Tandoor's shopping list, exposed as a Home Assistant to-do list."""

    _attr_name = "Tandoor Shopping List"
    _attr_icon = "mdi:cart"
    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
    )

    def __init__(self, coordinator: TandoorShoppingListCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_shopping_list"
        self._url = entry.data[CONF_URL]
        self._api_token = entry.data[CONF_API_TOKEN]
        self._update_todo_items()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update_todo_items()
        super()._handle_coordinator_update()

    def _update_todo_items(self) -> None:
        entries = self.coordinator.data or []
        self._attr_todo_items = [
            TodoItem(
                uid=str(entry["id"]),
                summary=_format_summary(entry),
                status=(
                    TodoItemStatus.COMPLETED
                    if entry.get("checked")
                    else TodoItemStatus.NEEDS_ACTION
                ),
            )
            for entry in entries
        ]

    async def async_create_todo_item(self, item: TodoItem) -> None:
        await async_create_shopping_list_item(
            async_get_clientsession(self.hass), self._url, self._api_token, item.summary
        )
        await self.coordinator.async_request_refresh()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        await async_set_shopping_list_item_checked(
            async_get_clientsession(self.hass),
            self._url,
            self._api_token,
            item.uid,
            checked=item.status == TodoItemStatus.COMPLETED,
        )
        await self.coordinator.async_request_refresh()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        session = async_get_clientsession(self.hass)
        for uid in uids:
            await async_delete_shopping_list_item(session, self._url, self._api_token, uid)
        await self.coordinator.async_request_refresh()
