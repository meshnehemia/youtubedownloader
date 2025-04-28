import mysql.connector
from mysql.connector import Error
from .database.connect import DatabaseConnector
class UserHistory:
    def __init__(self):
        self.connection = None
    def connect(self):
        """ Establish connection to the database """
        db_connector = DatabaseConnector()
        connection_status, connection_message = db_connector.connect()
        if connection_status:
            self.connection = db_connector.connection  # Set the connection to self.connection
            print("✅ Database connection is working.")
            return True, "✅ Database connection successful!"
        else:
            print("❌ Database connection failed.")
            return False, connection_message
    def get_download_history(self, user_id):
        """ Retrieve all download history for a specific user """
        # Step 1: Check database connection
        connection_status, connection_message = self.connect()
        if not connection_status:
            return False, connection_message

        try:
            cursor = self.connection.cursor()
            # Step 2: Retrieve all download history for the user
            cursor.execute(
                "SELECT * FROM video_downloads AS d INNER JOIN users u ON d.downloaded_by = u.id WHERE d.downloaded_by = %s;",
                (user_id,)
            )
            download_history = cursor.fetchall()

            if not download_history:
                return False, f"❌ No download history found for user ID {user_id}."
            # Step 3: Format and return the results
            history_list = []
            for record in download_history:
                history_list.append({
                    'video_title': record[1],
                    'downloaded_by': record[10] + " " + record[11],
                    'duration': record[3],
                    'video_link': record[4],
                    'resolution': record[5],
                    'file_size': record[6],
                    'file_type': record[7],
                    'date_downloaded': record[8],
                    'email': record[12]
                })
            return True, history_list
        except Error as e:
            return False, f"❌ Error: {e}"
        finally:
            # Step 4: Close the connection after operations
            if self.connection.is_connected():
                cursor.close()
                self.connection.close()

