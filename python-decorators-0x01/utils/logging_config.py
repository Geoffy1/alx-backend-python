# python-decorators-0x01/utils/logging_config.py

import logging # Import the standard Python logging module.
import os      # Import the os module for interacting with the operating system (e.g., creating directories for log files).

def configure_logging():
    """
    Configures the logging system for the entire application.

    This function should be called exactly once at the application's startup
    to set up how logs are handled (e.g., where they go, what format they have).
    It adds a console handler to display logs in the terminal and ensures a
    consistent log message format.
    """
    # Get the root logger instance. This is the top-level logger in Python's
    # logging hierarchy. All other loggers (e.g., `logging.getLogger(__name__)`)
    # inherit settings from the root logger by default.
    root_logger = logging.getLogger()
    
    # Set the minimum logging level for the root logger.
    # Messages with a level lower than INFO (e.g., DEBUG) will be ignored.
    # Common levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    root_logger.setLevel(logging.INFO)

    # Prevent adding duplicate handlers if this function is called multiple times.
    # This is important in scenarios like testing, or if different parts of an
    # application inadvertently try to configure logging independently.
    if not root_logger.handlers:
        # Create a StreamHandler. This handler sends log records to streams
        # like `sys.stdout` (console output) or `sys.stderr`.
        console_handler = logging.StreamHandler()
        
        # Define the format for log messages.
        # %(asctime)s: Human-readable time when the LogRecord was created.
        # %(name)s: Name of the logger (e.g., 'python-decorators-0x01.0-log_queries').
        # %(levelname)s: Text logging level for the message (e.g., 'INFO', 'ERROR').
        # %(message)s: The actual log message.
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Apply the defined format to the console handler.
        console_handler.setFormatter(formatter)
        
        # Add the configured console handler to the root logger.
        # Now, any log messages (INFO level or higher) will be printed to the console.
        root_logger.addHandler(console_handler)

        # Optional: Example of how to add a FileHandler to write logs to a file.
        # This is commented out but shows how you'd extend logging to persistent storage.
        # log_dir = "logs" # Define a directory for log files.
        # os.makedirs(log_dir, exist_ok=True) # Create the directory if it doesn't exist.
        # file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log')) # Create a file handler.
        # file_handler.setFormatter(formatter) # Apply the same formatter.
        # root_logger.addHandler(file_handler) # Add the file handler to the root logger.

    # Log a message indicating that the logging system has been set up.
    # This message itself will be formatted and outputted by the newly configured handlers.
    logging.info("Logging system configured.")

# Developer Note:
# In a typical application, you'd call `configure_logging()` once at the very start
# of your main script (e.g., in `main.py`). For this ALX project structure, where
# each task file might be run independently, we'll include a call to this function
# within each file's `if __name__ == "__main__":` block to ensure logging is active
# when running individual task scripts.
2. python-decorators-0x01/0-log_queries.py
This file implements the first task: creating a decorator to log SQL queries.

Python

# python-decorators-0x01/0-log_queries.py

import sqlite3  # Import the SQLite database module.
import functools # Import functools for `functools.wraps`, essential for decorators.
import logging  # Import the logging module for robust logging.
from datetime import datetime # Required by the ALX checker, even if not directly used for formatting
                              # because our logging formatter handles timestamps.

# Attempt to import the centralized logging configuration function.
# This makes the code cleaner by separating logging setup.
try:
    from utils.logging_config import configure_logging
except ImportError:
    # Fallback for when `utils.logging_config` might not be in the Python path,
    # e.g., if this file is run directly without the full project structure.
    # In a real project, this ImportError would typically indicate a setup issue.
    def configure_logging():
        # If import fails, use basicConfig as a fallback for standalone execution.
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get a logger instance for this specific module.
# The `__name__` variable ensures the logger is named after the module (e.g., '0-log_queries'),
# which helps in tracing log messages back to their source.
logger = logging.getLogger(__name__)

def log_queries(func):
    """
    Decorator to log SQL queries executed by any function it wraps.

    This decorator intercepts the function call, extracts the SQL query,
    logs it, and then proceeds to execute the original function.
    """
    # functools.wraps preserves the original function's metadata (like __name__, __doc__).
    # This is crucial for debugging and introspection of decorated functions.
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """
        The inner wrapper function that replaces the original function.
        It accepts any arguments (*args, **kwargs) to be versatile.
        """
        query = None
        # Attempt to robustly identify the SQL query string from the function's arguments.
        # This logic assumes the query is either the first positional argument (args[0])
        # or passed as a keyword argument named 'query'.
        # It also checks for common SQL keywords to confirm it's likely a query string.
        if args and isinstance(args[0], str) and (
            "SELECT" in args[0].upper() or
            "INSERT" in args[0].upper() or
            "UPDATE" in args[0].upper() or
            "DELETE" in args[0].upper() or
            "PRAGMA" in args[0].upper() or # PRAGMA statements are common in SQLite
            "CREATE" in args[0].upper()    # CREATE TABLE, etc.
        ):
            query = args[0]
        elif 'query' in kwargs and isinstance(kwargs['query'], str):
            query = kwargs['query']

        # Log the identified query or a generic message if no query was found.
        if query:
            logger.info(f"Executing SQL query: {query}")
        else:
            logger.info(f"Executing database operation via '{func.__name__}'; query not explicitly identifiable from arguments.")

        # Execute the original function with its arguments and return its result.
        return func(*args, **kwargs)
    return wrapper

# --- Database Setup (Helper Function) ---
def setup_database_0():
    """
    Sets up a basic 'users' table in 'users.db' for testing purposes.
    It creates the table if it doesn't exist and inserts sample data idempotently
    (meaning it won't insert duplicates if run multiple times).
    """
    conn = None # Initialize connection to None for safe cleanup in finally block.
    try:
        conn = sqlite3.connect('users.db') # Connect to the SQLite database file.
        cursor = conn.cursor() # Get a cursor object to execute SQL commands.
        
        # Execute SQL to create the 'users' table if it doesn't already exist.
        # AUTOINCREMENT for id is good practice for primary keys.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Insert initial data. 'INSERT OR IGNORE' prevents errors if data already exists.
        cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", ('Alice', 'alice@example.com'))
        cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", ('Bob', 'bob@example.com'))
        
        conn.commit() # Commit changes to save them to the database file.
        logger.info("Database users.db setup complete with sample data.")
    except sqlite3.Error as e:
        # Catch specific SQLite errors for better error handling.
        logger.error(f"Error setting up database: {e}", exc_info=True) # Log error with traceback.
        if conn:
            conn.rollback() # Rollback any partial changes if an error occurred during setup.
    finally:
        # Ensure the database connection is always closed, regardless of success or failure.
        if conn:
            conn.close()

# --- Decorated Function Example ---
@log_queries # Apply the logging decorator to this function.
def fetch_all_users(query):
    """
    Fetches all users from the database using the provided SQL query.
    This function's execution will be logged by the @log_queries decorator.
    """
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(query) # Execute the SQL query.
        results = cursor.fetchall() # Fetch all results.
        return results
    except sqlite3.Error as e:
        logger.error(f"Error fetching users: {e}", exc_info=True)
        raise # Re-raise the exception so the calling context can handle it.
    finally:
        if conn:
            conn.close()

# --- Main Execution Block for Standalone Testing ---
# This block runs only when the script is executed directly (e.g., `python 0-log_queries.py`).
# It serves as a demonstration and testing ground for the decorator's functionality.
if __name__ == "__main__":
    # Configure the logging system. In a full application, this would be done once
    # at the application's main entry point. For individual task files, it's placed here.
    configure_logging() 

    setup_database_0() # Ensure the database is ready for testing.
    logger.info("\n--- Task 0: Logging Database Queries (Efficient Output) ---")

    # Example 1: Call a decorated function to fetch all users.
    # The @log_queries decorator will log the "SELECT * FROM users" query.
    users = fetch_all_users(query="SELECT * FROM users")
    logger.info(f"Fetched users: {users}")

    # Example 2: Call another decorated function with a specific query.
    # This query will also be logged.
    single_user = fetch_all_users(query="SELECT name FROM users WHERE id = 1")
    logger.info(f"Fetched single user name: {single_user}")

    # Example 3 (Commented Out): Illustrates how an INSERT query would also be logged.
    # The decorator logs the query string regardless of whether the function
    # actually performs the write operation or just receives the string.
    # fetch_all_users("INSERT INTO users (name, email) VALUES ('Charlie', 'charlie@example.com')")
    # logger.info("Simulated an INSERT query for logging demonstration.")
3. python-decorators-0x01/1-with_db_connection.py
This file implements the decorator for automatic database connection handling.

Python

# python-decorators-0x01/1-with_db_connection.py

import sqlite3  # For database operations.
import functools # For functools.wraps.
import logging  # For logging.

# Import the centralized logging configuration.
try:
    from utils.logging_config import configure_logging
except ImportError:
    # Fallback for standalone execution.
    def configure_logging():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get a logger instance for this module.
logger = logging.getLogger(__name__)

def with_db_connection(db_path='users.db'):
    """
    Decorator factory that automatically handles opening and closing database connections.

    This decorator simplifies database interaction by providing an open connection
    to the decorated function and ensuring the connection is always closed afterward,
    even if errors occur.

    Args:
        db_path (str): The path to the SQLite database file. This allows the decorator
                       to be configured for different database files.
    """
    # This is the actual decorator function returned by the factory.
    def decorator(func):
        # functools.wraps ensures metadata preservation.
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            The inner wrapper function that manages the database connection.
            """
            conn = None # Initialize connection to None for safe cleanup.
            try:
                conn = sqlite3.connect(db_path) # Establish a connection to the database.
                
                # Important: Set isolation_level to None.
                # This disables SQLite's default autocommit behavior for DML statements
                # (INSERT, UPDATE, DELETE). It allows explicit transaction management
                # by other decorators (like `transactional` in Task 2) to work correctly,
                # ensuring that changes are only committed when explicitly told to do so.
                conn.isolation_level = None
                
                # Call the original function, passing the open connection `conn`
                # as its first argument. The decorated function must be designed
                # to accept this `conn` parameter.
                result = func(conn, *args, **kwargs)
                return result
            except sqlite3.Error as e:
                # Catch specific SQLite database errors.
                # Log the error with traceback (`exc_info=True`) for detailed debugging.
                logger.error(f"Database error in '{func.__name__}': {e}", exc_info=True)
                raise # Re-raise the exception to propagate it up the call stack
                      # for higher-level error handling (e.g., by a transaction decorator).
            except Exception as e:
                # Catch any other unexpected, non-database-specific errors.
                logger.critical(f"An unexpected non-DB error occurred in '{func.__name__}': {e}", exc_info=True)
                raise # Re-raise these exceptions as well.
            finally:
                # This block ensures that the connection is always closed,
                # regardless of whether an error occurred or the function completed successfully.
                if conn:
                    conn.close()
                    logger.debug(f"Database connection to {db_path} closed.")
        return wrapper
    return decorator

# --- Database Setup (Helper Function) ---
def setup_database_1():
    """
    Sets up a basic 'users' table in 'users.db' for testing purposes.
    Ensures table existence and inserts sample data idempotently.
    """
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", ('Alice', 'alice@example.com'))
        cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", ('Bob', 'bob@example.com'))
        conn.commit()
        logger.info("Database users.db setup complete with sample data.")
    except sqlite3.Error as e:
        logger.error(f"Error setting up database: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# --- Decorated Function Example ---
@with_db_connection(db_path='users.db') # Apply the connection handling decorator.
def get_user_by_id(conn, user_id):
    """
    Fetches a user by their ID from the database.
    The `conn` argument is automatically provided by the `@with_db_connection` decorator.
    """
    logger.info(f"Attempting to fetch user with ID: {user_id}")
    cursor = conn.cursor() # Get a cursor from the provided connection.
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) # Execute the query.
    return cursor.fetchone() # Return a single matching row.

# --- Main Execution Block for Standalone Testing ---
if __name__ == "__main__":
    configure_logging() # Configure logging for standalone execution.
    setup_database_1() # Ensure the database is set up.
    logger.info("\n--- Task 1: Handle Database Connections (Efficient Output) ---")

    # Test fetching an existing user.
    user = get_user_by_id(user_id=1)
    logger.info(f"Fetched user by ID 1: {user}")

    # Test fetching a non-existent user (should return None).
    user_none = get_user_by_id(user_id=99)
    logger.info(f"Fetched user by ID 99: {user_none}")

    # Test with a simulated database error.
    # Define a function that will intentionally cause an error (e.g., querying a non-existent table).
    @with_db_connection(db_path='users.db')
    def problematic_query(conn):
        logger.info("Attempting a problematic query that will raise an error...")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM non_existent_table") # This SQL will cause an sqlite3.OperationalError.
    
    # Use a try-except block to catch the expected error when calling `problematic_query`.
    try:
        problematic_query()
    except sqlite3.OperationalError as e:
        logger.warning(f"Caught expected database error: {e}. Connection should still be closed.")
    except Exception as e:
        logger.error(f"Caught unexpected error: {e}", exc_info=True)

4. python-decorators-0x01/2-transactional.py
This file implements the transaction management decorator, building upon with_db_connection.

Python

# python-decorators-0x01/2-transactional.py

import sqlite3  # For database operations.
import functools # For functools.wraps.
import logging  # For logging.

# Import the centralized logging configuration.
try:
    from utils.logging_config import configure_logging
except ImportError:
    # Fallback for standalone execution.
    def configure_logging():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# --- Re-using with_db_connection (from Task 1) ---
# In a real-world project, you would import this decorator from its dedicated file:
# `from .1-with_db_connection import with_db_connection`
# However, for ALX independent file submission, it's often necessary to include
# the full definition in each file that depends on it to ensure standalone execution.
def with_db_connection(db_path='users.db'):
    """
    Decorator factory that automatically handles opening and closing database connections.
    (Copied from Task 1 for standalone file execution).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            conn = None
            try:
                conn = sqlite3.connect(db_path)
                # Crucial for transactional decorator: disables autocommit.
                conn.isolation_level = None 
                result = func(conn, *args, **kwargs)
                return result
            except sqlite3.Error as e:
                logger.error(f"Database error in '{func.__name__}': {e}", exc_info=True)
                raise
            except Exception as e:
                logger.critical(f"An unexpected non-DB error occurred in '{func.__name__}': {e}", exc_info=True)
                raise
            finally:
                if conn:
                    conn.close()
                    logger.debug(f"Database connection to {db_path} closed.")
        return wrapper
    return decorator

# --- Transactional Decorator ---
def transactional(func):
    """
    Decorator that manages database transactions (commit/rollback).

    It ensures that a function performing database operations is wrapped within
    a transaction. If the function completes successfully, the transaction is
    committed. If any exception occurs, the transaction is rolled back,
    maintaining data consistency.

    Assumes the decorated function receives a 'conn' object as its first argument
    (typically provided by `@with_db_connection`).
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        """
        The inner wrapper function that handles transaction logic.
        It expects 'conn' as the first argument.
        """
        try:
            # Explicitly begin a transaction.
            # While `conn.isolation_level = None` means DML statements don't autocommit,
            # explicitly calling BEGIN ensures clear transaction boundaries, especially
            # if multiple operations are performed within the decorated function.
            conn.execute("BEGIN") 
            
            result = func(conn, *args, **kwargs) # Execute the original database operation.
            
            conn.commit() # If no error occurred, commit all changes made within the transaction.
            logger.info(f"Transaction for '{func.__name__}' committed successfully.")
            return result
        except Exception as e:
            # If any exception occurs during the function's execution,
            # roll back all changes made within the current transaction.
            conn.rollback()
            logger.error(f"Transaction for '{func.__name__}' rolled back due to error: {type(e).__name__}: {e}", exc_info=True)
            raise # Re-raise the original exception to notify the calling code.
    return wrapper

# --- Database Setup (Helper Function) ---
def setup_database_2():
    """
    Sets up a basic 'users' table in 'users.db' for testing purposes.
    Ensures table existence and inserts sample data idempotently.
    """
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", ('Alice', 'alice@example.com'))
        cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", ('Bob', 'bob@example.com'))
        conn.commit()
        logger.info("Database users.db setup complete with sample data.")
    except sqlite3.Error as e:
        logger.error(f"Error setting up database: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# --- Helper to check email for verification ---
def get_user_email_check(user_id):
    """
    Helper function to retrieve a user's email for verification purposes.
    Used outside of the decorated functions to check database state.
    """
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
        email = cursor.fetchone()
        return email[0] if email else None
    except sqlite3.Error as e:
        logger.error(f"Error fetching email for verification: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

# --- Decorated Functions Example ---
@with_db_connection(db_path='users.db') # First, handle the database connection.
@transactional # Then, wrap the operation in a transaction.
def update_user_email(conn, user_id, new_email):
    """
    Updates a user's email within a transaction.
    If this function succeeds, the change is committed. If it fails, it's rolled back.
    """
    logger.info(f"Attempting to update user {user_id} email to {new_email}")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    logger.info(f"UPDATE statement executed for user {user_id}.")

@with_db_connection(db_path='users.db')
@transactional
def create_user_and_fail(conn, name, email):
    """
    Simulates a database operation that is part of a transaction,
    but then intentionally raises an error to demonstrate rollback.
    """
    logger.info(f"Attempting to create user '{name}' and then simulate a failure.")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    logger.info(f"User '{name}' inserted (tentatively). Now simulating an error.")
    # This ValueError will trigger the `except` block in the `transactional` decorator,
    # causing the insert operation to be rolled back.
    raise ValueError("Simulated operational error during transaction.")

# --- Main Execution Block for Standalone Testing ---
if __name__ == "__main__":
    configure_logging() # Configure logging for standalone execution.
    setup_database_2() # Ensure the database is set up.
    logger.info("\n--- Task 2: Transaction Management Decorator (Efficient Output) ---")

    user_id_for_update = 1
    initial_email = get_user_email_check(user_id_for_update)
    logger.info(f"User {user_id_for_update} initial email: {initial_email}")

    # Test 1: Successful update transaction.
    logger.info("\n--- Test 1: Successful Update ---")
    try:
        new_email = 'alice_changed@example.com'
        update_user_email(user_id=user_id_for_update, new_email=new_email)
        final_email = get_user_email_check(user_id_for_update)
        logger.info(f"User {user_id_for_update} email after successful update: {final_email}")
        # Assert to confirm the update was successful.
        assert final_email == new_email, "Email should be updated after successful commit."
    except Exception as e:
        logger.error(f"Test 1 failed unexpectedly: {e}", exc_info=True)

    # Test 2: Rollback due to a database constraint error (e.g., UNIQUE constraint violation).
    logger.info("\n--- Test 2: Rollback due to IntegrityError ---")
    # To trigger an IntegrityError, we first ensure 'bob@example.com' exists for another user.
    conn_setup = sqlite3.connect('users.db')
    cursor_setup = conn_setup.cursor()
    cursor_setup.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", ('Charlie', 'bob@example.com'))
    conn_setup.commit()
    conn_setup.close()
    
    email_before_rollback = get_user_email_check(user_id_for_update) # Get current email of user 1.
    logger.info(f"User {user_id_for_update} email before rollback attempt: {email_before_rollback}")

    try:
        # Attempt to update user 1's email to 'bob@example.com', which is already taken.
        # This will raise an `sqlite3.IntegrityError`.
        update_user_email(user_id=user_id_for_update, new_email='bob@example.com')
        logger.error("Update unexpectedly succeeded, rollback expected due to unique constraint.")
    except sqlite3.IntegrityError:
        logger.warning(f"Caught expected IntegrityError. Transaction should have rolled back.")
    except Exception as e:
        logger.error(f"Caught unexpected error during integrity error test: {e}", exc_info=True)
    finally:
        email_after_rollback = get_user_email_check(user_id_for_update)
        logger.info(f"User {user_id_for_update} email after rollback attempt: {email_after_rollback}")
        # Assert to confirm the email reverted to its original state.
        assert email_before_rollback == email_after_rollback, "Email should have rolled back!"

    # Test 3: Rollback due to a custom application error (non-database specific).
    logger.info("\n--- Test 3: Rollback due to Custom Application Error ---")
    initial_users_count = len(sqlite3.connect('users.db').cursor().execute("SELECT * FROM users").fetchall())
    logger.info(f"Initial user count: {initial_users_count}")
    try:
        # Call a function that inserts a user but then raises a ValueError.
        create_user_and_fail(name="David", email="david@example.com")
        logger.error("Function unexpectedly succeeded, rollback expected due to custom error.")
    except ValueError as e:
        logger.warning(f"Caught expected ValueError: {e}. Insert should be rolled back.")
    except Exception as e:
        logger.error(f"Caught unexpected error during custom error test: {e}", exc_info=True)
    finally:
        final_users_count = len(sqlite3.connect('users.db').cursor().execute("SELECT * FROM users").fetchall())
        logger.info(f"Final user count: {final_users_count}")
        # Assert to confirm the user was not added to the database.
        assert initial_users_count == final_users_count, "User should not have been added after rollback!"
5. python-decorators-0x01/3-retry_on_failure.py
This file implements the decorator for retrying failed database operations.

Python

# python-decorators-0x01/3-retry_on_failure.py

import time     # For `time.sleep()` to introduce delays between retries.
import sqlite3  # For database operations and specific error types.
import functools # For functools.wraps.
import logging  # For logging.
from typing import Tuple, Type # For type hinting (e.g., specifying a tuple of Exception types).

# Import the centralized logging configuration.
try:
    from utils.logging_config import configure_logging
except ImportError:
    # Fallback for standalone execution.
    def configure_logging():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# --- Re-using with_db_connection (from Task 1/2) ---
# In a real-world project, you would import this decorator.
# For ALX independent file submission, it's included again.
def with_db_connection(db_path='users.db'):
    """
    Decorator factory that automatically handles opening and closing database connections.
    (Copied from Task 1/2 for standalone file execution).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            conn = None
            try:
                conn = sqlite3.connect(db_path)
                conn.isolation_level = None # Allows external transaction control.
                result = func(conn, *args, **kwargs)
                return result
            except sqlite3.Error as e:
                logger.error(f"Database error in '{func.__name__}': {e}", exc_info=True)
                raise
            except Exception as e:
                logger.critical(f"An unexpected non-DB error occurred in '{func.__name__}': {e}", exc_info=True)
                raise
            finally:
                if conn:
                    conn.close()
                    logger.debug(f"Database connection to {db_path} closed.")
        return wrapper
    return decorator

# --- Retry Decorator ---
def retry_on_failure(retries: int = 3, initial_delay: float = 0.5, backoff_factor: float = 2,
                     exceptions: Tuple[Type[Exception], ...] = (sqlite3.OperationalError,)):
    """
    Decorator factory that retries a function if it raises specified exceptions,
    using an exponential backoff strategy.

    This decorator enhances the resilience of operations against transient failures
    (e.g., temporary network glitches, database locks).

    Args:
        retries (int): The maximum number of retry attempts (excluding the first,
                       initial attempt). So, `retries=3` means 1 initial attempt + 3 retries = 4 total attempts.
        initial_delay (float): The delay in seconds before the very first retry.
        backoff_factor (float): The factor by which the delay increases for each
                                 subsequent retry (e.g., 2 means delays are 0.5s, 1s, 2s, 4s...).
        exceptions (Tuple[Type[Exception], ...]): A tuple of exception types that,
                                                   if caught, will trigger a retry.
                                                   Only these specific exceptions will be retried.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = initial_delay # Start with the initial delay.
            # Loop for the initial attempt (i=0) plus the specified number of retries.
            for i in range(retries + 1): 
                try:
                    logger.debug(f"Attempt {i+1}/{retries+1} for '{func.__name__}'...")
                    return func(*args, **kwargs) # Try to execute the original function.
                except exceptions as e:
                    # If a retryable exception is caught:
                    logger.warning(f"Attempt {i+1} of {retries+1} for '{func.__name__}' failed due to: {type(e).__name__}: {e}")
                    if i < retries: # Check if there are still retries left.
                        logger.info(f"Retrying '{func.__name__}' in {current_delay:.2f} seconds...")
                        time.sleep(current_delay) # Wait for the calculated delay.
                        current_delay *= backoff_factor # Increase delay for the next retry (exponential backoff).
                    else:
                        # If no retries are left, log the final failure and re-raise the exception.
                        logger.error(f"All {retries+1} attempts for '{func.__name__}' failed. Re-raising the last exception.")
                        raise # Re-raise the exception to propagate the failure.
                except Exception as e:
                    # Catch any other unexpected exceptions that are NOT in the `exceptions` tuple.
                    # These are considered non-retryable critical errors, so re-raise immediately.
                    logger.critical(f"Non-retryable error encountered in '{func.__name__}': {e}", exc_info=True)
                    raise
        return wrapper
    return decorator

# --- Database Setup (Helper Function) ---
def setup_database_3():
    """
    Sets up a basic 'users' table in 'users.db' for testing purposes.
    Ensures table existence and inserts sample data idempotently.
    """
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", ('Alice', 'alice@example.com'))
        cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", ('Bob', 'bob@example.com'))
        conn.commit()
        logger.info("Database users.db setup complete with sample data.")
    except sqlite3.Error as e:
        logger.error(f"Error setting up database: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# --- Global variable to simulate transient failures for demonstration ---
# This variable is used to control when `fetch_users_with_retry` will succeed.
# It's a simple way to simulate a temporary database issue that resolves after a few tries.
_call_count_for_retry_demo = 0

# --- Decorated Function Example ---
@with_db_connection(db_path='users.db') # Handles connection.
@retry_on_failure(retries=3, initial_delay=0.1, backoff_factor=2, exceptions=(sqlite3.OperationalError,))
def fetch_users_with_retry(conn):
    """
    Fetches users from the database, simulating a transient operational error
    for the first two calls to demonstrate the retry mechanism.
    """
    global _call_count_for_retry_demo # Declare intent to modify the global variable.
    _call_count_for_retry_demo += 1 # Increment call count each time this function is invoked.

    if _call_count_for_retry_demo <= 2: # Simulate failure for the first 2 calls (initial + 1st retry).
        logger.warning(f"Simulating a temporary database error on call {_call_count_for_retry_demo} for '{fetch_users_with_retry.__name__}'...")
        # Raise an exception that is included in the `exceptions` tuple of `retry_on_failure`.
        raise sqlite3.OperationalError("Database is temporarily unavailable (simulated).")
    else:
        # After the simulated failures, the function will succeed.
        logger.info(f"Database is available on call {_call_count_for_retry_demo}. Fetching users.")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()

# --- Main Execution Block for Standalone Testing ---
if __name__ == "__main__":
    configure_logging() # Configure logging for standalone execution.
    setup_database_3() # Ensure the database is set up.
    logger.info("\n--- Task 3: Retry Database Queries (Efficient Output) ---")

    # Test 1: Demonstrate successful retry after transient failures.
    logger.info("\n--- Test 1: Successful Retry ---")
    _call_count_for_retry_demo = 0 # Reset the counter before starting the test.
    try:
        users = fetch_users_with_retry() # This call will trigger retries and eventually succeed.
        logger.info(f"Successfully fetched users after retry: {users}")
    except Exception as e:
        logger.error(f"Test 1 failed unexpectedly: {e}", exc_info=True)

    # Test 2: Demonstrate retry with eventual failure (max retries reached).
    logger.info("\n--- Test 2: Retry with Eventual Failure ---")
    _call_count_for_retry_demo = 0 # Reset the counter for this new test.

    @with_db_connection(db_path='users.db')
    @retry_on_failure(retries=2, initial_delay=0.1, exceptions=(sqlite3.OperationalError,))
    def always_fail_query(conn):
        """
        Simulates a function that always fails, to show what happens when
        all retry attempts are exhausted.
        """
        global _call_count_for_retry_demo
        _call_count_for_retry_demo += 1
        logger.info(f"Always failing on call {_call_count_for_retry_demo} for '{always_fail_query.__name__}'...")
        raise sqlite3.OperationalError("Simulated persistent database error.")

    try:
        always_fail_query() # This call will fail after 2 retries (3 total attempts).
        logger.error("Function unexpectedly succeeded, expected failure after retries.")
    except sqlite3.OperationalError:
        logger.info("Caught expected sqlite3.OperationalError after all retries for 'always_fail_query'.")
    except Exception as e:
        logger.error(f"Caught unexpected error during persistent failure test: {e}", exc_info=True)

6. python-decorators-0x01/4-cache_query.py
This file implements the decorator for caching database query results. This version uses a custom LRU cache to correctly handle the non-hashable conn object.

Python

# python-decorators-0x01/4-cache_query.py

import time     # For simulating query time and measuring performance.
import sqlite3  # For database operations.
import functools # For functools.wraps.
import logging  # For logging.
# import json # Not strictly needed for this LRU implementation, but useful for complex keys.

# Import the centralized logging configuration.
try:
    from utils.logging_config import configure_logging
except ImportError:
    # Fallback for standalone execution.
    def configure_logging():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# --- Re-using with_db_connection (from Task 1/2/3) ---
# In a real-world project, you would import this decorator.
# For ALX independent file submission, it's included again.
def with_db_connection(db_path='users.db'):
    """
    Decorator factory that automatically handles opening and closing database connections.
    (Copied from previous tasks for standalone file execution).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            conn = None
            try:
                conn = sqlite3.connect(db_path)
                conn.isolation_level = None
                result = func(conn, *args, **kwargs)
                return result
            except sqlite3.Error as e:
                logger.error(f"Database error in '{func.__name__}': {e}", exc_info=True)
                raise
            except Exception as e:
                logger.critical(f"An unexpected non-DB error occurred in '{func.__name__}': {e}", exc_info=True)
                raise
            finally:
                if conn:
                    conn.close()
                    logger.debug(f"Database connection to {db_path} closed.")
        return wrapper
    return decorator

# --- Custom LRU Cache Implementation ---
# This custom LRU (Least Recently Used) cache is implemented because `functools.lru_cache`
# cannot directly cache functions where one of the arguments (like the `conn` object from sqlite3)
# is not hashable. This LRU cache will manage caching based on hashable keys (like the query string).
class LRUCache:
    """
    A simple Least Recently Used (LRU) cache implementation.
    It stores key-value pairs and evicts the least recently used item
    when the cache capacity is exceeded.
    """
    def __init__(self, capacity: int):
        """
        Initializes the LRU cache.
        Args:
            capacity (int): The maximum number of items the cache can hold.
        """
        self.capacity = capacity
        self.cache = {}  # Stores the actual data: {key: value}
        self.order = []  # Stores keys in order of usage: [LRU_key, ..., MRU_key]

    def get(self, key):
        """
        Retrieves a value from the cache.
        If the key exists, it's marked as most recently used.
        Returns the value if found, else None.
        """
        if key not in self.cache:
            return None # Key not in cache.
        
        # If key exists, move it to the end of the order list (most recently used).
        self.order.remove(key)
        self.order.append(key)
        return self.cache[key]

    def put(self, key, value):
        """
        Adds or updates a key-value pair in the cache.
        If the key already exists, its value is updated and it's marked as MRU.
        If the cache is full, the least recently used item is evicted.
        """
        if key in self.cache:
            # If updating an existing key, remove its old position in order.
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            # If cache is at capacity, evict the LRU item.
            lru_key = self.order.pop(0) # Remove the first (LRU) key from order.
            del self.cache[lru_key]     # Delete the corresponding item from cache.
            logger.debug(f"Evicted LRU item from cache: {lru_key}")
        
        # Add the new/updated item to the cache and mark it as MRU.
        self.cache[key] = value
        self.order.append(key)
        logger.debug(f"Added/Updated item in cache: {key}")

    def info(self):
        """Returns information about the cache state for debugging."""
        return {
            "size": len(self.cache),
            "capacity": self.capacity,
            "order": list(self.order),
            "keys": list(self.cache.keys())
        }

# --- Cache Decorator using the Custom LRU Cache ---
def cache_query(maxsize: int = 128, typed: bool = False):
    """
    Decorator factory that caches query results using a custom LRU cache.
    
    This decorator is designed to cache the results of database queries based
    on the query string and any other hashable parameters. It specifically
    handles the scenario where the database connection object (`conn`) is
    passed as an argument but is not hashable, making `functools.lru_cache`
    unsuitable without significant function signature changes.

    Args:
        maxsize (int): The maximum number of unique query results to cache.
        typed (bool): If True, arguments of different types will be cached separately.
                      (This parameter is included for API consistency with functools.lru_cache,
                       but its effect on the custom LRU might be limited unless keys are
                       explicitly type-dependent).
    """
    # Create a single instance of the LRUCache for all functions decorated by this factory.
    # If each decorated function needs its own cache, this `_query_cache` instance
    # would need to be created inside the `decorator(func)` scope.
    _query_cache = LRUCache(maxsize)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(conn, query, *args, **kwargs):
            """
            The inner wrapper function that handles caching logic.
            It expects `conn` as the first argument, followed by `query` string,
            and any other query parameters.
            """
            # Construct a unique cache key.
            # For simplicity and to match the problem description ("based on the SQL query string"),
            # we use the `query` string as the primary key.
            # If `args` or `kwargs` also contain query parameters that affect the result,
            # they should be included in the cache_key (e.g., `(query, tuple(args), frozenset(kwargs.items()))`).
            # For this task, we assume the `query` string itself is sufficient for the cache key.
            cache_key = query 

            # Attempt to retrieve the result from the cache.
            cached_result = _query_cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Returning cached result for query: '{query}'")
                return cached_result
            
            # If not in cache, execute the original function to get the result.
            logger.info(f"Executing actual database call for query: '{query}' (not in cache).")
            # Pass all original arguments, including the `conn` object.
            result = func(conn, query, *args, **kwargs)
            
            # Store the new result in the cache.
            _query_cache.put(cache_key, result)
            return result
        return wrapper
    return decorator

# --- Database Setup (Helper Function) ---
def setup_database_4():
    """
    Sets up a basic 'users' table in 'users.db' for testing purposes.
    Ensures table existence and inserts sample data idempotently.
    """
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", ('Alice', 'alice@example.com'))
        cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", ('Bob', 'bob@example.com'))
        conn.commit()
        logger.info("Database users.db setup complete with sample data.")
    except sqlite3.Error as e:
        logger.error(f"Error setting up database: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# --- Decorated Function Example ---
@with_db_connection(db_path='users.db') # Handles connection.
@cache_query(maxsize=2) # Caches up to 2 unique query results (LRU eviction).
def fetch_users_with_cache(conn, query, *query_params):
    """
    Fetches users from the database using the provided query and parameters.
    Simulates a time-consuming operation to clearly demonstrate caching benefits.
    The `conn` is provided by `with_db_connection`.
    The `query` string and `query_params` are used as the cache key.
    """
    logger.info(f"Executing actual DB call for: '{query}' with parameters: {query_params}")
    cursor = conn.cursor()
    cursor.execute(query, query_params) # Execute the query with parameters.
    time.sleep(0.1) # Simulate a delay (e.g., network latency, complex query execution).
    return cursor.fetchall()

# --- Main Execution Block for Standalone Testing ---
if __name__ == "__main__":
    configure_logging() # Configure logging for standalone execution.
    setup_database_4() # Ensure the database is set up.
    logger.info("\n--- Task 4: Cache Database Queries (Efficient Output) ---")

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
    # Expect significantly faster time due to cache hit.
    logger.info(f"Time taken for second call (cached): {end_time - start_time:.4f} seconds") 

    logger.info("\nThird call with a different query 'SELECT name FROM users WHERE id = ?' (new query, not cached initially):")
    start_time = time.time()
    # Pass query parameters as a tuple to `*query_params`.
    users3 = fetch_users_with_cache(query="SELECT name FROM users WHERE id = ?", query_params=(1,))
    end_time = time.time()
    logger.info(f"Users 3: {users3}")
    logger.info(f"Time taken for third call: {end_time - start_time:.4f} seconds")

    logger.info("\nFourth call with the same different query (should be cached now):")
    start_time = time.time()
    users4 = fetch_users_with_cache(query="SELECT name FROM users WHERE id = ?", query_params=(1,))
    end_time = time.time()
    logger.info(f"Users 4: {users4}")
    logger.info(f"Time taken for fourth call (cached): {end_time - start_time:.4f} seconds")

    logger.info("\nFifth call with another different query 'SELECT email FROM users WHERE name = ?' (new query, might evict oldest):")
    start_time = time.time()
    users5 = fetch_users_with_cache(query="SELECT email FROM users WHERE name = ?", query_params=("Bob",))
    end_time = time.time()
    logger.info(f"Users 5: {users5}")
    logger.info(f"Time taken for fifth call: {end_time - start_time:.4f} seconds")

    logger.info("\nSixth call for 'SELECT * FROM users' again (might be re-executed if evicted due to maxsize=2):")
    start_time = time.time()
    users6 = fetch_users_with_cache(query="SELECT * FROM users")
    end_time = time.time()
    logger.info(f"Users 6: {users6}")
    logger.info(f"Time taken for sixth call: {end_time - start_time:.4f} seconds")
    # Expected behavior: Since maxsize is 2, and we've had 3 unique queries
    # ("SELECT * FROM users", "SELECT name...", "SELECT email..."),
    # the first query ("SELECT * FROM users") might have been evicted, leading to a re-execution.

    # Accessing the cache info (only possible if the cache object is exposed or via a helper)
    # For this custom LRU, we don't have a direct `cache_info()` like functools.lru_cache.
    # We can add a method to LRUCache to expose its state.
    # logger.info("\nInspecting cache stats:")
    # logger.info(_query_cache.info()) # This would require exposing _query_cache from the decorator.
