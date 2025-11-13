"""Auto-discovery for OpenCtrol devices."""

import logging
from typing import Any
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf

_LOGGER = logging.getLogger(__name__)


class OpenCtrolListener(ServiceListener):
    """Listener for OpenCtrol mDNS services."""

    def __init__(self, callback):
        """Initialize listener."""
        self.callback = callback

    def add_service(self, zeroconf: Zeroconf, service_type: str, name: str) -> None:
        """Handle service discovered."""
        info = zeroconf.get_service_info(service_type, name)
        if info:
            properties = {}
            for key, value in info.properties.items():
                key_str = key.decode() if isinstance(key, bytes) else str(key)
                value_str = value.decode() if isinstance(value, bytes) else str(value)
                properties[key_str] = value_str

            host = str(info.parsed_addresses()[0]) if info.parsed_addresses() else None
            port = info.port

            _LOGGER.info(f"Discovered OpenCtrol device: {name} at {host}:{port}")
            self.callback({
                "name": name,
                "host": host,
                "port": port,
                "properties": properties
            })

    def remove_service(self, zeroconf: Zeroconf, service_type: str, name: str) -> None:
        """Handle service removed."""
        _LOGGER.info(f"OpenCtrol device removed: {name}")

    def update_service(self, zeroconf: Zeroconf, service_type: str, name: str) -> None:
        """Handle service updated."""
        pass


async def discover_opencrol_devices(zeroconf_instance=None) -> list[dict[str, Any]]:
    """Discover OpenCtrol devices on the network.
    
    Args:
        zeroconf_instance: Optional shared Zeroconf instance from Home Assistant.
                          If None, creates a new instance (not recommended in HA).
    """
    devices = []
    
    try:
        # Use shared instance if provided, otherwise create new one
        if zeroconf_instance is not None:
            zeroconf = zeroconf_instance
            _LOGGER.debug("Using shared Zeroconf instance from Home Assistant")
        else:
            zeroconf = Zeroconf()
            _LOGGER.warning("Creating new Zeroconf instance - should use shared instance in Home Assistant")

        def on_device_found(device_info):
            devices.append(device_info)
            _LOGGER.info(f"Discovered device: {device_info.get('name')} at {device_info.get('host')}:{device_info.get('port')}")

        listener = OpenCtrolListener(on_device_found)
        browser = ServiceBrowser(zeroconf, "_opencrol._tcp.local.", listener)

        # Wait longer for discovery (mDNS can be slow, especially on Windows)
        import asyncio
        _LOGGER.info("Searching for OpenCtrol devices on local network...")
        # Try multiple times with shorter intervals to catch services that register late
        for i in range(3):
            await asyncio.sleep(3)  # 3 seconds x 3 = 9 seconds total
            if devices:
                _LOGGER.info(f"Found {len(devices)} device(s) after {3*(i+1)} seconds")
                break

        browser.cancel()
        # Only close if we created the instance ourselves
        if zeroconf_instance is None:
            zeroconf.close()
        
        _LOGGER.info(f"Discovery complete. Found {len(devices)} device(s)")
    except Exception as ex:
        _LOGGER.error(f"Error during mDNS discovery: {ex}", exc_info=True)

    return devices

