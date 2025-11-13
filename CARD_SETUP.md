# OpenCtrol Lovelace Card Setup

## ✅ Card Status: Ready to Use

The OpenCtrol custom Lovelace card is fully implemented and ready for use!

## Installation

### Step 1: Install the Integration

1. Copy the `custom_components/opencrol` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the integration via Settings → Devices & Services → Add Integration

### Step 2: Add Card Resource

1. Go to **Settings** → **Dashboards** → **Resources** (or **Developer Tools** → **YAML** → **Resources**)
2. Click **"+ ADD RESOURCE"**
3. Enter the resource URL:
   ```
   /local/opencrol/opencrol-remote-card.js
   ```
4. Set resource type to **JavaScript Module**
5. Click **CREATE**

### Step 3: Add Card to Dashboard

1. Edit your Lovelace dashboard
2. Click **"+ ADD CARD"**
3. Search for **"OpenCtrol Remote"** or select **"Custom: OpenCtrol Remote Card"**
4. Configure the card:
   ```yaml
   type: custom:opencrol-remote-card
   entity: media_player.opencrol_your_pc_screen
   base_url: http://192.168.1.100:8080  # Optional: override base URL
   ```

## Card Features

✅ **Live Screen Viewing** - Real-time MJPEG stream  
✅ **Mouse Control** - Click, right-click, middle-click, Ctrl+Alt+Del  
✅ **Keyboard Input** - Type text, send keys, key combinations  
✅ **Volume Control** - Master volume slider  
✅ **Monitor Selection** - Switch between multiple displays  
✅ **Status Display** - Online/offline indicator  

## Card Configuration

```yaml
type: custom:opencrol-remote-card
entity: media_player.opencrol_mypc_screen
base_url: http://192.168.1.100:8080  # Optional
```

### Configuration Options

- **entity** (required): The media_player entity for your OpenCtrol device
- **base_url** (optional): Override the base URL for API calls (defaults to entity attributes)

## Troubleshooting

### Card Not Appearing

1. **Check Resource is Added:**
   - Go to Settings → Dashboards → Resources
   - Verify `/local/opencrol/opencrol-remote-card.js` is listed
   - If missing, add it (see Step 2 above)

2. **Check Browser Console:**
   - Press F12 in your browser
   - Look for JavaScript errors
   - Check if card files are loading

3. **Clear Browser Cache:**
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Or clear browser cache completely

### Screen Not Showing

1. **Check Entity State:**
   - Verify the media_player entity is `on` or `online`
   - Check entity attributes for `stream_url` and `frame_url`

2. **Check Network:**
   - Ensure Home Assistant can reach the Windows PC
   - Verify the base URL is correct
   - Check firewall settings

3. **Check Windows Client:**
   - Ensure OpenCtrol client is running
   - Verify screen capture is started
   - Check client logs for errors

### Controls Not Working

1. **Check API Connection:**
   - Verify the Windows client API is accessible
   - Test with: `http://YOUR_PC_IP:8080/api/v1/health`

2. **Check Entity:**
   - Ensure the entity ID is correct
   - Verify the coordinator is updating

## Manual Card Resource URL

If the automatic registration doesn't work, you can manually add the card resource:

**Resource URL:** `/local/opencrol/opencrol-remote-card.js`  
**Resource Type:** JavaScript Module

## Files Included

- `opencrol-remote-card.js` - Main card JavaScript
- `opencrol-remote-card.css` - Card styling

Both files are automatically served from the integration's `www` directory.

## Support

For issues or questions:
- Check the main README.md
- Review Home Assistant logs
- Check Windows client logs
- Open an issue on GitHub

