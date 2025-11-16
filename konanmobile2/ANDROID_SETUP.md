# Android Development Setup Guide

## Problem
You're getting: `CommandError: No Android connected device found, and no emulators could be started automatically.`

## Solutions

### Option 1: Use Expo Go (Easiest for Development)

1. Install **Expo Go** app on your Android device from Google Play Store
2. Connect your device via USB and enable USB debugging
3. Run: `npx expo start`
4. Press `a` to open on Android
5. Scan the QR code with Expo Go app

**OR** run: `.\start-dev.ps1`

---

### Option 2: Set Up Android Emulator (For Native Builds)

#### Step 1: Install Android Studio
1. Download and install [Android Studio](https://developer.android.com/studio)
2. During installation, make sure to install:
   - Android SDK
   - Android SDK Platform
   - Android Virtual Device (AVD)

#### Step 2: Create an Android Virtual Device (AVD)
1. Open Android Studio
2. Go to **Tools** → **Device Manager** (or **AVD Manager**)
3. Click **Create Device**
4. Select a device (e.g., Pixel 5)
5. Select a system image (e.g., API 33 or API 34)
6. Click **Finish**

#### Step 3: Set Environment Variables
Add to your system environment variables:
- `ANDROID_HOME`: `C:\Users\Queen Bee\AppData\Local\Android\Sdk`
- Add to PATH: `%ANDROID_HOME%\platform-tools` and `%ANDROID_HOME%\emulator`

#### Step 4: Start the Emulator
1. Start the emulator from Android Studio's Device Manager, OR
2. Run: `emulator -avd <AVD_NAME>`
3. Wait for the emulator to fully boot

#### Step 5: Run Your App
```powershell
npx expo run:android
```

---

### Option 3: Use Physical Android Device

#### Step 1: Enable Developer Options
1. Go to **Settings** → **About phone**
2. Tap **Build number** 7 times
3. Go back to **Settings** → **Developer options**
4. Enable **USB debugging**

#### Step 2: Connect Device
1. Connect your device via USB
2. On your phone, allow USB debugging when prompted
3. Verify connection: `adb devices`
4. Your device should appear in the list

#### Step 3: Run Your App
```powershell
npx expo run:android
```

---

### Quick Check Commands

```powershell
# Check if devices are connected
adb devices

# List available emulators (if Android Studio is installed)
$env:LOCALAPPDATA\Android\Sdk\emulator\emulator.exe -list-avds

# Check if Android SDK is set up
echo $env:ANDROID_HOME
```

---

### Troubleshooting

**If emulator won't start:**
- Make sure virtualization is enabled in BIOS
- Check if Hyper-V is enabled (Windows)
- Try creating a new AVD with different settings

**If device not detected:**
- Install USB drivers for your device
- Try different USB cable/port
- Restart ADB: `adb kill-server && adb start-server`

**If build fails:**
- Make sure you've run `npx expo prebuild` (you already did this)
- Clean build: `cd android && .\gradlew clean && cd ..`

