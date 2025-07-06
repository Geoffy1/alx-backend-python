# File: python-generators-0x00/1-batch_processing.py

import mysql.connector

# Database connection parameters - these should match your setup
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', # Your MySQL username
    'password': '', # Your MySQL password
    'database': 'ALX_prodev'
}
TABLE_NAME = 'user_data'

def stream_users_in_batches(batch_size):
    """
    Generator function that fetches rows from the 'user_data' table
    in specified batch sizes.

    Yields a list of user dictionaries for each batch.
    Uses one loop.
    """
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if not connection.is_connected():
            print("Failed to connect to the database for batch streaming.")
            return

        cursor = connection.cursor(dictionary=True, buffered=False) # Use dictionary=True for dict rows
        cursor.execute(f"SELECT user_id, name, email, age FROM {TABLE_NAME}")

        # Loop 1: Continually fetch batches until no more rows
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch: # If batch is empty, no more rows
                break
            yield batch
            
    except mysql.connector.Error as err:
        print(f"Database error during batch streaming: {err}")
    except Exception as e:
        print(f"An unexpected error occurred during batch streaming: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def batch_processing(batch_size):
    """
    Generator function that processes users in batches.
    It fetches batches using stream_users_in_batches,
    then filters users older than 25 within each batch.

    Yields individual user dictionaries that meet the criteria.
    Uses two internal loops (one for batches, one for users within batch),
    plus the loop from stream_users_in_batches, totaling 3 loops.
    """
    # Loop 2: Iterate over batches provided by the generator
    for batch in stream_users_in_batches(batch_size):
        # Loop 3: Iterate over users within the current batch
        for user in batch:
            if user['age'] > 25:
                yield user
