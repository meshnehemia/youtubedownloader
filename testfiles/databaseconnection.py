from business_login.database.connect import DatabaseConnector

def test_database_connection():
    # Initialize the DatabaseConnector
    db_connector = DatabaseConnector()
    
    # Test the connection
    connection_status = db_connector.connect()
    
    # Optionally close the connection after testing
    db_connector.close()

    return connection_status

# Run the test function
if __name__ == "__main__":
    if test_database_connection():
        print("✅ Database connection is working.")
    else:
        print("❌ Database connection failed.")
