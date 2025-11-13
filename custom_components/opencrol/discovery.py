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
                properties[key.decode()] = value.decode() if isinstance(value, bytes) else value

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


async def discover_opencrol_devices() -> list[dict[str, Any]]:
    """Discover OpenCtrol devices on the network."""
    devices = []
    zeroconf = Zeroconf()

    def on_device_found(device_info):
        devices.append(device_info)

    listener = OpenCtrolListener(on_device_found)
    browser = ServiceBrowser(zeroconf, "_opencrol._tcp.local.", listener)

    # Wait a bit for discovery
    import asyncio
    await asyncio.sleep(2)

    browser.cancel()
    zeroconf.close()

    return devices

