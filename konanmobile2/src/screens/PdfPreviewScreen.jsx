import React from 'react';
import { View, ActivityIndicator } from 'react-native';
import { WebView } from 'react-native-webview';
import { colors } from '../theme/colors';

export default function PdfPreviewScreen({ route }) {
  const { url } = route.params; // URL publique backend /api/files/{file_id}
  // Affiche directement le PDF si Android ≥ 5. Sur iOS c’est OK.
  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <WebView
        source={{ uri: url }}
        startInLoadingState
        renderLoading={() => <ActivityIndicator style={{ marginTop: 30 }} />}
        allowFileAccess
        allowingReadAccessToURL={url}
      />
    </View>
  );
}
