# File: python-generators-0x00/2-lazy_paginate.py

import sys
# Assuming seed.py is in the same directory or accessible via PYTHONPATH
# A simple way to import from sibling directories in a structured project
# would involve adjusting sys.path, but for this specific task structure,
# direct import based on the main script's context is implied.
# Given the example uses `seed = import('seed')`, we'll follow that convention
# (though direct `import seed` is standard for installed modules).
# For direct execution of this file, we'd need a proper import.

# To make 'import seed' work as in the main scripts,
# we need to ensure the parent directory is in sys.path or use __import__.
# For a clean script that runs independently for testing, we'll import it standardly.
try:
    import seed
except ImportError:
    # If seed.py is not a proper package or in sys.path, you might need to adjust
    # For ALX tasks, often implies modules are side-by-side.
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
        # It's good practice to select specific columns rather than *
        # assuming user_data has user_id, name, email, age
        cursor.execute(f"SELECT user_id, name, email, age FROM user_data LIMIT {page_size} OFFSET {offset}")
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
