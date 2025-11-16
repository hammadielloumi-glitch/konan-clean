import React, { useState } from "react";
import { View, TextInput, Button, Text, StyleSheet } from "react-native";
import axios from "axios";
// FI9_NAYEK v12.1 : Unification API_BASE_URL
import { API_BASE_URL } from "../config/api";

export default function AuthTest() {
  const [email, setEmail] = useState("admin@konan.tn");
  const [password, setPassword] = useState("admin123");
  const [token, setToken] = useState("");
  const [userInfo, setUserInfo] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async () => {
    setError("");
    try {
      const res = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        email,
        password,
      });
      setToken(res.data.access_token);
      alert("✅ Login OK — token reçu");
    } catch (err) {
      console.log(err.response?.data);
      setError("❌ Login échoué : " + (err.response?.data?.detail || err.message));
    }
  };

  const handleMe = async () => {
    if (!token) {
      setError("Token manquant. Fais un login d'abord.");
      return;
    }
    try {
      const res = await axios.get(`${API_BASE_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUserInfo(JSON.stringify(res.data, null, 2));
    } catch (err) {
      console.log(err.response?.data);
      setError("❌ /me échoué : " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🔐 Test Auth KONAN</Text>
      <TextInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        style={styles.input}
        autoCapitalize="none"
      />
      <TextInput
        placeholder="Mot de passe"
        value={password}
        onChangeText={setPassword}
        style={styles.input}
        secureTextEntry
      />
      <Button title="Se connecter" onPress={handleLogin} />
      <Button title="Tester /me" onPress={handleMe} color="#00A67E" />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      {userInfo ? <Text style={styles.success}>{userInfo}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#000", justifyContent: "center" },
  title: { color: "#00A67E", fontSize: 18, textAlign: "center", marginBottom: 20 },
  input: {
    backgroundColor: "#111",
    color: "#fff",
    padding: 10,
    marginBottom: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#222",
  },
  error: { color: "#FF5555", marginTop: 20 },
  success: { color: "#00A67E", marginTop: 20 },
});
