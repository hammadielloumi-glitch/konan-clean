Write-Host ""
Write-Host "=== FI9 SAFE PUSH v13 ===" -ForegroundColor Cyan

# 1) Branche courante
$branch = git branch --show-current
if ([string]::IsNullOrWhiteSpace($branch)) {
    Write-Host "[ERREUR] Impossible de detecter la branche courante" -ForegroundColor Red
    exit 1
}
Write-Host ("[INFO] Branche courante : {0}" -f $branch)

# 2) Scan fichiers > 100MB
Write-Host "[CHECK] Scan fichiers > 100MB avant push..."
$largeFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -gt 100MB }

if ($largeFiles.Count -gt 0) {
    Write-Host "[ERREUR] Fichiers volumineux detectes, push bloque :" -ForegroundColor Red
    foreach ($f in $largeFiles) {
        $sizeMb = [math]::Round($f.Length / 1MB, 2)
        Write-Host (" - {0} [{1} MB]" -f $f.FullName, $sizeMb)
    }
    exit 1
}

Write-Host "[OK] Aucun fichier > 100MB dans le repo" -ForegroundColor Green

# 3) Push
Write-Host ("[PUSH] git push origin {0} --force-with-lease" -f $branch) -ForegroundColor Yellow
git push origin $branch --force-with-lease

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERREUR] git push a echoue" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "=== FI9 SAFE PUSH v13 OK ===" -ForegroundColor Green
