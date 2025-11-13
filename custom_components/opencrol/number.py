"""Number platform for OpenCtrol volume control."""

import logging
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_CLIENT_ID, ATTR_VOLUME
from .coordinator import OpenCtrolCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenCtrol number entities."""
    coordinator: OpenCtrolCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [OpenCtrolMasterVolume(coordinator, entry)]
    
    # Add app volume controls
    for app in coordinator.data.get("audio_apps", []):
        entities.append(OpenCtrolAppVolume(coordinator, entry, app))
    
    async_add_entities(entities)


class OpenCtrolMasterVolume(NumberEntity):
    """Representation of master volume control."""

    _attr_should_poll = True

    def __init__(self, coordinator: OpenCtrolCoordinator, entry: ConfigEntry) -> None:
        """Initialize master volume."""
        self.coordinator = coordinator
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_master_volume"
        self._attr_name = f"{entry.data.get(ATTR_CLIENT_ID)} Master Volume"
        self._attr_min_value = 0.0
        self._attr_max_value = 1.0
        self._attr_step = 0.01
        self._attr_mode = "slider"
        self._attr_native_value = 0.5

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_set_native_value(self, value: float) -> None:
        """Set master volume."""
        await self.coordinator.send_command("set_volume", volume=value)

    async def async_update(self) -> None:
        """Update volume from coordinator."""
        audio_data = self.coordinator.data.get("audio", {})
        self._attr_native_value = audio_data.get("master_volume", 0.5)


class OpenCtrolAppVolume(NumberEntity):
    """Representation of app-specific volume control."""

    _attr_should_poll = True

    def __init__(
        self, 
        coordinator: OpenCtrolCoordinator, 
        entry: ConfigEntry,
        app: dict[str, Any]
    ) -> None:
        """Initialize app volume."""
        self.coordinator = coordinator
        self.entry = entry
        self.app = app
        # Use process_id for unique ID, fallback to id
        app_id = app.get("process_id") or app.get("id")
        self._attr_unique_id = f"{entry.entry_id}_app_volume_{app_id}"
        self._attr_name = f"{entry.data.get(ATTR_CLIENT_ID)} {app.get('name')} Volume"
        self._attr_min_value = 0.0
        self._attr_max_value = 1.0
        self._attr_step = 0.01
        self._attr_mode = "slider"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_set_native_value(self, value: float) -> None:
        """Set app volume."""
        # API returns process_id, but we store it as 'id' in the app dict
        process_id = self.app.get("process_id") or self.app.get("id")
        if not process_id:
            _LOGGER.error(f"App {self.app.get('name')} has no process_id")
            return
        await self.coordinator.send_command(
            "set_app_volume",
            process_id=process_id,
            volume=value
        )

    async def async_update(self) -> None:
        """Update app volume from coordinator."""
        self._attr_native_value = self.app.get(ATTR_VOLUME, 0.5)

