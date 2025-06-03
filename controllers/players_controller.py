from utils.db import get_connection
from controllers.auth_controller import hash_password

def log_admin_action(admin_id, action, target_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_log (admin_id, action, target_player_id) VALUES (?, ?, ?)",
        (admin_id, action, target_id)
    )
    conn.commit()

def get_all_players(search=""):
    conn = get_connection()
    cursor = conn.cursor()
    if search:
        cursor.execute("SELECT id, name, pw, role FROM players WHERE name LIKE ?", (f"%{search}%",))
    else:
        cursor.execute("SELECT id, name, pw, role FROM players")
    return cursor.fetchall()

def add_player(name, password, role, admin_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    cursor.execute("INSERT INTO players (name, pw, role) VALUES (?, ?, ?)", (name, hashed_pw, role))
    conn.commit()
    if admin_id:
        log_admin_action(admin_id, "add_player", cursor.lastrowid)

def update_player(player_id, name, password, role, admin_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    cursor.execute("UPDATE players SET name = ?, pw = ?, role = ? WHERE id = ?", (name, hashed_pw, role, player_id))
    conn.commit()
    if admin_id:
        log_admin_action(admin_id, "update_player", player_id)

def delete_player(player_id, admin_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
    conn.commit()
    if admin_id:
        log_admin_action(admin_id, "delete_player", player_id)

def get_audit_logs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.timestamp, p.name, a.action, a.target_player_id
        FROM audit_log a
        LEFT JOIN players p ON a.admin_id = p.id
        ORDER BY a.timestamp DESC
    """)
    return cursor.fetchall()
