# File: python-generators-0x00/0-stream_users.py

import mysql.connector

# Database connection parameters - these should match your setup
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', # Your MySQL username
    'password': '', # Your MySQL password
    'database': 'ALX_prodev'
}
TABLE_NAME = 'user_data'

def stream_users():
    """
    A generator function that streams rows from the 'user_data' table
    one by one, yielding each row as a dictionary.

    The function establishes and closes its own database connection.
    It ensures only one loop is used to fetch data incrementally.
    """
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if not connection.is_connected():
            print("Failed to connect to the database.")
            return # Exit if connection fails

        cursor = connection.cursor(dictionary=True) # Use dictionary=True to fetch rows as dictionaries
        
        # Execute the query
        cursor.execute(f"SELECT user_id, name, email, age FROM {TABLE_NAME}")
        
        # Loop to fetch and yield rows one by one
        while True:
            row = cursor.fetchone()
            if row is None:
                break # No more rows to fetch
            yield row
            
    except mysql.connector.Error as err:
        print(f"Database error during streaming: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure cursor and connection are closed
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            # print("Database connection closed.") # Uncomment for debugging
