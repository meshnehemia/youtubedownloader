import mysql.connector
from mysql.connector import Error
from connect import DatabaseConnector
def create_database_and_tables():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='meshcloudatabase.cqbq0ewwi0q8.us-east-1.rds.amazonaws.com',
            user='root',
            password='Mesh2254452'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            # Create database if it does not exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS youtubedownloader")
            print("✅ Database 'youtubedownloader' created or already exists.")
            
            # Use the 'construction' database
            cursor.execute("USE youtubedownloader")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ Table 'users' created or already exists.")
            
            # Create video_downloads table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS video_downloads (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    video_title VARCHAR(255) NOT NULL,
                    downloaded_by INT NOT NULL,  -- Foreign key referencing 'users' table
                    duration INT NOT NULL,  -- Duration in seconds
                    video_link TEXT NOT NULL,
                    resolution VARCHAR(50) NOT NULL,
                    file_size INT NOT NULL,  -- File size in bytes
                    file_type VARCHAR(50) NOT NULL,  -- e.g. 'mp4', 'mkv'
                    date_downloaded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (downloaded_by) REFERENCES users(id)  -- Foreign key constraint
                );
            """)
            print("✅ Table 'video_downloads' created or already exists.")
    
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Call the function to create database and tables
create_database_and_tables()
