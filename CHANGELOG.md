# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-11-13

### Added
- Initial release of OpenCtrol Home Assistant Integration
- Full HTTP REST API integration (replacing MQTT)
- Custom Lovelace card with live screen streaming
- Mouse control (move, click, scroll)
- Keyboard control (type, keys, combinations)
- Audio management (master and per-app volume)
- Multi-monitor support
- Secure desktop access (Ctrl+Alt+Del, login screen)
- Auto-discovery via mDNS/Bonjour
- Screenshot functionality
- Client restart capability
- Per-app audio device selection

### Features
- **Live Screen Viewing**: Real-time MJPEG stream
- **Interactive Controls**: Mouse and keyboard via card UI
- **Volume Control**: Master and per-application sliders
- **Monitor Selection**: Switch between multiple displays
- **Status Indicators**: Online/offline status display

### Technical
- HTTP client with retry logic and connection pooling
- Coordinator with automatic data updates
- Comprehensive error handling
- Connection validation during setup
- Resource management and cleanup

## [Unreleased]

### Planned
- WebRTC video streaming (structure ready)
- Automatic card resource registration
- Enhanced auto-discovery UI
- Windows Service installation option

