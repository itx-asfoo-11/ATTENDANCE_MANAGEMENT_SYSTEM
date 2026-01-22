import sqlite3
from pathlib import Path

# Database file path
BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "attendance.db"

def get_connection():
    """Return a connection to the SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    return conn

def create_tables():
    """Create required tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()

    # Students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_no TEXT UNIQUE NOT NULL,
        class TEXT NOT NULL,
        section TEXT NOT NULL
    )
    """)

    # Attendance table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )
    """)

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully!")
