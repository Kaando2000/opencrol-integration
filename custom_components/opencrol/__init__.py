"""OpenCtrol Integration for Home Assistant."""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

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
            try:
                if hasattr(hass.http, 'register_static_path'):
                    hass.http.register_static_path(
                        "/local/opencrol",
                        str(www_dir),
                        cache_headers=False
                    )
                    _LOGGER.info(f"Registered static path: /local/opencrol -> {www_dir}")
                elif hasattr(hass.http, 'app'):
                    # Alternative: register with the app router
                    from aiohttp import web
                    hass.http.app.router.add_static(
                        "/local/opencrol",
                        str(www_dir)
                    )
                    _LOGGER.info(f"Registered static path via app router: /local/opencrol -> {www_dir}")
                else:
                    _LOGGER.warning("Could not register static path - card may need manual setup")
            except Exception as ex:
                _LOGGER.warning(f"Could not register static path: {ex} - card may need manual setup")
            
            # Auto-register card resource if frontend is available
            card_url = "/local/opencrol/opencrol-remote-card.js"
            card_type = "module"
            
            # Delay resource registration to ensure frontend is loaded
            async def _register_card_resource():
                try:
                    # Wait for frontend to be available
                    await asyncio.sleep(2)
                    
                    # Try to get Lovelace resources manager
                    try:
                        from homeassistant.components import lovelace
                        
                        lovelace_data = hass.data.get("lovelace")
                        if lovelace_data:
                            try:
                                # Use attribute access instead of .get() for future compatibility (HA 2026.2+)
                                if hasattr(lovelace_data, "resources"):
                                    resources = lovelace_data.resources
                                elif hasattr(lovelace_data, "get"):
                                    resources = lovelace_data.get("resources")
                                else:
                                    resources = None
                                
                                if resources:
                                    # Check if resource already exists
                                    existing = False
                                    try:
                                        async for resource in resources.async_items():
                                            if hasattr(resource, "url"):
                                                url = resource.url
                                            elif isinstance(resource, dict):
                                                url = resource.get("url")
                                            else:
                                                continue
                                            
                                            if url == card_url:
                                                existing = True
                                                break
                                    except Exception:
                                        # If async_items fails, try alternative method
                                        try:
                                            items = await resources.async_get_items()
                                            if items:
                                                for resource in items:
                                                    url = resource.get("url") if isinstance(resource, dict) else getattr(resource, "url", None)
                                                    if url == card_url:
                                                        existing = True
                                                        break
                                        except Exception:
                                            pass
                                    
                                    if not existing:
                                        # Add resource
                                        try:
                                            await resources.async_create_item({
                                                "type": card_type,
                                                "url": card_url
                                            })
                                            _LOGGER.info(f"✓ Automatically added Lovelace card resource: {card_url}")
                                        except Exception as create_ex:
                                            _LOGGER.debug(f"Could not auto-create resource: {create_ex}")
                                            _LOGGER.info(f"Card available at: {card_url} - add manually via Settings → Dashboards → Resources")
                                    else:
                                        _LOGGER.debug(f"Lovelace card resource already exists: {card_url}")
                            except Exception as lovelace_ex:
                                _LOGGER.debug(f"Could not access Lovelace resources: {lovelace_ex}")
                                _LOGGER.info(f"Card available at: {card_url} - add manually via Settings → Dashboards → Resources")
                        else:
                            _LOGGER.debug("Lovelace data not available yet")
                            _LOGGER.info(f"Card available at: {card_url} - add manually via Settings → Dashboards → Resources")
                    except ImportError:
                        _LOGGER.debug("Lovelace component not available")
                        _LOGGER.info(f"Card available at: {card_url} - add manually via Settings → Dashboards → Resources")
                    
                except Exception as ex:
                    _LOGGER.debug(f"Error auto-registering card resource (non-critical): {ex}")
                    _LOGGER.info(f"Card available at: {card_url} - add manually via Settings → Dashboards → Resources")
            
            # Schedule resource registration
            hass.async_create_task(_register_card_resource())
            
            _LOGGER.info(f"Registered OpenCtrol frontend resources from {www_dir}")
            _LOGGER.info(f"Card will be available as 'OpenCtrol Remote' in the card picker")
        else:
            _LOGGER.warning(f"www directory not found at {www_dir}")
    except Exception as ex:
        _LOGGER.warning(f"Failed to register frontend resources: {ex}")


    # Setup platforms - register all entity types
    platforms = ["remote", "media_player", "number", "select", "button"]
    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    # Setup services (only once per domain)
    from . import services
    if DOMAIN not in hass.data or "services_registered" not in hass.data.setdefault(DOMAIN, {}):
        services.async_setup_services(hass)
        hass.data[DOMAIN]["services_registered"] = True

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

