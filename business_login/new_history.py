from aifc import Error
from .database.connect import DatabaseConnector  # Ensure proper import

class Userhistory:
    def __init__(self):
        self.connection = None

    def connect(self):
        """ Establish connection to the database """
        db_connector = DatabaseConnector()  # Create an instance of DatabaseConnector
        connection_status, connection_message = db_connector.connect()  # Call connect method on the instance
        
        if connection_status:
            self.connection = db_connector.connection  # Set the connection to self.connection
            print("✅ Database connection is working.")
            return True, "✅ Database connection successful!"
        else:
            print("❌ Database connection failed.")
            return False, connection_message

    def register_download_history(self, video_title, downloaded_by, duration=None, video_link=None, resolution=None, file_size=None, file_type=None):
        """ Register a new video download history entry securely """
        
        # Step 1: Check database connection
        connection_status, connection_message = self.connect()
        if not connection_status:
            return False, connection_message

        # Step 2: Check if the user exists
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (downloaded_by,))
        user = cursor.fetchone()

        if not user:
            return False, f"❌ User with ID {downloaded_by} does not exist!"

        try:
            # Step 3: Insert video download history into the database using parameterized query
            cursor.execute(
                "INSERT INTO video_downloads (video_title, downloaded_by, duration, video_link, resolution, file_size, file_type) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (video_title, downloaded_by, duration, video_link, resolution, file_size, file_type)
            )

            # Commit the changes to the database
            self.connection.commit()
            return True, "✅ Video download history registered successfully!"
        except Error as e:
            return False, f"❌ Error: {e}"

        finally:
            # Step 4: Close the connection after operations
            if self.connection.is_connected():
                cursor.close()
                self.connection.close()
