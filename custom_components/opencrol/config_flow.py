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
        super().__init__()
        self._discovered_devices: list[dict[str, Any]] = []
        self._selected_device: dict[str, Any] | None = None
        self._password_step_data: dict[str, Any] = {}  # Store data for password step

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - auto-discovery."""
        errors = {}
        
        # Try auto-discovery if no user input yet
        if user_input is None:
            try:
                from . import discovery
                from homeassistant.components import zeroconf
                _LOGGER.info("Starting auto-discovery...")
                # Get shared Zeroconf instance from Home Assistant
                zeroconf_instance = await zeroconf.async_get_instance(self.hass)
                self._discovered_devices = await discovery.discover_opencrol_devices(zeroconf_instance)
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
                            self._password_step_data = {
                                "host": host,
                                "port": port,
                                "client_id": client_id
                            }
                            return await self.async_step_password()
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
                    _LOGGER.debug(f"Connection details: host={host}, port={port}, base_url={base_url}")
                    # Create session with connector for better connection handling
                    connector = aiohttp.TCPConnector(limit=10, limit_per_host=5, force_close=False)
                    async with aiohttp.ClientSession(connector=connector) as session:
                        # First, test health endpoint (no auth required)
                        try:
                            _LOGGER.debug(f"Attempting to connect to health endpoint: {base_url}/api/v1/health")
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
                                                self._password_step_data = {
                                                    "host": host,
                                                    "port": port,
                                                    "client_id": client_id
                                                }
                                                return await self.async_step_password()
                                            elif status_response.status == 200:
                                                # Status accessible - always proceed to password step
                                                # User can leave password empty if no password is set
                                                try:
                                                    # status_response.json() is already a coroutine, await it
                                                    status_data = await status_response.json()
                                                    if isinstance(status_data, dict):
                                                        actual_client_id = status_data.get('client_id', client_id)
                                                    else:
                                                        _LOGGER.warning(f"Unexpected response type: {type(status_data)}")
                                                        actual_client_id = client_id
                                                    _LOGGER.info(f"Status accessible. Client ID: {actual_client_id}. Proceeding to password step.")
                                                    self._password_step_data = {
                                                        "host": host,
                                                        "port": port,
                                                        "client_id": actual_client_id
                                                    }
                                                    return await self.async_step_password()
                                                except Exception as json_ex:
                                                    _LOGGER.error(f"Error parsing status JSON: {json_ex}", exc_info=True)
                                                    # Proceed to password step anyway with original client_id
                                                    self._password_step_data = {
                                                        "host": host,
                                                        "port": port,
                                                        "client_id": client_id
                                                    }
                                                    return await self.async_step_password()
                                            else:
                                                _LOGGER.warning(f"Unexpected status code: {status_response.status}")
                                                errors["base"] = "cannot_connect"
                                    except aiohttp.ClientError as ex:
                                        _LOGGER.error(f"Error checking status endpoint: {ex}")
                                        # Assume password required if status check fails
                                        self._password_step_data = {
                                            "host": host,
                                            "port": port,
                                            "client_id": client_id
                                        }
                                        return await self.async_step_password()
                                    except aiohttp.ClientConnectorError as ex:
                                        _LOGGER.error(f"Connection error checking status: {ex}")
                                        errors["base"] = "cannot_connect"
                                    except aiohttp.ServerTimeoutError as ex:
                                        _LOGGER.error(f"Timeout checking status: {ex}")
                                        errors["base"] = "timeout"
                                    except asyncio.TimeoutError as ex:
                                        _LOGGER.error(f"Request timeout checking status: {ex}")
                                        errors["base"] = "timeout"
                                    except Exception as ex:
                                        _LOGGER.exception(f"Unexpected error checking status: {ex}")
                                        error_msg = str(ex).lower()
                                        if "connection" in error_msg or "connect" in error_msg or "refused" in error_msg:
                                            errors["base"] = "cannot_connect"
                                        elif "timeout" in error_msg:
                                            errors["base"] = "timeout"
                                        else:
                                            errors["base"] = "cannot_connect"
                                            _LOGGER.error(f"Unhandled error, treating as connection error: {error_msg}")
                                else:
                                    _LOGGER.error(f"Health endpoint returned status: {health_response.status}")
                                    errors["base"] = "cannot_connect"
                        except aiohttp.ClientConnectorError as ex:
                            _LOGGER.error(f"Connection error to {base_url}: {ex}")
                            _LOGGER.error(f"Connection error details: {type(ex).__name__}: {str(ex)}")
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
                except aiohttp.ClientConnectorError as ex:
                    _LOGGER.error(f"Connection error: {ex}")
                    errors["base"] = "cannot_connect"
                except aiohttp.ServerTimeoutError as ex:
                    _LOGGER.error(f"Server timeout: {ex}")
                    errors["base"] = "timeout"
                except asyncio.TimeoutError as ex:
                    _LOGGER.error(f"Request timeout: {ex}")
                    errors["base"] = "timeout"
                except Exception as ex:
                    _LOGGER.exception(f"Unexpected error during connection test: {ex}")
                    error_msg = str(ex).lower()
                    error_type = type(ex).__name__
                    _LOGGER.error(f"Error type: {error_type}, Message: {error_msg}")
                    
                    if "connection" in error_msg or "connect" in error_msg or "refused" in error_msg:
                        errors["base"] = "cannot_connect"
                    elif "timeout" in error_msg:
                        errors["base"] = "timeout"
                    elif "name resolution" in error_msg or "dns" in error_msg:
                        errors["base"] = "cannot_connect"
                    else:
                        # Treat unknown errors as connection errors for better UX
                        errors["base"] = "cannot_connect"
                        _LOGGER.error(f"Unhandled error type: {error_type}, treating as connection error")

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
        
        # Get device info from previous step (stored in flow instance)
        # If user_input has the data (first call), use it and store it
        if user_input and "host" in user_input:
            self._password_step_data = {
                "host": user_input.get("host", ""),
                "port": user_input.get("port", 8080),
                "client_id": user_input.get("client_id", "")
            }
        
        # Use stored data
        host = self._password_step_data.get("host", "")
        port = self._password_step_data.get("port", 8080)
        client_id = self._password_step_data.get("client_id", host)
        
        # Validate host is not empty
        if not host:
            _LOGGER.error("Host is empty in password step - this should not happen")
            errors["base"] = "cannot_connect"
            return self.async_show_form(
                step_id="password",
                data_schema=vol.Schema({
                    vol.Required("password"): str,
                }),
                description_placeholders={"device": "OpenCtrol Device"},
                errors=errors,
            )
        
        if user_input is not None and "password" in user_input:
            password = user_input.get("password", "").strip()
            
            # Test connection with password
            import aiohttp
            base_url = f"http://{host}:{port}"
            headers = {}
            if password:
                headers["X-Password"] = password
            
            try:
                _LOGGER.info(f"Validating password for {base_url}")
                _LOGGER.debug(f"Password validation: host={host}, port={port}, base_url={base_url}, has_password={bool(password)}")
                # Use TCPConnector for better connection handling
                connector = aiohttp.TCPConnector(limit=10, limit_per_host=5, force_close=False)
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(
                        f"{base_url}/api/v1/status",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10, connect=5)
                    ) as response:
                        _LOGGER.info(f"Password validation response: {response.status}")
                        if response.status == 200:
                            # Password correct (or no password required), create entry
                            try:
                                # response.json() is already a coroutine, await it
                                status_data = await response.json()
                                if isinstance(status_data, dict):
                                    actual_client_id = status_data.get('client_id', client_id)
                                else:
                                    _LOGGER.warning(f"Unexpected response type: {type(status_data)}")
                                    actual_client_id = client_id
                                _LOGGER.info(f"Connection successful. Client ID: {actual_client_id}")
                                return self.async_create_entry(
                                    title=f"OpenCtrol - {actual_client_id}",
                                    data={
                                        "host": host,
                                        "port": port,
                                        "client_id": actual_client_id,
                                        "password": password,
                                        "base_url": base_url
                                    }
                                )
                            except Exception as json_ex:
                                _LOGGER.error(f"Error parsing JSON response: {json_ex}", exc_info=True)
                                errors["base"] = "cannot_connect"
                        elif response.status == 401:
                            if password:
                                _LOGGER.warning("Password validation failed: invalid password")
                                errors["base"] = "invalid_auth"
                            else:
                                # No password provided but password is required
                                _LOGGER.warning("Password is required but not provided")
                                errors["base"] = "invalid_auth"
                        else:
                            _LOGGER.error(f"Unexpected status code: {response.status}")
                            errors["base"] = "cannot_connect"
            except aiohttp.ClientConnectorError as ex:
                _LOGGER.error(f"Connection error during password validation: {ex}")
                error_msg = str(ex).lower()
                if "name resolution" in error_msg or "dns" in error_msg:
                    errors["base"] = "cannot_connect"
                elif "refused" in error_msg or "connection refused" in error_msg:
                    errors["base"] = "cannot_connect"
                else:
                    errors["base"] = "cannot_connect"
            except aiohttp.ServerTimeoutError as ex:
                _LOGGER.error(f"Connection timeout during password validation: {ex}")
                errors["base"] = "timeout"
            except asyncio.TimeoutError as ex:
                _LOGGER.error(f"Request timeout during password validation: {ex}")
                errors["base"] = "timeout"
            except aiohttp.ClientResponseError as ex:
                _LOGGER.error(f"HTTP client response error: {ex.status} - {ex.message}")
                if ex.status == 401:
                    errors["base"] = "invalid_auth"
                elif ex.status == 404:
                    errors["base"] = "cannot_connect"
                else:
                    errors["base"] = "cannot_connect"
            except aiohttp.ClientError as ex:
                _LOGGER.error(f"HTTP client error during password validation: {ex}")
                errors["base"] = "cannot_connect"
            except Exception as ex:
                _LOGGER.exception(f"Unexpected error during password validation: {ex}")
                # Show actual error message instead of generic "unknown"
                error_msg = str(ex).lower()
                error_type = type(ex).__name__
                _LOGGER.error(f"Error type: {error_type}, Message: {error_msg}")
                
                if "connection" in error_msg or "connect" in error_msg or "refused" in error_msg:
                    errors["base"] = "cannot_connect"
                elif "timeout" in error_msg:
                    errors["base"] = "timeout"
                elif "name resolution" in error_msg or "dns" in error_msg:
                    errors["base"] = "cannot_connect"
                elif "json" in error_msg or "decode" in error_msg:
                    errors["base"] = "cannot_connect"
                else:
                    # Last resort - but log the actual error
                    errors["base"] = "cannot_connect"
                    _LOGGER.error(f"Unhandled error type: {error_type}, treating as connection error")

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

    async def async_step_zeroconf(
        self, discovery_info: dict[str, Any]
    ) -> FlowResult:
        """Handle automatic discovery via zeroconf."""
        _LOGGER.info(f"OpenCtrol discovered via zeroconf: {discovery_info}")
        
        try:
            # Extract service information
            service_type = discovery_info.get("type", "")
            properties = discovery_info.get("properties", {})
            
            # Get host - try multiple locations
            host = (
                discovery_info.get("host") 
                or discovery_info.get("hostname", "") 
                or discovery_info.get("hostname", "")
            )
            
            # Parse IP from addresses if host is not available
            if not host or host.endswith(".local"):
                addresses = discovery_info.get("addresses", [])
                if addresses:
                    # Prefer IPv4
                    for addr in addresses:
                        if "." in str(addr) and ":" not in str(addr):
                            host = str(addr)
                            break
                    if not host or "." not in host:
                        host = str(addresses[0])
            
            # Get port from discovery info or properties
            port = discovery_info.get("port")
            if not port:
                port_str = properties.get("port", "8080")
                try:
                    port = int(port_str)
                except (ValueError, TypeError):
                    port = 8080
            
            # Get client_id from properties or service name
            client_id = (
                properties.get("client_id", "") 
                or properties.get("hostname", "") 
                or host
            )
            
            # Extract from service name if needed
            if not client_id or client_id == host or client_id.endswith(".local"):
                name = discovery_info.get("name", "")
                if name:
                    # Extract from "OpenCtrol_Hostname._opencrol._tcp.local."
                    parts = name.split(".")
                    if parts:
                        service_name = parts[0]
                        if service_name.startswith("OpenCtrol_"):
                            client_id = service_name.replace("OpenCtrol_", "")
                        elif "_" in service_name:
                            client_id = service_name.split("_", 1)[1]
                        else:
                            client_id = service_name
            
            if not client_id or client_id.endswith(".local"):
                client_id = host.split(".")[0] if "." in host else host
            
            # Check if password is required
            requires_password = properties.get("requires_password", "false").lower() == "true"
            
            # Create unique_id to prevent duplicate entries
            unique_id = f"{host}_{port}"
            
            # Normalize unique_id (remove .local, lowercase)
            unique_id = unique_id.lower().replace(".local", "")
            
            # Check if we already have this entry
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured(
                updates={
                    "host": host,
                    "port": port,
                    "client_id": client_id
                }
            )
            
            # Store discovered device info for password step
            self._selected_device = {
                "host": host,
                "port": port,
                "client_id": client_id,
                "properties": properties,
                "requires_password": requires_password
            }
            
            # Set context title for UI
            self.context["title_placeholders"] = {
                "name": client_id,
                "host": host,
                "port": str(port)
            }
            
            # If password required, go to password step, otherwise create entry directly
            if requires_password:
                self._password_step_data = {
                    "host": host,
                    "port": port,
                    "client_id": client_id
                }
                return await self.async_step_password()
            else:
                # No password required, create entry directly
                return self.async_create_entry(
                    title=f"OpenCtrol - {client_id}",
                    data={
                        "host": host,
                        "port": port,
                        "client_id": client_id,
                        "password": "",
                        "base_url": f"http://{host}:{port}"
                    }
                )
                
        except ImportError as ex:
            # Integration not installed - show helpful error
            _LOGGER.error(f"OpenCtrol integration not installed: {ex}")
            return self.async_abort(
                reason="integration_not_installed",
                description_placeholders={
                    "repo_url": "https://github.com/Kaando2000/opencrol-integration",
                    "hacs_url": "https://hacs.xyz"
                }
            )
        except Exception as ex:
            _LOGGER.exception(f"Error processing zeroconf discovery: {ex}")
            # Fall back to manual entry
            return await self.async_step_manual()


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
