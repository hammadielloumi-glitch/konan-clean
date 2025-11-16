// src/services/PdfService.js
import * as Print from 'expo-print';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { conversationToHTML } from '../utils/htmlExport';

/**
 * messages: [{ id, role, content, citations?: [{code, article, url}] }]
 * annexes : [{ name, url, mime }]
 */
export async function exportConversationPDF({ title, messages, annexes = [] }) {
  const html = conversationToHTML({ title, messages, annexes });
  const { uri } = await Print.printToFileAsync({ html });
  const dest = FileSystem.documentDirectory + `${(title || 'konan_chat').replace(/\s+/g, '_')}.pdf`;
  await FileSystem.moveAsync({ from: uri, to: dest });
  if (await Sharing.isAvailableAsync()) await Sharing.shareAsync(dest);
  return dest;
}
