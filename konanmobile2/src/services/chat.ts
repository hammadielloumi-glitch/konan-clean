import { http } from "./client";

type ChatPayload = {
  message: string;
  session_id?: string;
};

export async function sendMessage(payload: ChatPayload) {
  return http("/api/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}


