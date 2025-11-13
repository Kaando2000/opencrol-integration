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
    CONF_MQTT_BROKER,
    CONF_MQTT_USERNAME,
    CONF_MQTT_PASSWORD,
    CONF_CLIENT_ID,
    CONF_AUTH_KEY,
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenCtrol."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        
        # Try auto-discovery if no user input yet
        if user_input is None:
            try:
                from . import discovery
                devices = await discovery.discover_opencrol_devices()
                if devices:
                    _LOGGER.info(f"Discovered {len(devices)} OpenCtrol device(s)")
                    # Show discovered devices as options
                    # For now, we'll just log them and let user enter manually
            except Exception as ex:
                _LOGGER.debug(f"Auto-discovery failed: {ex}")

        if user_input is not None:
            try:
                # Validate connection
                host = user_input.get("host", "")
                port = user_input.get("port", 8080)
                client_id = user_input.get(CONF_CLIENT_ID, "default")
                api_key = user_input.get("api_key", "")
                
                # Test connection
                import aiohttp
                base_url = f"http://{host}:{port}"
                headers = {}
                if api_key:
                    headers["X-API-Key"] = api_key
                
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(
                            f"{base_url}/api/v1/health",
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as response:
                            if response.status == 200:
                                # Connection successful
                                pass
                            elif response.status == 401:
                                errors["base"] = "invalid_auth"
                            else:
                                errors["base"] = "cannot_connect"
                    except aiohttp.ClientError:
                        errors["base"] = "cannot_connect"
                    except asyncio.TimeoutError:
                        errors["base"] = "timeout"
                
                if not errors:
                    # Create entry
                    return self.async_create_entry(
                        title=f"OpenCtrol - {client_id}",
                        data=user_input,
                    )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception as ex:
                _LOGGER.exception("Unexpected error during config flow")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host"): str,
                vol.Required("port", default=8080): int,
                vol.Required(CONF_CLIENT_ID): str,
                vol.Optional("api_key"): str,
            }),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

