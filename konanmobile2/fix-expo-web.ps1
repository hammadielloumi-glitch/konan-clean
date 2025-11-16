# Fix Expo Web Setup
Write-Host "Clearing Expo cache..." -ForegroundColor Yellow
npx expo start --clear

Write-Host "`nIf the issue persists, try:" -ForegroundColor Cyan
Write-Host "1. Stop the Expo server (Ctrl+C)" -ForegroundColor White
Write-Host "2. Delete .expo and node_modules/.cache directories" -ForegroundColor White
Write-Host "3. Run: npx expo start --clear --web" -ForegroundColor White
Write-Host "`nAlternatively, use Vite for web development:" -ForegroundColor Cyan
Write-Host "npm run dev" -ForegroundColor Green

