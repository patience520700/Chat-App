// // Tab Switching Logic
// document.querySelectorAll('.tab-btn').forEach(button => {
//   button.addEventListener('click', () => {
//     document.querySelectorAll('.tab-btn, .tab-pane').forEach(el => el.classList.remove('active'));
//     button.classList.add('active');
//     document.getElementById(button.dataset.tab).classList.add('active');
//   });
// });

// // Variables globales
// let currentUserId = null;
// let currentChatId = null;
// let messageHistory = JSON.parse(localStorage.getItem('messageHistory')) || [];

// // Profile Dropdown
// document.addEventListener('DOMContentLoaded', () => {
//   const profileIcon = document.getElementById('profile-icon');
//   const dropdownContent = document.getElementById('profile-dropdown-content');
//   const uploadButton = document.getElementById('upload-profile-pic');
//   const deleteButton = document.getElementById('delete-profile-pic');
//   const setDefaultButton = document.getElementById('set-default-pic');
//   const fileInput = document.getElementById('profile-pic-upload');

//   // Toggle dropdown visibility
//   profileIcon.addEventListener('click', (e) => {
//     e.stopPropagation();
//     dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
//   });

//   document.addEventListener('click', () => dropdownContent.style.display = 'none');
//   dropdownContent.addEventListener('click', (e) => e.stopPropagation());

//   // Profile picture handlers
//   uploadButton.addEventListener('click', () => fileInput.click());
//   fileInput.addEventListener('change', handleProfilePicUpload);
//   deleteButton.addEventListener('click', resetProfilePic);
//   setDefaultButton.addEventListener('click', resetProfilePic);

//   function handleProfilePicUpload(e) {
//       const file = e.target.files[0];
//       if (file) {
//           const reader = new FileReader();
//           reader.onload = (event) => {
//               profileIcon.textContent = '';
//               profileIcon.style.backgroundImage = `url(${event.target.result})`;
//               profileIcon.style.backgroundSize = 'cover';
//           };
//           reader.readAsDataURL(file);
//       }
//   }

//   function resetProfilePic() {
//       profileIcon.style.backgroundImage = '';
//       profileIcon.textContent = '👤';
//   }
// });

// // Initialize chat
// auth.onAuthStateChanged(user => {
//   if (user) {
//       currentUserId = user.uid;
//       loadContacts(user.uid);
//   } else {
//       window.location.href = 'login.html';
//   }
// });

// // Contacts and Messaging Functions
// async function loadContacts(userId) {
//   const contactsRef = collection(db, 'users');
//   const q = query(contactsRef, where('uid', '!=', userId));
  
//   onSnapshot(q, (snapshot) => {
//       const contactsList = document.getElementById('contacts-list');
//       contactsList.innerHTML = '';
      
//       snapshot.forEach(doc => {
//           const contact = doc.data();
//           const li = document.createElement('li');
//           li.innerHTML = `
//               <div class="contact" data-id="${contact.uid}">
//                   <img src="${contact.photoURL || 'default-avatar.png'}" alt="${contact.displayName}">
//                   <span>${contact.displayName}</span>
//                   <span class="status ${contact.status || 'offline'}"></span>
//               </div>
//           `;
//           li.addEventListener('click', () => openChat(contact.uid));
//           contactsList.appendChild(li);
//       });
//   });
// }

// function openChat(contactId) {
//   currentChatId = contactId;
//   document.getElementById('current-chat-name').textContent = 
//       document.querySelector(`[data-id="${contactId}"] span`).textContent;
//   loadMessages(currentUserId, contactId);
// }

// // Message History Functions
// function saveToHistory(message, isSent) {
//   const historyItem = {
//       text: message,
//       timestamp: new Date().toISOString(),
//       isSent: isSent
//   };
  
//   messageHistory.unshift(historyItem);
//   if (messageHistory.length > 100) {
//       messageHistory.pop();
//   }
  
//   localStorage.setItem('messageHistory', JSON.stringify(messageHistory));
//   updateHistoryUI();
// }

// function updateHistoryUI() {
//   const historyList = document.getElementById('history-list');
//   if (!historyList) return;
  
//   historyList.innerHTML = '';
//   messageHistory.forEach(item => {
//       const messageDiv = document.createElement('div');
//       messageDiv.className = `history-message ${item.isSent ? 'sent' : 'received'}`;
//       const time = new Date(item.timestamp).toLocaleTimeString();
//       messageDiv.innerHTML = `
//           <div>${item.text}</div>
//           <span class="time">${time} - ${item.isSent ? 'Sent' : 'Received'}</span>
//       `;
//       historyList.appendChild(messageDiv);
//   });
// }

// // Modified Messaging Functions
// function loadMessages(userId, contactId) {
//   const messagesRef = collection(db, 'private_messages');
//   const q = query(
//       messagesRef,
//       where('participants', 'array-contains', userId),
//       orderBy('timestamp', 'asc')
//   );
  
//   onSnapshot(q, (snapshot) => {
//       const messagesContainer = document.getElementById('messages-container');
//       messagesContainer.innerHTML = '';
      
//       snapshot.forEach(doc => {
//           const msg = doc.data();
//           if ((msg.sender === userId && msg.receiver === contactId) || 
//               (msg.sender === contactId && msg.receiver === userId)) {
//               displayMessage(msg);
              
//               if (msg.sender === contactId) {
//                   saveToHistory(msg.text, false);
//               }
//           }
//       });
//       messagesContainer.scrollTop = messagesContainer.scrollHeight;
//   });
// }

// function displayMessage(msg) {
//   const messagesContainer = document.getElementById('messages-container');
//   const messageDiv = document.createElement('div');
//   messageDiv.className = `message ${msg.sender === currentUserId ? 'sent' : 'received'}`;
  
//   messageDiv.innerHTML = `
//       <div class="message-content">${msg.text}</div>
//       <div class="message-time">${formatTime(msg.timestamp?.toDate())}</div>
//   `;
  
//   messagesContainer.appendChild(messageDiv);
// }

// async function sendMessage() {
//   const input = document.getElementById('message-input');
//   const text = input.value.trim();
  
//   if (text && currentChatId) {
//       try {
//           await addDoc(collection(db, 'private_messages'), {
//               text,
//               sender: currentUserId,
//               receiver: currentChatId,
//               participants: [currentUserId, currentChatId],
//               timestamp: serverTimestamp(),
//               read: false
//            });
          
//           saveToHistory(text, true);
//           input.value = '';
//       } catch (error) {
//           console.error("Error sending message:", error);
//       }
//   }
// }

// // Helper Functions
// function formatTime(date) {
//   return date ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
// }

// // Event Listeners
// document.getElementById('send-button').addEventListener('click', sendMessage);
// document.getElementById('message-input').addEventListener('keypress', (e) => {
//   if (e.key === 'Enter') sendMessage();
// });

// document.getElementById('history-tab')?.addEventListener('click', () => {
//   const historyContainer = document.getElementById('history-container');
//   if (historyContainer) {
//       historyContainer.style.display = historyContainer.style.display === 'block' ? 'none' : 'block';
//       updateHistoryUI();
//   }
// });

// document.getElementById('clear-history')?.addEventListener('click', () => {
//   messageHistory = [];
//   localStorage.removeItem('messageHistory');
//   updateHistoryUI();
// });

// // Audio Recording (keep your existing implementation)
// const wavesurfer = WaveSurfer.create({
//   container: '#waveform',
//   waveColor: '#007bff',
//   progressColor: '#0056b3',
//   height: 90,
//   barWidth: 4,
//   responsive: true
// });

// document.getElementById('record-button').addEventListener('click', handleRecording);

// async function handleRecording() {
//   const recordButton = this;
//   const container = document.getElementById('audio-recording-container');
  
//   if (!recordButton.isRecording) {
//       try {
//           const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//           recordButton.isRecording = true;
//           recordButton.innerHTML = '⏹';
//           container.style.display = 'block';
          
//           const mediaRecorder = new MediaRecorder(stream);
//           let audioChunks = [];
          
//           wavesurfer.load(stream);
          
//           mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
//           mediaRecorder.onstop = () => {
//               const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
//               console.log('Audio enregistré:', audioBlob);
//           };
          
//           mediaRecorder.start();
//           recordButton.mediaRecorder = mediaRecorder;
//           recordButton.stream = stream;
//       } catch (err) {
//           console.error("Erreur microphone:", err);
//           alert("Impossible d'accéder au microphone: " + err.message);
//       }
//   } else {
//       recordButton.isRecording = false;
//       recordButton.innerHTML = '🎤';
//       recordButton.mediaRecorder.stop();
//       recordButton.stream.getTracks().forEach(track => track.stop());
//       wavesurfer.stop();
//   }
// }

import { db } from './firebase.js';

export const createConversation = (participants) => {
  return db.collection('conversations').add({
    participants: participants,
    lastMessage: '',
    lastMessageTime: firebase.firestore.FieldValue.serverTimestamp(),
    unreadCount: {}
  });
};

export const getConversations = (userId, callback) => {
  return db.collection('conversations')
    .where('participants', 'array-contains', userId)
    .orderBy('lastMessageTime', 'desc')
    .onSnapshot(snapshot => {
      const conversations = [];
      snapshot.forEach(doc => {
        conversations.push({ id: doc.id, ...doc.data() });
      });
      callback(conversations);
    });
};