import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { colors } from '../theme/colors';

export default function PlanGate({ onUpgrade }) {
  return (
    <View style={{ padding: 16, borderTopWidth: 1, borderTopColor: colors.divider }}>
      <View style={{ backgroundColor: colors.surface, borderRadius: 12, padding: 16 }}>
        <Text style={{ color: colors.text, fontWeight: '700', marginBottom: 6 }}>Passez à KONAN Premium</Text>
        <Text style={{ color: colors.textMuted, marginBottom: 12 }}>
          Limite atteinte en mode Free. Bénéficiez de l’illimité, de l’export PDF et des favoris.
        </Text>
        <TouchableOpacity onPress={onUpgrade} style={{ backgroundColor: colors.primary, padding: 12, borderRadius: 10, alignSelf: 'flex-start' }}>
          <Text style={{ color: 'white', fontWeight: '600' }}>Voir les offres</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}
