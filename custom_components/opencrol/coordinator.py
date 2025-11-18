"""DataUpdateCoordinator for OpenCtrol."""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    STATE_ONLINE,
    STATE_OFFLINE,
    CONF_CLIENT_ID,
)
from .http_client import OpenCtrolHttpClient

_LOGGER = logging.getLogger(__name__)


class OpenCtrolCoordinator(DataUpdateCoordinator):
    """Class to manage fetching OpenCtrol data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.entry = entry
        self.client_id = entry.data.get(CONF_CLIENT_ID, "default")
        self._http_client: OpenCtrolHttpClient | None = None
        self._available = False

        # Get base URL from config
        base_url = entry.data.get("base_url", f"http://{entry.data.get('host', 'localhost')}:{entry.data.get('port', 8080)}")
        password = entry.data.get("password")

        self._http_client = OpenCtrolHttpClient(base_url, password)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=10),  # Reduced frequency for better performance
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from OpenCtrol."""
        if not self._http_client:
            return {
                "status": STATE_OFFLINE,
                "monitors": [],
                "audio_apps": [],
                "audio_devices": [],
            }

        try:
            # Get status
            status_data = await self._http_client.get_status()
            self._available = status_data.get("online", False)

            # Get monitors
            monitors_data = await self._http_client.get_monitors()
            
            # Extract monitors list and current_monitor
            monitors = []
            current_monitor = 0
            if isinstance(monitors_data, dict):
                monitors = monitors_data.get("monitors", [])
                current_monitor = monitors_data.get("current_monitor", 0)
            elif isinstance(monitors_data, list):
                monitors = monitors_data
                # Get current monitor from status endpoint if available
                current_monitor = status_data.get("current_monitor", 0)

            # Get audio apps and devices
            try:
                audio_apps = await self._http_client.get_audio_apps()
                audio_devices = await self._http_client.get_audio_devices()
            except Exception as ex:
                _LOGGER.warning(f"Error fetching audio data: {ex}")
                audio_apps = []
                audio_devices = []

            return {
                "status": STATE_ONLINE if self._available else STATE_OFFLINE,
                "monitors": monitors,
                "current_monitor": current_monitor,
                "total_monitors": len(monitors),
                "audio_apps": audio_apps,
                "audio_devices": audio_devices,
                "capabilities": status_data.get("capabilities", {}),
                "master_volume": status_data.get("master_volume", 0.0),
                "screen_capture_active": status_data.get("screen_capture_active", False),
            }
        except ConnectionError as ex:
            _LOGGER.warning(f"Connection error: {ex}")
            self._available = False
            raise UpdateFailed(f"Cannot connect to OpenCtrol: {ex}") from ex
        except TimeoutError as ex:
            _LOGGER.warning(f"Timeout error: {ex}")
            self._available = False
            raise UpdateFailed(f"Connection timeout: {ex}") from ex
        except Exception as ex:
            _LOGGER.error(f"Error updating OpenCtrol data: {ex}", exc_info=True)
            self._available = False
            raise UpdateFailed(f"Error communicating with OpenCtrol: {ex}") from ex

    async def send_command(self, command: str, **kwargs: Any) -> bool:
        """Send command to OpenCtrol client via HTTP."""
        if not self._http_client or not self._available:
            _LOGGER.error("Cannot send command: HTTP client not available")
            return False

        try:
            if command == "move_mouse":
                relative = kwargs.get("relative", False)
                return await self._http_client.move_mouse(kwargs.get("x", 0), kwargs.get("y", 0), relative=relative)
            elif command == "click":
                return await self._http_client.click(kwargs.get("button", "left"), kwargs.get("x"), kwargs.get("y"))
            elif command == "scroll":
                return await self._http_client.scroll(kwargs.get("delta", 0))
            elif command == "type_text":
                return await self._http_client.type_text(kwargs.get("text", ""))
            elif command == "send_key":
                return await self._http_client.send_key(kwargs.get("key"), kwargs.get("keys"))
            elif command == "secure_attention":
                return await self._http_client.send_secure_attention()
            elif command == "set_volume":
                return await self._http_client.set_volume(kwargs.get("volume", 0.0))
            elif command == "set_app_volume":
                return await self._http_client.set_app_volume(kwargs.get("process_id", 0), kwargs.get("volume", 0.0))
            elif command == "select_monitor":
                return await self._http_client.select_monitor(kwargs.get("monitor_index", 0))
            elif command == "start_screen_capture":
                return await self._http_client.start_screen_capture()
            elif command == "stop_screen_capture":
                return await self._http_client.stop_screen_capture()
            elif command == "send_to_secure_desktop":
                return await self._http_client.send_to_secure_desktop(kwargs.get("text", ""))
            elif command == "take_screenshot":
                result = await self._http_client.take_screenshot()
                return result is not None and result.get("success", False)
            elif command == "restart":
                return await self._http_client.restart_client()
            elif command == "lock":
                return await self._http_client.lock_workstation()
            elif command == "set_app_device":
                return await self._http_client.set_app_device(
                    kwargs.get("process_id", 0),
                    kwargs.get("device_id", "")
                )
            elif command == "set_default_device":
                return await self._http_client.set_default_device(
                    kwargs.get("device_id", "")
                )
            else:
                _LOGGER.warning(f"Unknown command: {command}")
                return False
        except Exception as ex:
            _LOGGER.error(f"Error sending command {command}: {ex}")
            return False

    async def async_shutdown(self) -> None:
        """Shutdown coordinator."""
        if self._http_client:
            await self._http_client.close()
