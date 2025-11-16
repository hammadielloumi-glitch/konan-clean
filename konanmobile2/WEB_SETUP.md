# Web Development Setup

This project has **two separate web setups**:

## 1. Vite Web App (Recommended for Web Development)
- **Entry Point**: `src/App.jsx` (React web app)
- **Command**: `npm run dev`
- **Port**: http://localhost:5173
- **Status**: ✅ Working
- **Use Case**: Web-only development with Tailwind CSS

## 2. Expo Web (For React Native Web)
- **Entry Point**: `App.js` (React Native app)
- **Command**: `expo start --web` or `npm run web`
- **Status**: ⚠️ May have issues with module resolution
- **Use Case**: Running React Native app on web using react-native-web

## Current Issue

When running `expo start --web`, you may see errors like:
```
Unable to resolve "react-native-web/dist/exports/TouchableOpacity" from "App.js"
```

## Solutions

### Option 1: Use Vite for Web (Recommended)
```bash
npm run dev
```
This runs the separate web app at `src/App.jsx` which is designed for web.

### Option 2: Fix Expo Web
1. Clear the cache:
   ```bash
   npx expo start --clear --web
   ```

2. If that doesn't work, delete cache directories:
   ```bash
   # Delete .expo and node_modules/.cache
   rm -rf .expo node_modules/.cache
   # Then restart
   npx expo start --clear --web
   ```

3. Verify react-native-web is installed:
   ```bash
   npm list react-native-web
   ```

## Version Compatibility

- React: 19.1.0
- React DOM: 19.1.0 (matched)
- React Native: 0.81.5
- React Native Web: 0.21.2
- Expo SDK: 54.0.22

## Development Workflow

- **Mobile Development**: Use `npm start` or `expo start` (Android/iOS)
- **Web Development**: Use `npm run dev` (Vite)
- **Expo Web**: Use `npm run web` (if needed for React Native Web)

## Notes

- The Vite setup (`src/App.jsx`) is a separate web-only application
- The Expo setup (`App.js`) is for React Native (mobile + web via react-native-web)
- For best results, use Vite for web development and Expo for mobile development

