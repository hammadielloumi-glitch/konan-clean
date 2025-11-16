// src/components/TypingIndicator.jsx
import React from "react";
import { View, Text, StyleSheet, ActivityIndicator } from "react-native";

export default function TypingIndicator({ visible }) {
  if (!visible) return null;
  return (
    <View style={styles.row}>
      <ActivityIndicator size="small" />
      <Text style={styles.text}>  Konan rédige...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: "row", alignItems: "center", padding: 8 },
  text: { color: "#BFBFBF", fontSize: 13 },
});
