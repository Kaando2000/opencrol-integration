"""Unified remote entity for OpenCtrol."""

from typing import Any
from homeassistant.components.remote import RemoteEntity, RemoteEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OpenCtrolCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenCtrol remote entity."""
    coordinator: OpenCtrolCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OpenCtrolRemote(coordinator, entry)])


class OpenCtrolRemote(CoordinatorEntity, RemoteEntity):
    """Representation of OpenCtrol remote control."""

    _attr_supported_features = (
        RemoteEntityFeature.ACTIVITY
        | RemoteEntityFeature.TURN_ON
        | RemoteEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator: OpenCtrolCoordinator, entry: ConfigEntry) -> None:
        """Initialize the remote."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_remote"
        self._attr_name = f"{entry.data.get('client_id', 'OpenCtrol')} Remote"
        self._attr_is_on = False

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data.get("status") == "online"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        # Get base URL for screen streaming
        host = self.entry.data.get("host", "localhost")
        port = self.entry.data.get("port", 8080)
        base_url = f"http://{host}:{port}"
        
        return {
            "client_id": self.entry.data.get("client_id"),
            "base_url": base_url,
            "monitors": self.coordinator.data.get("monitors", []),
            "audio_apps": self.coordinator.data.get("audio_apps", []),
            "audio_devices": self.coordinator.data.get("audio_devices", []),
            "capabilities": self.coordinator.data.get("capabilities", {}),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the remote connection."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the remote connection."""
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_send_command(self, command: list[str], **kwargs: Any) -> None:
        """Send commands."""
        # Commands are handled via services, not through remote entity
        pass

