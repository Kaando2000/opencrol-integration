# Push to GitHub - Step by Step Guide

## Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. **Repository name**: `opencrol-integration` (or your preferred name)
3. **Description**: "OpenCtrol Home Assistant Integration - Remote control for Windows PCs"
4. **Visibility**: **Public** (required for HACS)
5. **DO NOT** check:
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
6. Click **"Create repository"**

## Step 2: Initialize Git (if not done)

If you haven't run the setup script yet:

```powershell
cd E:\OpenCtrol\Cursor\Integration
git init
git branch -M main
git add .
git commit -m "Initial commit - OpenCtrol Home Assistant Integration v2.0.0"
```

## Step 3: Add Remote and Push

Replace `YOUR_USERNAME` with your GitHub username:

```powershell
cd E:\OpenCtrol\Cursor\Integration

# Add remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/opencrol-integration.git

# Push to GitHub
git push -u origin main
```

If you get authentication errors, you may need to:
- Use a Personal Access Token instead of password
- Or use SSH: `git@github.com:YOUR_USERNAME/opencrol-integration.git`

## Step 4: Create First Release

1. Go to your repository on GitHub
2. Click **"Releases"** → **"Create a new release"**
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

## Step 5: Verify HACS Compatibility

1. Go to your repository → **Actions** tab
2. You should see workflows running
3. Wait for them to complete (should show ✅)

## Step 6: Install via HACS

1. In Home Assistant, go to **HACS** → **Integrations**
2. Click **"+"** → **Custom Repository**
3. Repository: `https://github.com/YOUR_USERNAME/opencrol-integration`
4. Category: **Integration**
5. Click **Install**
6. Restart Home Assistant

## Troubleshooting

### Authentication Issues

If `git push` fails with authentication:

**Option 1: Use Personal Access Token**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Use token as password when pushing

**Option 2: Use SSH**
```powershell
git remote set-url origin git@github.com:YOUR_USERNAME/opencrol-integration.git
git push -u origin main
```

### Remote Already Exists

If you get "remote origin already exists":
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/opencrol-integration.git
```

### Push Rejected

If push is rejected:
```powershell
git pull origin main --allow-unrelated-histories
# Resolve any conflicts, then:
git push -u origin main
```

## Quick Command Reference

```powershell
# Navigate to Integration directory
cd E:\OpenCtrol\Cursor\Integration

# Check status
git status

# Add all files
git add .

# Commit
git commit -m "Initial commit - OpenCtrol Integration v2.0.0"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/opencrol-integration.git

# Push
git push -u origin main
```

## Next Steps After Push

1. ✅ Create release on GitHub
2. ✅ Verify GitHub Actions pass
3. ✅ Test HACS installation
4. ✅ Share repository URL with users

