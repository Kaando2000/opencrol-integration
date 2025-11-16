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
                # Try to automatically add the card resource to Lovelace
                card_url = "/local/opencrol/opencrol-remote-card.js"
                card_type = "module"
                
                # Try to get Lovelace resources manager
                try:
                    from homeassistant.components import lovelace
                    lovelace_data = hass.data.get("lovelace")
                    if lovelace_data:
                        # Try to add resource programmatically
                        try:
                            resources = lovelace_data.get("resources")
                            if resources:
                                # Check if resource already exists
                                existing = False
                                async for resource in resources.async_items():
                                    if resource.get("url") == card_url:
                                        existing = True
                                        break
                                
                                if not existing:
                                    # Add resource
                                    await resources.async_create_item({
                                        "type": card_type,
                                        "url": card_url
                                    })
                                    _LOGGER.info(f"Automatically added Lovelace card resource: {card_url}")
                                else:
                                    _LOGGER.debug(f"Lovelace card resource already exists: {card_url}")
                        except Exception as lovelace_ex:
                            _LOGGER.debug(f"Could not auto-add Lovelace resource (non-critical): {lovelace_ex}")
                            _LOGGER.info(f"Card available at: {card_url} - add manually via Settings → Dashboards → Resources")
                except ImportError:
                    _LOGGER.debug("Lovelace component not available, card will be registered when frontend loads")
                
                _LOGGER.info(f"OpenCtrol remote card available at: {card_url}")
                _LOGGER.info("Add to Lovelace: Settings → Dashboards → Resources → Add Resource")
                _LOGGER.info(f"Resource URL: {card_url}, Type: JavaScript Module")
            except Exception as ex:
                _LOGGER.debug(f"Error auto-registering card resource (non-critical): {ex}")
                _LOGGER.info("Card resource may need to be added manually via Lovelace Resources")
            
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

