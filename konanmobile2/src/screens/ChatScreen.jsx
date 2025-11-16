// src/screens/ChatScreen.jsx
import React, { useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { useAuth } from "../hooks/useAuth";
import { sendMessage } from "../services/ChatService";
import MessageBubble from "../components/MessageBubble";
import Composer from "../components/Composer";

export default function ChatScreen({ navigation }) {
  const { token, user, logout, status } = useAuth();
  const [messages, setMessages] = useState([]);
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (status === "unauthenticated") {
      navigation.replace("Login");
    }
  }, [status, navigation]);

  useEffect(() => {
    scrollRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const handleSend = async (text) => {
    if (!token) {
      Alert.alert("Session", "Veuillez vous reconnecter");
      navigation.replace("Login");
      return;
    }

    const optimistic = {
      id: `${Date.now()}-user`,
      role: "user",
      content: text,
      pending: true,
    };
    setMessages((prev) => [...prev, optimistic]);
    setBusy(true);

    try {
      const nextMessages = await sendMessage(text, token);
      setMessages((prev) => {
        const history = prev.filter((msg) => !msg.pending);
        if (!Array.isArray(nextMessages) || nextMessages.length === 0) {
          return history;
        }

        if (nextMessages.length >= history.length) {
          return nextMessages;
        }

        const existingById = new Map(history.map((msg) => [msg.id, msg]));
        const merged = [...history];

        nextMessages.forEach((msg) => {
          if (existingById.has(msg.id)) {
            const index = merged.findIndex((item) => item.id === msg.id);
            if (index >= 0) {
              merged[index] = msg;
            }
          } else {
            merged.push(msg);
          }
        });

        return merged;
      });
    } catch (error) {
      setMessages((prev) => [
        ...prev.filter((msg) => !msg.pending),
        {
          id: `${Date.now()}-error`,
          role: "assistant",
          content: `Erreur: ${error?.message || "échec de la requête"}`,
        },
      ]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        <View style={styles.topbar}>
          <Text style={styles.topbarTitle}>Chat KONAN</Text>
          <View style={styles.topbarRight}>
            <Text style={styles.userLabel}>{user?.sub ?? "Invité"}</Text>
            <TouchableOpacity
              style={styles.logoutButton}
              onPress={async () => {
                await logout();
                navigation.replace("Login");
              }}
              activeOpacity={0.85}
            >
              <Text style={styles.logoutText}>Déconnexion</Text>
            </TouchableOpacity>
          </View>
        </View>

        {status === "loading" ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator color="#ffffff" />
          </View>
        ) : (
          <>
            <ScrollView
              ref={scrollRef}
              style={styles.messages}
              contentContainerStyle={
                messages.length === 0 ? styles.emptyContainer : styles.messageList
              }
            >
              {messages.length === 0 ? (
                <Text style={styles.emptyText}>Démarrez une conversation</Text>
              ) : (
                messages.map((msg) => (
                  <MessageBubble key={msg.id} role={msg.role} content={msg.content} />
                ))
              )}
            </ScrollView>

            <Composer onSend={handleSend} disabled={busy || status !== "authenticated"} />
          </>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: "#0B0B0B",
  },
  container: {
    flex: 1,
    backgroundColor: "#0B0B0B",
  },
  topbar: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: "rgba(255,255,255,0.05)",
    backgroundColor: "rgba(11,11,11,0.92)",
  },
  topbarTitle: {
    color: "#FFFFFF",
    fontSize: 18,
    fontWeight: "600",
    letterSpacing: 0.5,
  },
  topbarRight: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  userLabel: {
    color: "rgba(255,255,255,0.6)",
    fontSize: 13,
  },
  logoutButton: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 16,
    backgroundColor: "rgba(255,255,255,0.12)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
  },
  logoutText: {
    color: "#FFFFFF",
    fontWeight: "600",
    fontSize: 13,
  },
  messages: {
    flex: 1,
  },
  messageList: {
    paddingTop: 20,
    paddingBottom: 12,
  },
  emptyContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  emptyText: {
    color: "rgba(255,255,255,0.4)",
    fontSize: 15,
  },
  loadingContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#0B0B0B",
  },
});
