# ==============================================
# test_phase3.ps1 — Phase 3 complète Konan API
# ==============================================

$baseUrl = "http://127.0.0.1:8000"
$results = New-Object System.Collections.ArrayList

function Test-Endpoint($name, $method, $url, $body=$null) {
    Write-Host "→ Test $name ($method $url)" -ForegroundColor Cyan
    try {
        if ($method -eq "GET") {
            $response = Invoke-RestMethod -Uri $url -Method GET -TimeoutSec 10
        } else {
            $response = Invoke-RestMethod -Uri $url -Method POST -Body $body -ContentType "application/json" -TimeoutSec 15
        }
        $status = "✅ OK"
        $detail = ($response | ConvertTo-Json -Depth 5)
        Write-Host "   $status" -ForegroundColor Green
    }
    catch {
        $status = "❌ FAIL"
        $detail = $_.Exception.Message
        Write-Host "   $status : $detail" -ForegroundColor Red
    }
    $null = $results.Add([pscustomobject]@{
        Endpoint = $name
        Status   = $status
        Detail   = $detail
    })
}

Write-Host "`n=== TESTS KONAN API ===`n" -ForegroundColor Yellow

# 1️⃣ Health
Test-Endpoint "Health" "GET" "$baseUrl/health"

# 2️⃣ Test DB
Test-Endpoint "Test_DB" "GET" "$baseUrl/test_db"

# 3️⃣ Memory
Test-Endpoint "Memory_Test" "GET" "$baseUrl/api/memory/test"

# 4️⃣ Chat
$body = '{"message":"Bonjour Konan"}'
Test-Endpoint "Chat" "POST" "$baseUrl/api/chat" $body

# 5️⃣ Laws
Test-Endpoint "Laws_Search" "GET" "$baseUrl/api/laws/search?query=divorce"

Write-Host "`n=== RÉSUMÉ ===" -ForegroundColor Yellow
$results | Format-Table -AutoSize

# Sauvegarde rapport JSON
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$reportName = "report_phase3_$timestamp.json"
$results | ConvertTo-Json -Depth 5 | Out-File -Encoding UTF8 $reportName

Write-Host "`nRapport sauvegardé : $reportName" -ForegroundColor Green
