// src/api/http.js
// FI9_NAYEK v12.1 : Unification API_BASE_URL
import axios from "axios";
import * as SecureStore from "expo-secure-store";
import { API_BASE_URL } from "../config/api";

// Création du client HTTP principal
const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: { "Content-Type": "application/json" },
});

// Intercepteur : ajoute automatiquement le token au header
http.interceptors.request.use(
  async (config) => {
    try {
      const token = await SecureStore.getItemAsync("konan_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (err) {
      console.warn("Erreur lecture SecureStore:", err);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur : gère les réponses et erreurs globales
http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error?.response?.status;
    if (status === 401 || status === 403) {
      try {
        await SecureStore.deleteItemAsync("konan_token");
        console.warn("Token supprimé après erreur d’autorisation");
      } catch (err) {
        console.warn("Erreur suppression token:", err);
      }
    }
    return Promise.reject(error);
  }
);

export default http;
