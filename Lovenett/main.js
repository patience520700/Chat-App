import { initAuth, loginUser, registerUser, logoutUser } from './auth.js';
import { getConversations, createConversation } from './chat.js';
import { getMessages, sendMessage } from './message.js';
import { getUserProfile } from './user.js';

// Variables globales
let currentUser = null;
let currentChatId = null;

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
  // Gestion de l'authentification
  initAuth(
    (user) => { // onAuthSuccess
      currentUser = user;
      setupChatUI();
      loadUserData();
    },
    () => { // onAuthFailure
      showLoginScreen();
    }
  );

  // Écouteurs d'événements
  setupEventListeners();
});

function setupChatUI() {
  // Cacher l'écran de login, montrer le chat
  document.getElementById('auth-container').style.display = 'none';
  document.getElementById('chat-container').style.display = 'flex';

  // Charger les conversations
  getConversations(currentUser.uid, (conversations) => {
    updateContactsList(conversations);
  });
}

function loadUserData() {
  getUserProfile(currentUser.uid).then(profile => {
    if (profile) {
      document.getElementById('profile-icon').textContent = profile.name.charAt(0);
      document.getElementById('app-name').textContent = `Hi, ${profile.name}! 💞`;
    }
  });
}

function setupEventListeners() {
  // Bouton d'envoi de message
  document.getElementById('send-button').addEventListener('click', () => {
    const input = document.getElementById('message-input');
    if (currentChatId && input.value.trim()) {
      sendMessage(currentChatId, currentUser.uid, input.value.trim());
      input.value = '';
    }
  });

  // ... (vos autres écouteurs existants)
}

// ... (vos fonctions existantes comme updateContactsList, displayMessage, etc.)