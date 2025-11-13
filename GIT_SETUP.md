# Git Repository Setup Instructions

Follow these steps to create a GitHub repository and make the integration available via HACS.

## Quick Setup

### 1. Create GitHub Repository

```bash
# On GitHub.com:
# 1. Click "+" → "New repository"
# 2. Name: opencrol-integration (or opencrol)
# 3. Description: "OpenCtrol Home Assistant Integration"
# 4. Public visibility
# 5. DO NOT initialize with README
# 6. Click "Create repository"
```

### 2. Initialize and Push

```bash
cd Integration

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - OpenCtrol Home Assistant Integration v2.0.0"

# Rename branch to main
git branch -M main

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/opencrol-integration.git

# Push to GitHub
git push -u origin main
```

### 3. Create First Release

1. Go to your repository on GitHub
2. Click **"Releases"** → **"Draft a new release"**
3. **Tag version**: `v2.0.0`
4. **Release title**: `v2.0.0 - Initial Release`
5. **Description**:
   ```markdown
   ## Initial Release
   
   - Full Home Assistant integration
   - Custom Lovelace card with screen streaming
   - Mouse and keyboard control
   - Audio management
   - Multi-monitor support
   - Auto-discovery via mDNS
   ```
6. Click **"Publish release"**

### 4. Install via HACS

1. In Home Assistant, go to **HACS** → **Integrations**
2. Click **"+"** → **Custom Repository**
3. Repository: `https://github.com/YOUR_USERNAME/opencrol-integration`
4. Category: **Integration**
5. Click **Install**
6. Restart Home Assistant

### 5. Add Card Resource

After restart:

1. **Settings** → **Dashboards** → **Resources**
2. **"+ ADD RESOURCE"**
3. URL: `/local/opencrol/opencrol-remote-card.js`
4. Type: **JavaScript Module**
5. **CREATE**

## Repository Structure

Your repository should have this structure:

```
opencrol-integration/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/
│       ├── validate.yml
│       ├── hacs.yml
│       └── release.yml
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
│       ├── const.py
│       └── www/
│           ├── opencrol-remote-card.js
│           └── opencrol-remote-card.css
├── .gitignore
├── hacs.json
├── README.md
├── LICENSE
├── REPOSITORY_SETUP.md
├── AUTO_SETUP.md
└── GIT_SETUP.md
```

## Updating the Repository

When you make changes:

```bash
# Stage changes
git add .

# Commit
git commit -m "Description of changes"

# Push
git push

# Create new release for version updates
# 1. Update version in manifest.json
# 2. Create new release on GitHub
```

## HACS Validation

The repository includes GitHub Actions workflows that automatically validate HACS compatibility on:
- Every push
- Every pull request
- Daily (scheduled)

Check the **Actions** tab in your GitHub repository to see validation results.

## Making it a Default HACS Repository (Optional)

To make it available in HACS default repository list:

1. Fork [hacs/default](https://github.com/hacs/default)
2. Add your integration to `integration` category
3. Submit a pull request

## Notes

- ✅ Repository is already configured for HACS
- ✅ All required files are in place
- ✅ GitHub Actions workflows are configured
- ⚠️ Card resource must be added manually (Home Assistant security requirement)
- ✅ Integration automatically registers the card path

## Support

For issues or questions:
- Open an issue on GitHub
- Check the README.md for documentation
- Review AUTO_SETUP.md for card setup instructions

