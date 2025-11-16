import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, FlatList, TextInput, Alert } from 'react-native';
import { colors } from '../theme/colors';
import { useAuth } from '../auth/useAuth';
import { pageConversations, setConversationTitle, toggleFavorite, softDeleteConversation, searchMessagesLocal } from '../store/dao';
import { pullConversationsPaged, pushConvMeta, deleteConversationServer } from '../services/SyncService';

export default function ConversationsScreen({ navigation }) {
  const { token } = useAuth();
  const [items, setItems] = useState([]);
  const [cursor, setCursor] = useState(null);
  const [query, setQuery] = useState('');
  const [favoritesOnly, setFavoritesOnly] = useState(false);

  async function loadLocal(reset=false) {
    const page = await pageConversations({ limit: 30, cursor: reset ? null : cursor, favoritesOnly });
    setItems(reset ? page : [...items, ...page]);
    if (page.length) setCursor(page[page.length - 1].updated_at);
  }

  async function pullCloud() {
    let cur = null;
    for (let i=0; i<4; i++) { // 4 pages max par rafraîchissement
      cur = await pullConversationsPaged({ token, limit: 50, cursor: cur });
      if (!cur) break;
    }
    setCursor(null);
    await loadLocal(true);
  }

  useEffect(() => { pullCloud().catch(()=>{}); }, [favoritesOnly]);

  async function onRename(c) {
    const title = promptPolyfill('Nouveau titre:', c.title || 'Sans titre');
    if (!title) return;
    await setConversationTitle(c.id, title);
    try { await pushConvMeta({ token, convId: c.id, title }); } catch {}
    await loadLocal(true);
  }

  async function onFavorite(c) {
    const value = c.favorite ? 0 : 1;
    await toggleFavorite(c.id, value);
    try { await pushConvMeta({ token, convId: c.id, favorite: !!value }); } catch {}
    await loadLocal(true);
  }

  async function onDelete(c) {
    await softDeleteConversation(c.id);
    try { await deleteConversationServer({ token, convId: c.id }); } catch {}
    await loadLocal(true);
  }

  async function onSearch() {
    if (!query.trim()) { await loadLocal(true); return; }
    const hits = await searchMessagesLocal(query.trim(), 200);
    const convIds = Array.from(new Set(hits.map(h => h.conv_local_id)));
    // Charger les conversations filtrées
    const filtered = items.filter(c => convIds.includes(c.id));
    setItems(filtered);
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg, padding: 12 }}>
      <View style={{ flexDirection: 'row', gap: 8, marginBottom: 8 }}>
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="Recherche locale plein texte…"
          placeholderTextColor={colors.textMuted}
          style={{ flex: 1, backgroundColor: colors.surface, color: colors.text, padding: 10, borderRadius: 10 }}
          onSubmitEditing={onSearch}
        />
        <TouchableOpacity onPress={onSearch} style={{ backgroundColor: colors.surface, padding: 10, borderRadius: 10 }}>
          <Text style={{ color: colors.text }}>Rechercher</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => setFavoritesOnly(v => !v)} style={{ backgroundColor: colors.surface, padding: 10, borderRadius: 10 }}>
          <Text style={{ color: colors.text }}>{favoritesOnly ? 'Tous' : 'Favoris'}</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        onPress={() => navigation.navigate('Chat', { conversationId: 'new' })}
        style={{ backgroundColor: colors.surface, padding: 12, borderRadius: 12, marginBottom: 12 }}
      >
        <Text style={{ color: colors.text, fontWeight: '700' }}>+ Nouveau chat</Text>
      </TouchableOpacity>

      <FlatList
        data={items}
        keyExtractor={(it) => it.id}
        renderItem={({ item }) => (
          <View style={{ backgroundColor: colors.surface, padding: 12, borderRadius: 12, marginBottom: 8 }}>
            <TouchableOpacity onPress={() => navigation.navigate('Chat', { conversationId: item.id })}>
              <Text style={{ color: colors.text, fontWeight: '600' }}>{item.title || 'Sans titre'}</Text>
              <Text style={{ color: colors.textMuted, fontSize: 12 }}>{new Date(item.updated_at).toLocaleString()}</Text>
            </TouchableOpacity>
            <View style={{ flexDirection: 'row', gap: 12, marginTop: 8 }}>
              <TouchableOpacity onPress={() => onRename(item)}><Text style={{ color: '#93C5FD' }}>Renommer</Text></TouchableOpacity>
              <TouchableOpacity onPress={() => onFavorite(item)}><Text style={{ color: item.favorite ? '#F59E0B' : '#CBD5E1' }}>★ Favori</Text></TouchableOpacity>
              <TouchableOpacity onPress={() => onDelete(item)}><Text style={{ color: '#FCA5A5' }}>Supprimer</Text></TouchableOpacity>
            </View>
          </View>
        )}
        onEndReached={() => loadLocal(false)}
        onEndReachedThreshold={0.5}
      />
    </View>
  );
}

/** Ersatz prompt sur mobile */
function promptPolyfill(label, initial) {
  // Remplacez par un modal custom si besoin
  return global?.prompt ? global.prompt(label, initial) : initial;
}
