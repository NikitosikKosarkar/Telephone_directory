import psycopg2
import sys


class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                database='database_name',
                user='user_name',
                password='your_password',
                host='localhost',
                port='your_port'
            )
            self.cursor = self.conn.cursor()
            print("[DEBUG] Connected to the database")
        except psycopg2.Error as e:
            print(f"[ERROR] Error {e} while connecting to the database")
            sys.exit(1)

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"[ERROR] Error {e} while request execution")
            raise e

    def fetch_all(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"[ERROR] Error {e} while request execution")
            return []

    def close(self):
        self.cursor.close()
        self.conn.close()
        print("[DEBUG] Connection to the database is closed")
