import pymysql

def test_mysql_connection():
    try:
        # Connect to MySQL
        connection = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='99782@Md',  # Replace with your MySQL root password
            port=3306
        )
        
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS healthcare_db")
        print("Database 'healthcare_db' created or already exists")
        
        # Switch to the database
        cursor.execute("USE healthcare_db")
        print("Using database: healthcare_db")
        
        # Show tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("\nExisting tables:")
        for table in tables:
            print(f"- {table[0]}")
            
        cursor.close()
        connection.close()
        print("\nMySQL connection test successful!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_mysql_connection() 