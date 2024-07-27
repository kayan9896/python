
import sqlite3

def create_connection():
    return sqlite3.connect("renovation_tracker.db")

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses
                    (id INTEGER PRIMARY KEY,
                     category TEXT,
                     amount REAL,
                     hst REAL,
                     company TEXT,
                     description TEXT,
                     date TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS invoices
                    (id INTEGER PRIMARY KEY,
                     invoice_number TEXT,
                     amount REAL,
                     hst REAL,
                     status TEXT,
                     date TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS gallery
                    (id INTEGER PRIMARY KEY,
                     image_path TEXT,
                     description TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS timeline
                    (id INTEGER PRIMARY KEY,
                     start_date TEXT,
                     end_date TEXT,
                     description TEXT,
                     company TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS companies
                    (id INTEGER PRIMARY KEY,
                     name TEXT UNIQUE,
                     color TEXT)''')

    conn.commit()