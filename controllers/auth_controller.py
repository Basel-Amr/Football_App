import hashlib
import os
from utils.db import get_connection
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
ADMIN_SECRET = os.getenv("ADMIN_SECRET")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, pw, role FROM players WHERE name = ?", (username,))
    row = cursor.fetchone()
    if row and verify_password(password, row[1]):
        return {"id": row[0], "username": username, "role": row[2]}
    return None

def signup(username, password, admin_code=None):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if username already exists
    cursor.execute("SELECT id FROM players WHERE name = ?", (username,))
    if cursor.fetchone():
        return False, "Username already exists"

    hashed_pw = hash_password(password)

    # Determine role
    role = "admin" if admin_code == ADMIN_SECRET else "user"

    try:
        cursor.execute("INSERT INTO players (name, pw, role) VALUES (?, ?, ?)", (username, hashed_pw, role))
        conn.commit()
        return True, f"Account created successfully as {role}."
    except Exception as e:
        return False, f"Error: {str(e)}"
