// src/utils/env.js
// FI9_NAYEK v12.1 : Unification API_BASE_URL
// Délègue la résolution à config.ts pour éviter le hard-coding
export { API_BASE_URL } from '../config/config';

export const STRIPE_PUBLISHABLE_KEY = "pk_test_FAKE_FOR_SIM";

export const APP_CONFIG = {
  freeChatQuota: 20, // nombre de messages gratuits avant blocage
};
