// Configuration Firebase (à remplacer par la vôtre)
const firebaseConfig = {
  apiKey: "AIzaSyD1234567890abcdefghijklmnopqrstuvwxyz",
  authDomain: "votre-projet.firebaseapp.com",
  projectId: "votre-projet-12345",
  storageBucket: "votre-projet-12345.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef1234567890"
};

// Initialisation Firebase
try {
  firebase.initializeApp(firebaseConfig);
  console.log("Firebase initialisé avec succès");
  
  const auth = firebase.auth();
  const db = firebase.firestore();
  const storage = firebase.storage();
  
  // Vérification que Firestore est bien initialisé
  db.enablePersistence()
    .then(() => console.log("Firestore persistence activée"))
    .catch(err => console.error("Erreur Firestore:", err));
  
} catch (error) {
  console.error("Erreur d'initialisation Firebase:", error);
  alert("Une erreur est survenue lors de l'initialisation de l'application. Veuillez recharger la page.");
}