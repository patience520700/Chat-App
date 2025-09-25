// db.js - The "bridge" to MySQL
const mysql = require('mysql2');

// Connection configuration
const pool = mysql.createPool({
    host: 'localhost',      // Where MySQL is located (on your machine)
    user: 'root',           // Your MySQL username
    password: 'Lovenett123', // YOUR MySQL password
    database: 'chat_app',   // Your database name
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

// Allows using async/await (more modern)
const promisePool = pool.promise();

// Export to use elsewhere
module.exports = promisePool;