# File: python-generators-0x00/4-stream_ages.py

import sys
import mysql.connector

# Import the seed module for database connection
try:
    import seed
except ImportError:
    print("Error: 'seed.py' module not found. Please ensure it's in the same directory or accessible.", file=sys.stderr)
    sys.exit(1)

TABLE_NAME = 'user_data'

def stream_user_ages():
    """
    A generator function that streams user ages one by one from the
    'user_data' table in the database.

    Uses one loop to fetch data incrementally.
    Yields each user's age as a numeric value.
    """
    connection = None
    cursor = None
    try:
        connection = seed.connect_to_prodev()
        if not connection or not connection.is_connected():
            print("Failed to connect to the database for streaming ages.", file=sys.stderr)
            return # Generator stops if connection fails

        cursor = connection.cursor(dictionary=True) # Fetch rows as dictionaries to easily access 'age' by name
        cursor.execute(f"SELECT age FROM {TABLE_NAME}")
        
        # Loop 1: Fetch and yield ages one by one
        while True:
            row = cursor.fetchone()
            if row is None:
                break # No more rows
            yield float(row['age']) # Yield age as float for calculation
            
    except mysql.connector.Error as err:
        print(f"Database error during age streaming: {err}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during age streaming: {e}", file=sys.stderr)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def calculate_average_age():
    """
    Calculates the average age of users by streaming ages using a generator,
    thus avoiding loading the entire dataset into memory.

    Uses one loop to iterate over the streamed ages.
    """
    total_age = 0
    user_count = 0

    # Loop 2: Iterate over the ages yielded by the generator
    for age in stream_user_ages():
        total_age += age
        user_count += 1
    
    if user_count > 0:
        average_age = total_age / user_count
        print(f"Average age of users: {average_age:.2f}") # Format to 2 decimal places
    else:
        print("No users found to calculate average age.")

if __name__ == "__main__":
    calculate_average_age()
