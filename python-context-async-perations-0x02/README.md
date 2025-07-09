Project Guide: Context Managers and Async Programming in Python
🔧 Project Setup & GitHub
1. Create the GitHub Repository
From your terminal:

bash
Copy
Edit
git init alx-backend-python
cd alx-backend-python
gh repo create alx-backend-python --public --source=. --remote=origin
Replace --public with --private if required by ALX guidelines.

2. Create the Required Directory
bash
Copy
Edit
mkdir -p python-context-async-perations-0x02
cd python-context-async-perations-0x02
Create the files:

bash
Copy
Edit
touch 0-databaseconnection.py 1-execute.py 3-concurrent.py README.md
 Task Explanations & Implementation
 Task 0: Custom Class-Based Context Manager
Objective: Manage SQLite DB connection using a class-based context manager.

📄 File: 0-databaseconnection.py
💡 Key Concepts: __enter__, __exit__, with

 Steps:
Import sqlite3

Create DatabaseConnection class with:

__enter__() → returns cursor

__exit__() → commits and closes connection

Use with DatabaseConnection(...) to run query

 Task 1: Reusable Query Context Manager
Objective: Reuse a query context manager with parameters.

📄 File: 1-execute.py
💡 Key Concepts: Context logic with dynamic parameters

 Steps:
Accept query and params via __init__()

Execute query in __enter__()

Return results

Ensure commit & close in __exit__()

 Task 2: Concurrent Asynchronous Queries
Objective: Use asyncio and aiosqlite to fetch users concurrently

📄 File: 3-concurrent.py
💡 Key Concepts: async/await, asyncio.gather(), coroutines

 Steps:
Install aiosqlite:

bash
Copy
Edit
pip install aiosqlite
Write async functions:

async_fetch_users()

async_fetch_older_users()

Use asyncio.gather() to run both concurrently.

🗃 Database Setup
Create the SQLite DB using Python or SQLite CLI.

Option 1: Using SQLite3 CLI
bash
Copy
Edit
sqlite3 users.db
Paste this SQL:

sql
Copy
Edit
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL
);

INSERT INTO users (name, age) VALUES 
('Alice', 30),
('Bob', 45),
('Charlie', 20),
('Diana', 50);
Exit with .exit.

Option 2: Python script to seed data
python
Copy
Edit
# seed_users.py
import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL
)
''')

users = [('Alice', 30), ('Bob', 45), ('Charlie', 20), ('Diana', 50)]
cursor.executemany("INSERT INTO users (name, age) VALUES (?, ?)", users)

conn.commit()
conn.close()
Then run:

bash
Copy
Edit
python3 seed_users.py
 Testing Your Scripts
Test each file:

bash
Copy
Edit
python3 0-databaseconnection.py
python3 1-execute.py
python3 3-concurrent.py
Expected output:

All users in 0-databaseconnection.py

Users age > 25 in 1-execute.py

Both groups concurrently printed in 3-concurrent.py

📦 Git Workflow & Submission
Stage and commit:

bash
Copy
Edit
git add .
git commit -m "Completed context manager and async tasks"
Push to GitHub:

bash
Copy
Edit
git push origin main
