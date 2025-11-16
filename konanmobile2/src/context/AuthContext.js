import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { login as loginRequest, register as registerRequest } from "../services/AuthService";

const TOKEN_KEY = "konan.jwt";
const TEST_EMAIL = "test@konan.ai";
const TEST_PASSWORD = "Test123!";
const IS_DEV = process.env.NODE_ENV === "development";

if (typeof globalThis.Buffer === "undefined") {
  globalThis.Buffer = require("buffer").Buffer;
}

function decodeJwt(token) {
  if (!token) return null;
  try {
    const payload = token.split(".")[1] || "";
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded =
      normalized.length % 4 === 0
        ? normalized
        : normalized.padEnd(normalized.length + (4 - (normalized.length % 4)), "=");
    const decoded =
      typeof globalThis.atob === "function"
        ? globalThis.atob(padded)
        : Buffer.from(padded, "base64").toString("utf8");
    return JSON.parse(decoded);
  } catch (error) {
    console.warn("Impossible de décoder le token JWT", error);
    return null;
  }
}

async function applyToken(accessToken, setters) {
  const { setToken, setUser, setStatus } = setters;
  await AsyncStorage.setItem(TOKEN_KEY, accessToken);
  setToken(accessToken);
  setUser(decodeJwt(accessToken));
  setStatus("authenticated");
}

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState("loading");
  const subscription = "free";

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const stored = await AsyncStorage.getItem(TOKEN_KEY);
        if (mounted && stored) {
          await applyToken(stored, { setToken, setUser, setStatus });
          return;
        }

        if (!mounted) return;

        if (IS_DEV) {
          try {
            const response = await loginRequest(TEST_EMAIL, TEST_PASSWORD);
            if (response?.access_token) {
              await applyToken(response.access_token, { setToken, setUser, setStatus });
              return;
            }
          } catch (error) {
            console.warn("Auto-login de développement impossible", error?.message || error);
          }
        }

        setStatus("unauthenticated");
      } catch (error) {
        console.warn("Erreur chargement session", error);
        if (mounted) setStatus("unauthenticated");
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const performLogin = async (email, password) => {
    const trimmedEmail = email?.trim();
    const trimmedPassword = password?.trim();
    if (!trimmedEmail || !trimmedPassword) {
      throw new Error("Identifiants requis");
    }
    try {
      const response = await loginRequest(trimmedEmail, trimmedPassword);
      if (!response?.access_token) {
        throw new Error("Token manquant dans la réponse de l'API");
      }
      await applyToken(response.access_token, { setToken, setUser, setStatus });
      return response.access_token;
    } catch (error) {
      setStatus("unauthenticated");
      throw error;
    }
  };

  const performRegister = async (email, password) => {
    const trimmedEmail = email?.trim();
    const trimmedPassword = password?.trim();
    if (!trimmedEmail || !trimmedPassword) {
      throw new Error("Email et mot de passe requis");
    }
    return registerRequest(trimmedEmail, trimmedPassword);
  };

  const performLogout = async () => {
    await AsyncStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    setStatus("unauthenticated");
  };

  const value = useMemo(
    () => ({
      token,
      user,
      status,
      subscription,
      isAuthenticated: status === "authenticated",
      login: performLogin,
      register: performRegister,
      logout: performLogout,
      signIn: ({ email, password }) => performLogin(email, password),
      signUp: ({ email, password }) => performRegister(email, password),
      signOut: performLogout,
    }),
    [token, user, status]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
