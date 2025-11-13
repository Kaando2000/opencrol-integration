# OpenCtrol Integration - Git Repository Setup Script
# This script helps set up the repository for GitHub and HACS

Write-Host "OpenCtrol Integration - Repository Setup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/downloads" -ForegroundColor Red
    exit 1
}

Write-Host "Git found: $(git --version)" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the Integration directory
if (-not (Test-Path "custom_components\opencrol\manifest.json")) {
    Write-Host "ERROR: Please run this script from the Integration directory!" -ForegroundColor Red
    exit 1
}

# Check if git is already initialized
if (Test-Path ".git") {
    Write-Host "Git repository already initialized." -ForegroundColor Yellow
    $continue = Read-Host "Continue with setup? (y/n)"
    if ($continue -ne "y") {
        exit 0
    }
} else {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
    git branch -M main
}

# Get GitHub username
Write-Host ""
$githubUsername = Read-Host "Enter your GitHub username"
$repoName = Read-Host "Enter repository name (default: opencrol-integration)"
if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "opencrol-integration"
}

# Add all files
Write-Host ""
Write-Host "Adding files to git..." -ForegroundColor Yellow
git add .

# Create initial commit
Write-Host "Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit - OpenCtrol Home Assistant Integration v2.0.0"

# Add remote
$remoteUrl = "https://github.com/$githubUsername/$repoName.git"
Write-Host ""
Write-Host "Adding remote: $remoteUrl" -ForegroundColor Yellow

# Check if remote already exists
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    Write-Host "Remote 'origin' already exists: $existingRemote" -ForegroundColor Yellow
    $update = Read-Host "Update to $remoteUrl? (y/n)"
    if ($update -eq "y") {
        git remote set-url origin $remoteUrl
    }
} else {
    git remote add origin $remoteUrl
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create repository on GitHub:" -ForegroundColor White
Write-Host "   - Go to https://github.com/new" -ForegroundColor Gray
Write-Host "   - Name: $repoName" -ForegroundColor Gray
Write-Host "   - Visibility: Public" -ForegroundColor Gray
Write-Host "   - DO NOT initialize with README" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Push to GitHub:" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Create first release:" -ForegroundColor White
Write-Host "   - Go to repository → Releases → Create new release" -ForegroundColor Gray
Write-Host "   - Tag: v2.0.0" -ForegroundColor Gray
Write-Host "   - Title: v2.0.0 - Initial Release" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Install via HACS:" -ForegroundColor White
Write-Host "   - HACS → Integrations → + → Custom Repository" -ForegroundColor Gray
Write-Host "   - Repository: https://github.com/$githubUsername/$repoName" -ForegroundColor Gray
Write-Host "   - Category: Integration" -ForegroundColor Gray
Write-Host ""

