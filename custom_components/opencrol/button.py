"""Button platform for OpenCtrol actions."""

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_CLIENT_ID
from .coordinator import OpenCtrolCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenCtrol button entities."""
    coordinator: OpenCtrolCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        OpenCtrolScreenshotButton(coordinator, entry),
        OpenCtrolRestartButton(coordinator, entry),
    ])


class OpenCtrolScreenshotButton(ButtonEntity):
    """Representation of screenshot button."""

    _attr_should_poll = False

    def __init__(self, coordinator: OpenCtrolCoordinator, entry: ConfigEntry) -> None:
        """Initialize screenshot button."""
        self.coordinator = coordinator
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_screenshot"
        self._attr_name = f"{entry.data.get(ATTR_CLIENT_ID)} Take Screenshot"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.send_command("take_screenshot")


class OpenCtrolRestartButton(ButtonEntity):
    """Representation of restart button."""

    _attr_should_poll = False

    def __init__(self, coordinator: OpenCtrolCoordinator, entry: ConfigEntry) -> None:
        """Initialize restart button."""
        self.coordinator = coordinator
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_restart"
        self._attr_name = f"{entry.data.get(ATTR_CLIENT_ID)} Restart Client"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.send_command("restart")

