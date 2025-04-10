// import { initializeApp } from "https://www.gstatic.com/firebasejs/10.0.0/firebase-app.js";
// import { getFirestore, collection, doc, updateDoc, serverTimestamp, query, orderBy, onSnapshot } from "https://www.gstatic.com/firebasejs/10.0.0/firebase-firestore.js";
// import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.0.0/firebase-auth.js";

// const firebaseConfig = {
//   apiKey: "AIzaSyD-XSpFD6zXeM3eIh9xnMmHyvyxdJBhIEU",
//   authDomain: "lovenett-ec1aa.firebaseapp.com",
//   projectId: "lovenett-ec1aa",
//   storageBucket: "lovenett-ec1aa.firebasestorage.app",
//   messagingSenderId: "933622260517",
//   appId: "1:933622260517:web:4bec5a2443a11f2ee330cc",
//   measurementId: "G-17ZPHEDBW6"
// };

// const app = initializeApp(firebaseConfig);
// const db = getFirestore(app);
// const auth = getAuth(app);

// // Make db and auth globally available
// window.db = db;
// window.auth = auth;

// // Update user status to "online" when they log in
// onAuthStateChanged(auth, async (user) => {
//   if (user) {
//     await updateDoc(doc(db, 'users', user.uid), {
//       status: 'online',
//       lastActive: serverTimestamp(),
//     });
//   } else {
//     // Update user status to "offline" when they log out
//     const currentUser = auth.currentUser;
//     if (currentUser) {
//       await updateDoc(doc(db, 'users', currentUser.uid), {
//         status: 'offline',
//         lastActive: serverTimestamp(),
//       });
//     }
//   }
// });

// const messagesQuery = query(collection(db, 'messages'), orderBy('timestamp'));
// onSnapshot(messagesQuery, (snapshot) => {
//   snapshot.forEach((doc) => {
//     const data = doc.data();
//     displayMessage(data.text, data.sender);
//   });
// });

// // Edit message
// document.querySelector('.edit-button').addEventListener('click', async () => {
//   const newText = prompt('Edit your message:', message);
//   if (newText) {
//     await updateDoc(doc(db, 'messages', messageId), {
//       text: newText,
//     });
//   }
// });

// // Delete message
// document.querySelector('.delete-button').addEventListener('click', async () => {
//   await deleteDoc(doc(db, 'messages', messageId));
// });

// /* Update the user’s profile  */
// document.getElementById('save-profile').addEventListener('click', async () => {
//   const name = document.getElementById('name').value;
//   const status = document.getElementById('status').value;
//   const user = auth.currentUser;

//   if (user) {
//     await updateDoc(doc(db, 'users', user.uid), {
//       name: name,
//       status: status,
//     });
//     alert('Profile updated successfully!');
//   }
// });





import { initializeApp } from "https://www.gstatic.com/firebasejs/10.0.0/firebase-app.js";
import { 
  getFirestore, collection, addDoc, query, 
  where, orderBy, onSnapshot, serverTimestamp 
} from "https://www.gstatic.com/firebasejs/10.0.0/firebase-firestore.js";
import { 
  getAuth, onAuthStateChanged 
} from "https://www.gstatic.com/firebasejs/10.0.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);


// S'assurer que ces fonctions sont bien exportées
export { 
  db, auth, collection, addDoc, query, 
  where, orderBy, onSnapshot, serverTimestamp 
};