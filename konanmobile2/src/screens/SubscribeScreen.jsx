// src/screens/SubscribeScreen.jsx
import React, { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, Alert } from "react-native";
import { STRIPE_PUBLISHABLE_KEY } from "../utils/env";
// ⚠️ Stripe désactivé temporairement pour test
// import { StripeProvider, useStripe } from "@stripe/stripe-react-native";
// import { createStripeCheckoutSession } from "../services/AuthService";

export default function SubscribeScreen() {
  const [busy, setBusy] = useState(false);

  async function onSubscribe() {
    setBusy(true);
    try {
      // Simulation de succès
      Alert.alert("Succès", "Abonnement activé (simulation).");
    } catch (e) {
      Alert.alert("Erreur", e?.message || "Échec du paiement (simulation).");
    } finally {
      setBusy(false);
    }
  }

  return (
    <View style={styles.wrap}>
      <Text style={styles.title}>Passez en Premium</Text>
      <Text style={styles.desc}>
        Accès illimité aux réponses et fonctionnalités avancées.
      </Text>
      <TouchableOpacity
        style={[styles.btn, busy && styles.btnDisabled]}
        disabled={busy}
        onPress={onSubscribe}
      >
        <Text style={styles.btnText}>
          {busy ? "Ouverture..." : "S’abonner"}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flex: 1,
    backgroundColor: "#0B0B0B",
    padding: 16,
    justifyContent: "center",
  },
  title: { color: "#FFFFFF", fontSize: 22, marginBottom: 8, fontWeight: "700" },
  desc: { color: "#CFCFCF", marginBottom: 20 },
  btn: {
    backgroundColor: "#10A37F",
    padding: 14,
    borderRadius: 10,
    alignItems: "center",
  },
  btnDisabled: { opacity: 0.7 },
  btnText: { color: "#FFFFFF", fontWeight: "600" },
});
