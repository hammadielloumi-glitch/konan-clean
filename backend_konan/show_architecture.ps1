<#
.SYNOPSIS
  Script FI9_NAYEK — Affiche uniquement backend, app, scripts et alembic.
#>

param([string]$Path = ".", [string]$Export = "")

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host ""
Write-Host "=== Analyse sélective KONAN (Protocole FI9_NAYEK) ===" -ForegroundColor Cyan

$Path = (Resolve-Path $Path).Path
Write-Host ("Racine analysée : " + $Path + "`n") -ForegroundColor Yellow

# ---------------------------------------------------------
# Fonction d’affichage récursive avec indentation
# ---------------------------------------------------------
function Show-Tree {
    param([string]$root, [int]$level = 0)
    Get-ChildItem -Path $root -Force | Sort-Object PSIsContainer, Name | ForEach-Object {
        $indent = " " * ($level * 3)
        if ($_.PSIsContainer) {
            Write-Host ("$indent[DIR] " + $_.Name) -ForegroundColor Cyan
            Show-Tree $_.FullName ($level + 1)
        } else {
            Write-Host ("$indent[file] " + $_.Name) -ForegroundColor Gray
        }
    }
}

# ---------------------------------------------------------
# Corps principal : affichage sélectif
# ---------------------------------------------------------
$exportBuffer = @()

function Capture-Tree($root, $level = 0) {
    Get-ChildItem -Path $root -Force | Sort-Object PSIsContainer, Name | ForEach-Object {
        $indent = " " * ($level * 3)
        if ($_.PSIsContainer) {
            $line = "$indent[DIR] $($_.Name)"
            Write-Host $line -ForegroundColor Cyan
            $exportBuffer += $line
            Capture-Tree $_.FullName ($level + 1)
        } else {
            $line = "$indent[file] $($_.Name)"
            Write-Host $line -ForegroundColor Gray
            $exportBuffer += $line
        }
    }
}

# === 1️⃣ Fichiers à la racine du backend ===
Write-Host "`n[SECTION] backend_konan (fichiers seuls)" -ForegroundColor Green
Get-ChildItem -Path $Path -File | ForEach-Object {
    $line = "[file] $($_.Name)"
    Write-Host $line -ForegroundColor Gray
    $exportBuffer += $line
}

# === 2️⃣ Dossier app ===
if (Test-Path "$Path\app") {
    Write-Host "`n[SECTION] app" -ForegroundColor Green
    $exportBuffer += "`n[SECTION] app"
    Capture-Tree "$Path\app"
}

# === 3️⃣ Dossier scripts ===
if (Test-Path "$Path\scripts") {
    Write-Host "`n[SECTION] scripts" -ForegroundColor Green
    $exportBuffer += "`n[SECTION] scripts"
    Capture-Tree "$Path\scripts"
}

# === 4️⃣ Dossier alembic ===
if (Test-Path "$Path\alembic") {
    Write-Host "`n[SECTION] alembic" -ForegroundColor Green
    $exportBuffer += "`n[SECTION] alembic"
    Capture-Tree "$Path\alembic"
}

# ---------------------------------------------------------
# Export facultatif
# ---------------------------------------------------------
if ($Export) {
    $exportBuffer | Out-File -Encoding UTF8 -FilePath $Export
    Write-Host "`n✅ Structure sauvegardée dans : $Export" -ForegroundColor Green
}

Write-Host "`n=== Fin de l’analyse FI9_NAYEK ===`n" -ForegroundColor Green
