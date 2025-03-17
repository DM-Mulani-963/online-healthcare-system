from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

def test_connection():
    try:
        # Create Flask app
        app = Flask(__name__)
        
        # Configure database with encoded password
        password = quote_plus('99782@Md')  # URL encode the password
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{password}@127.0.0.1:3306/healthcare_db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize SQLAlchemy
        db = SQLAlchemy(app)
        
        with app.app_context():
            # Try to query the database
            result = db.session.execute(text('SELECT 1'))
            print("Database connection successful!")
            
            # Print all tables
            result = db.session.execute(text('SHOW TABLES'))
            print("\nAvailable tables:")
            for table in result:
                print(f"- {table[0]}")
                
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")

if __name__ == "__main__":
    test_connection() 