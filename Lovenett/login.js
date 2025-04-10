// Add event listener to the login form
document.getElementById('login-form').addEventListener('submit', function(event) {
    // Prevent the default form submission
    event.preventDefault();
    
    // Get form inputs
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    // Basic validation (optional)
    if (!email || !password) {
        alert('Please fill in all fields.');
        return;
    }
    
    // Simulate a successful login (replace with actual authentication logic)
    console.log('Logging in with:', email, password);
    
    // Redirect to the chat page (e.g., chat.html)
    window.location.href = 'chat.html';
    });