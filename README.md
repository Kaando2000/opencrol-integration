# OpenCtrol Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/opencrol/integration.svg)](https://github.com/opencrol/integration/releases)
[![License](https://img.shields.io/github/license/opencrol/integration.svg)](LICENSE)

Custom Home Assistant integration for controlling Windows PCs remotely via HTTP REST API.

## Features

- **Live Screen Viewing**: Real-time MJPEG stream with interactive controls
- **Mouse Control**: Remote mouse movement, clicks, and scrolling
- **Keyboard Control**: Text input, key combinations, and secure desktop access
- **Audio Management**: Master and per-application volume control
- **Multi-Monitor Support**: Switch between multiple displays
- **Secure Desktop**: Control Windows login screen and secure scenarios
- **Custom Lovelace Card**: Integrated UI with screen view and controls (auto-installed)
- **Auto-Discovery**: Automatic device discovery via mDNS/Bonjour

## Installation

### HACS (Recommended)

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Go to **HACS** → **Integrations**
3. Click **"+"** → **Custom Repository**
4. Add repository: `https://github.com/opencrol/integration`
5. Category: **Integration**
6. Click **Install**
7. Restart Home Assistant

The integration will automatically register the Lovelace card. After restart, add the card resource:

1. Go to **Settings** → **Dashboards** → **Resources**
2. Click **"+ ADD RESOURCE"**
3. Enter: `/local/opencrol/opencrol-remote-card.js`
4. Type: **JavaScript Module**
5. Click **CREATE**

### Manual Installation

1. Copy `custom_components/opencrol` to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add integration via **Settings** → **Devices & Services** → **Add Integration**
4. Add card resource as described above

## Configuration

### Setup via UI

1. Go to **Settings** → **Devices & Services**
2. Click **"Add Integration"**
3. Search for **"OpenCtrol"**
4. Enter connection details:
   - **Host**: IP address or hostname of Windows PC
   - **Port**: HTTP API port (default: 8080)
   - **Client ID**: Unique identifier for this PC
   - **API Key**: Authentication key (optional but recommended)

The integration will automatically validate the connection before saving.

### Auto-Discovery

If your Windows PC is running OpenCtrol with mDNS enabled, the integration will attempt to discover it automatically when you add the integration.

## Usage

### Screen Viewing

The screen viewer appears as a media player entity:

```yaml
# automation.yaml
- alias: View PC Screen
  trigger:
    platform: state
    entity_id: media_player.opencrol_mypc_screen
    to: 'on'
  action:
    - service: media_player.play_media
      target:
        entity_id: media_player.opencrol_mypc_screen
```

### Using the Lovelace Card

Add the card to your dashboard:

```yaml
type: custom:opencrol-remote-card
entity: media_player.opencrol_mypc_screen
```

The card provides:
- Live screen streaming
- Mouse controls (click, right-click, Ctrl+Alt+Del)
- Keyboard input
- Volume control
- Monitor selection

### Mouse Control

```yaml
service: opencrol.move_mouse
target:
  entity_id: media_player.opencrol_mypc_screen
data:
  x: 960
  y: 540

service: opencrol.click
target:
  entity_id: media_player.opencrol_mypc_screen
data:
  button: left
```

### Keyboard Control

```yaml
service: opencrol.type_text
target:
  entity_id: media_player.opencrol_mypc_screen
data:
  text: "Hello World"

service: opencrol.send_key
target:
  entity_id: media_player.opencrol_mypc_screen
data:
  key: "CTRL+S"
```

### Audio Control

```yaml
service: opencrol.set_app_volume
target:
  entity_id: number.opencrol_app_volume_chrome
data:
  volume: 0.75

service: opencrol.set_app_device
target:
  entity_id: select.opencrol_app_device_spotify
data:
  device_id: "headphones_id"
```

## Entities

### Media Player
- `media_player.opencrol_{client_id}_screen` - Screen viewer
  - State: on/off/idle
  - Actions: turn_on, turn_off, take_screenshot

### Number
- `number.opencrol_{client_id}_master_volume` - Master volume (0-1)
- `number.opencrol_{client_id}_app_volume_{app_name}` - Per-app volume

### Select
- `select.opencrol_{client_id}_output_device` - System output device
- `select.opencrol_{client_id}_app_device_{app_name}` - Per-app device

### Button
- `button.opencrol_{client_id}_screenshot` - Take screenshot
- `button.opencrol_{client_id}_restart` - Restart client

## Services

See [services.yaml](custom_components/opencrol/services.yaml) for complete service documentation.

## Requirements

- Home Assistant 2024.1.0 or later
- Windows PC with OpenCtrol client installed
- Network connectivity between HA and Windows PC

## Troubleshooting

### Card Not Appearing

1. **Check Resource is Added:**
   - Go to Settings → Dashboards → Resources
   - Verify `/local/opencrol/opencrol-remote-card.js` is listed
   - If missing, add it manually

2. **Check Browser Console:**
   - Press F12 in your browser
   - Look for JavaScript errors

3. **Clear Browser Cache:**
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

### Connection Issues

- Verify Windows client is running
- Check firewall settings
- Verify IP address and port are correct
- Check Home Assistant logs for errors

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) file

## Support

- **Issues**: [GitHub Issues](https://github.com/opencrol/integration/issues)
- **Documentation**: [Full Documentation](https://github.com/opencrol/integration/wiki)
