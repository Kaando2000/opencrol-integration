# Fixes Applied - Connection and Permission Issues

## Issues Fixed

### 1. ✅ Connection Closed Error
**Problem:** `aiohttp.client_exceptions.ClientConnectionError: Connection closed`

**Root Cause:** HTTP responses were being read outside the context manager, causing the connection to close before the response body was fully read.

**Solution:** 
- Modified `_retry_request` to return the response object directly (not using context manager)
- Added proper `finally` blocks to all HTTP methods to ensure responses are closed after reading
- All methods now properly close responses: `get_status`, `get_monitors`, `get_audio_apps`, `get_audio_devices`, and all POST methods

**Files Modified:**
- `Integration/custom_components/opencrol/http_client.py`

### 2. ✅ Auto-Discovery Implementation
**Problem:** Auto-discovery not working for finding OpenCtrol devices

**Solution:**
- Added auto-discovery attempt in config flow
- Discovery runs when user opens the integration setup
- Uses zeroconf to discover `_opencrol._tcp.local.` services
- Logs discovered devices (can be enhanced to show in UI)

**Files Modified:**
- `Integration/custom_components/opencrol/config_flow.py`

**Note:** Auto-discovery requires:
- Windows client to be running with mDNS service active
- Network connectivity between Home Assistant and Windows PC
- Firewall rules allowing mDNS traffic

### 3. ✅ Permission Error 740 (Elevation Required)
**Problem:** Error 740 when running client after installation - requires administrator privileges

**Solution:**
- Updated installer to stop running app before installation
- Changed post-install launch to use `runascurrentuser` flag (runs with current user, not admin)
- Added `PrepareToInstall` function to gracefully stop the app before upgrade

**Files Modified:**
- `WindowsClient/OpenCtrolSetup.iss`

**Note:** The application manifest requires administrator privileges (`requireAdministrator`). Users should:
1. Right-click the executable and select "Run as administrator"
2. Or configure Windows to always run with admin privileges
3. Or install as a Windows Service (future enhancement)

## Testing Recommendations

1. **Connection Fix:**
   - Restart Home Assistant
   - Check logs - should no longer see "Connection closed" errors
   - Verify coordinator updates successfully

2. **Auto-Discovery:**
   - Ensure Windows client is running
   - Add integration via UI
   - Check logs for discovery messages
   - Manually enter connection details if discovery doesn't find device

3. **Permission Fix:**
   - Rebuild installer with updated script
   - Test installation on clean system
   - Verify app can start after installation
   - If error 740 persists, run as administrator manually

## Additional Notes

- The connection fix ensures all HTTP responses are properly closed, preventing connection pool exhaustion
- Auto-discovery is a best-effort feature - manual entry is always available
- Permission issues may require running the app as administrator until a Windows Service version is available

