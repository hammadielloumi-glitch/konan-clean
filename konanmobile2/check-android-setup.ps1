# Android Setup Checker and Emulator Starter
# This script helps diagnose and fix Android development setup issues

Write-Host "=== Android Development Setup Check ===" -ForegroundColor Cyan
Write-Host ""

# Initialize variables
$deviceCount = 0
$avds = $null

# Check if Android SDK is installed
$androidSdk = $env:ANDROID_HOME
if (-not $androidSdk) {
    $androidSdk = "$env:LOCALAPPDATA\Android\Sdk"
}

if (Test-Path $androidSdk) {
    Write-Host "Android SDK found at: $androidSdk" -ForegroundColor Green
} else {
    Write-Host "Android SDK not found" -ForegroundColor Red
    Write-Host "  Please install Android Studio from https://developer.android.com/studio" -ForegroundColor Yellow
    exit 1
}

# Check for ADB
$adbPath = "$androidSdk\platform-tools\adb.exe"
if (Test-Path $adbPath) {
    Write-Host "ADB found" -ForegroundColor Green
    
    # Check for connected devices
    Write-Host ""
    Write-Host "Checking for connected devices..." -ForegroundColor Cyan
    $devices = & $adbPath devices
    $deviceCount = ($devices | Select-String -Pattern "device$" | Measure-Object).Count
    
    if ($deviceCount -gt 0) {
        Write-Host "Found $deviceCount connected device(s)" -ForegroundColor Green
        $devices | ForEach-Object { Write-Host "  $_" }
    } else {
        Write-Host "No devices connected" -ForegroundColor Yellow
    }
} else {
    Write-Host "ADB not found at: $adbPath" -ForegroundColor Red
}

# Check for emulator
$emulatorPath = "$androidSdk\emulator\emulator.exe"
if (Test-Path $emulatorPath) {
    Write-Host ""
    Write-Host "Emulator found" -ForegroundColor Green
    
    # List available AVDs
    Write-Host ""
    Write-Host "Checking for available emulators..." -ForegroundColor Cyan
    try {
        $avds = & $emulatorPath -list-avds
        if ($avds -and $avds.Count -gt 0) {
            Write-Host "Found the following emulators:" -ForegroundColor Green
            $avds | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }
            
            # Ask if user wants to start an emulator
            Write-Host ""
            Write-Host "Would you like to start an emulator? (y/n)" -ForegroundColor Yellow
            $response = Read-Host
            if ($response -eq 'y' -or $response -eq 'Y') {
                if ($avds.Count -eq 1) {
                    $avdName = $avds[0]
                    Write-Host "Starting emulator: $avdName" -ForegroundColor Green
                    Start-Process -FilePath $emulatorPath -ArgumentList "-avd", $avdName
                    Write-Host "Emulator is starting... Please wait for it to boot, then run: npx expo run:android" -ForegroundColor Yellow
                } else {
                    Write-Host "Multiple emulators found. Please select one:" -ForegroundColor Yellow
                    for ($i = 0; $i -lt $avds.Count; $i++) {
                        Write-Host "  [$i] $($avds[$i])" -ForegroundColor White
                    }
                    $selection = Read-Host "Enter number"
                    if ($selection -ge 0 -and $selection -lt $avds.Count) {
                        $avdName = $avds[$selection]
                        Write-Host "Starting emulator: $avdName" -ForegroundColor Green
                        Start-Process -FilePath $emulatorPath -ArgumentList "-avd", $avdName
                        Write-Host "Emulator is starting... Please wait for it to boot, then run: npx expo run:android" -ForegroundColor Yellow
                    }
                }
            }
        } else {
            Write-Host "No emulators (AVDs) found" -ForegroundColor Yellow
            Write-Host "  Please create an emulator in Android Studio:" -ForegroundColor Yellow
            Write-Host "  1. Open Android Studio" -ForegroundColor White
            Write-Host "  2. Go to Tools -> Device Manager" -ForegroundColor White
            Write-Host "  3. Click 'Create Device'" -ForegroundColor White
        }
    } catch {
        Write-Host "Could not list emulators: $_" -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "Emulator not found at: $emulatorPath" -ForegroundColor Yellow
    Write-Host "  You may need to install Android Emulator through Android Studio SDK Manager" -ForegroundColor Yellow
}

# Summary and recommendations
Write-Host ""
Write-Host "=== Recommendations ===" -ForegroundColor Cyan
if ($deviceCount -eq 0 -and (-not $avds -or $avds.Count -eq 0)) {
    Write-Host "1. Install Android Studio and create an emulator, OR" -ForegroundColor White
    Write-Host "2. Connect a physical Android device with USB debugging enabled, OR" -ForegroundColor White
    Write-Host "3. Use Expo Go: Install Expo Go app on your phone and run 'npx expo start'" -ForegroundColor White
} elseif ($deviceCount -eq 0) {
    Write-Host "Start an emulator or connect a physical device, then run:" -ForegroundColor White
    Write-Host "  npx expo run:android" -ForegroundColor Green
} else {
    Write-Host "You're ready! Run:" -ForegroundColor White
    Write-Host "  npx expo run:android" -ForegroundColor Green
}

Write-Host ""
Write-Host "For more details, see: ANDROID_SETUP.md" -ForegroundColor Cyan

