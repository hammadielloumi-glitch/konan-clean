import React from 'react';
import { View, Text, TouchableOpacity, Linking } from 'react-native';
import { colors } from '../theme/colors';

export default function CitationChips({ citations=[] }) {
  if (!citations.length) return null;
  return (
    <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>
      {citations.map((c, i) => {
        const label = `${c.code} · Art. ${c.article}`;
        return (
          <TouchableOpacity
            key={`${c.code}-${c.article}-${i}`}
            onPress={() => c.url && Linking.openURL(c.url)}
            style={{ backgroundColor: colors.surfaceAlt, paddingHorizontal: 10, paddingVertical: 6, borderRadius: 10 }}
          >
            <Text style={{ color: '#93C5FD', fontSize: 12 }}>{label}</Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}
