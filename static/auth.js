import { auth, db } from './firebase.js';

export const initAuth = (onAuthSuccess, onAuthFailure) => {
  auth.onAuthStateChanged((user) => {
    if (user) {
      // Mettre à jour le statut
      db.collection('users').doc(user.uid).update({
        status: 'online',
        lastSeen: null
      });
      
      onAuthSuccess(user);
    } else {
      onAuthFailure();
    }
  });
};

export const loginUser = (email, password) => {
  return auth.signInWithEmailAndPassword(email, password);
};

export const registerUser = (email, password, name) => {
  return auth.createUserWithEmailAndPassword(email, password)
    .then((userCredential) => {
      // Créer le profil utilisateur
      return db.collection('users').doc(userCredential.user.uid).set({
        name: name,
        email: email,
        avatarUrl: '',
        status: 'online',
        lastSeen: null
      });
    });
};

export const logoutUser = () => {
  const userId = auth.currentUser?.uid;
  if (userId) {
    db.collection('users').doc(userId).update({
      status: 'offline',
      lastSeen: firebase.firestore.FieldValue.serverTimestamp()
    });
  }
  return auth.signOut();
};