# OpenCtrol Integration - Create Repository and Push Script
# This script helps create the GitHub repository and push the code

param(
    [string]$GitHubUsername = "kaando2000",
    [string]$RepoName = "opencrol-integration"
)

Write-Host "OpenCtrol Integration - GitHub Setup" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

$ErrorActionPreference = "Stop"

# Check if we're in the Integration directory
if (-not (Test-Path "custom_components\opencrol\manifest.json")) {
    Write-Host "ERROR: Please run this script from the Integration directory!" -ForegroundColor Red
    exit 1
}

# Check git status
Write-Host "Checking git status..." -ForegroundColor Cyan
$gitStatus = git status --porcelain 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Not a git repository!" -ForegroundColor Red
    exit 1
}

# Check if there are uncommitted changes
if ($gitStatus -match "^[^ ]") {
    Write-Host "WARNING: You have uncommitted changes!" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 0
    }
}

# Check if GitHub CLI is available
$useGhCli = $false
if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "GitHub CLI found!" -ForegroundColor Green
    $useGhCli = $true
    
    # Check if authenticated
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "GitHub CLI not authenticated. Please run:" -ForegroundColor Yellow
        Write-Host "  gh auth login" -ForegroundColor Cyan
        Write-Host ""
        $login = Read-Host "Do you want to login now? (y/n)"
        if ($login -eq "y") {
            gh auth login
        } else {
            $useGhCli = $false
        }
    }
}

# Create repository on GitHub
Write-Host ""
Write-Host "Creating repository on GitHub..." -ForegroundColor Cyan

if ($useGhCli) {
    # Use GitHub CLI
    Write-Host "Using GitHub CLI to create repository..." -ForegroundColor Green
    try {
        gh repo create $RepoName --public --source=. --remote=origin --push 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Repository created and pushed successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Repository URL: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Cyan
            exit 0
        }
    } catch {
        Write-Host "GitHub CLI failed, trying manual method..." -ForegroundColor Yellow
        $useGhCli = $false
    }
}

# Manual method - check if repository exists
Write-Host "Checking if repository exists on GitHub..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "https://api.github.com/repos/$GitHubUsername/$RepoName" -Method Get -ErrorAction Stop
    Write-Host "Repository already exists!" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "Repository does not exist. Please create it manually:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Go to: https://github.com/new" -ForegroundColor Cyan
        Write-Host "2. Repository name: $RepoName" -ForegroundColor White
        Write-Host "3. Visibility: Public" -ForegroundColor White
        Write-Host "4. DO NOT initialize with README" -ForegroundColor White
        Write-Host "5. Click 'Create repository'" -ForegroundColor White
        Write-Host ""
        $created = Read-Host "Have you created the repository? (y/n)"
        if ($created -ne "y") {
            Write-Host "Please create the repository first, then run this script again." -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "Error checking repository: $_" -ForegroundColor Red
        exit 1
    }
}

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan

# Check if remote exists
$remoteExists = git remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Adding remote..." -ForegroundColor Yellow
    git remote add origin "https://github.com/$GitHubUsername/$RepoName.git"
}

# Try to push
Write-Host "Attempting to push..." -ForegroundColor Yellow
git push -u origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository URL: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Create release: https://github.com/$GitHubUsername/$RepoName/releases/new" -ForegroundColor White
    Write-Host "2. Tag: v2.0.0" -ForegroundColor White
    Write-Host "3. Install via HACS using the repository URL" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "Push failed. You may need to authenticate." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "1. Use GitHub Desktop (easiest)" -ForegroundColor White
    Write-Host "2. Create Personal Access Token:" -ForegroundColor White
    Write-Host "   https://github.com/settings/tokens/new" -ForegroundColor Gray
    Write-Host "   Scope: repo" -ForegroundColor Gray
    Write-Host "   Then use token as password when pushing" -ForegroundColor Gray
    Write-Host "3. Install GitHub CLI: https://cli.github.com/" -ForegroundColor White
    Write-Host "   Then run: gh auth login" -ForegroundColor Gray
}

