"""HTTP client for OpenCtrol communication."""

import logging
from typing import Any
import aiohttp
import asyncio

_LOGGER = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0  # seconds
MAX_RETRY_DELAY = 10.0  # seconds


class OpenCtrolHttpClient:
    """HTTP client for communicating with OpenCtrol Windows client."""

    def __init__(self, base_url: str, password: str | None = None):
        """Initialize HTTP client."""
        self.base_url = base_url.rstrip("/")
        self.password = password
        self._session: aiohttp.ClientSession | None = None

    async def _retry_request(
        self,
        method: str,
        url: str,
        retry_on: tuple[type[Exception], ...] = (aiohttp.ClientError, asyncio.TimeoutError),
        **kwargs: Any
    ) -> aiohttp.ClientResponse:
        """Execute HTTP request with exponential backoff retry logic."""
        last_exception = None
        
        for attempt in range(MAX_RETRIES):
            try:
                session = await self._get_session()
                # Don't use context manager - we need to return the response
                # The caller is responsible for closing it
                response = await session.request(method, url, **kwargs)
                
                # Don't retry on client errors (4xx) except for specific cases
                if response.status < 500 or attempt == MAX_RETRIES - 1:
                    return response
                
                # Retry on server errors (5xx) - close the response first
                response.close()
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=response.reason
                )
            except retry_on as ex:
                last_exception = ex
                if attempt < MAX_RETRIES - 1:
                    # Exponential backoff: delay = initial * (2 ^ attempt), capped at max
                    delay = min(INITIAL_RETRY_DELAY * (2 ** attempt), MAX_RETRY_DELAY)
                    _LOGGER.warning(
                        f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {ex}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    _LOGGER.error(f"Request failed after {MAX_RETRIES} attempts: {ex}")
                    raise
        
        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
        raise RuntimeError("Request failed without exception")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            headers = {
                "User-Agent": "HomeAssistant-OpenCtrol/2.0",
                "Accept": "application/json"
            }
            if self.password:
                headers["X-Password"] = self.password

            # Performance: Optimize connection pooling
            connector = aiohttp.TCPConnector(
                limit=20,  # Increased pool size
                limit_per_host=10,  # More connections per host
                ttl_dns_cache=300,  # Cache DNS for 5 minutes
                enable_cleanup_closed=True  # Clean up closed connections
            )
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30, connect=10),
                connector=connector,
                read_bufsize=65536  # Larger read buffer for better performance
            )
        return self._session

    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_status(self) -> dict[str, Any]:
        """Get client status."""
        response = None
        try:
            response = await self._retry_request("GET", f"{self.base_url}/api/v1/status")
            response.raise_for_status()
            data = await response.json()
            return data
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error getting status: {ex}")
            raise
        finally:
            if response:
                response.close()

    async def get_monitors(self) -> list[dict[str, Any]]:
        """Get available monitors."""
        response = None
        try:
            response = await self._retry_request("GET", f"{self.base_url}/api/v1/status/monitors")
            response.raise_for_status()
            data = await response.json()
            # API returns {monitors: [...], current_monitor: 0, total_monitors: 3}
            # Return just the monitors list for compatibility
            if isinstance(data, dict) and "monitors" in data:
                return data.get("monitors", [])
            # Fallback if response is already a list
            return data if isinstance(data, list) else []
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error getting monitors: {ex}")
            raise
        finally:
            if response:
                response.close()

    async def move_mouse(self, x: int, y: int) -> bool:
        """Move mouse cursor."""
        response = None
        try:
            response = await self._retry_request(
                "POST",
                f"{self.base_url}/api/v1/remotecontrol/mouse/move",
                json={"x": x, "y": y}
            )
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error moving mouse: {ex}")
            return False
        finally:
            if response:
                response.close()

    async def click(self, button: str = "left", x: int | None = None, y: int | None = None) -> bool:
        """Click mouse button."""
        response = None
        try:
            payload = {"button": button}
            if x is not None:
                payload["x"] = x
            if y is not None:
                payload["y"] = y
            response = await self._retry_request(
                "POST",
                f"{self.base_url}/api/v1/remotecontrol/mouse/click",
                json=payload
            )
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error clicking: {ex}")
            return False
        finally:
            if response:
                response.close()

    async def scroll(self, delta: int, delta_x: int = 0) -> bool:
        """Scroll mouse wheel."""
        response = None
        try:
            # API expects delta for vertical scrolling
            response = await self._retry_request(
                "POST",
                f"{self.base_url}/api/v1/remotecontrol/mouse/scroll",
                json={"delta": delta}
            )
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error scrolling: {ex}")
            return False
        finally:
            if response:
                response.close()

    async def type_text(self, text: str) -> bool:
        """Type text."""
        response = None
        try:
            response = await self._retry_request(
                "POST",
                f"{self.base_url}/api/v1/remotecontrol/keyboard/type",
                json={"text": text}
            )
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error typing text: {ex}")
            return False
        finally:
            if response:
                response.close()

    async def send_key(self, key: str | None = None, keys: str | None = None) -> bool:
        """Send key or key combination."""
        response = None
        try:
            payload = {}
            if key:
                payload["key"] = key
            if keys:
                payload["keys"] = keys
            response = await self._retry_request(
                "POST",
                f"{self.base_url}/api/v1/remotecontrol/keyboard/key",
                json=payload
            )
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error sending key: {ex}")
            return False
        finally:
            if response:
                response.close()

    async def send_secure_attention(self) -> bool:
        """Send Ctrl+Alt+Del."""
        response = None
        try:
            response = await self._retry_request(
                "POST",
                f"{self.base_url}/api/v1/remotecontrol/keyboard/secure-attention"
            )
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error sending secure attention: {ex}")
            return False
        finally:
            if response:
                response.close()

    async def set_volume(self, volume: float) -> bool:
        """Set master volume (0.0-1.0)."""
        response = None
        try:
            response = await self._retry_request(
                "POST",
                f"{self.base_url}/api/v1/remotecontrol/audio/volume",
                json={"volume": volume}
            )
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error setting volume: {ex}")
            return False
        finally:
            if response:
                response.close()

    async def set_app_volume(self, process_id: int, volume: float) -> bool:
        """Set app volume."""
        response = None
        try:
            # Validate process_id
            if process_id <= 0:
                _LOGGER.error(f"Invalid process_id: {process_id}")
                return False
            
            response = await self._retry_request(
                "POST",
                f"{self.base_url}/api/v1/remotecontrol/audio/app-volume",
                json={"process_id": process_id, "volume": volume}
            )
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error setting app volume: {ex}")
            return False
        finally:
            if response:
                response.close()

    async def get_audio_apps(self) -> list[dict[str, Any]]:
        """Get audio apps."""
        response = None
        try:
            response = await self._retry_request("GET", f"{self.base_url}/api/v1/remotecontrol/audio/apps")
            response.raise_for_status()
            return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error getting audio apps: {ex}")
            raise
        finally:
            if response:
                response.close()

    async def get_audio_devices(self) -> list[dict[str, Any]]:
        """Get audio devices."""
        response = None
        try:
            response = await self._retry_request("GET", f"{self.base_url}/api/v1/remotecontrol/audio/devices")
            response.raise_for_status()
            return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error getting audio devices: {ex}")
            raise
        finally:
            if response:
                response.close()

    async def select_monitor(self, monitor_index: int) -> bool:
        """Select monitor for screen capture."""
        response = None
        try:
            response = await self._retry_request(
                "POST",
                f"{self.base_url}/api/v1/screen/monitor/{monitor_index}"
            )
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error selecting monitor: {ex}")
            return False
        finally:
            if response:
                response.close()

    async def start_screen_capture(self) -> bool:
        """Start screen capture."""
        response = None
        try:
            response = await self._retry_request("POST", f"{self.base_url}/api/v1/screen/start")
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error starting screen capture: {ex}")
            return False
        finally:
            if response:
                response.close()

    async def stop_screen_capture(self) -> bool:
        """Stop screen capture."""
        response = None
        try:
            response = await self._retry_request("POST", f"{self.base_url}/api/v1/screen/stop")
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error stopping screen capture: {ex}")
            return False
        finally:
            if response:
                response.close()

    async def send_to_secure_desktop(self, text: str) -> bool:
        """Send text to secure desktop."""
        response = None
        try:
            response = await self._retry_request(
                "POST",
                f"{self.base_url}/api/v1/remotecontrol/keyboard/secure-desktop/send-text",
                json={"text": text}
            )
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error sending text to secure desktop: {ex}")
            return False
        finally:
            if response:
                response.close()

    async def take_screenshot(self) -> dict[str, Any] | None:
        """Take a screenshot."""
        response = None
        try:
            response = await self._retry_request(
                "POST",
                f"{self.base_url}/api/v1/screenstream/screenshot"
            )
            response.raise_for_status()
            return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error taking screenshot: {ex}")
            return None
        finally:
            if response:
                response.close()

    async def restart_client(self) -> bool:
        """Restart the OpenCtrol client."""
        response = None
        try:
            response = await self._retry_request(
                "POST",
                f"{self.base_url}/api/v1/system/restart"
            )
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error restarting client: {ex}")
            return False
        finally:
            if response:
                response.close()

    async def set_app_device(self, process_id: int, device_id: str) -> bool:
        """Set app output device."""
        response = None
        try:
            if process_id <= 0:
                _LOGGER.error(f"Invalid process_id: {process_id}")
                return False
            
            response = await self._retry_request(
                "POST",
                f"{self.base_url}/api/v1/remotecontrol/audio/app-device",
                json={"process_id": process_id, "device_id": device_id}
            )
            response.raise_for_status()
            data = await response.json()
            return data.get("success", False)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.error(f"Error setting app device: {ex}")
            return False
        finally:
            if response:
                response.close()

