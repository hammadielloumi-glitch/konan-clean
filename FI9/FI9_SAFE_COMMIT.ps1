Write-Host ""
Write-Host "=== FI9 SAFE COMMIT v13 ===" -ForegroundColor Cyan

# 1) Scan fichiers > 100MB
Write-Host "[CHECK] Scan fichiers > 100MB..."
$largeFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -gt 100MB }

if ($largeFiles.Count -gt 0) {
    Write-Host "[ERREUR] Fichiers volumineux detectes, commit bloque :" -ForegroundColor Red
    foreach ($f in $largeFiles) {
        $sizeMb = [math]::Round($f.Length / 1MB, 2)
        Write-Host (" - {0} [{1} MB]" -f $f.FullName, $sizeMb)
    }
    exit 1
}

Write-Host "[OK] Aucun fichier > 100MB" -ForegroundColor Green

# 2) Etat Git
$status = git status --porcelain

if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "[INFO] Rien a committer (working tree clean)" -ForegroundColor Yellow
    exit 0
}

Write-Host "[INFO] Modifications detectees, ajout des chemins FI9..." -ForegroundColor Yellow

# 3) Ajout des zones principales (ajuste si besoin)
git add backend_konan
git add konanmobile2
git add FI9
git add .github 2>$null

# 4) Verifier le staging
$staged = git diff --cached --name-only

if ([string]::IsNullOrWhiteSpace($staged)) {
    Write-Host "[INFO] Aucun fichier en staging apres git add, commit annule." -ForegroundColor Yellow
    exit 0
}

Write-Host "[OK] Fichiers en staging :" -ForegroundColor Green
$staged | ForEach-Object { Write-Host (" - {0}" -f $_) }

# 5) Commit
$commitMessage = "FI9 v13: Commit automatique"
Write-Host ("[COMMIT] {0}" -f $commitMessage) -ForegroundColor Yellow
git commit -m "$commitMessage"

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERREUR] git commit a echoue" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "[OK] Commit FI9 cree avec succes" -ForegroundColor Green
