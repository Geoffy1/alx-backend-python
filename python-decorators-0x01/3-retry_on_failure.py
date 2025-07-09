import time
import sqlite3
import functools
import logging
from typing import Tuple, Type

logger = logging.getLogger(__name__)

# Re-using the improved with_db_connection from Task 1 (or Task 2, ensuring isolation_level=None)
def with_db_connection(db_path='users.db'):
    """
    Decorator factory that automatically handles opening and closing database connections.
    It passes the connection object as the first argument to the decorated function.
    Args:
        db_path (str): The path to the SQLite database file.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            conn = None
            try:
                conn = sqlite3.connect(db_path)
                conn.isolation_level = None # Allow external transaction management or autocommit for reads
                result = func(conn, *args, **kwargs)
                return result
            except sqlite3.Error as e:
                logger.error(f"Database error in '{func.__name__}': {e}")
                raise
            except Exception as e:
                logger.critical(f"An unexpected error occurred in '{func.__name__}': {e}")
                raise
            finally:
                if conn:
                    conn.close()
                    logger.debug(f"Database connection to {db_path} closed.")
        return wrapper
    return decorator


def retry_on_failure(retries: int = 3, initial_delay: float = 1, backoff_factor: float = 2,
                     exceptions: Tuple[Type[Exception], ...] = (sqlite3.OperationalError,)):
    """
    Decorator factory that retries a function if it raises specified exceptions,
    using exponential backoff.
    Args:
        retries (int): The maximum number of times to retry (excluding the first attempt).
        initial_delay (float): The initial delay in seconds before the first retry.
        backoff_factor (float): Factor by which the delay increases for each subsequent retry.
        exceptions (Tuple[Type[Exception], ...]): A tuple of exception types to catch and retry on.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = initial_delay
            for i in range(retries + 1): # +1 to include the initial attempt
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"Attempt {i+1} of {retries+1} for '{func.__name__}' failed due to: {type(e).__name__}: {e}")
                    if i < retries: # If not the last attempt
                        logger.info(f"Retrying '{func.__name__}' in {current_delay:.2f} seconds...")
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(f"All {retries+1} attempts for '{func.__name__}' failed. Re-raising the last exception.")
                        raise # Re-raise after all retries are exhausted
                except Exception as e:
                    # Catch any other unexpected exceptions immediately
                    logger.error(f"Non-retryable error encountered in '{func.__name__}': {e}")
                    raise
        return wrapper
    return decorator

# Global variable to simulate transient failures for demonstration
_call_count_for_retry_demo = 0

# Example Usage
def setup_database_3():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)", (1, 'Alice', 'alice@example.com'))
    conn.commit()
    conn.close()

@with_db_connection(db_path='users.db')
@retry_on_failure(retries=3, initial_delay=0.5, backoff_factor=2, exceptions=(sqlite3.OperationalError, ValueError))
def fetch_users_with_retry(conn):
    global _call_count_for_retry_demo
    _call_count_for_retry_demo += 1

    if _call_count_for_retry_demo < 3: # Simulate failure for the first 2 calls
        logger.warning(f"Simulating a temporary database error on call {_call_count_for_retry_demo}...")
        # Raise an exception that is in our 'exceptions' tuple for retry
        raise sqlite3.OperationalError("Database is temporarily unavailable.")
    else:
        logger.info(f"Database is available on call {_call_count_for_retry_demo}. Fetching users.")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()

if __name__ == "__main__":
    setup_database_3()
    print("\n--- Task 3: Retry Database Queries (Efficient Output) ---")
    try:
        users = fetch_users_with_retry()
        logger.info(f"Successfully fetched users after retry: {users}")
    except Exception as e:
        logger.error(f"Failed to fetch users after all retries: {e}")

    # Reset for another test, if needed
    _call_count_for_retry_demo = 0
    print("\n--- Testing retry with eventual failure ---")
    @with_db_connection(db_path='users.db')
    @retry_on_failure(retries=2, initial_delay=0.1, exceptions=(sqlite3.OperationalError,))
    def always_fail_query(conn):
        global _call_count_for_retry_demo
        _call_count_for_retry_demo += 1
        logger.info(f"Always failing on call {_call_count_for_retry_demo}...")
        raise sqlite3.OperationalError("Always failing.")

    try:
        always_fail_query()
    except sqlite3.OperationalError:
        logger.info("Caught expected OperationalError after all retries for 'always_fail_query'.")
