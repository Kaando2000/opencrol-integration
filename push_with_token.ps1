# Push to GitHub using Personal Access Token
# This script helps you push without interactive prompts

param(
    [Parameter(Mandatory=$true)]
    [string]$Token
)

$ErrorActionPreference = "Stop"

Write-Host "Pushing to GitHub..." -ForegroundColor Cyan

# Update remote URL to include token
$remoteUrl = "https://$Token@github.com/Kaando2000/opencrol-integration.git"
git remote set-url origin $remoteUrl

# Push
Write-Host "Pushing code..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository: https://github.com/Kaando2000/opencrol-integration" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next: Create release on GitHub" -ForegroundColor Yellow
} else {
    Write-Host "Push failed. Check your token and try again." -ForegroundColor Red
}

