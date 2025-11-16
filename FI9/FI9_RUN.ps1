Write-Host ""
Write-Host "=== FI9_NAYEK v13 - RUN ENGINE ===" -ForegroundColor Cyan

# Paths
$versionFile = ".\FI9\FI9_VERSION.json"
$commitFile  = ".\FI9\FI9_SAFE_COMMIT.ps1"
$pushFile    = ".\FI9\FI9_SAFE_PUSH.ps1"

# Check version file
if (-not (Test-Path $versionFile)) {
    Write-Host "[ERREUR] FI9_VERSION.json introuvable" -ForegroundColor Red
    exit 1
}

# Load version file
try {
    $jsonText = Get-Content $versionFile -Raw
    $fi9 = $jsonText | ConvertFrom-Json
} catch {
    Write-Host "[ERREUR] Impossible de lire FI9_VERSION.json" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Version : $($fi9.version)"
Write-Host "[INFO] Mode    : $($fi9.mode)"

# Check commit module
if (-not (Test-Path $commitFile)) {
    Write-Host "[ERREUR] FI9_SAFE_COMMIT.ps1 manquant" -ForegroundColor Red
    exit 1
}

# Check push module
if (-not (Test-Path $pushFile)) {
    Write-Host "[ERREUR] FI9_SAFE_PUSH.ps1 manquant" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Modules FI9 v13 charges" -ForegroundColor Green

# Execute commit script
Write-Host ""
Write-Host "[1] Execution FI9_SAFE_COMMIT..." -ForegroundColor Yellow
& $commitFile

# Execute push script
Write-Host ""
Write-Host "[2] Execution FI9_SAFE_PUSH..." -ForegroundColor Yellow
& $pushFile

Write-Host ""
Write-Host "=== FIN EXECUTION FI9 v13 ===" -ForegroundColor Green
