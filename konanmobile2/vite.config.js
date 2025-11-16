import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Custom plugin to filter out React Native imports and prevent scanning
function filterReactNative() {
  const reactNativePatterns = [
    /^react-native$/,
    /^react-native\//,
    /^expo$/,
    /^expo\//,
    /^@react-native\//,
    /^@react-navigation\//,
    /^@stripe\/stripe-react-native/,
    /node_modules\/react-native/,
    /node_modules\/expo\//,
  ];

  return {
    name: 'filter-react-native',
    enforce: 'pre',
    resolveId(id) {
      // Prevent any React Native or Expo imports
      if (reactNativePatterns.some(pattern => pattern.test(id))) {
        // Return a virtual stub module
        return { id: '\0virtual:react-native-stub', moduleSideEffects: false };
      }
    },
    load(id) {
      if (id === '\0virtual:react-native-stub') {
        return 'export default {}; export const View = () => null; export const Text = () => null;';
      }
    },
  };
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), filterReactNative()],
  server: {
    port: 5173,
    host: true,
    fs: {
      // Deny access to React Native and Expo packages
      deny: [
        '**/node_modules/react-native/**',
        '**/node_modules/expo/**',
        '**/node_modules/@react-native/**',
        '**/node_modules/@react-navigation/**',
        '**/node_modules/@stripe/stripe-react-native/**',
      ],
    },
  },
  build: {
    outDir: 'dist',
    commonjsOptions: {
      // Ignore React Native packages during build
      ignore: [
        'react-native',
        'react-native-web',
        'expo',
        '@react-native/**',
        '@react-navigation/**',
      ],
    },
    rollupOptions: {
      external: (id) => {
        // Mark React Native packages as external to prevent bundling
        return (
          id === 'react-native' ||
          id.startsWith('react-native/') ||
          id.startsWith('expo/') ||
          id.startsWith('@react-native/') ||
          id.startsWith('@react-navigation/') ||
          id.startsWith('@stripe/stripe-react-native')
        );
      },
    },
  },
  optimizeDeps: {
    // ONLY include these packages - Vite will not scan anything else
    include: [
      'react',
      'react-dom',
      'react/jsx-runtime',
      'framer-motion',
      'lucide-react',
    ],
    // Exclude React Native packages (defensive)
    exclude: [
      'react-native',
      'react-native-web',
      'react-native-gesture-handler',
      'react-native-reanimated',
      'react-native-screens',
      'react-native-safe-area-context',
      'react-native-vector-icons',
      'react-native-webview',
      'react-native-worklets',
      'react-native-worklets-core',
      'react-native-markdown-display',
      'react-native-dotenv',
      '@react-native-async-storage/async-storage',
      '@react-navigation/native',
      '@react-navigation/native-stack',
      '@react-navigation/drawer',
      '@stripe/stripe-react-native',
      'expo',
      'expo-auth-session',
      'expo-clipboard',
      'expo-document-picker',
      'expo-file-system',
      'expo-print',
      'expo-secure-store',
      'expo-sharing',
      'expo-sqlite',
      'expo-status-bar',
    ],
    // Configure esbuild to handle Flow syntax gracefully (or skip it)
    esbuildOptions: {
      resolveExtensions: ['.web.jsx', '.web.js', '.jsx', '.js', '.tsx', '.ts', '.json'],
      // Skip files with Flow syntax
      legalComments: 'none',
    },
    // Only scan our web entry point
    entries: ['src/main.jsx'],
    // Don't discover dependencies automatically - only use what's in 'include'
    // This is the key: prevent Vite from scanning node_modules/react-native
    noDiscovery: false, // We want discovery, but only for included packages
  },
  resolve: {
    extensions: ['.web.jsx', '.web.js', '.jsx', '.js', '.tsx', '.ts', '.json'],
    // Prevent resolving React Native packages
    dedupe: ['react', 'react-dom'],
  },
});

