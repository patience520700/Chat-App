import { db, storage } from './firebase.js';

export const getUserProfile = (userId) => {
  return db.collection('users').doc(userId).get()
    .then(doc => doc.exists ? doc.data() : null);
};

export const updateProfile = (userId, updates) => {
  return db.collection('users').doc(userId).update(updates);
};

export const uploadUserAvatar = (userId, file) => {
  const storageRef = storage.ref(`avatars/${userId}`);
  return storageRef.put(file)
    .then(() => storageRef.getDownloadURL())
    .then(url => {
      return db.collection('users').doc(userId).update({
        avatarUrl: url
      });
    });
};