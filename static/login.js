document.addEventListener('DOMContentLoaded', () => {
    // Initialisation du stockage
    initUserStorage();
    
    // Gestion de la connexion
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // Gestion de l'inscription
    document.getElementById('signupForm').addEventListener('submit', handleSignup);
});

function initUserStorage() {
    if (!localStorage.getItem('registeredUsers')) {
        localStorage.setItem('registeredUsers', JSON.stringify([]));
    }
    if (!localStorage.getItem('conversations')) {
        localStorage.setItem('conversations', JSON.stringify([]));
    }
}

function handleLogin(e) {
    e.preventDefault();
    
    const email = document.querySelector('#loginForm input[type="email"]').value;
    const password = document.querySelector('#loginForm input[type="password"]').value;
    
    const users = JSON.parse(localStorage.getItem('registeredUsers'));
    const user = users.find(u => u.email === email && u.password === password);
    
    if (user) {
        localStorage.setItem('currentUser', JSON.stringify(user));
        window.location.href = 'chat.html';
    } else {
        showError('Email ou mot de passe incorrect');
    }
}

function handleSignup(e) {
    e.preventDefault();
    
    // Validation
    if (document.getElementById('password').value !== document.getElementById('confirm-password').value) {
        alert('Les mots de passe ne correspondent pas!');
        return;
    }
    
    // Création utilisateur
    const newUser = {
        id: Date.now().toString(),
        username: document.getElementById('register-username').value,
        email: document.getElementById('email').value,
        gender: document.getElementById('gender').value,
        country: document.getElementById('country').value,
        phone: document.getElementById('phone').value,
        birthdate: document.getElementById('register-birthdate').value,
        password: document.getElementById('password').value,
        avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(document.getElementById('register-username').value)}&background=random`,
        verified: false,
        lastSeen: new Date().toISOString()
    };
    
    // Sauvegarde
    const users = JSON.parse(localStorage.getItem('registeredUsers'));
    users.push(newUser);
    localStorage.setItem('registeredUsers', JSON.stringify(users));
    
    // Soumission FormSubmit
    e.target.submit();
    alert('Inscription réussie! Un email de confirmation a été envoyé.');
}

function showError(message) {
    const existingError = document.querySelector('.login-error');
    if (existingError) existingError.remove();
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'login-error';
    errorDiv.textContent = message;
    
    const submitButton = document.querySelector('#loginForm .button');
    submitButton.parentNode.insertBefore(errorDiv, submitButton);
}