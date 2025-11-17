# Lovelace Card Troubleshooting Guide

## Issue: Card Not Appearing in Card Picker / "Custom element does not exist"

### Quick Fix Steps

1. **Restart Home Assistant** - This ensures the integration loads the card files
2. **Clear Browser Cache** - Press `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac) to hard refresh
3. **Manually Add Resource** (if auto-registration fails):
   - Go to **Settings** → **Dashboards** → **Resources**
   - Click **"+ ADD RESOURCE"**
   - URL: `/local/opencrol/opencrol-remote-card.js`
   - Type: **JavaScript Module**
   - Click **CREATE**
   - Clear browser cache and refresh

### Verify Card Files Exist

Check that these files exist in your Home Assistant installation:
- `custom_components/opencrol/www/opencrol-remote-card.js`
- `custom_components/opencrol/www/opencrol-remote-card.css`

### Check Browser Console

1. Open browser Developer Tools (F12)
2. Go to **Console** tab
3. Look for:
   - `OpenCtrol Remote card registered:` - confirms card loaded
   - Any errors about missing files or failed loads
   - Check Network tab for 404 errors on `/local/opencrol/opencrol-remote-card.js`

### Verify Static Path Registration

Check Home Assistant logs for:
- `✓ Registered static path: /local/opencrol -> ...`
- `✓ Automatically added Lovelace card resource: ...`

If you see warnings, the static path registration failed and you need to manually add the resource.

### Manual Resource Addition

If auto-registration fails:

1. **Settings** → **Dashboards** → **Resources**
2. Click **"+ ADD RESOURCE"**
3. Enter:
   - **URL**: `/local/opencrol/opencrol-remote-card.js`
   - **Type**: `JavaScript Module`
4. Click **CREATE**
5. **Clear browser cache** (Ctrl+Shift+R)
6. Refresh the page

### Verify Card is Loaded

After adding the resource, check browser console:
```javascript
// Should return the card definition
window.customCards.find(c => c.type === 'custom:opencrol-remote-card')

// Should return the custom element constructor
customElements.get('opencrol-remote-card')
```

### Common Issues

1. **"Custom element does not exist"**
   - Card file not loaded - check resource is added
   - Browser cache - clear and refresh
   - Wrong URL - must be `/local/opencrol/opencrol-remote-card.js`

2. **Card not in picker list**
   - Resource not added to Lovelace
   - Card not registered in `window.customCards`
   - Check browser console for registration messages

3. **404 Error on card file**
   - Static path not registered
   - Files not in correct location
   - Check integration logs for static path registration

### Alternative: Copy Files to www Directory

If static path registration fails, you can manually copy files:

1. Copy `custom_components/opencrol/www/` to `www/opencrol/`
2. Add resource: `/local/opencrol/opencrol-remote-card.js`
3. Restart Home Assistant
4. Clear browser cache

### Still Not Working?

1. Check Home Assistant logs for errors
2. Verify integration is loaded: **Settings** → **Devices & Services** → **OpenCtrol**
3. Check browser console for JavaScript errors
4. Verify file permissions (files should be readable)
5. Try accessing the card file directly: `http://your-ha-ip:8123/local/opencrol/opencrol-remote-card.js`

