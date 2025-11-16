"""Select platform for OpenCtrol device selection."""

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_CLIENT_ID, ATTR_DEVICE_ID
from .coordinator import OpenCtrolCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenCtrol select entities."""
    coordinator: OpenCtrolCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [OpenCtrolOutputDevice(coordinator, entry)]
    
    # Add app device selectors
    for app in coordinator.data.get("audio_apps", []):
        entities.append(OpenCtrolAppDevice(coordinator, entry, app))
    
    async_add_entities(entities)


class OpenCtrolOutputDevice(SelectEntity):
    """Representation of system output device selection."""

    _attr_should_poll = True

    def __init__(self, coordinator: OpenCtrolCoordinator, entry: ConfigEntry) -> None:
        """Initialize output device selector."""
        self.coordinator = coordinator
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_output_device"
        self._attr_name = f"{entry.data.get(ATTR_CLIENT_ID)} Output Device"
        self._attr_current_option = None
        self._attr_options = []

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_select_option(self, option: str) -> None:
        """Set output device."""
        await self.coordinator.send_command("set_default_device", device_id=option)

    async def async_update(self) -> None:
        """Update device list and current selection."""
        devices = self.coordinator.data.get("audio_devices", [])
        self._attr_options = [d.get("id") for d in devices]
        
        # Find default device
        default_device = next((d for d in devices if d.get("is_default")), None)
        if default_device:
            self._attr_current_option = default_device.get("id")


class OpenCtrolAppDevice(SelectEntity):
    """Representation of app-specific device selection."""

    _attr_should_poll = True

    def __init__(
        self, 
        coordinator: OpenCtrolCoordinator, 
        entry: ConfigEntry,
        app: dict[str, Any]
    ) -> None:
        """Initialize app device selector."""
        self.coordinator = coordinator
        self.entry = entry
        self.app = app
        # Use process_id for unique ID, fallback to id
        app_id = app.get("process_id") or app.get("id")
        self._attr_unique_id = f"{entry.entry_id}_app_device_{app_id}"
        self._attr_name = f"{entry.data.get(ATTR_CLIENT_ID)} {app.get('name')} Device"
        self._attr_current_option = None
        self._attr_options = []

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_select_option(self, option: str) -> None:
        """Set app output device."""
        # API returns process_id, but we store it as 'id' in the app dict
        process_id = self.app.get("process_id") or self.app.get("id")
        if not process_id:
            _LOGGER.error(f"App {self.app.get('name')} has no process_id")
            return
        await self.coordinator.send_command("set_app_device", process_id=process_id, device_id=option)

    async def async_update(self) -> None:
        """Update device list and current selection."""
        devices = self.coordinator.data.get("audio_devices", [])
        self._attr_options = [d.get("id") for d in devices]
        self._attr_current_option = self.app.get(ATTR_DEVICE_ID)

