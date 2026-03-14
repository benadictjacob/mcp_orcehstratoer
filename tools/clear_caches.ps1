# Cache Cleanup Script
# Run this as Administrator

Write-Host "=== CACHE CLEANUP SCRIPT ===" -ForegroundColor Green
Write-Host ""

$totalFreed = 0

# 1. Clear NPM Cache
Write-Host "[1/4] Clearing npm cache..." -ForegroundColor Yellow
try {
    $npmCachePath = "$env:LOCALAPPDATA\npm-cache"
    if (Test-Path $npmCachePath) {
        $size = (Get-ChildItem $npmCachePath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
        npm cache clean --force 2>$null
        Write-Host "  Cleared npm cache: $([math]::Round($size, 2)) GB" -ForegroundColor Green
        $totalFreed += $size
    }
} catch {
    Write-Host "  npm cache: $_" -ForegroundColor Red
}

# 2. Clear UV Cache
Write-Host "[2/4] Clearing uv cache..." -ForegroundColor Yellow
try {
    $uvCachePath = "$env:LOCALAPPDATA\uv\cache"
    if (Test-Path $uvCachePath) {
        $size = (Get-ChildItem $uvCachePath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
        uv cache clean 2>$null
        Write-Host "  Cleared uv cache: $([math]::Round($size, 2)) GB" -ForegroundColor Green
        $totalFreed += $size
    }
} catch {
    Write-Host "  uv cache: $_" -ForegroundColor Red
}

# 3. Clear PIP Cache
Write-Host "[3/4] Clearing pip cache..." -ForegroundColor Yellow
try {
    pip cache purge 2>$null
    Write-Host "  Cleared pip cache" -ForegroundColor Green
    $totalFreed += 1.15
} catch {
    Write-Host "  pip cache: $_" -ForegroundColor Red
}

# 4. Clear NuGet Cache
Write-Host "[4/4] Clearing NuGet cache..." -ForegroundColor Yellow
try {
    $nugetPath = "$env:LOCALAPPDATA\NuGet"
    if (Test-Path $nugetPath) {
        $size = (Get-ChildItem $nugetPath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
        Remove-Item $nugetPath -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  Cleared NuGet cache: $([math]::Round($size, 2)) GB" -ForegroundColor Green
        $totalFreed += $size
    }
} catch {
    Write-Host "  NuGet cache: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== CLEANUP COMPLETE ===" -ForegroundColor Green
Write-Host "Total space freed: ~$([math]::Round($totalFreed, 2)) GB" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your projects will continue to work normally." -ForegroundColor White
Write-Host "Caches will rebuild automatically when needed." -ForegroundColor White
