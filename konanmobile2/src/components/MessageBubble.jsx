import React, { memo } from "react";
import { View, Text, StyleSheet } from "react-native";

function MessageBubble({ role = "assistant", content = "" }) {
  const isUser = role === "user";

  return (
    <View style={[styles.row, isUser ? styles.alignEnd : styles.alignStart]}>
      <View style={[styles.bubble, isUser ? styles.userBubble : styles.assistantBubble]}>
        <Text style={[styles.label, isUser ? styles.userLabel : styles.assistantLabel]}>
          {isUser ? "Vous" : "KONAN"}
        </Text>
        <Text style={styles.content}>{content}</Text>
      </View>
    </View>
  );
}

export default memo(MessageBubble);

const styles = StyleSheet.create({
  row: {
    width: "100%",
    paddingHorizontal: 16,
    marginBottom: 12,
    flexDirection: "row",
  },
  alignEnd: {
    justifyContent: "flex-end",
  },
  alignStart: {
    justifyContent: "flex-start",
  },
  bubble: {
    maxWidth: "78%",
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 24,
    backgroundColor: "rgba(17,17,17,0.95)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.04)",
    shadowColor: "#000",
    shadowOpacity: 0.2,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
    elevation: 3,
  },
  assistantBubble: {
    backgroundColor: "#111111",
  },
  userBubble: {
    backgroundColor: "rgba(255,255,255,0.14)",
    borderColor: "rgba(255,255,255,0.18)",
  },
  label: {
    fontSize: 11,
    marginBottom: 6,
    letterSpacing: 0.6,
  },
  assistantLabel: {
    color: "rgba(255,255,255,0.55)",
  },
  userLabel: {
    color: "rgba(255,255,255,0.65)",
    textAlign: "right",
  },
  content: {
    color: "#EDEDED",
    fontSize: 15,
    lineHeight: 22,
  },
});