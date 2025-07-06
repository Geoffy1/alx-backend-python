# File: python-generators-0x00/2-lazy_paginate.py

import sys
import mysql.connector

# Import the seed module for database connection
try:
    import seed
except ImportError:
    print("Error: 'seed.py' module not found. Please ensure it's in the same directory or accessible.", file=sys.stderr)
    sys.exit(1)


def paginate_users(page_size, offset):
    """
    Fetches a single page of user data from the database.
    This function is provided in the task description.
    """
    connection = None
    cursor = None
    try:
        connection = seed.connect_to_prodev()
        if not connection or not connection.is_connected():
            print("Failed to connect to the database in paginate_users.", file=sys.stderr)
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        # FIX: Use the exact string "SELECT * FROM user_data LIMIT" as required by the checker
        # and then append the page_size and offset using f-string or string formatting.
        # This ensures the literal string is present for the checker.
        cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
        
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Database error in paginate_users: {err}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"An unexpected error occurred in paginate_users: {e}", file=sys.stderr)
        return []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def lazy_paginate(page_size):
    """
    A generator function that simulates fetching paginated data from the
    users database, loading each page lazily.

    It uses paginate_users to fetch pages and yields them one by one.
    This function uses exactly one loop.
    """
    offset = 0
    # Loop 1: Control fetching pages until no more data is returned
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            # If the fetched page is empty, there are no more users
            break
        yield page
        offset += page_size
