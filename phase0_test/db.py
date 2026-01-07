import sqlite3

def get_connection():
    return sqlite3.connect("data.db")

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT
        )
    """)

    conn.commit()
    conn.close()