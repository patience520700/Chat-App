import { getAuth, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.0.0/firebase-auth.js";
import { getFirestore, collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.0.0/firebase-firestore.js";

const auth = getAuth();
const db = getFirestore();

// Sign-Up Form Submission
const signupForm = document.getElementById('signup-form');
if (signupForm) {
  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get form inputs
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const fullName = document.getElementById('fullname').value;
    const phone = document.getElementById('phone').value;

    // Basic validation
    if (!email || !password || !fullName || !phone) {
      alert('Please fill in all fields.');
      return;
    }

    try {
      // Create user with Firebase Authentication
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      // Save additional user data to Firestore
      await addDoc(collection(db, 'users'), {
        uid: user.uid, // Unique ID from Firebase Authentication
        email: user.email, // User's email
        fullName: fullName, // Full name from the form
        phone: phone, // Phone number from the form
        createdAt: serverTimestamp(), // Timestamp of when the user was created
      });

      alert('Sign-up successful!');
      window.location.href = 'chat.html'; // Redirect to chat page
    } catch (error) {
      console.error('Error during sign-up:', error);
      alert(`Sign-up failed: ${error.message}`);
    }
  });
}

// Countries Data
const countries = [
  "Australia",  "Brazil", "Canada", "China", "France", "Germany", "India",  "Italy",  "Japan", "Mexico", "Netherlands",  "Russia", "South Korea", "Spain", "Switzerland", "United Kingdom", "United States",   
];

// Handle Google Sign-In
function handleGoogleSignIn(response) {
  // Decode the JWT token to get user info
  const payload = JSON.parse(atob(response.credential.split('.')[1]));
  
  console.log('Google user:', payload);
  
  // You can now use this data to:
  // 1. Auto-fill your form
  document.getElementById('register-username').value = payload.name || '';
  document.getElementById('email').value = payload.email || '';
  
  // 2. Or submit directly to your backend
  fetch('/api/auth/google', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({
          token: response.credential,
          username: payload.name,
          email: payload.email
      })
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          window.location.href = '/dashboard'; // Redirect on success
      }
  })
  .catch(error => {
      console.error('Error:', error);
  });
}