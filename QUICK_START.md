# Quick Start - HACS Installation

## 🚀 Install via HACS (5 minutes)

### Step 1: Install via HACS

1. Open Home Assistant
2. Go to **HACS** → **Integrations**
3. Click **"+"** (top right)
4. Search for **"OpenCtrol"** or add custom repository:
   - Repository: `https://github.com/YOUR_USERNAME/opencrol-integration`
   - Category: **Integration**
5. Click **Install**
6. **Restart Home Assistant**

### Step 2: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **"Add Integration"**
3. Search for **"OpenCtrol"**
4. Enter your Windows PC details:
   - **Host**: IP address (e.g., `192.168.1.100`)
   - **Port**: `8080` (default)
   - **Client ID**: Unique name (e.g., `MyPC`)
   - **API Key**: (optional)
5. Click **Submit**

### Step 3: Add Card Resource

1. Go to **Settings** → **Dashboards** → **Resources**
2. Click **"+ ADD RESOURCE"**
3. Enter:
   - **URL**: `/local/opencrol/opencrol-remote-card.js`
   - **Type**: **JavaScript Module**
4. Click **CREATE**

### Step 4: Add Card to Dashboard

1. Edit any dashboard
2. Click **"+ ADD CARD"**
3. Search for **"OpenCtrol Remote"**
4. Select your media player entity
5. Click **ADD**

## ✅ Done!

You can now:
- View your PC screen in real-time
- Control mouse and keyboard
- Adjust volume
- Take screenshots
- Switch monitors

## Troubleshooting

**Card not appearing?**
- Check Resources: Settings → Dashboards → Resources
- Verify `/local/opencrol/opencrol-remote-card.js` is listed
- Clear browser cache (Ctrl+Shift+R)

**Connection errors?**
- Verify Windows client is running
- Check firewall settings
- Verify IP address and port

