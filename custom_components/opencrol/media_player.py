"""Media Player platform for OpenCtrol screen viewing."""

from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerState,
    MediaPlayerEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ATTR_CLIENT_ID
from .coordinator import OpenCtrolCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenCtrol media player."""
    coordinator: OpenCtrolCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OpenCtrolScreenViewer(coordinator, entry)])


class OpenCtrolScreenViewer(
    CoordinatorEntity, MediaPlayerEntity
):
    """Representation of OpenCtrol screen viewer."""

    _attr_should_poll = False

    def __init__(self, coordinator: OpenCtrolCoordinator, entry: ConfigEntry) -> None:
        """Initialize the screen viewer."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_screen"
        self._attr_name = f"{entry.data.get(ATTR_CLIENT_ID)} Screen"
        self._attr_state = MediaPlayerState.IDLE
        self._attr_supported_features = (
            MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data.get("status") == "online"

    @property
    def state(self) -> str:
        """Return the state of the device."""
        if not self.coordinator.last_update_success:
            return MediaPlayerState.OFF

        data = self.coordinator.data
        status = data.get("status", "offline")
        
        if status == "offline":
            return MediaPlayerState.OFF
        
        # Check if screen capture is active
        screen_capture_active = data.get("screen_capture_active", False)
        if screen_capture_active:
            return MediaPlayerState.PLAYING
        return MediaPlayerState.IDLE

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        host = self.entry.data.get("host", "localhost")
        port = self.entry.data.get("port", 8080)
        base_url = f"http://{host}:{port}"
        data = self.coordinator.data
        
        attrs = {
            "client_id": self.entry.data.get(ATTR_CLIENT_ID),
            "base_url": base_url,
            "stream_url": f"{base_url}/api/v1/screenstream/stream",
            "frame_url": f"{base_url}/api/v1/screenstream/frame",
            "status": data.get("status", "offline"),
            "monitors": data.get("monitors", []),
            "current_monitor": data.get("current_monitor", 0),
            "total_monitors": data.get("total_monitors", 0),
            "master_volume": data.get("master_volume", 0.0),
            "screen_capture_active": data.get("screen_capture_active", False),
            "audio_apps": data.get("audio_apps", []),
            "audio_devices": data.get("audio_devices", []),
            "default_output_device": next(
                (d.get("id") for d in data.get("audio_devices", []) if d.get("is_default")),
                None
            ),
        }
        # Add MAC address if configured
        mac_address = self.entry.data.get("mac_address")
        if mac_address:
            attrs["mac_address"] = mac_address
        return attrs

    async def async_turn_on(self) -> None:
        """Turn on the screen capture."""
        await self.coordinator.send_command("start_screen_capture")

    async def async_turn_off(self) -> None:
        """Turn off the screen capture."""
        await self.coordinator.send_command("stop_screen_capture")

    async def async_set_volume_level(self, volume: float) -> None:
        """Set master volume level."""
        await self.coordinator.send_command("set_volume", volume=volume)

