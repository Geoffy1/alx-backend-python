import time
import sqlite3
import functools
import logging

logger = logging.getLogger(__name__)

# Re-using the improved with_db_connection from Task 1 (or Task 2/3)
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


# Using functools.lru_cache for efficient caching
def cache_query(maxsize: int = 128, typed: bool = False):
    """
    Decorator factory that caches query results based on the SQL query string
    and other arguments, using functools.lru_cache.
    Args:
        maxsize (int): The maximum number of most recent calls to cache.
        typed (bool): If True, arguments of different types will be cached separately.
    """
    def decorator(func):
        @functools.lru_cache(maxsize=maxsize, typed=typed)
        @functools.wraps(func) # Use wraps here to preserve metadata after lru_cache
        def wrapper(conn, query, *args, **kwargs):
            # lru_cache expects a hashable key for caching.
            # We'll pass the query and any other relevant hashable args.
            # Note: The 'conn' object is NOT hashable, so it cannot be part of the cache key.
            # The lru_cache is applied directly to the function that *receives* the hashable args.
            
            # This print will only show when the actual database call is made, not from cache hits.
            logger.info(f"Executing query and caching result: {query} (Args: {args}, Kwargs: {kwargs})")
            
            # Execute the original function (which will interact with the DB via 'conn')
            result = func(conn, query, *args, **kwargs)
            return result
        return wrapper
    return decorator

# Example Usage
def setup_database_4():
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
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)", (2, 'Bob', 'bob@example.com'))
    conn.commit()
    conn.close()

@with_db_connection(db_path='users.db')
@cache_query(maxsize=128) # Apply the cache decorator
def fetch_users_with_cache(conn, query, user_id=None):
    """
    Fetches users from the database.
    Simulates a time-consuming query to demonstrate caching.
    """
    cursor = conn.cursor()
    if user_id:
        cursor.execute(query, (user_id,))
    else:
        cursor.execute(query)
    time.sleep(0.1) # Simulate some processing time
    return cursor.fetchall()


if __name__ == "__main__":
    setup_database_4()
    print("\n--- Task 4: Cache Database Queries (Efficient Output) ---")

    logger.info("First call for 'SELECT * FROM users':")
    start_time = time.time()
    users1 = fetch_users_with_cache(query="SELECT * FROM users")
    end_time = time.time()
    logger.info(f"Users 1: {users1}")
    logger.info(f"Time taken for first call: {end_time - start_time:.4f} seconds")

    logger.info("\nSecond call for 'SELECT * FROM users' (should be cached):")
    start_time = time.time()
    users2 = fetch_users_with_cache(query="SELECT * FROM users")
    end_time = time.time()
    logger.info(f"Users 2: {users2}")
    logger.info(f"Time taken for second call: {end_time - start_time:.4f} seconds") # Should be much faster

    logger.info("\nThird call with a different query 'SELECT name FROM users WHERE id = ?' (should not be cached initially):")
    start_time = time.time()
    users3 = fetch_users_with_cache(query="SELECT name FROM users WHERE id = ?", user_id=1)
    end_time = time.time()
    logger.info(f"Users 3: {users3}")
    logger.info(f"Time taken for third call: {end_time - start_time:.4f} seconds")

    logger.info("\nFourth call with the different query (should be cached now):")
    start_time = time.time()
    users4 = fetch_users_with_cache(query="SELECT name FROM users WHERE id = ?", user_id=1)
    end_time = time.time()
    logger.info(f"Users 4: {users4}")
    logger.info(f"Time taken for fourth call: {end_time - start_time:.4f} seconds") # Should be much faster

    logger.info("\nInspecting cache stats:")
    logger.info(fetch_users_with_cache.cache_info())
