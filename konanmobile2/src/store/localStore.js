import AsyncStorage from '@react-native-async-storage/async-storage';

const key = (conv) => `konan:conv:${conv}`;

export async function saveMessage(convId, msg) {
  const raw = (await AsyncStorage.getItem(key(convId))) || '[]';
  const arr = JSON.parse(raw);
  arr.push(msg);
  await AsyncStorage.setItem(key(convId), JSON.stringify(arr));
}

export async function loadMessages(convId) {
  const raw = (await AsyncStorage.getItem(key(convId))) || '[]';
  return JSON.parse(raw);
}

export async function clearConversation(convId) {
  await AsyncStorage.removeItem(key(convId));
}
