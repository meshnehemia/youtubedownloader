import mysql.connector
import bcrypt
import re
from .database.connect import DatabaseConnector

def test_database_connection():
    db_connector = DatabaseConnector()
    connection_status = db_connector.connect()
    db_connector.close()
    return connection_status

class UserRegistration:
    def __init__(self):
        self.connection = None

    def connect(self):
        """ Establish connection to the database """
        db_connector = DatabaseConnector()
        if db_connector.connect():
            self.connection = db_connector.connection  # Set the connection to self.connection
            print("✅ Database connection is working.")
            return True   
        else:
            print("❌ Database connection failed.")
            return False

    def validate_email(self, email):
        """ Validate the email format """
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.match(email_regex, email):
            return True
        return False

    def hash_password(self, password):
        """ Hash the password using bcrypt """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password

    def register_user(self, first_name, last_name, email, password, confirm_password):
        """ Register a new user with secure practices """
        if password != confirm_password:
            print("❌ Passwords do not match!")
            return False , "❌ Passwords do not match!"

        if not self.validate_email(email):
            print("❌ Invalid email format!")
            return False, "❌ Invalid email format!"

        if len(password) < 8:
            print("❌ Password must be at least 8 characters long!")
            return False, "❌ Password must be at least 8 characters long!"

        # Hash the password
        hashed_password = self.hash_password(password)
        try:
            self.connect()
            cursor = self.connection.cursor()

            # Check if the email already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                print("❌ Email already in use!")
                return False, "❌ Email already in use!"

            # Insert new user into the database using parameterized query
            cursor.execute(
                "INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)",
                (first_name, last_name, email, hashed_password)
            )
            self.connection.commit()
            print("✅ User registered successfully!")
            return True, "✅ User registered successfully!"

        except Exception as e:
            print(f"❌ Error: {e}")
            return False, f"❌ Database error: {e}"

    def close(self):
        """ Close the database connection """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 Connection closed.")
