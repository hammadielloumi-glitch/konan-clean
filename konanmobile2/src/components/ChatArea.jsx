// ================ src/components/ChatArea.jsx ================
import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Menu, ChevronDown } from "lucide-react";
// Use web version for Vite build
import MessageBubble from "./MessageBubble.web.jsx";
import MessageInput from "./MessageInput";

export default function ChatArea({ title, messages, onSend, onRename, onMenuClick }) {
  const containerRef = useRef(null);
  const [editTitle, setEditTitle] = useState(false);
  const [tempTitle, setTempTitle] = useState(title);

  useEffect(() => {
    // Auto-scroll to bottom on new messages
    if (containerRef.current) containerRef.current.scrollTop = containerRef.current.scrollHeight;
  }, [messages]);

  useEffect(() => setTempTitle(title), [title]);

  return (
    <div className="h-full flex flex-col">
      {/* Top bar */}
      <div className="sticky top-0 z-10 flex items-center gap-2 px-4 py-3 bg-[#0B0B0B]/90 backdrop-blur border-b border-slate-800/60">
        <button onClick={onMenuClick} className="md:hidden rounded-xl p-2 hover:bg-slate-800/60" aria-label="Menu">
          <Menu className="h-5 w-5" />
        </button>
        {editTitle ? (
          <input
            autoFocus
            value={tempTitle}
            onChange={(e) => setTempTitle(e.target.value)}
            onBlur={() => {
              onRename(tempTitle.trim() || "Sans titre");
              setEditTitle(false);
            }}
            className="bg-slate-900/60 border border-slate-800/60 rounded-xl px-3 py-1 text-sm outline-none"
          />
        ) : (
          <button onClick={() => setEditTitle(true)} className="text-sm font-medium hover:underline flex items-center gap-1">
            {title}
            <ChevronDown className="h-4 w-4 text-slate-400" />
          </button>
        )}
        <div className="ml-auto text-xs text-slate-400">Interface mock • API à brancher ultérieurement</div>
      </div>

      {/* Messages */}
      <div ref={containerRef} className="flex-1 overflow-y-auto px-4 py-6 md:px-8 custom-scroll">
        <div className="mx-auto w-full md:max-w-3xl space-y-3">
          {messages.map((m) => (
            <motion.div key={m.id} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}>
              <MessageBubble role={m.role} content={m.content} />
            </motion.div>
          ))}
        </div>
      </div>

      {/* Composer */}
      <div className="px-4 pb-4 md:px-8">
        <div className="mx-auto w-full md:max-w-3xl">
          <MessageInput onSend={onSend} />
          <div className="mt-2 text-[11px] text-slate-500/80 text-center">
            Ne partagez pas d’informations sensibles. Les réponses affichées ici sont simulées.
          </div>
        </div>
      </div>
    </div>
  );
}
