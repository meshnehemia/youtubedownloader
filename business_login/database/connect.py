import mysql.connector
from mysql.connector import Error

class DatabaseConnector:
    def __init__(self):
        self.host = 'meshcloudatabase.cqbq0ewwi0q8.us-east-1.rds.amazonaws.com'
        self.database = 'youtubedownloader'
        self.user = 'root'
        self.password = 'Mesh2254452'
        self.connection = None
        # self.host = 'localhost'
        # self.database = 'youtubedownloader'
        # self.user = 'root'
        # self.password = ''
        # self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print("✅ Connection successful!")
                return True, "✅ Connection successful!"
            else:
                print("❌ Connection failed!")
                return False, "❌ Connection failed!"
        except Error as e:
            print(f"❌ Connection error: {e}")
            return False, f"❌ Connection error: {e}"

    def close(self):
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("🔒 Connection closed.")
                return True, "🔒 Connection closed."
            else:
                print("⚠️ No active connection to close.")
                return False, "⚠️ No active connection to close."
        except Error as e:
            print(f"❌ Error closing connection: {e}")
            return False, f"❌ Error closing connection: {e}"
