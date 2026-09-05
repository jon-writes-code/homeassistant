"""Sensor platform for the Tandoor Meal Plan integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TandoorMealPlanCoordinator, TandoorRecipeCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinators = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            TandoorMealPlanSensor(coordinators["meal_plan"], entry),
            TandoorRecipesSensor(coordinators["recipes"], entry),
        ]
    )


class TandoorMealPlanSensor(CoordinatorEntity[TandoorMealPlanCoordinator], SensorEntity):
    """Number of upcoming planned meals, with the meal list as an attribute."""

    _attr_name = "Tandoor Meal Plan"
    _attr_icon = "mdi:food"
    _attr_native_unit_of_measurement = "meals"

    def __init__(self, coordinator: TandoorMealPlanCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        # Keep this unchanged from the original release: it's already live in
        # your entity registry as sensor.tandoor_meal_plan. Changing it would
        # orphan that entity and create a new sensor.tandoor_meal_plan_2.
        self._attr_unique_id = entry.entry_id

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data or [])

    @property
    def extra_state_attributes(self) -> dict:
        return {"meals": self.coordinator.data or []}


class TandoorRecipesSensor(CoordinatorEntity[TandoorRecipeCoordinator], SensorEntity):
    """Total recipe count, with a page of recipes as an attribute."""

    _attr_name = "Tandoor Recipes"
    _attr_icon = "mdi:book-open-variant"
    _attr_native_unit_of_measurement = "recipes"

    def __init__(self, coordinator: TandoorRecipeCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_recipes"

    @property
    def native_value(self) -> int:
        return (self.coordinator.data or {}).get("count", 0)

    @property
    def extra_state_attributes(self) -> dict:
        results = (self.coordinator.data or {}).get("results", [])
        return {
            "recipes": [
                {
                    "id": recipe.get("id"),
                    "name": recipe.get("name"),
                    "rating": recipe.get("rating"),
                    "last_cooked": recipe.get("last_cooked"),
                }
                for recipe in results
            ]
        }
