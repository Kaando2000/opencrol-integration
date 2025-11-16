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
    
    Returns:
        List of discovered device dictionaries with host, port, and properties.
    """
    devices = []
    zeroconf = None
    browser = None
    
    try:
        # Use shared instance if provided, otherwise create new one
        if zeroconf_instance is not None:
            zeroconf = zeroconf_instance
            _LOGGER.debug("Using shared Zeroconf instance from Home Assistant")
        else:
            zeroconf = Zeroconf()
            _LOGGER.warning("Creating new Zeroconf instance - should use shared instance in Home Assistant")

        def on_device_found(device_info):
            # Validate device info before adding
            host = device_info.get('host')
            port = device_info.get('port')
            
            if not host:
                _LOGGER.warning(f"Discovered device missing host: {device_info.get('name')}")
                return
            
            if not port or port <= 0:
                _LOGGER.warning(f"Discovered device has invalid port: {device_info.get('name')} - {port}")
                return
            
            devices.append(device_info)
            _LOGGER.info(f"Discovered OpenCtrol device: {device_info.get('name')} at {host}:{port}")

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
        
        if not devices:
            _LOGGER.info("No OpenCtrol devices discovered after 9 seconds")
        
    except Exception as ex:
        _LOGGER.error(f"Error during mDNS discovery: {ex}", exc_info=True)
    finally:
        # Clean up browser and zeroconf instance
        if browser:
            try:
                browser.cancel()
            except Exception as ex:
                _LOGGER.debug(f"Error canceling browser: {ex}")
        
        # Only close if we created the instance ourselves
        if zeroconf_instance is None and zeroconf:
            try:
                zeroconf.close()
            except Exception as ex:
                _LOGGER.debug(f"Error closing Zeroconf instance: {ex}")
        
        _LOGGER.info(f"Discovery complete. Found {len(devices)} device(s)")

    return devices

