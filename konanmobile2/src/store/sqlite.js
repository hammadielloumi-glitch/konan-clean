import * as SQLite from 'expo-sqlite';

export const db = SQLite.openDatabase('konan.db');

// Initialisation et création des tables
db.transaction(tx => {
  // Mode WAL pour de meilleures performances et cohérence concurrente
  tx.executeSql('PRAGMA journal_mode = WAL;');

  // Table des conversations
  tx.executeSql(`
    CREATE TABLE IF NOT EXISTS conversations (
      id TEXT PRIMARY KEY NOT NULL,           -- local_id
      server_id TEXT,                         -- id côté backend si connu
      title TEXT,
      plan_used TEXT,
      created_at INTEGER,
      updated_at INTEGER,
      dirty INTEGER DEFAULT 0                 -- 1 si en attente de synchronisation
    );
  `);

  tx.executeSql(`
    CREATE INDEX IF NOT EXISTS idx_conv_updated ON conversations(updated_at);
  `);

  // Table des messages
  tx.executeSql(`
    CREATE TABLE IF NOT EXISTS messages (
      id TEXT PRIMARY KEY NOT NULL,           -- local_id
      conv_local_id TEXT NOT NULL,
      server_id TEXT,                         -- id côté backend si connu
      role TEXT CHECK(role IN ('user','konan')),
      content_md TEXT,
      created_at INTEGER,
      updated_at INTEGER,
      dirty INTEGER DEFAULT 0,                -- 1 si à pousser
      FOREIGN KEY(conv_local_id) REFERENCES conversations(id) ON DELETE CASCADE
    );
  `);

  tx.executeSql(`
    CREATE INDEX IF NOT EXISTS idx_msg_conv ON messages(conv_local_id, created_at);
  `);
});

/**
 * Exécute une requête SQL dans une transaction existante
 */
export function sql(tx, query, args = []) {
  return new Promise((resolve, reject) => {
    tx.executeSql(
      query,
      args,
      (_, res) => resolve(res),
      (_, err) => {
        console.error('SQLite error:', err);
        reject(err);
        return true; // Stoppe la propagation de l'erreur
      }
    );
  });
}

/**
 * Enveloppe pour exécuter une transaction SQLite proprement
 * @param {Function} fn - Fonction recevant l'objet transaction
 */
export async function withTx(fn) {
  return new Promise((resolve, reject) => {
    db.transaction(
      async tx => {
        try {
          const result = await fn(tx);
          resolve(result);
        } catch (err) {
          console.error('Transaction error:', err);
          reject(err);
        }
      },
      err => {
        // Callback en cas d'échec de transaction globale
        console.error('Transaction failed:', err);
        reject(err);
      }
    );
  });
}
