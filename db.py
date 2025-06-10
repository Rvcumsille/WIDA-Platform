import sqlite3

DB_NAME = "clima.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predicciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        temperatura REAL,
        pronostico TEXT
    )''')
    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect(DB_NAME)