# Push Integration to GitHub

## Changes Ready to Push

The following changes have been committed locally and are ready to push:

### Modified Files:
- `custom_components/opencrol/config_flow.py` - Password-only config flow with auto-discovery
- `custom_components/opencrol/const.py` - Updated constants (removed MQTT, added password)
- `custom_components/opencrol/coordinator.py` - Updated to use password instead of API key
- `custom_components/opencrol/discovery.py` - Enhanced mDNS discovery with TXT record parsing
- `custom_components/opencrol/http_client.py` - Updated to use X-Password header

### New Features:
- ✅ Password-only authentication (no API key needed)
- ✅ Auto-discovery of OpenCtrol devices on local network
- ✅ Simplified config flow (only asks for password)
- ✅ Automatic device detection with host/port/client_id

## How to Push

### Option 1: GitHub Desktop (Recommended)
1. Open GitHub Desktop
2. You should see the commit ready to push
3. Click "Push origin" button

### Option 2: Command Line with Personal Access Token
```bash
cd Integration
git push https://YOUR_TOKEN@github.com/Kaando2000/opencrol-integration.git main
```

### Option 3: SSH (if configured)
```bash
cd Integration
git push git@github.com:Kaando2000/opencrol-integration.git main
```

## After Pushing

Once pushed, you can:
1. Install the integration in Home Assistant via HACS or manual installation
2. The integration will auto-discover your OpenCtrol client
3. You'll only need to enter the password to complete setup

## Testing

After installation:
1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "OpenCtrol"
4. The integration should auto-discover your device
5. Enter the password you set in the OpenCtrol client
6. Complete the setup
