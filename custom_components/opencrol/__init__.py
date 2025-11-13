"""OpenCtrol Integration for Home Assistant."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import logging

from .const import DOMAIN
from .coordinator import OpenCtrolCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenCtrol from a config entry."""
    _LOGGER.info("Setting up OpenCtrol integration")

    coordinator = OpenCtrolCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register frontend resources for Lovelace card
    try:
        from pathlib import Path
        www_dir = Path(__file__).parent / "www"
        if www_dir.exists():
            # Register static path for card resources
            # Card will be available at: /local/opencrol/opencrol-remote-card.js
            # Try different methods based on Home Assistant version
            try:
                if hasattr(hass.http, 'register_static_path'):
                    hass.http.register_static_path(
                        f"/local/opencrol",
                        str(www_dir),
                        cache_headers=False
                    )
                elif hasattr(hass.http, 'app'):
                    # Alternative: register with the app router
                    from aiohttp import web
                    hass.http.app.router.add_static(
                        "/local/opencrol",
                        str(www_dir)
                    )
                else:
                    _LOGGER.warning("Could not register static path - card may need manual setup")
            except AttributeError as ex:
                _LOGGER.warning(f"Could not register static path: {ex} - card may need manual setup")
            
            # Auto-register card resource if frontend is available
            try:
                # Try to automatically add the card resource
                frontend = hass.data.get("frontend")
                if frontend:
                    # Get the frontend store
                    frontend_store = frontend.get("store")
                    if frontend_store:
                        # Add resource automatically
                        card_url = "/local/opencrol/opencrol-remote-card.js"
                        _LOGGER.info(f"Card available at: {card_url}")
                        _LOGGER.info("Add this resource manually: Settings → Dashboards → Resources → Add Resource")
                        _LOGGER.info(f"Resource URL: {card_url}")
                        _LOGGER.info("Resource Type: JavaScript Module")
            except Exception:
                pass  # Frontend not available yet, user will add manually
            
            _LOGGER.info(f"Registered OpenCtrol frontend resources from {www_dir}")
        else:
            _LOGGER.warning(f"www directory not found at {www_dir}")
    except Exception as ex:
        _LOGGER.warning(f"Failed to register frontend resources: {ex}")

    # Setup platforms - register all entity types
    platforms = ["remote", "media_player", "number", "select", "button"]
    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    # Setup services
    from . import services
    services.async_setup_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload OpenCtrol config entry."""
    _LOGGER.info("Unloading OpenCtrol integration")

    platforms = ["remote", "media_player", "number", "select", "button"]
    unload_ok = await hass.config_entries.async_unload_platforms(entry, platforms)
    
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        if coordinator:
            await coordinator.async_shutdown()

    return unload_ok

