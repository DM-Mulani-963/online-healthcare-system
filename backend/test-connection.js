const mysql = require('mysql2');

const connection = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '99782@Md'  // Your MySQL password
});

connection.connect((err) => {
    if (err) {
        console.error('Error connecting to MySQL:', err);
        return;
    }
    console.log('Successfully connected to MySQL!');
    
    // Show all databases
    connection.query('SHOW DATABASES', (err, results) => {
        if (err) {
            console.error('Error querying databases:', err);
            return;
        }
        console.log('Available databases:');
        results.forEach(row => {
            console.log(row.Database);
        });
        connection.end();
    });
}); 