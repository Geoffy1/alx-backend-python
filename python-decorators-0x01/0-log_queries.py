import sqlite3
import functools
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_queries(func):
    """
    Decorator to log SQL queries executed by a function using the logging module.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = None
        # Attempt to find the query string from args or kwargs.
        # This assumes the query is either the first positional argument
        # or explicitly named 'query'. Adapt as needed for other function signatures.
        if args and isinstance(args[0], str) and ("SELECT" in args[0].upper() or "INSERT" in args[0].upper() or "UPDATE" in args[0].upper() or "DELETE" in args[0].upper()):
            query = args[0]
        elif 'query' in kwargs and isinstance(kwargs['query'], str):
            query = kwargs['query']

        if query:
            logger.info(f"Executing SQL query: {query}")
        else:
            logger.info(f"Executing a database operation ({func.__name__}); query not explicitly found.")

        return func(*args, **kwargs)
    return wrapper

# Example Usage (with a setup function for a clean test environment)
def setup_database_0():
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

@log_queries
def fetch_user_data(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    setup_database_0()
    print("\n--- Task 0: Logging Database Queries (Efficient Output) ---")
    users = fetch_user_data(query="SELECT * FROM users WHERE id = 1")
    logger.info(f"Fetched user: {users}")
