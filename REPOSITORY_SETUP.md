# Repository Setup Guide for HACS

This guide will help you set up the OpenCtrol integration as a GitHub repository that can be installed via HACS.

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click **"+"** → **"New repository"**
3. Repository name: `opencrol` or `opencrol-integration`
4. Description: "OpenCtrol Home Assistant Integration - Remote control for Windows PCs"
5. Visibility: **Public** (required for HACS)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click **"Create repository"**

## Step 2: Initialize Git Repository

```bash
cd Integration
git init
git add .
git commit -m "Initial commit - OpenCtrol Home Assistant Integration"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/opencrol-integration.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Step 3: Create Release

1. Go to your repository on GitHub
2. Click **"Releases"** → **"Create a new release"**
3. Tag version: `v2.0.0`
4. Release title: `v2.0.0`
5. Description: Copy from CHANGELOG.md or write release notes
6. Click **"Publish release"**

## Step 4: Verify HACS Compatibility

The repository is already configured for HACS with:
- ✅ `hacs.json` file
- ✅ Proper directory structure (`custom_components/opencrol/`)
- ✅ `manifest.json` with required fields
- ✅ GitHub Actions workflow for validation

## Step 5: Test HACS Installation

1. In Home Assistant, go to **HACS** → **Integrations**
2. Click **"+"** → **Custom Repository**
3. Add: `https://github.com/YOUR_USERNAME/opencrol-integration`
4. Category: **Integration**
5. Click **Install**
6. Restart Home Assistant

## Step 6: Add Card Resource

After installation and restart:

1. Go to **Settings** → **Dashboards** → **Resources**
2. Click **"+ ADD RESOURCE"**
3. URL: `/local/opencrol/opencrol-remote-card.js`
4. Type: **JavaScript Module**
5. Click **CREATE**

## Repository Structure

```
opencrol-integration/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/
│       ├── validate.yml
│       └── hacs.yml
├── custom_components/
│   └── opencrol/
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── coordinator.py
│       ├── http_client.py
│       ├── discovery.py
│       ├── services.py
│       ├── services.yaml
│       ├── remote.py
│       ├── media_player.py
│       ├── number.py
│       ├── select.py
│       ├── button.py
│       └── www/
│           ├── opencrol-remote-card.js
│           └── opencrol-remote-card.css
├── .gitignore
├── hacs.json
├── README.md
└── LICENSE
```

## Future Updates

To release updates:

1. Update version in `custom_components/opencrol/manifest.json`
2. Update version in `hacs.json` if needed
3. Commit changes:
   ```bash
   git add .
   git commit -m "Update to v2.0.1"
   git push
   ```
4. Create new release on GitHub with tag `v2.0.1`

## HACS Default Repository (Optional)

To make it available in HACS default repository list:

1. Fork the [HACS default repository](https://github.com/hacs/default)
2. Add your integration to the appropriate category
3. Submit a pull request

## Notes

- The card resource must be added manually after installation (HACS limitation)
- The integration automatically registers the static path for the card
- Users will see instructions in the logs about adding the card resource
- Consider creating a setup script or automation to auto-add the resource (future enhancement)

