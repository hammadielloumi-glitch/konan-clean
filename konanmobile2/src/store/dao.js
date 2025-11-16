import { withTx, sql } from './sqlite';

// Upsert conversation
export async function upsertConversation(conv) {
  const now = Date.now();
  return withTx(async (tx) => {
    await sql(
      tx,
      `INSERT INTO conversations (id, server_id, title, plan_used, created_at, updated_at, dirty)
       VALUES (?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(id) DO UPDATE SET
         server_id = excluded.server_id,
         title = excluded.title,
         plan_used = excluded.plan_used,
         updated_at = excluded.updated_at,
         dirty = excluded.dirty`,
      [
        conv.id,
        conv.server_id ?? null,
        conv.title ?? null,
        conv.plan_used ?? null,
        conv.created_at ?? now,
        conv.updated_at ?? now,
        conv.dirty ? 1 : 0,
      ]
    );
  });
}

// Liste des conversations triées par date
export async function listConversations(limit = 50) {
  return withTx(async (tx) => {
    const res = await sql(
      tx,
      `SELECT * FROM conversations ORDER BY updated_at DESC LIMIT ?`,
      [limit]
    );
    return res.rows._array;
  });
}

// Upsert message
export async function upsertMessage(m) {
  const now = Date.now();
  return withTx(async (tx) => {
    await sql(
      tx,
      `INSERT INTO messages (id, conv_local_id, server_id, role, content_md, created_at, updated_at, dirty)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(id) DO UPDATE SET
         server_id = excluded.server_id,
         role = excluded.role,
         content_md = excluded.content_md,
         updated_at = excluded.updated_at,
         dirty = excluded.dirty`,
      [
        m.id,
        m.conv_local_id,
        m.server_id ?? null,
        m.role,
        m.content_md ?? '',
        m.created_at ?? now,
        m.updated_at ?? now,
        m.dirty ? 1 : 0,
      ]
    );
  });
}

// Charger messages d'une conversation
export async function loadMessages(convLocalId, limit = 500) {
  return withTx(async (tx) => {
    const res = await sql(
      tx,
      `SELECT * FROM messages WHERE conv_local_id = ? ORDER BY created_at ASC LIMIT ?`,
      [convLocalId, limit]
    );
    return res.rows._array;
  });
}

// Supprimer conversation et messages localement
export async function clearConversationLocal(convLocalId) {
  return withTx(async (tx) => {
    await sql(tx, `DELETE FROM messages WHERE conv_local_id = ?`, [convLocalId]);
    await sql(tx, `DELETE FROM conversations WHERE id = ?`, [convLocalId]);
  });
}

// Récupérer messages "dirty" à synchroniser
export async function dirtyMessages() {
  return withTx(async (tx) => {
    const res = await sql(
      tx,
      `SELECT * FROM messages WHERE dirty = 1 ORDER BY created_at ASC`
    );
    return res.rows._array;
  });
}

// Marquer un message comme synchronisé
export async function markMessageSynced(localId, serverId) {
  return withTx(async (tx) => {
    await sql(
      tx,
      `UPDATE messages
       SET dirty = 0,
           server_id = ?,
           updated_at = ?
       WHERE id = ?`,
      [serverId ?? null, Date.now(), localId]
    );
  });
}
