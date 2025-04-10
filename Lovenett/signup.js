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