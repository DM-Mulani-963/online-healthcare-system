const mysql = require('mysql2/promise');

async function testConnection() {
    const connection = await mysql.createConnection({
        host: 'localhost',
        user: 'root',
        password: '99782@Md',
        database: 'healthcaredb'
    });

    try {
        // Test the connection
        console.log('Connected to MySQL successfully!');

        // Get all tables
        const [tables] = await connection.query('SHOW TABLES');
        console.log('\nTables in healthcaredb:');
        tables.forEach(table => {
            console.log(Object.values(table)[0]);
        });

        // For each table, show its structure
        for (const table of tables) {
            const tableName = Object.values(table)[0];
            const [columns] = await connection.query(`DESCRIBE ${tableName}`);
            console.log(`\nStructure of ${tableName}:`);
            columns.forEach(column => {
                console.log(`${column.Field}: ${column.Type}`);
            });
        }

    } catch (error) {
        console.error('Error:', error);
    } finally {
        await connection.end();
    }
}

testConnection(); 