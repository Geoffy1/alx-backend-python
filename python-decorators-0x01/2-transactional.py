import sqlite3
import functools
import logging

logger = logging.getLogger(__name__)

# Re-using the improved with_db_connection from Task 1
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
                # Important: Set isolation_level to None to manage transactions manually
                conn.isolation_level = None
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


def transactional(func):
    """
    Decorator that manages database transactions.
    It commits changes if the decorated function succeeds, and rolls back if an error occurs.
    Assumes the decorated function receives a 'conn' object as its first argument.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Begin an explicit transaction
            conn.execute("BEGIN")
            result = func(conn, *args, **kwargs)
            conn.commit()
            logger.info(f"Transaction for '{func.__name__}' committed successfully.")
            return result
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction for '{func.__name__}' rolled back due to error: {e}")
            raise # Re-raise the exception after rollback
    return wrapper

# Example Usage
def setup_database_2():
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

def get_user_email_check(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    email = cursor.fetchone()
    conn.close()
    return email[0] if email else None

@with_db_connection(db_path='users.db')
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    logger.info(f"Executed UPDATE for user {user_id} to email {new_email}")

@with_db_connection(db_path='users.db')
@transactional
def create_user_and_fail(conn, name, email):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    # Simulate an error after the insert
    raise ValueError("Simulated error after insert")


if __name__ == "__main__":
    setup_database_2()
    print("\n--- Task 2: Transaction Management Decorator (Efficient Output) ---")

    user_id_for_update = 1
    initial_email = get_user_email_check(user_id_for_update)
    logger.info(f"User {user_id_for_update} initial email: {initial_email}")

    # Test successful update
    try:
        update_user_email(user_id=user_id_for_update, new_email='alice_new@example.com')
        logger.info(f"User {user_id_for_update} email after successful update: {get_user_email_check(user_id_for_update)}")
    except Exception as e:
        logger.error(f"Error during successful update test: {e}")

    # Test rollback
    logger.info(f"\n--- Testing transaction rollback ---")
    # Ensure a duplicate email exists to cause an IntegrityError
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)", (3, 'Charlie', 'bob@example.com'))
    conn.commit()
    conn.close()

    user_id_for_rollback_test = 1
    email_before_rollback = get_user_email_check(user_id_for_rollback_test)
    logger.info(f"User {user_id_for_rollback_test} email before rollback attempt: {email_before_rollback}")

    try:
        # This will cause an IntegrityError because 'bob@example.com' is already taken
        update_user_email(user_id=user_id_for_rollback_test, new_email='bob@example.com')
    except sqlite3.IntegrityError:
        logger.warning(f"Caught expected IntegrityError during rollback test. User email should not change.")
    except Exception as e:
        logger.error(f"Caught unexpected error during rollback test: {e}")
    finally:
        email_after_rollback = get_user_email_check(user_id_for_rollback_test)
        logger.info(f"User {user_id_for_rollback_test} email after rollback attempt: {email_after_rollback}")
        assert email_before_rollback == email_after_rollback, "Email should have rolled back!"

    # Test custom error rollback
    logger.info(f"\n--- Testing custom error rollback ---")
    initial_users_count = len(sqlite3.connect('users.db').cursor().execute("SELECT * FROM users").fetchall())
    logger.info(f"Initial user count: {initial_users_count}")
    try:
        create_user_and_fail(name="David", email="david@example.com")
    except ValueError as e:
        logger.warning(f"Caught expected ValueError: {e}. Insert should be rolled back.")
    finally:
        final_users_count = len(sqlite3.connect('users.db').cursor().execute("SELECT * FROM users").fetchall())
        logger.info(f"Final user count: {final_users_count}")
        assert initial_users_count == final_users_count, "User should not have been added!"
