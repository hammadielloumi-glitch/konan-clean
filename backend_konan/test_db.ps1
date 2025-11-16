# ============================================================
# KONAN TEST_DB.PS1 - Vérification et Lancement Backend (UTF-8)
# Version ASCII compatible PowerShell 5/7
# ============================================================

Write-Host "`n=== KONAN BACKEND CHECK ===" -ForegroundColor Cyan

# --- Chargement du fichier .env ---
$envPath = ".env"
if (Test-Path $envPath) {
    Write-Host "Lecture du fichier .env..." -ForegroundColor Yellow
    Get-Content $envPath | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.+)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($name, $value)
        }
    }
    Write-Host "Variables d'environnement .env chargees." -ForegroundColor Green
} else {
    Write-Host "Fichier .env introuvable." -ForegroundColor Red
    exit 1
}

# --- Vérification de cohérence du .env ---
$errors = @()
if (-not $env:DATABASE_URL) { $errors += "DATABASE_URL manquant" }
elseif ($env:DATABASE_URL -notmatch "postgresql\+psycopg2://") { $errors += "DATABASE_URL mal formate" }

if (-not $env:POSTGRES_HOST) { $errors += "POSTGRES_HOST manquant" }
if (-not $env:POSTGRES_PORT) { $errors += "POSTGRES_PORT manquant" }
if (-not $env:POSTGRES_DB) { $errors += "POSTGRES_DB manquant" }
if (-not $env:POSTGRES_USER) { $errors += "POSTGRES_USER manquant" }
if (-not $env:POSTGRES_PASSWORD) { $errors += "POSTGRES_PASSWORD manquant" }

if (-not $env:OPENAI_API_KEY -or $env:OPENAI_API_KEY -match "sk-fake|sk-test|xxxxx") {
    $errors += "Clé OpenAI invalide ou manquante"
}

if ($errors.Count -gt 0) {
    Write-Host "`nErreurs detectees dans le fichier .env :" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
    Write-Host "Corrige le fichier .env avant de relancer." -ForegroundColor Yellow
    exit 1
}
Write-Host ".env verifie - toutes les variables critiques sont presentes." -ForegroundColor Green

# --- Test de la connexion PostgreSQL ---
Write-Host "`nTest de connexion PostgreSQL..." -ForegroundColor Yellow
try {
    docker exec konan_db psql -U postgres -d konan_db -c "SELECT NOW();" | Out-Null
    Write-Host "Database reachable on $($env:POSTGRES_HOST):$($env:POSTGRES_PORT)" -ForegroundColor Green
} catch {
    Write-Host "Impossible de se connecter a PostgreSQL." -ForegroundColor Red
    exit 1
}

# --- Vérification du port 8000 ---
$portInUse = (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue)
if ($portInUse) {
    Write-Host "Port 8000 deja utilise. Arret des anciens processus Python..." -ForegroundColor Yellow
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# --- Vérifie Python ---
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python non detecte dans le PATH." -ForegroundColor Red
    exit 1
}

# --- Lancement du backend FastAPI ---
Write-Host "`nDemarrage du backend Konan sur http://127.0.0.1:8000 ..." -ForegroundColor Cyan
$env:PYTHONIOENCODING = "utf-8"
Start-Process -NoNewWindow python -ArgumentList "-m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
Start-Sleep -Seconds 4

# --- Test /health ---
Write-Host "`nTest du point /health..."
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 6
    Write-Host "Backend Konan operationnel : $($health.message)" -ForegroundColor Green
} catch {
    Write-Host "Le backend ne repond pas encore. Verifie les logs." -ForegroundColor Yellow
}

# --- Test /api/chat ---
Write-Host "`nTest du point /api/chat..."
try {
    $body = @{ message = "Bonjour"; session_id = "konan-session" } | ConvertTo-Json -Depth 3
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/chat" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
    Write-Host "Reponse IA recue :" -ForegroundColor Green
    Write-Host "------------------------"
    Write-Host $response.reply
    Write-Host "------------------------"
} catch {
    Write-Host "Echec du test /api/chat : $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Verifie la connexion Internet et ta cle OpenAI." -ForegroundColor Yellow
}

Write-Host "`n=== Test complet termine ===`n" -ForegroundColor Cyan
