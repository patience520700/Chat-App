// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBAhMyzijLxn-s-Cmk3EhFPALVMxlwToL8",
  authDomain: "lovenett-28b3f.firebaseapp.com",
  projectId: "lovenett-28b3f",
  storageBucket: "lovenett-28b3f.firebasestorage.app",
  messagingSenderId: "447456050145",
  appId: "1:447456050145:web:16748dbe3f2a9948b330a0",
  measurementId: "G-69GGH6RQG7"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);