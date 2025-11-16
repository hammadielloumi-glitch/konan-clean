// FI9_NAYEK v12.1 : Unification API_BASE_URL
import React, { createContext, useContext, useEffect, useState } from 'react';
import * as SecureStore from 'expo-secure-store';
import { API_BASE_URL } from '../config/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    SecureStore.getItemAsync('konan_token').then((v) => {
      if (v) setToken(v);
      setLoading(false);
    });
  }, []);

  const login = async (email, password) => {
    const r = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || 'Erreur de connexion');
    await SecureStore.setItemAsync('konan_token', data.access_token);
    setToken(data.access_token);
  };

  const register = async (email, password) => {
    const r = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!r.ok) throw new Error((await r.json()).detail || 'Erreur');
    await login(email, password);
  };

  const logout = async () => {
    await SecureStore.deleteItemAsync('konan_token');
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
