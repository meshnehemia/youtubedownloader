import mysql.connector
import bcrypt
import re
from .database.connect import DatabaseConnector

class UserLogin:
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
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA0-9-.]+$'
        if re.match(email_regex, email):
            return True
        return False

    def check_password(self, stored_password, entered_password):
        """ Check if the entered password matches the stored hashed password """
        return bcrypt.checkpw(entered_password.encode('utf-8'), stored_password.encode('utf-8'))

    def login_user(self, email, password):
        """ Log in the user by checking the email and password """
        self.connect()
        if not self.validate_email(email):
            return False, "❌ Invalid email format!"

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                return False, "❌ No user found with this email!"
            stored_password = user[4] 
            if not self.check_password(stored_password, password):
                return False, "❌ Incorrect password!"

            print("✅ Login successful!")

            # Returning the user information as a dictionary
            user_info = {
                "id": user[0],  # Assuming id is in the 1st column
                "first_name": user[1],  # Assuming first_name is in the 2nd column
                "last_name": user[2],  # Assuming last_name is in the 3rd column
                "email": user[3],  # Assuming email is in the 4th column
                "password": user[4],  # Password is stored as a hash (not for display)
                "date_registered": user[5]  # Assuming date_registered is in the 6th column
            }

            return True, user_info

        except Exception as e:
            print(f"❌ Error: {e}")
            return False, f"❌ Database error: {e}"

    def close(self):
        """ Close the database connection """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 Connection closed.")
