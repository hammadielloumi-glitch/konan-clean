import 'dotenv/config';
import type { ExpoConfig } from 'expo/config';

const API_BASE_URL = process.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

const config: ExpoConfig = {
  name: 'Konanmobile2',
  slug: 'konanmobile2',
  version: '1.0.0',
  sdkVersion: '54.0.0',
  extra: {
    API_BASE_URL,
  },
  experiments: {
    tsconfigPaths: true,
  },
};

export default config;
