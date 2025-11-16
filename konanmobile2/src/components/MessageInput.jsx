// ============== src/components/MessageInput.jsx ==============
import React, { useState } from "react";
import { motion } from "framer-motion";
import { Send } from "lucide-react";

export default function MessageInput({ onSend }) {
  const [text, setText] = useState("");

  const submit = () => {
    const t = text.trim();
    if (!t) return;
    onSend(t);
    setText("");
  };

  return (
    <div className="rounded-2xl bg-slate-900/60 border border-slate-800/60 shadow-md p-2">
      <div className="flex items-end gap-2">
        <textarea
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Écrire un message..."
          className="flex-1 resize-none bg-transparent outline-none px-3 py-2 text-sm placeholder:text-slate-500"
        />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.97 }}
          onClick={submit}
          className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-100 text-slate-900 hover:bg-white shadow"
        >
          <Send className="h-4 w-4" />
          <span className="text-sm font-medium hidden sm:inline">Envoyer</span>
        </motion.button>
      </div>
    </div>
  );
}
