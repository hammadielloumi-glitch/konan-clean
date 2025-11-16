// ========================= src/App.jsx =========================
import React, { useEffect, useMemo, useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatArea from "./components/ChatArea";
import { API_BASE_URL } from "./config/api";
import { http } from "./services/client";

export default function App() {
  console.log("API_BASE_URL", API_BASE_URL);

  const runHealth = async () => {
    try {
      const r = await http("/health");
      console.log("[TEST] GET /health =>", r);
    } catch (e) {
      console.log("[TEST] GET /health error =>", String(e));
    }
  };

  const runChat = async () => {
    try {
      const r = await http("/api/chat", {
        method: "POST",
        body: JSON.stringify({ message: "Bonjour" }),
      });
      console.log("[TEST] POST /api/chat =>", r);
    } catch (e) {
      console.log("[TEST] POST /api/chat error =>", String(e));
    }
  };

  useEffect(() => {
    // Auto-run once for convenience
    runHealth();
    runChat();
  }, []);
  const initialChat = useMemo(
    () => ({
      id: crypto.randomUUID(),
      title: "Nouvelle discussion",
      messages: [
        { id: crypto.randomUUID(), role: "assistant", content: "Bienvenue sur KONAN. Comment puis-je aider ?" },
        { id: crypto.randomUUID(), role: "user", content: "Explique la procédure d'appel." },
      ],
    }),
    []
  );

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [chats, setChats] = useState([initialChat]);
  const [activeChatId, setActiveChatId] = useState(initialChat.id);

  const activeChat = chats.find((c) => c.id === activeChatId);

  const handleNewChat = () => {
    const nc = {
      id: crypto.randomUUID(),
      title: "Nouvelle discussion",
      messages: [
        { id: crypto.randomUUID(), role: "assistant", content: "Nouveau chat démarré. Posez votre question juridique." },
      ],
    };
    setChats((prev) => [nc, ...prev]);
    setActiveChatId(nc.id);
  };

  const handleRenameChat = (title) => {
    setChats((prev) => prev.map((c) => (c.id === activeChatId ? { ...c, title } : c)));
  };

  const handleSelectChat = (id) => setActiveChatId(id);

  const handleSend = (text) => {
    if (!text?.trim()) return;
    // Append user message
    setChats((prev) =>
      prev.map((c) =>
        c.id === activeChatId
          ? { ...c, messages: [...c.messages, { id: crypto.randomUUID(), role: "user", content: text.trim() }] }
          : c
      )
    );
    // Mock assistant reply after a short delay (pure UI mock)
    setTimeout(() => {
      setChats((prev) =>
        prev.map((c) =>
          c.id === activeChatId
            ? {
                ...c,
                messages: [
                  ...c.messages,
                  {
                    id: crypto.randomUUID(),
                    role: "assistant",
                    content:
                      "Réponse simulée de KONAN. L’API sera branchée plus tard. Vous pourrez ici afficher des citations d’articles et des liens.",
                  },
                ],
              }
            : c
        )
      );
    }, 500);
  };

  const handleDeleteChat = (id) => {
    setChats((prev) => prev.filter((c) => c.id !== id));
    if (id === activeChatId && chats.length > 1) {
      const next = chats.find((c) => c.id !== id);
      if (next) setActiveChatId(next.id);
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#0B0B0B] text-slate-200 flex">
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen((v) => !v)}
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
      />

      <main className="flex-1 h-screen overflow-hidden">
        <div className="p-2 flex gap-2">
          <button className="px-3 py-1 bg-slate-700 rounded" onClick={runHealth}>
            Test /health
          </button>
          <button className="px-3 py-1 bg-slate-700 rounded" onClick={runChat}>
            Test /api/chat
          </button>
        </div>
        <ChatArea
          title={activeChat?.title || "Chat"}
          messages={activeChat?.messages || []}
          onSend={handleSend}
          onRename={handleRenameChat}
          onMenuClick={() => setSidebarOpen((v) => !v)}
        />
      </main>
    </div>
  );
}