# File: python-generators-0x00/seed.py

import mysql.connector
import csv
import uuid

# Database connection parameters (modify if necessary)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', # Your MySQL username
    'password': '' # Your MySQL password (often empty for root on local setup)
}
DATABASE_NAME = 'ALX_prodev'
TABLE_NAME = 'user_data'

def connect_db():
    """
    Connects to the MySQL database server.
    Returns a connection object if successful, None otherwise.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to MySQL server.")
            return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL server: {err}")
    return None

def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist.
    """
    if not connection:
        print("No database connection to create database.")
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
        print(f"Database {DATABASE_NAME} created or already exists.")
        return True
    except mysql.connector.Error as err:
        print(f"Error creating database {DATABASE_NAME}: {err}")
    finally:
        if cursor:
            cursor.close()
    return False

def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL.
    Returns a connection object if successful, None otherwise.
    """
    db_config_with_db = DB_CONFIG.copy()
    db_config_with_db['database'] = DATABASE_NAME
    try:
        connection = mysql.connector.connect(**db_config_with_db)
        if connection.is_connected():
            print(f"Successfully connected to database {DATABASE_NAME}.")
            return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database {DATABASE_NAME}: {err}")
    return None

def create_table(connection):
    """
    Creates a table user_data if it does not exist with the required fields.
    """
    if not connection:
        print("No database connection to create table.")
        return False
    try:
        cursor = connection.cursor()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(5,2) NOT NULL,
            UNIQUE (email) # Added unique constraint for email as it's common practice
        );
        """
        cursor.execute(create_table_query)
        print(f"Table {TABLE_NAME} created successfully.")
        return True
    except mysql.connector.Error as err:
        print(f"Error creating table {TABLE_NAME}: {err}")
    finally:
        if cursor:
            cursor.close()
    return False

def insert_data(connection, csv_file_path):
    """
    Inserts data from a CSV file into the user_data table.
    Uses INSERT IGNORE to skip rows with duplicate primary keys.
    """
    if not connection:
        print("No database connection to insert data.")
        return False

    insert_query = f"INSERT IGNORE INTO {TABLE_NAME} (user_id, name, email, age) VALUES (%s, %s, %s, %s)"
    success_count = 0
    fail_count = 0

    try:
        cursor = connection.cursor()
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader) # Skip header row

            for row in reader:
                try:
                    # Ensure UUID is a valid string, and age is converted to decimal
                    user_id = str(row[0]) # Assuming user_id is the first column and a UUID string
                    name = row[1]
                    email = row[2]
                    age = float(row[3]) # Convert age to float for DECIMAL type

                    data_tuple = (user_id, name, email, age)
                    cursor.execute(insert_query, data_tuple)
                    success_count += 1
                except (IndexError, ValueError, mysql.connector.Error) as e:
                    # Handle rows that don't match expected format or other SQL errors (e.g., duplicate email)
                    print(f"Skipping row due to error: {row} - {e}")
                    fail_count += 1
        connection.commit()
        print(f"Data insertion complete: {success_count} rows inserted/ignored, {fail_count} rows failed.")
        return True
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}")
    except Exception as e:
        print(f"An unexpected error occurred during data insertion: {e}")
    finally:
        if cursor:
            cursor.close()
    return False

def stream_users_from_db(connection):
    """
    A generator that streams rows from the user_data table one by one.
    Yields each row as a tuple.
    """
    if not connection:
        print("No database connection to stream data.")
        return # Generator stops if no connection

    try:
        cursor = connection.cursor(buffered=True) # buffered=True to fetch all rows at once, then iterate
                                                # For very large tables, consider fetchone() in a loop to truly stream
        cursor.execute(f"SELECT user_id, name, email, age FROM {TABLE_NAME}")
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row
    except mysql.connector.Error as err:
        print(f"Error streaming data: {err}")
    finally:
        if cursor:
            cursor.close()

# Note: The 0-main.py provided in the prompt is a separate script that will import and use these functions.
# Ensure you have the `mysql-connector-python` package installed: `pip install mysql-connector-python`
