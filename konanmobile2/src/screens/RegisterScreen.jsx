import React, { useEffect, useState } from "react";
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { useAuth } from "../hooks/useAuth";

export default function RegisterScreen({ navigation }) {
  const { register, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isAuthenticated) {
      navigation.replace("Chat");
    }
  }, [isAuthenticated, navigation]);

  const handleSubmit = async () => {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      await register(email, password);
      navigation.replace("Login");
    } catch (err) {
      const message = err?.message || "Création impossible";
      setError(message);
      Alert.alert("Inscription", message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={styles.safe}
      >
        <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
          <View style={styles.card}>
            <Text style={styles.title}>Créer un compte</Text>
            <TextInput
              style={styles.input}
              placeholder="Email"
              placeholderTextColor="rgba(255,255,255,0.35)"
              autoCapitalize="none"
              keyboardType="email-address"
              value={email}
              onChangeText={setEmail}
            />
            <TextInput
              style={styles.input}
              placeholder="Mot de passe"
              placeholderTextColor="rgba(255,255,255,0.35)"
              secureTextEntry
              value={password}
              onChangeText={setPassword}
            />
            {error && <Text style={styles.error}>{error}</Text>}
            <TouchableOpacity
              style={[styles.button, busy && styles.buttonDisabled]}
              onPress={handleSubmit}
              disabled={busy}
              activeOpacity={0.85}
            >
              <Text style={styles.buttonText}>{busy ? "Création…" : "Créer"}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => navigation.navigate("Login")}>
              <Text style={styles.link}>Déjà inscrit ? Se connecter</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: "#0B0B0B",
  },
  container: {
    flexGrow: 1,
    justifyContent: "center",
    padding: 24,
  },
  card: {
    backgroundColor: "rgba(17,17,17,0.96)",
    padding: 24,
    borderRadius: 28,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.05)",
    shadowColor: "#000",
    shadowOpacity: 0.2,
    shadowRadius: 18,
    shadowOffset: { width: 0, height: 12 },
    elevation: 8,
  },
  title: {
    color: "#F5F5F5",
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 18,
    letterSpacing: 0.6,
  },
  input: {
    backgroundColor: "rgba(255,255,255,0.06)",
    borderColor: "rgba(255,255,255,0.05)",
    borderWidth: 1,
    borderRadius: 18,
    paddingHorizontal: 16,
    paddingVertical: 12,
    color: "#F0F0F0",
    marginBottom: 14,
    fontSize: 15,
  },
  error: {
    color: "#F87171",
    marginBottom: 12,
  },
  button: {
    backgroundColor: "rgba(255,255,255,0.12)",
    borderRadius: 18,
    paddingVertical: 14,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: "#FFFFFF",
    fontWeight: "600",
    fontSize: 16,
    letterSpacing: 0.4,
  },
  link: {
    color: "rgba(255,255,255,0.65)",
    textAlign: "center",
    marginTop: 16,
  },
});
