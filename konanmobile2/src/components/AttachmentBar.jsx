// src/components/AttachmentBar.jsx
import React from 'react';
import { View, Text, TouchableOpacity, View as RNView } from 'react-native';
import { colors } from '../theme/colors';

export default function AttachmentBar({ items = [], onPreview, onRemove }) {
  if (!items.length) return null;
  return (
    <View style={{ paddingHorizontal: 8, paddingTop: 6 }}>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6 }}>
        {items.map((it) => (
          <TouchableOpacity
            key={it.localId}
            onPress={() => it.file_id && onPreview ? onPreview(it) : null}
            onLongPress={() => onRemove?.(it.localId)}
            style={{ backgroundColor: colors.surface, borderRadius: 10, paddingVertical: 6, paddingHorizontal: 10, minWidth: 140 }}
          >
            <Text style={{ color: colors.textMuted, fontSize: 12 }} numberOfLines={1}>
              {it.name} • {Math.ceil((it.size || 0) / 1024)} Ko
            </Text>
            {/* barre de progression si en cours */}
            {typeof it.progress === 'number' && it.progress < 100 && (
              <RNView style={{ marginTop: 6, height: 6, backgroundColor: '#1F2937', borderRadius: 6 }}>
                <RNView style={{ height: 6, width: `${it.progress}%`, backgroundColor: '#60A5FA', borderRadius: 6 }} />
              </RNView>
            )}
            {it.file_id && (
              <Text style={{ color: '#93C5FD', fontSize: 11, marginTop: 4 }}>Prêt • Aperçu</Text>
            )}
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}
