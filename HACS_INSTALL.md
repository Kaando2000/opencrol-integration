# HACS Installation Guide

## Quick Install via HACS

### Prerequisites
- Home Assistant 2024.1.0 or later
- [HACS](https://hacs.xyz/) installed

### Installation Steps

1. **Open HACS**
   - Go to **HACS** in your Home Assistant sidebar
   - Click **Integrations**

2. **Add Custom Repository**
   - Click the **"+"** button (top right)
   - Repository: `https://github.com/YOUR_USERNAME/opencrol-integration`
   - Category: **Integration**
   - Click **Add**

3. **Install Integration**
   - Find **OpenCtrol** in the list
   - Click **Install**
   - Wait for installation to complete
   - **Restart Home Assistant**

4. **Add Card Resource** (Required)
   - Go to **Settings** → **Dashboards** → **Resources**
   - Click **"+ ADD RESOURCE"**
   - URL: `/local/opencrol/opencrol-remote-card.js`
   - Type: **JavaScript Module**
   - Click **CREATE**

5. **Configure Integration**
   - Go to **Settings** → **Devices & Services**
   - Click **"Add Integration"**
   - Search for **"OpenCtrol"**
   - Enter your Windows PC connection details

6. **Add Card to Dashboard**
   - Edit any dashboard
   - Click **"+ ADD CARD"**
   - Search for **"OpenCtrol Remote"**
   - Select your media player entity

## Automatic Updates

HACS will automatically notify you when updates are available:
- Go to **HACS** → **Integrations**
- Look for the update badge on OpenCtrol
- Click **Update** to install the latest version

## Troubleshooting

### Card Not Appearing
- Verify resource is added (Step 4 above)
- Clear browser cache
- Check browser console for errors

### Integration Not Found
- Verify repository URL is correct
- Check HACS logs for errors
- Ensure repository is public on GitHub

### Installation Fails
- Check Home Assistant logs
- Verify you have the latest HACS version
- Try manual installation as fallback

## Manual Installation (Fallback)

If HACS installation fails:

1. Download the repository as ZIP
2. Extract to `custom_components/opencrol/`
3. Restart Home Assistant
4. Follow steps 4-6 above

