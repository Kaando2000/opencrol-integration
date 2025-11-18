"""Services for OpenCtrol integration."""

import logging
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN, SERVICE_LOCK

_LOGGER = logging.getLogger(__name__)

SERVICE_MOVE_MOUSE = "move_mouse"
SERVICE_CLICK = "click"
SERVICE_SCROLL = "scroll"
SERVICE_TYPE_TEXT = "type_text"
SERVICE_SEND_KEY = "send_key"
SERVICE_SECURE_ATTENTION = "secure_attention"
SERVICE_SET_VOLUME = "set_volume"
SERVICE_SET_APP_VOLUME = "set_app_volume"
SERVICE_SET_APP_DEVICE = "set_app_device"
SERVICE_SET_DEFAULT_DEVICE = "set_default_device"
SERVICE_SELECT_MONITOR = "select_monitor"
SERVICE_START_SCREEN_CAPTURE = "start_screen_capture"
SERVICE_STOP_SCREEN_CAPTURE = "stop_screen_capture"
SERVICE_SEND_TO_SECURE_DESKTOP = "send_to_secure_desktop"

SERVICE_SCHEMA_MOVE_MOUSE = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required("x"): vol.Coerce(int),
    vol.Required("y"): vol.Coerce(int),
})

SERVICE_SCHEMA_CLICK = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Optional("x"): vol.Coerce(int),
    vol.Optional("y"): vol.Coerce(int),
    vol.Optional("button", default="left"): vol.In(["left", "right", "middle"]),
})

SERVICE_SCHEMA_SCROLL = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required("delta"): vol.Coerce(int),
})

SERVICE_SCHEMA_TYPE_TEXT = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required("text"): cv.string,
})

SERVICE_SCHEMA_SEND_KEY = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Exclusive("key", "key_input"): cv.string,
    vol.Exclusive("keys", "key_input"): cv.string,
})

SERVICE_SCHEMA_SECURE_ATTENTION = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
})

SERVICE_SCHEMA_SET_VOLUME = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required("volume"): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
})

SERVICE_SCHEMA_SET_APP_VOLUME = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required("process_id"): vol.Coerce(int),
    vol.Required("volume"): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
})

SERVICE_SCHEMA_SET_DEFAULT_DEVICE = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required("device_id"): cv.string,
})

SERVICE_SCHEMA_SELECT_MONITOR = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required("monitor_index"): vol.Coerce(int),
})

SERVICE_SCHEMA_START_SCREEN_CAPTURE = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
})

SERVICE_SCHEMA_STOP_SCREEN_CAPTURE = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
})

SERVICE_SCHEMA_SEND_TO_SECURE_DESKTOP = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required("text"): cv.string,
})

SERVICE_SCHEMA_LOCK = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
})


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for OpenCtrol."""
    # Check if services are already registered to avoid duplicates
    if hass.services.has_service(DOMAIN, SERVICE_MOVE_MOUSE):
        _LOGGER.debug("OpenCtrol services already registered, skipping")
        return

    async def handle_move_mouse(call: ServiceCall) -> None:
        """Handle move_mouse service call."""
        entity_id = call.data["entity_id"]
        x = call.data["x"]
        y = call.data["y"]

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("move_mouse", x=x, y=y)

    async def handle_click(call: ServiceCall) -> None:
        """Handle click service call."""
        entity_id = call.data["entity_id"]
        button = call.data.get("button", "left")
        x = call.data.get("x")
        y = call.data.get("y")

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("click", button=button, x=x, y=y)

    async def handle_scroll(call: ServiceCall) -> None:
        """Handle scroll service call."""
        entity_id = call.data["entity_id"]
        delta = call.data["delta"]

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("scroll", delta=delta)

    async def handle_type_text(call: ServiceCall) -> None:
        """Handle type_text service call."""
        entity_id = call.data["entity_id"]
        text = call.data["text"]

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("type_text", text=text)

    async def handle_send_key(call: ServiceCall) -> None:
        """Handle send_key service call."""
        entity_id = call.data["entity_id"]
        key = call.data.get("key")
        keys = call.data.get("keys")

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("send_key", key=key, keys=keys)

    async def handle_secure_attention(call: ServiceCall) -> None:
        """Handle secure_attention service call."""
        entity_id = call.data["entity_id"]

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("secure_attention")

    async def handle_set_volume(call: ServiceCall) -> None:
        """Handle set_volume service call."""
        entity_id = call.data["entity_id"]
        volume = call.data["volume"]

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("set_volume", volume=volume)

    async def handle_set_app_volume(call: ServiceCall) -> None:
        """Handle set_app_volume service call."""
        entity_id = call.data["entity_id"]
        process_id = call.data["process_id"]
        volume = call.data["volume"]

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("set_app_volume", process_id=process_id, volume=volume)

    async def handle_select_monitor(call: ServiceCall) -> None:
        """Handle select_monitor service call."""
        entity_id = call.data["entity_id"]
        monitor_index = call.data["monitor_index"]

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("select_monitor", monitor_index=monitor_index)

    async def handle_start_screen_capture(call: ServiceCall) -> None:
        """Handle start_screen_capture service call."""
        entity_id = call.data["entity_id"]

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("start_screen_capture")

    async def handle_stop_screen_capture(call: ServiceCall) -> None:
        """Handle stop_screen_capture service call."""
        entity_id = call.data["entity_id"]

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("stop_screen_capture")

    async def handle_send_to_secure_desktop(call: ServiceCall) -> None:
        """Handle send_to_secure_desktop service call."""
        entity_id = call.data["entity_id"]
        text = call.data["text"]

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("send_to_secure_desktop", text=text)

    async def handle_set_default_device(call: ServiceCall) -> None:
        """Handle set_default_device service call."""
        entity_id = call.data["entity_id"]
        device_id = call.data["device_id"]

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("set_default_device", device_id=device_id)

    async def handle_lock(call: ServiceCall) -> None:
        """Handle lock service call."""
        entity_id = call.data["entity_id"]

        coordinator = _get_coordinator(hass, entity_id)
        if coordinator:
            await coordinator.send_command("lock")

    hass.services.async_register(
        DOMAIN, SERVICE_MOVE_MOUSE, handle_move_mouse, schema=SERVICE_SCHEMA_MOVE_MOUSE
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CLICK, handle_click, schema=SERVICE_SCHEMA_CLICK
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SCROLL, handle_scroll, schema=SERVICE_SCHEMA_SCROLL
    )
    hass.services.async_register(
        DOMAIN, SERVICE_TYPE_TEXT, handle_type_text, schema=SERVICE_SCHEMA_TYPE_TEXT
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_KEY, handle_send_key, schema=SERVICE_SCHEMA_SEND_KEY
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SECURE_ATTENTION, handle_secure_attention, schema=SERVICE_SCHEMA_SECURE_ATTENTION
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_VOLUME, handle_set_volume, schema=SERVICE_SCHEMA_SET_VOLUME
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_APP_VOLUME, handle_set_app_volume, schema=SERVICE_SCHEMA_SET_APP_VOLUME
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SELECT_MONITOR, handle_select_monitor, schema=SERVICE_SCHEMA_SELECT_MONITOR
    )
    hass.services.async_register(
        DOMAIN, SERVICE_START_SCREEN_CAPTURE, handle_start_screen_capture, schema=SERVICE_SCHEMA_START_SCREEN_CAPTURE
    )
    hass.services.async_register(
        DOMAIN, SERVICE_STOP_SCREEN_CAPTURE, handle_stop_screen_capture, schema=SERVICE_SCHEMA_STOP_SCREEN_CAPTURE
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_TO_SECURE_DESKTOP, handle_send_to_secure_desktop, schema=SERVICE_SCHEMA_SEND_TO_SECURE_DESKTOP
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_DEFAULT_DEVICE, handle_set_default_device, schema=SERVICE_SCHEMA_SET_DEFAULT_DEVICE
    )
    hass.services.async_register(
        DOMAIN, SERVICE_LOCK, handle_lock, schema=SERVICE_SCHEMA_LOCK
    )


def _get_coordinator(hass: HomeAssistant, entity_id: str):
    """Get coordinator for entity."""
    from .coordinator import OpenCtrolCoordinator
    from homeassistant.helpers import entity_registry as er

    # Find the entry_id from entity_id
    try:
        entity_registry = er.async_get(hass)
        if entity := entity_registry.async_get(entity_id):
            entry_id = entity.config_entry_id
            if entry_id and entry_id in hass.data.get(DOMAIN, {}):
                coordinator = hass.data[DOMAIN][entry_id]
                if isinstance(coordinator, OpenCtrolCoordinator):
                    return coordinator
    except Exception:
        # Fallback: try to find coordinator by entity_id pattern
        for entry_id, coordinator in hass.data.get(DOMAIN, {}).items():
            if isinstance(coordinator, OpenCtrolCoordinator):
                # Check if entity matches this coordinator's entities
                if entity_id and hasattr(coordinator, 'entry'):
                    # Try to match by checking if entity belongs to this entry
                    return coordinator
    return None

