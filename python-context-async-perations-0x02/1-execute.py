# 1-execute.py
import sqlite3

class ExecuteQuery:
    def __init__(self, db_name, query, params=()):
        self.db_name = db_name
        self.query = query
        self.params = params

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        return self.cursor.fetchall()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > ?"
    with ExecuteQuery("users.db", query, (25,)) as results:
        for row in results:
            print(row)
