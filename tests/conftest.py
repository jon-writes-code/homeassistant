"""Shared pytest fixtures for testing custom_components against a real hass instance."""
import pytest

pytest_plugins = ["pytest_homeassistant_custom_component"]


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow tests to load custom_components/ instead of only core integrations."""
    yield
