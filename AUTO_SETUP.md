# Automatic Card Setup

The OpenCtrol integration automatically registers the card resources, but due to Home Assistant's security model, the card resource must be added manually to your Lovelace dashboard resources.

## Automatic Setup (After Installation)

After installing the integration via HACS:

1. **Restart Home Assistant** (required)
2. **Add Card Resource:**
   - Go to **Settings** → **Dashboards** → **Resources**
   - Click **"+ ADD RESOURCE"**
   - URL: `/local/opencrol/opencrol-remote-card.js`
   - Type: **JavaScript Module**
   - Click **CREATE**

## Verification

After adding the resource:

1. Go to **Settings** → **Dashboards**
2. Edit any dashboard
3. Click **"+ ADD CARD"**
4. Search for **"OpenCtrol Remote"**
5. The card should appear in the list

## Troubleshooting

### Card Not in List

1. **Check Resource:**
   - Settings → Dashboards → Resources
   - Verify `/local/opencrol/opencrol-remote-card.js` is listed
   - If not, add it (see above)

2. **Check Browser Console:**
   - Press F12
   - Look for errors loading the card
   - Check Network tab for 404 errors

3. **Clear Cache:**
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Or clear browser cache completely

4. **Check Logs:**
   - Settings → System → Logs
   - Look for "Registered OpenCtrol frontend resources" message

## Future Enhancement

A future version may include automatic resource registration via a Home Assistant script or automation. For now, manual addition is required for security reasons.

