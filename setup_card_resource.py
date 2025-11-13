"""
Helper script to automatically add the OpenCtrol card resource to Home Assistant.

This can be run as a Home Assistant script or automation to automatically
add the card resource after the integration is installed.

Usage in Home Assistant:
1. Create a new script in Home Assistant
2. Copy the content of this file
3. Run the script after installing the integration
"""

import logging
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

async def async_setup_card_resource(hass: HomeAssistant):
    """Automatically add the OpenCtrol card resource."""
    try:
        # Get the frontend store
        frontend = hass.data.get("frontend")
        if not frontend:
            _LOGGER.warning("Frontend not available")
            return False
        
        # Get resources
        resources = await hass.http.async_get_resources()
        
        # Check if resource already exists
        card_url = "/local/opencrol/opencrol-remote-card.js"
        for resource in resources:
            if resource.get("url") == card_url:
                _LOGGER.info("Card resource already exists")
                return True
        
        # Add resource
        # Note: This requires direct access to the frontend store
        # which may not be available in all Home Assistant versions
        _LOGGER.info("Card resource needs to be added manually")
        _LOGGER.info(f"Go to Settings → Dashboards → Resources → Add Resource")
        _LOGGER.info(f"URL: {card_url}")
        _LOGGER.info("Type: JavaScript Module")
        
        return False
    except Exception as ex:
        _LOGGER.error(f"Error setting up card resource: {ex}")
        return False

