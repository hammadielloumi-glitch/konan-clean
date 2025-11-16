// src/components/ApiTester.jsx
// FI9_NAYEK v12.1 : Unification API_BASE_URL
import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { API_BASE_URL } from '../config/api';
import { colors } from '../theme/colors';

export default function ApiTester() {
  const [status, setStatus] = useState('idle'); // 'idle' | 'checking' | 'ok' | 'error'
  const [message, setMessage] = useState('');

  async function checkApi() {
    setStatus('checking');
    setMessage('');
    try {
      const res = await fetch(`${API_BASE_URL}/health`); // endpoint simple dans ton backend
      if (res.ok) {
        setStatus('ok');
        setMessage('Connexion API réussie ✅');
      } else {
        setStatus('error');
        setMessage(`Réponse inattendue : ${res.status}`);
      }
    } catch (err) {
      setStatus('error');
      setMessage(err.message || 'Erreur de connexion');
    }
  }

  useEffect(() => {
    checkApi();
  }, []);

  return (
    <View
      style={{
        margin: 16,
        padding: 16,
        borderRadius: 12,
        backgroundColor: colors.surface || '#1E293B',
        borderWidth: 1,
        borderColor: '#334155',
      }}
    >
      <Text style={{ color: '#93C5FD', fontSize: 16, fontWeight: '600', marginBottom: 8 }}>
        Diagnostic connexion API
      </Text>

      {status === 'checking' && (
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
          <ActivityIndicator color="#3B82F6" />
          <Text style={{ color: '#CBD5E1' }}>Vérification en cours...</Text>
        </View>
      )}

      {status === 'ok' && (
        <Text style={{ color: '#22C55E', fontWeight: '600' }}>{message}</Text>
      )}

      {status === 'error' && (
        <Text style={{ color: '#EF4444', fontWeight: '600' }}>❌ {message}</Text>
      )}

      <TouchableOpacity
        onPress={checkApi}
        style={{
          marginTop: 16,
          paddingVertical: 10,
          borderRadius: 8,
          backgroundColor: '#3B82F6',
          alignItems: 'center',
        }}
      >
        <Text style={{ color: 'white', fontWeight: '600' }}>Re-tester</Text>
      </TouchableOpacity>

      <Text
        style={{
          marginTop: 12,
          color: '#94A3B8',
          fontSize: 13,
          textAlign: 'center',
        }}
      >
        API_BASE_URL : {API_BASE_URL}
      </Text>
    </View>
  );
}
