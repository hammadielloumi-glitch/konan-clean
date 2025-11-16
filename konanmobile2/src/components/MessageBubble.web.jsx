// Web version of MessageBubble - uses HTML/React instead of React Native
import React, { memo } from "react";

/**
 * MessageBubble (Web)
 * Props:
 *  - content: string (required)
 *  - role: "user" | "assistant" (default "assistant")
 */
function MessageBubble({ content = "", role = "assistant" }) {
  const isUser = role === "user";

  return (
    <div
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-1 px-2`}
    >
      <div
        className={`max-w-[85%] rounded-2xl px-3 py-2.5 border ${
          isUser
            ? "bg-[#10A37F] border-[#0E8E6F] text-[#0A0A0A] rounded-tr-sm"
            : "bg-[#1E1E1E] border-[#2A2A2A] text-[#EDEDED] rounded-tl-sm"
        } shadow-sm`}
      >
        <p className="text-[15px] leading-5 select-text whitespace-pre-wrap break-words">
          {content}
        </p>
      </div>
    </div>
  );
}

export default memo(MessageBubble);

