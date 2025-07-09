import sqlite3
import functools
import logging

logger = logging.getLogger(__name__)

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
                conn.isolation_level = None # Autocommit mode for simple reads, or handled by transactional decorator
                result = func(conn, *args, **kwargs)
                return result
            except sqlite3.Error as e:
                logger.error(f"Database error in '{func.__name__}': {e}")
                raise # Re-raise the original database exception
            except Exception as e:
                logger.critical(f"An unexpected error occurred in '{func.__name__}': {e}")
                raise # Re-raise any other unexpected exceptions
            finally:
                if conn:
                    conn.close()
                    logger.debug(f"Database connection to {db_path} closed.")
        return wrapper
    return decorator

# Example Usage
def setup_database_1():
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
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

if __name__ == "__main__":
    setup_database_1()
    print("\n--- Task 1: Handle Database Connections (Efficient Output) ---")
    user = get_user_by_id(user_id=1)
    logger.info(f"Fetched user by ID 1: {user}")

    user_none = get_user_by_id(user_id=99)
    logger.info(f"Fetched user by ID 99: {user_none}")
