"""Config flow for OpenCtrol."""

from typing import Any
import asyncio
import voluptuous as vol
import logging

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

from .const import (
    DOMAIN,
    CONF_CLIENT_ID,
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenCtrol."""

    VERSION = 1

    def __init__(self):
        """Initialize config flow."""
        self._discovered_devices: list[dict[str, Any]] = []
        self._selected_device: dict[str, Any] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - auto-discovery."""
        errors = {}
        
        # Try auto-discovery if no user input yet
        if user_input is None:
            try:
                from . import discovery
                _LOGGER.info("Starting auto-discovery...")
                self._discovered_devices = await discovery.discover_opencrol_devices()
                if self._discovered_devices:
                    _LOGGER.info(f"Discovered {len(self._discovered_devices)} OpenCtrol device(s)")
                    # Show discovered devices
                    return await self.async_step_discovery()
                else:
                    _LOGGER.info("No devices discovered via mDNS, allowing manual entry")
            except Exception as ex:
                _LOGGER.warning(f"Auto-discovery failed: {ex}, allowing manual entry")

        # If no devices found or user wants manual entry
        return await self.async_step_manual()

    async def async_step_discovery(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle device selection from discovered devices."""
        errors = {}
        
        if user_input is not None:
            device_index_str = user_input.get("device")
            if device_index_str is not None:
                try:
                    device_index = int(device_index_str)
                    if 0 <= device_index < len(self._discovered_devices):
                        self._selected_device = self._discovered_devices[device_index]
                        # Extract info from discovered device
                        properties = self._selected_device.get("properties", {})
                        host = self._selected_device.get("host", "")
                        port = int(properties.get("port", self._selected_device.get("port", 8080)))
                        client_id = properties.get("client_id", self._selected_device.get("name", "unknown"))
                        
                        # Check if password is required
                        requires_password = properties.get("requires_password", "false").lower() == "true"
                        
                        if requires_password:
                            # Go to password entry step
                            return await self.async_step_password({
                                "host": host,
                                "port": port,
                                "client_id": client_id
                            })
                        else:
                            # No password required, create entry directly
                            return await self.async_create_entry(
                                title=f"OpenCtrol - {client_id}",
                                data={
                                    "host": host,
                                    "port": port,
                                    "client_id": client_id,
                                    "password": "",
                                    "base_url": f"http://{host}:{port}"
                                }
                            )
                    else:
                        errors["base"] = "invalid_device"
                except (ValueError, TypeError):
                    errors["base"] = "invalid_device"

        # Show device selection form
        device_options = {}
        for idx, device in enumerate(self._discovered_devices):
            properties = device.get("properties", {})
            client_id = properties.get("client_id", device.get("name", "Unknown"))
            host = device.get("host", "Unknown")
            port = properties.get("port", device.get("port", 8080))
            device_options[str(idx)] = f"{client_id} ({host}:{port})"

        return self.async_show_form(
            step_id="discovery",
            data_schema=vol.Schema({
                vol.Required("device"): vol.In(device_options)
            }),
            errors=errors,
            description_placeholders={
                "count": str(len(self._discovered_devices))
            }
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual device entry."""
        errors = {}
        
        if user_input is not None:
            host = user_input.get("host", "").strip()
            port = user_input.get("port", 8080)
            client_id = user_input.get("client_id", host)
            
            if not host:
                errors["host"] = "host_required"
            else:
                # Test connection and check if password is required
                import aiohttp
                base_url = f"http://{host}:{port}"
                
                try:
                    _LOGGER.info(f"Testing connection to {base_url}")
                    async with aiohttp.ClientSession() as session:
                        # First, test health endpoint (no auth required)
                        try:
                            async with session.get(
                                f"{base_url}/api/v1/health",
                                timeout=aiohttp.ClientTimeout(total=10, connect=5)
                            ) as health_response:
                                if health_response.status == 200:
                                    _LOGGER.info(f"Health endpoint accessible: {health_response.status}")
                                    # Connection successful, check status for password requirement
                                    try:
                                        async with session.get(
                                            f"{base_url}/api/v1/status",
                                            timeout=aiohttp.ClientTimeout(total=10, connect=5)
                                        ) as status_response:
                                            _LOGGER.info(f"Status endpoint response: {status_response.status}")
                                            if status_response.status == 401:
                                                # Password required
                                                _LOGGER.info("Password required, proceeding to password step")
                                                return await self.async_step_password({
                                                    "host": host,
                                                    "port": port,
                                                    "client_id": client_id
                                                })
                                            elif status_response.status == 200:
                                                # No password required
                                                status_data = await status_response.json()
                                                _LOGGER.info(f"Connection successful, no password required. Client ID: {status_data.get('client_id', 'unknown')}")
                                                return await self.async_create_entry(
                                                    title=f"OpenCtrol - {client_id}",
                                                    data={
                                                        "host": host,
                                                        "port": port,
                                                        "client_id": client_id,
                                                        "password": "",
                                                        "base_url": base_url
                                                    }
                                                )
                                            else:
                                                _LOGGER.warning(f"Unexpected status code: {status_response.status}")
                                                errors["base"] = "cannot_connect"
                                    except aiohttp.ClientError as ex:
                                        _LOGGER.error(f"Error checking status endpoint: {ex}")
                                        # Assume password required if status check fails
                                        return await self.async_step_password({
                                            "host": host,
                                            "port": port,
                                            "client_id": client_id
                                        })
                                    except Exception as ex:
                                        _LOGGER.exception(f"Unexpected error checking status: {ex}")
                                        errors["base"] = "unknown"
                                else:
                                    _LOGGER.error(f"Health endpoint returned status: {health_response.status}")
                                    errors["base"] = "cannot_connect"
                        except aiohttp.ClientConnectorError as ex:
                            _LOGGER.error(f"Connection error: {ex}")
                            errors["base"] = "cannot_connect"
                        except aiohttp.ServerTimeoutError:
                            _LOGGER.error("Connection timeout")
                            errors["base"] = "timeout"
                        except asyncio.TimeoutError:
                            _LOGGER.error("Request timeout")
                            errors["base"] = "timeout"
                except aiohttp.ClientError as ex:
                    _LOGGER.error(f"Client error: {ex}")
                    errors["base"] = "cannot_connect"
                except asyncio.TimeoutError:
                    _LOGGER.error("Connection timeout")
                    errors["base"] = "timeout"
                except Exception as ex:
                    _LOGGER.exception(f"Unexpected error during connection test: {ex}")
                    errors["base"] = "unknown"

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema({
                vol.Required("host"): str,
                vol.Optional("port", default=8080): int,
                vol.Optional("client_id", default=""): str,
            }),
            errors=errors,
        )

    async def async_step_password(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle password entry."""
        errors = {}
        
        # Get device info from previous step
        device_info = user_input or {}
        host = device_info.get("host", "")
        port = device_info.get("port", 8080)
        client_id = device_info.get("client_id", host)
        
        if user_input is not None and "password" in user_input:
            password = user_input.get("password", "")
            
            # Test connection with password
            import aiohttp
            base_url = f"http://{host}:{port}"
            headers = {}
            if password:
                headers["X-Password"] = password
            
            try:
                _LOGGER.info(f"Validating password for {base_url}")
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{base_url}/api/v1/status",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10, connect=5)
                    ) as response:
                        _LOGGER.info(f"Password validation response: {response.status}")
                        if response.status == 200:
                            # Password correct, create entry
                            status_data = await response.json()
                            _LOGGER.info(f"Password validated successfully. Client ID: {status_data.get('client_id', 'unknown')}")
                            return await self.async_create_entry(
                                title=f"OpenCtrol - {client_id}",
                                data={
                                    "host": host,
                                    "port": port,
                                    "client_id": client_id,
                                    "password": password,
                                    "base_url": base_url
                                }
                            )
                        elif response.status == 401:
                            _LOGGER.warning("Password validation failed: invalid password")
                            errors["base"] = "invalid_auth"
                        else:
                            _LOGGER.error(f"Unexpected status code: {response.status}")
                            errors["base"] = "cannot_connect"
            except aiohttp.ClientConnectorError as ex:
                _LOGGER.error(f"Connection error during password validation: {ex}")
                errors["base"] = "cannot_connect"
            except aiohttp.ServerTimeoutError:
                _LOGGER.error("Connection timeout during password validation")
                errors["base"] = "timeout"
            except asyncio.TimeoutError:
                _LOGGER.error("Request timeout during password validation")
                errors["base"] = "timeout"
            except Exception as ex:
                _LOGGER.exception(f"Unexpected error during password validation: {ex}")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="password",
            data_schema=vol.Schema({
                vol.Required("password"): str,
            }),
            errors=errors,
            description_placeholders={
                "device": f"{client_id} ({host}:{port})"
            }
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
