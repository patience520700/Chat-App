
// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBcNUSVuZSIRw2LTbtdugEMt741MhdKe7o",
  authDomain: "lovenett-82e79.firebaseapp.com",
  projectId: "lovenett-82e79",
  storageBucket: "lovenett-82e79.firebasestorage.app",
  messagingSenderId: "599780179872",
  appId: "1:599780179872:web:d5a91746694d7e77a06ec5"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);







  // Variables globales
  let currentChatUser = null;
  let currentUserId = null;
  let conversations = {};
  let currentTab = 'contacts';
  let friendsListener = null;
  let messagesListener = null;

  // Initialisation
  document.addEventListener('DOMContentLoaded', () => {
    // Check if user is authenticated
    auth.onAuthStateChanged((user) => {
      if (user) {
        currentUserId = user.uid;
        loadUserProfile(user);
        loadFriends();
        setupRealTimeListeners();
      } else {
        // Redirect to login if not authenticated
        window.location.href = "forms.html";
      }
    });

    // Profile menu toggle
    const profileMenuBtn = document.getElementById('profileMenuBtn');
    const profileMenu = document.getElementById('profileMenu');
    
    profileMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      profileMenu.classList.toggle('show');
    });
    
    // Close profile menu when clicking outside
    document.addEventListener('click', () => {
      profileMenu.classList.remove('show');
    });
    
    // Profile modal
    const editProfileBtn = document.getElementById('editProfileBtn');
    const profileModal = document.getElementById('profileModal');
    const modalClose = document.getElementById('modalClose');
    const cancelBtn = document.getElementById('cancelBtn');
    const saveProfileBtn = document.getElementById('saveProfileBtn');
    const avatarUploadBtn = document.getElementById('avatarUploadBtn');
    const avatarInput = document.getElementById('avatarInput');
    const avatarPreview = document.getElementById('avatarPreview');
    
    editProfileBtn.addEventListener('click', (e) => {
      e.preventDefault();
      profileModal.classList.add('show');
    });
    
    modalClose.addEventListener('click', () => {
      profileModal.classList.remove('show');
    });
    
    cancelBtn.addEventListener('click', () => {
      profileModal.classList.remove('show');
    });
    
    saveProfileBtn.addEventListener('click', () => {
      const userName = document.getElementById('userName').value;
      const userStatus = document.getElementById('userStatus').value;
      
      // Update profile in Firebase
      db.collection('users').doc(currentUserId).update({
        name: userName,
        status: userStatus,
        lastSeen: firebase.firestore.FieldValue.serverTimestamp()
      }).then(() => {
        document.getElementById('currentUserName').textContent = userName;
        showNotification('Profile updated successfully');
        profileModal.classList.remove('show');
      }).catch((error) => {
        console.error("Error updating profile: ", error);
        showNotification('Error updating profile');
      });
    });
    
    avatarUploadBtn.addEventListener('click', () => {
      avatarInput.click();
    });
    
    avatarInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          avatarPreview.src = event.target.result;
          document.getElementById('currentUserAvatar').src = event.target.result;
          
          // In a real app, you would upload this to Firebase Storage
          // and update the user's profile with the image URL
        };
        reader.readAsDataURL(file);
      }
    });
    
    // Logout functionality
    document.getElementById('logoutBtn').addEventListener('click', (e) => {
      e.preventDefault();
      if (confirm('Are you sure you want to logout?')) {
        auth.signOut().then(() => {
          window.location.href = "forms.html";
        }).catch((error) => {
          console.error("Logout error: ", error);
        });
      }
    });
    
    // Sticker functionality
    const stickerBtn = document.getElementById('stickerBtn');
    const stickerPicker = document.getElementById('stickerPicker');
    
    stickerBtn.addEventListener('click', () => {
      stickerPicker.classList.toggle('show');
    });
    
    // Close sticker picker when clicking outside
    document.addEventListener('click', (e) => {
      if (!stickerBtn.contains(e.target) && !stickerPicker.contains(e.target)) {
        stickerPicker.classList.remove('show');
      }
    });
    
    // Notification functionality
    const notificationClose = document.getElementById('notificationClose');
    
    notificationClose.addEventListener('click', () => {
      document.getElementById('notification').classList.remove('show');
    });
    
    // Tab switching
    document.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentTab = tab.dataset.tab;
        
        if (currentTab === 'discover') {
          loadDiscoverUsers();
          showNotification('Browse and discover new people to connect with');
        } else if (currentTab === 'invitations') {
          loadFriendRequests();
          showNotification('Manage your connection invitations');
        } else if (currentTab === 'contacts') {
          loadFriends();
        }
      });
    });
    
    // Search functionality
    document.getElementById('searchInput').addEventListener('input', (e) => {
      if (e.target.value.length > 2) {
        searchUsers(e.target.value);
      } else {
        loadFriends();
      }
    });
    
    // Send message on Enter key
    document.getElementById('messageInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });
    
    // Send button functionality
    document.getElementById('sendButton').addEventListener('click', sendMessage);
  });

  // Load user profile from Firebase
  function loadUserProfile(user) {
    db.collection('users').doc(user.uid).get().then((doc) => {
      if (doc.exists) {
        const userData = doc.data();
        document.getElementById('currentUserName').textContent = userData.name;
        document.getElementById('userName').value = userData.name;
        document.getElementById('userStatus').value = userData.status || 'Online';
        
        if (userData.avatar) {
          document.getElementById('currentUserAvatar').src = userData.avatar;
          document.getElementById('avatarPreview').src = userData.avatar;
        }
      } else {
        // Create user profile if it doesn't exist
        db.collection('users').doc(user.uid).set({
          name: user.displayName || 'User',
          email: user.email,
          avatar: user.photoURL || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.displayName || 'User')}&background=0062cc&color=fff`,
          status: 'Online',
          lastSeen: firebase.firestore.FieldValue.serverTimestamp(),
          createdAt: firebase.firestore.FieldValue.serverTimestamp()
        });
      }
    }).catch((error) => {
      console.error("Error loading user profile: ", error);
    });
  }

  // Load friends list
  function loadFriends() {
    const contactsList = document.getElementById('contactsList');
    contactsList.innerHTML = '<div class="no-contacts"><i class="fas fa-user-friends"></i><h3>Loading contacts...</h3></div>';
    
    if (friendsListener) {
      friendsListener(); // Remove previous listener
    }
    
    friendsListener = db.collection('friendships')
      .where('users', 'array-contains', currentUserId)
      .where('status', '==', 'accepted')
      .onSnapshot((snapshot) => {
        if (snapshot.empty) {
          contactsList.innerHTML = '<div class="no-contacts"><i class="fas fa-user-friends"></i><h3>No contacts yet</h3><p>Go to the "Discover" tab to find people to add</p></div>';
          return;
        }
        
        contactsList.innerHTML = '';
        snapshot.forEach((doc) => {
          const friendship = doc.data();
          const friendId = friendship.users.find(id => id !== currentUserId);
          
          // Get friend details
          db.collection('users').doc(friendId).get().then((friendDoc) => {
            if (friendDoc.exists) {
              const friendData = friendDoc.data();
              displayFriend(friendData, friendId, contactsList);
            }
          });
        });
      }, (error) => {
        console.error("Error loading friends: ", error);
        contactsList.innerHTML = '<div class="no-contacts"><i class="fas fa-exclamation-triangle"></i><h3>Error loading contacts</h3></div>';
      });
  }

  // Display a friend in the contacts list
  function displayFriend(friendData, friendId, contactsList) {
    const contactElement = document.createElement('div');
    contactElement.className = 'contact';
    contactElement.dataset.userId = friendId;
    
    contactElement.innerHTML = `
      <img class="contact-avatar" src="${friendData.avatar || 'https://ui-avatars.com/api/?name=User&background=0062cc&color=fff'}">
      <div class="contact-info">
        <h4>${friendData.name}</h4>
        <p>${friendData.status || 'Online'}</p>
      </div>
      <div class="contact-time">Now</div>
    `;
    
    contactElement.addEventListener('click', () => {
      openChat(friendData, friendId);
    });
    
    contactsList.appendChild(contactElement);
  }

  // Open chat with a friend
  function openChat(friendData, friendId) {
    currentChatUser = friendId;
    
    // Update chat header
    document.getElementById('chatContactName').textContent = friendData.name;
    document.getElementById('chatContactStatus').textContent = friendData.status || 'Online';
    document.getElementById('chatContactAvatar').src = friendData.avatar || 'https://ui-avatars.com/api/?name=User&background=0062cc&color=fff';
    
    // Show chat area
    document.getElementById('noChatSelected').style.display = 'none';
    document.getElementById('chatInputContainer').style.display = 'flex';
    
    // Clear previous messages
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = '';
    
    // Load messages
    loadMessages(friendId);
  }

  // Load messages for a conversation
  function loadMessages(friendId) {
    // Stop previous listener if exists
    if (messagesListener) {
      messagesListener();
    }
    
    // Generate conversation ID (sorted to ensure consistency)
    const conversationId = [currentUserId, friendId].sort().join('_');
    
    messagesListener = db.collection('messages')
      .where('conversationId', '==', conversationId)
      .orderBy('timestamp', 'asc')
      .onSnapshot((snapshot) => {
        const chatMessages = document.getElementById('chatMessages');
        
        snapshot.docChanges().forEach((change) => {
          if (change.type === 'added') {
            const message = change.doc.data();
            displayMessage(message, message.senderId === currentUserId);
          }
        });
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
      });
  }

  // Send a message
  function sendMessage() {
    if (!currentChatUser) return;
    
    const input = document.getElementById('messageInput');
    const messageContent = input.value.trim();
    
    if (messageContent) {
      // Generate conversation ID
      const conversationId = [currentUserId, currentChatUser].sort().join('_');
      
      const message = {
        content: messageContent,
        senderId: currentUserId,
        receiverId: currentChatUser,
        conversationId: conversationId,
        timestamp: firebase.firestore.FieldValue.serverTimestamp(),
        read: false
      };
      
      // Add message to Firestore
      db.collection('messages').add(message)
        .then(() => {
          input.value = '';
        })
        .catch((error) => {
          console.error("Error sending message: ", error);
          showNotification('Error sending message');
        });
    }
  }

  // Display a message in the chat
  function displayMessage(message, isSent) {
    const chatMessages = document.getElementById('chatMessages');
    
    const time = new Date(message.timestamp?.toDate() || new Date()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${isSent ? 'sent' : 'received'}`;
    
    messageElement.innerHTML = `
      <div class="message-content">
        ${message.content}
        <div class="message-time">${time}</div>
      </div>
    `;
    
    chatMessages.appendChild(messageElement);
    
    // Animate message
    setTimeout(() => {
      messageElement.classList.add('visible');
    }, 10);
  }

  // Load discover users (people you're not friends with)
  function loadDiscoverUsers() {
    const contactsList = document.getElementById('contactsList');
    contactsList.innerHTML = '<div class="no-contacts"><i class="fas fa-search"></i><h3>Finding people...</h3></div>';
    
    // Get all users except current user and friends
    db.collection('users')
      .where('__name__', '!=', currentUserId)
      .limit(20)
      .get()
      .then((snapshot) => {
        if (snapshot.empty) {
          contactsList.innerHTML = '<div class="no-contacts"><i class="fas fa-user-friends"></i><h3>No users found</h3></div>';
          return;
        }
        
        contactsList.innerHTML = '';
        snapshot.forEach((doc) => {
          const userData = doc.data();
          const userId = doc.id;
          
          // Check if already friends or request sent
          checkFriendshipStatus(userId).then((status) => {
            if (status === 'none') {
              displayDiscoverUser(userData, userId, contactsList);
            }
          });
        });
      })
      .catch((error) => {
        console.error("Error loading discover users: ", error);
        contactsList.innerHTML = '<div class="no-contacts"><i class="fas fa-exclamation-triangle"></i><h3>Error loading users</h3></div>';
      });
  }

  // Check friendship status between current user and another user
  function checkFriendshipStatus(otherUserId) {
    return db.collection('friendships')
      .where('users', 'array-contains', currentUserId)
      .get()
      .then((snapshot) => {
        let status = 'none';
        
        snapshot.forEach((doc) => {
          const friendship = doc.data();
          if (friendship.users.includes(otherUserId)) {
            status = friendship.status;
          }
        });
        
        return status;
      });
  }

  // Display a user in the discover list
  function displayDiscoverUser(userData, userId, contactsList) {
    const contactElement = document.createElement('div');
    contactElement.className = 'contact';
    
    contactElement.innerHTML = `
      <img class="contact-avatar" src="${userData.avatar || 'https://ui-avatars.com/api/?name=User&background=0062cc&color=fff'}">
      <div class="contact-info">
        <h4>${userData.name}</h4>
        <p>${userData.status || 'Click to send friend request'}</p>
      </div>
      <button class="add-friend-btn" data-user-id="${userId}">
        <i class="fas fa-user-plus"></i>
      </button>
    `;
    
    const addButton = contactElement.querySelector('.add-friend-btn');
    addButton.addEventListener('click', (e) => {
      e.stopPropagation();
      sendFriendRequest(userId);
    });
    
    contactsList.appendChild(contactElement);
  }

  // Send a friend request
  function sendFriendRequest(friendId) {
    // Create a friendship document
    const friendshipId = [currentUserId, friendId].sort().join('_');
    
    db.collection('friendships').doc(friendshipId).set({
      users: [currentUserId, friendId],
      status: 'pending',
      requestedBy: currentUserId,
      createdAt: firebase.firestore.FieldValue.serverTimestamp()
    })
    .then(() => {
      showNotification('Friend request sent');
    })
    .catch((error) => {
      console.error("Error sending friend request: ", error);
      showNotification('Error sending friend request');
    });
  }

  // Load friend requests
  function loadFriendRequests() {
    const contactsList = document.getElementById('contactsList');
    contactsList.innerHTML = '<div class="no-contacts"><i class="fas fa-envelope"></i><h3>Loading requests...</h3></div>';
    
    db.collection('friendships')
      .where('users', 'array-contains', currentUserId)
      .where('status', '==', 'pending')
      .where('requestedBy', '!=', currentUserId)
      .get()
      .then((snapshot) => {
        if (snapshot.empty) {
          contactsList.innerHTML = '<div class="no-contacts"><i class="fas fa-envelope-open"></i><h3>No pending requests</h3></div>';
          return;
        }
        
        contactsList.innerHTML = '';
        snapshot.forEach((doc) => {
          const friendship = doc.data();
          const requesterId = friendship.requestedBy;
          
          // Get requester details
          db.collection('users').doc(requesterId).get().then((userDoc) => {
            if (userDoc.exists) {
              const userData = userDoc.data();
              displayFriendRequest(userData, requesterId, doc.id, contactsList);
            }
          });
        });
      })
      .catch((error) => {
        console.error("Error loading friend requests: ", error);
        contactsList.innerHTML = '<div class="no-contacts"><i class="fas fa-exclamation-triangle"></i><h3>Error loading requests</h3></div>';
      });
  }

  // Display a friend request
  function displayFriendRequest(userData, userId, friendshipId, contactsList) {
    const contactElement = document.createElement('div');
    contactElement.className = 'contact';
    
    contactElement.innerHTML = `
      <img class="contact-avatar" src="${userData.avatar || 'https://ui-avatars.com/api/?name=User&background=0062cc&color=fff'}">
      <div class="contact-info">
        <h4>${userData.name}</h4>
        <p>Wants to be your friend</p>
      </div>
      <div class="request-actions">
        <button class="accept-btn" data-friendship-id="${friendshipId}">
          <i class="fas fa-check"></i>
        </button>
        <button class="reject-btn" data-friendship-id="${friendshipId}">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;
    
    const acceptBtn = contactElement.querySelector('.accept-btn');
    const rejectBtn = contactElement.querySelector('.reject-btn');
    
    acceptBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      respondToFriendRequest(friendshipId, 'accepted');
    });
    
    rejectBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      respondToFriendRequest(friendshipId, 'rejected');
    });
    
    contactsList.appendChild(contactElement);
  }

  // Respond to a friend request
  function respondToFriendRequest(friendshipId, response) {
    db.collection('friendships').doc(friendshipId).update({
      status: response,
      respondedAt: firebase.firestore.FieldValue.serverTimestamp()
    })
    .then(() => {
      showNotification(`Friend request ${response}`);
      loadFriendRequests(); // Reload the list
    })
    .catch((error) => {
      console.error(`Error ${response} friend request: `, error);
      showNotification(`Error ${response} friend request`);
    });
  }

  // Search users
  function searchUsers(query) {
    const contactsList = document.getElementById('contactsList');
    contactsList.innerHTML = '<div class="no-contacts"><i class="fas fa-search"></i><h3>Searching...</h3></div>';
    
    db.collection('users')
      .where('name', '>=', query)
      .where('name', '<=', query + '\uf8ff')
      .limit(10)
      .get()
      .then((snapshot) => {
        if (snapshot.empty) {
          contactsList.innerHTML = '<div class="no-contacts"><i class="fas fa-search"></i><h3>No users found</h3></div>';
          return;
        }
        
        contactsList.innerHTML = '';
        snapshot.forEach((doc) => {
          if (doc.id !== currentUserId) {
            const userData = doc.data();
            displayFriend(userData, doc.id, contactsList);
          }
        });
      })
      .catch((error) => {
        console.error("Error searching users: ", error);
        contactsList.innerHTML = '<div class="no-contacts"><i class="fas fa-exclamation-triangle"></i><h3>Error searching</h3></div>';
      });
  }

  // Setup real-time listeners for notifications
  function setupRealTimeListeners() {
    // Listen for new friend requests
    db.collection('friendships')
      .where('users', 'array-contains', currentUserId)
      .where('status', '==', 'pending')
      .where('requestedBy', '!=', currentUserId)
      .onSnapshot((snapshot) => {
        snapshot.docChanges().forEach((change) => {
          if (change.type === 'added') {
            const friendship = change.doc.data();
            const requesterId = friendship.requestedBy;
            
            // Get requester name
            db.collection('users').doc(requesterId).get().then((userDoc) => {
              if (userDoc.exists) {
                const userData = userDoc.data();
                showNotification(`${userData.name} sent you a friend request`);
              }
            });
          }
        });
      });
    
    // Listen for new messages
    db.collection('messages')
      .where('receiverId', '==', currentUserId)
      .where('read', '==', false)
      .onSnapshot((snapshot) => {
        snapshot.docChanges().forEach((change) => {
          if (change.type === 'added') {
            const message = change.doc.data();
            
            // Get sender name
            db.collection('users').doc(message.senderId).get().then((userDoc) => {
              if (userDoc.exists) {
                const userData = userDoc.data();
                
                // Only show notification if not in the current chat
                if (message.senderId !== currentChatUser) {
                  showNotification(`New message from ${userData.name}`);
                }
                
                // Mark as read if in the current chat
                if (message.senderId === currentChatUser) {
                  change.doc.ref.update({ read: true });
                }
              }
            });
          }
        });
      });
  }

  function addSticker(sticker) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = sticker;
    stickerPicker.classList.remove('show');
    sendMessage();
  }

  function showNotification(message) {
    const notification = document.getElementById('notification');
    const notificationContent = document.getElementById('notificationContent');
    
    notificationContent.textContent = message;
    notification.classList.add('show');
    
    // Hide automatically after 3 seconds
    setTimeout(() => {
      notification.classList.remove('show');
    }, 3000);
  }
