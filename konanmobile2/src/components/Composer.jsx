// src/components/Composer.jsx
import React, { useState } from "react";
import { View, TextInput, StyleSheet, TouchableOpacity, Text, Keyboard } from "react-native";

export default function Composer({ onSend, disabled }) {
  const [value, setValue] = useState("");

  const handleSend = () => {
    const text = value.trim();
    if (!text || disabled) {
      return;
    }
    setValue("");
    Keyboard.dismiss();
    onSend?.(text);
  };

  const canSend = value.trim().length > 0 && !disabled;

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Écrire un message…"
        placeholderTextColor="rgba(255,255,255,0.35)"
        value={value}
        onChangeText={setValue}
        multiline
        textAlignVertical="top"
      />
      <TouchableOpacity
        style={[styles.button, !canSend && styles.buttonDisabled]}
        onPress={handleSend}
        disabled={!canSend}
        activeOpacity={0.8}
      >
        <Text style={styles.buttonText}>Envoyer</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "flex-end",
    gap: 12,
    paddingHorizontal: 18,
    paddingVertical: 14,
    borderTopWidth: 1,
    borderTopColor: "rgba(255,255,255,0.05)",
    backgroundColor: "#0B0B0B",
  },
  input: {
    flex: 1,
    minHeight: 46,
    maxHeight: 140,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    color: "#F2F2F2",
    backgroundColor: "rgba(255,255,255,0.06)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.04)",
    fontSize: 15,
    lineHeight: 20,
  },
  button: {
    borderRadius: 18,
    paddingHorizontal: 18,
    paddingVertical: 12,
    backgroundColor: "rgba(255,255,255,0.12)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
  },
  buttonDisabled: {
    opacity: 0.4,
  },
  buttonText: {
    color: "#FFFFFF",
    fontWeight: "600",
    letterSpacing: 0.3,
  },
});
