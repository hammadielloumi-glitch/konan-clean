// =================== src/components/Sidebar.jsx ===================
import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { PlusCircle, Search, Library, Brain, MessageSquare } from "lucide-react";

export default function Sidebar({ open, onToggle, chats, activeChatId, onSelectChat, onNewChat, onDeleteChat }) {
  const width = open ? 280 : 72;

  return (
    <AnimatePresence initial={false}>
      <motion.aside
        key="sidebar"
        initial={{ width: 72, opacity: 0.9 }}
        animate={{ width, opacity: 1 }}
        exit={{ width: 0, opacity: 0 }}
        transition={{ type: "spring", stiffness: 240, damping: 26 }}
        className="h-screen bg-[#0E0E0E] border-r border-slate-800/60 shadow-md overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center gap-2 px-3 py-3 border-b border-slate-800/60">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-slate-600 to-slate-800 grid place-items-center text-white shadow" title="KONAN">
            K
          </div>
          {open && <div className="font-semibold tracking-wide">KONAN</div>}
          <button
            onClick={onToggle}
            className="ml-auto rounded-xl px-2 py-1 hover:bg-slate-800/60 focus:outline-none"
            aria-label="Toggle sidebar"
            title="Ouvrir/fermer"
          >
            <MessageSquare className="h-5 w-5" />
          </button>
        </div>

        {/* Actions */}
        <nav className="p-3 space-y-2">
          <SidebarItem open={open} icon={PlusCircle} label="Nouveau chat" onClick={onNewChat} />
          <SidebarItem open={open} icon={Search} label="Rechercher des chats" />
          <SidebarItem open={open} icon={Library} label="Bibliothèque" />
          <SidebarItem open={open} icon={Brain} label="Projets" />
        </nav>

        {/* Chats list */}
        <div className="mt-1 px-2 pb-2 overflow-y-auto custom-scroll">
          {chats.map((c) => (
            <motion.div key={c.id} layout className="mb-2">
              <button
                onClick={() => onSelectChat(c.id)}
                className={`group w-full flex items-center gap-3 px-2 py-2 rounded-2xl hover:bg-slate-800/60 border border-transparent hover:border-slate-700 transition ${
                  activeChatId === c.id ? "bg-slate-800/60 border-slate-700" : ""
                }`}
                title={c.title}
              >
                <div className="h-8 w-8 rounded-xl bg-slate-700 grid place-items-center text-xs">{c.title.slice(0, 2).toUpperCase()}</div>
                {open && (
                  <div className="flex-1 text-left">
                    <div className="text-sm truncate">{c.title}</div>
                    <div className="text-[11px] text-slate-400">{c.messages.length} messages</div>
                  </div>
                )}
                {open && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteChat(c.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-400 text-xs px-2 py-1 rounded-lg"
                  >
                    Suppr
                  </button>
                )}
              </button>
            </motion.div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-auto p-3 text-[11px] text-slate-500/80">UI Mockup • v1.0</div>
      </motion.aside>
    </AnimatePresence>
  );
}

function SidebarItem({ icon: Icon, label, open, onClick }) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="w-full flex items-center gap-3 px-3 py-2 rounded-2xl bg-slate-900/60 hover:bg-slate-800/70 border border-slate-800/60 shadow-sm"
    >
      <Icon className="h-5 w-5" />
      {open && <span className="text-sm">{label}</span>}
    </motion.button>
  );
}
