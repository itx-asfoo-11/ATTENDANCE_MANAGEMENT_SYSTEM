from app.database.connection import get_connection
import hashlib

def hash_password(password):
    """Convert plain text password to hashed version"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, role="admin"):
    """Add a new user"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role)
        )
        conn.commit()
        print(f"User '{username}' created successfully!")
    except Exception as e:
        print("Error creating user:", e)
    finally:
        conn.close()

def login(username, password):
    """Check credentials"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password, role FROM users WHERE username=?",
        (username,)
    )
    result = cursor.fetchone()
    conn.close()
    if result and hash_password(password) == result[0]:
        return True, result[1]
    return False, None
