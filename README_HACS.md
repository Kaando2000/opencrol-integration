# OpenCtrol - HACS Ready Integration

## ✅ Repository is HACS-Ready!

This integration is fully configured for HACS installation with automatic card resource registration.

## 🚀 Quick Setup (3 Steps)

### 1. Create GitHub Repository

Run the setup script:
```powershell
cd Integration
.\setup_repository.ps1
```

Or manually:
```bash
cd Integration
git init
git add .
git commit -m "Initial commit - OpenCtrol Integration v2.0.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/opencrol-integration.git
git push -u origin main
```

### 2. Create Release on GitHub

1. Go to your repository → **Releases** → **Create new release**
2. Tag: `v2.0.0`
3. Title: `v2.0.0 - Initial Release`
4. Publish

### 3. Install via HACS

1. **HACS** → **Integrations** → **"+"**
2. Repository: `https://github.com/YOUR_USERNAME/opencrol-integration`
3. Category: **Integration**
4. Click **Install**
5. **Restart Home Assistant**

## 📦 What's Included

### Integration Files
- ✅ All Python integration files
- ✅ Config flow with auto-discovery
- ✅ HTTP client with retry logic
- ✅ All entity platforms (remote, media_player, number, select, button)
- ✅ Services definitions

### Lovelace Card
- ✅ JavaScript card file (`opencrol-remote-card.js`)
- ✅ CSS styling (`opencrol-remote-card.css`)
- ✅ Auto-loads CSS from JavaScript
- ✅ Registered at `/local/opencrol/`

### HACS Configuration
- ✅ `hacs.json` - HACS metadata
- ✅ GitHub Actions workflows
- ✅ Issue templates
- ✅ Proper directory structure

## 🎯 Card Auto-Setup

The card is **automatically registered** when the integration loads. Users just need to:

1. Add the resource URL: `/local/opencrol/opencrol-remote-card.js`
2. Type: **JavaScript Module**

The integration logs clear instructions on how to add it.

## 📋 Repository Structure

```
opencrol-integration/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/
│       ├── validate.yml      # HACS validation
│       ├── hacs.yml          # HACS action
│       └── release.yml       # Release validation
├── custom_components/
│   └── opencrol/
│       ├── __init__.py       # Auto-registers card path
│       ├── manifest.json     # Integration manifest
│       ├── www/              # Card files
│       │   ├── opencrol-remote-card.js
│       │   └── opencrol-remote-card.css
│       └── ... (all other files)
├── .gitignore
├── hacs.json                 # HACS configuration
├── README.md                 # Main documentation
├── LICENSE                   # MIT License
└── CHANGELOG.md              # Version history
```

## 🔄 Updates

When you update the integration:

1. Update version in `custom_components/opencrol/manifest.json`
2. Update `CHANGELOG.md`
3. Commit and push:
   ```bash
   git add .
   git commit -m "Update to v2.0.1"
   git push
   ```
4. Create new release on GitHub with tag `v2.0.1`

HACS will automatically detect the new version and notify users.

## ✅ HACS Validation

The repository includes GitHub Actions that automatically validate:
- ✅ HACS compatibility
- ✅ Integration structure
- ✅ Required files
- ✅ Manifest validation

Check the **Actions** tab in your GitHub repository to see validation results.

## 📝 Notes

- **Card Resource**: Must be added manually (Home Assistant security requirement)
- **Auto-Discovery**: Works if Windows client has mDNS enabled
- **Updates**: HACS will notify users of new versions
- **Compatibility**: Home Assistant 2024.1.0+

## 🎉 Ready to Publish!

Your integration is ready for HACS! Just:
1. Push to GitHub
2. Create a release
3. Share the repository URL
4. Users can install via HACS!

