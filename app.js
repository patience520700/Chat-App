// app.js - Your main application
const express = require('express');
const pool = require('./db'); // Import the connection

const app = express();
app.use(express.json());

// Route to get all users
app.get('/users', async (req, res) => {
    try {
        const [users] = await pool.execute('SELECT * FROM user');
        res.json(users);
    } catch (error) {
        console.error('Error:', error);
        res.status(500).send('Server error');
    }
});

// Start the server
app.listen(3000, () => {
    console.log('Server started on port 3000');
});