// src/components/TopProgressBar.jsx
import React from 'react';
import { View } from 'react-native';
import { colors } from '../theme/colors';

/**
 * Affiche une barre fine tout en haut si 0 < progress < 100
 * @param {number} progress 0..100
 */
export default function TopProgressBar({ progress = 0 }) {
  if (!Number.isFinite(progress) || progress <= 0 || progress >= 100) return null;
  return (
    <View style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, backgroundColor: '#3B82F6' }}>
      <View style={{ width: `${Math.max(5, Math.min(100, progress))}%`, height: 3, backgroundColor: '#60A5FA' }} />
    </View>
  );
}
