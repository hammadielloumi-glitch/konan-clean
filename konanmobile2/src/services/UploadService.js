// src/services/UploadService.js
import * as FileSystem from 'expo-file-system';
import { API_BASE_URL } from 'src/config/api';

const MAX_SIZE = 10 * 1024 * 1024; // 10 Mo

export async function uploadFileWithProgress({ token, file, onProgress }) {
  // file = { uri, name, mime, size }
  const info = await FileSystem.getInfoAsync(file.uri);
  const size = info?.size ?? file.size ?? 0;
  if (!info.exists) throw new Error('Fichier introuvable');
  if (size > MAX_SIZE) throw new Error('Fichier trop volumineux (>10 Mo)');

  // Expo FileSystem.createUploadTask permet la progression
  const url = `${API_BASE_URL}/api/upload`;
  const headers = { Authorization: `Bearer ${token}` };
  const uploadTask = FileSystem.createUploadTask(url, file.uri, {
    fieldName: 'file',
    httpMethod: 'POST',
    uploadType: FileSystem.FileSystemUploadType.MULTIPART,
    parameters: { name: file.name || 'document', mime: file.mime || 'application/octet-stream' },
    headers,
  }, (progress) => {
    // progress.totalBytesSent / progress.totalBytesExpectedToSend
    if (progress.totalBytesExpectedToSend > 0) {
      const pct = Math.min(
        100,
        Math.round((progress.totalBytesSent / progress.totalBytesExpectedToSend) * 100)
      );
      onProgress?.(pct);
    }
  });

  const result = await uploadTask.uploadAsync();
  if (result.status !== 200 && result.status !== 201) {
    throw new Error(`HTTP ${result.status} ${result.body}`);
  }
  const parsed = JSON.parse(result.body || '{}');
  return parsed; // { file_id, name, mime, size_bytes, sha256 }
}

export async function extractLawRefs({ token, file_id }) {
  const r = await fetch(`${API_BASE_URL}/api/tools/extract_law_refs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ file_id }),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status} ${await r.text()}`);
  return r.json();
}

export function filePublicUrl(file_id) {
  return `${API_BASE_URL}/api/files/${file_id}`;
}
