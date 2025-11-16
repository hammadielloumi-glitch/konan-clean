// src/services/SyncService.js
import { API_BASE_URL } from 'src/config/api';
import {
  upsertConversation,
  upsertMessage,
  dirtyMessages,
  markMessageSynced,
} from '../store/dao';

/** JSON sûr: gère 204/vides sans planter */
async function safeJson(res) {
  const text = await res.text();
  if (!text) return null;
  try { return JSON.parse(text); }
  catch { return null; }
}

/** lève si !ok, sinon renvoie JSON sûr */
async function jsonOrThrow(res) {
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status} ${body}`);
  }
  return safeJson(res);
}

function parseTs(value, fallback = Date.now()) {
  const n = typeof value === 'number' ? value : Date.parse(value);
  return Number.isFinite(n) ? n : fallback;
}

/**
 * Pull: récupère conversations du serveur et derniers messages
 * API attendue:
 *  - GET /api/conversations -> soit [{...}], soit {items:[...]}
 *  - GET /api/conversations/{id} -> {messages:[{...}]}
 */
export async function pullServer({ token, takeMessagesPerConv = 200 }) {
  const headers = { Authorization: `Bearer ${token}` };

  const convRes = await fetch(`${API_BASE_URL}/api/conversations`, { headers });
  const convPayload = await jsonOrThrow(convRes);
  const convs = Array.isArray(convPayload)
    ? convPayload
    : Array.isArray(convPayload?.items)
      ? convPayload.items
      : [];

  for (const c of convs) {
    try {
      const localId = c.id;

      await upsertConversation({
        id: localId,
        server_id: c.id ?? null,
        title: c.title ?? null,
        plan_used: c.plan_used ?? null,
        created_at: parseTs(c.created_at),
        updated_at: parseTs(c.last_message_at ?? c.created_at),
        dirty: 0,
      });

      const detailRes = await fetch(`${API_BASE_URL}/api/conversations/${c.id}`, { headers });
      const detail = await jsonOrThrow(detailRes);
      const msgs = Array.isArray(detail?.messages) ? detail.messages : [];
      const tail = msgs.slice(-takeMessagesPerConv);

      for (const m of tail) {
        await upsertMessage({
          id: m.id,
          server_id: m.id ?? null,
          conv_local_id: localId,
          role: m.role,
          content_md: m.content ?? '',
          created_at: parseTs(m.created_at),
          updated_at: Date.now(),
          dirty: 0,
        });
      }
    } catch (e) {
      // On continue même si une conv échoue
      // Option: logger e.message si besoin
    }
  }
}

/**
 * Push: envoie les messages "dirty" (créés offline) vers le serveur.
 * API attendue:
 *  - POST /api/chat {conversation_id, message, stream:false} -> {id}
 */
export async function pushLocal({ token }) {
  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };
  const pendings = await dirtyMessages();

  for (const m of pendings) {
    try {
      const body = JSON.stringify({
        conversation_id: m.conv_local_id,
        message: m.content_md,
        stream: false,
      });
      const res = await fetch(`${API_BASE_URL}/api/chat`, { method: 'POST', headers, body });
      if (!res.ok) {
        // on n'efface pas le dirty: on réessaiera plus tard
        continue;
      }
      const data = await safeJson(res);
      if (data?.id) {
        await markMessageSynced(m.id, data.id);
      }
    } catch {
      // réseau ou autre: laisser dirty pour retry
    }
  }
}

/** Sync bidirectionnelle simple */
export async function syncAll({ token }) {
  await pullServer({ token });
  await pushLocal({ token });
}

export default { pullServer, pushLocal, syncAll };
