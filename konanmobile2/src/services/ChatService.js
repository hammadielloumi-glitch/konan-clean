import { API_BASE_URL } from "src/config/api";

function normalizeMessages(payload) {
  if (!payload) return [];
  const source = Array.isArray(payload?.messages)
    ? payload.messages
    : Array.isArray(payload)
    ? payload
    : [];
  return source.map((msg, index) => ({
    id: msg?.id || `${Date.now()}-${index}`,
    role: msg?.role === "user" || msg?.role === "assistant" ? msg.role : "assistant",
    content: msg?.content ?? msg?.message ?? "",
  }));
}

export async function sendMessage(message, token) {
  const text = message?.trim();
  if (!text) {
    throw new Error("Message vide");
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ message: text }),
    });

    const contentType = response.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");
    const body = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const detail = isJson ? body?.detail || JSON.stringify(body) : body;
      throw new Error(detail || `Erreur serveur ${response.status}`);
    }

    const normalized = normalizeMessages(body);
    if (normalized.length === 0) {
      return [
        {
          id: Date.now().toString(),
          role: "assistant",
          content:
            (isJson && (body?.reply || body?.text || body?.response || body?.answer)) ||
            "Réponse vide du backend.",
        },
      ];
    }

    return normalized;
  } catch (error) {
    throw new Error(error?.message || "Serveur injoignable");
  }
}
