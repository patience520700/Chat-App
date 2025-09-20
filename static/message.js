import { db } from './firebase.js';

export const sendMessage = (conversationId, senderId, content, type = 'text') => {
  const messageData = {
    senderId: senderId,
    content: content,
    type: type,
    timestamp: firebase.firestore.FieldValue.serverTimestamp(),
    status: 'sent'
  };

  // Ajouter le message
  return db.collection('conversations').doc(conversationId)
    .collection('messages').add(messageData)
    .then(() => {
      // Mettre à jour la conversation
      return db.collection('conversations').doc(conversationId).update({
        lastMessage: type === 'text' ? content : `[${type}]`,
        lastMessageTime: firebase.firestore.FieldValue.serverTimestamp()
      });
    });
};

export const getMessages = (conversationId, callback) => {
  return db.collection('conversations').doc(conversationId)
    .collection('messages')
    .orderBy('timestamp')
    .onSnapshot(snapshot => {
      const messages = [];
      snapshot.forEach(doc => {
        messages.push({ id: doc.id, ...doc.data() });
      });
      callback(messages);
    });
};