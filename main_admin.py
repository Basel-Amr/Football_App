import streamlit as st
import sqlite3
import hashlib


# ----------------------------- #
# Connect to the database
# ----------------------------- #
@st.cache_resource
def get_connection():
    conn = sqlite3.connect("football_game.db", check_same_thread=False)
    return conn

conn = get_connection()
cursor = conn.cursor()

# ----------------------------- #
# Password hashing
# ----------------------------- #
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# ----------------------------- #
# Create login/signup UI
# ----------------------------- #
def login_page():
    st.title("⚽ Football Prediction Game - Login")

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            cursor.execute("SELECT id, pw, role FROM players WHERE name = ?", (username,))
            row = cursor.fetchone()
            if row and verify_password(password, row[1]):
                st.session_state["user_id"] = row[0]
                st.session_state["username"] = username
                st.session_state["role"] = row[2]
                st.success(f"Welcome back, {username}!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")

    with tab2:
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        role = st.selectbox("Role", ["user", "admin"])
        if st.button("Sign Up"):
            try:
                hashed_pw = hash_password(new_password)
                cursor.execute("INSERT INTO players (name, pw, role) VALUES (?, ?, ?)",
                               (new_username, hashed_pw, role))
                conn.commit()
                st.success("Account created! You can now log in.")
            except sqlite3.IntegrityError:
                st.error("Username already exists.")

# ----------------------------- #
# Main App Logic
# ----------------------------- #
def main():
    if "user_id" not in st.session_state:
        login_page()
    else:
        st.sidebar.title(f"Hello, {st.session_state['username']}! 👋")
        role = st.session_state["role"]

        page = st.sidebar.radio("Navigation", ["🏠 Home", "📅 View Matches", "📊 My Scores"] + (["🛠️ Admin Panel"] if role == "admin" else []))

        if page == "🏠 Home":
            st.title("🏆 Welcome to the Football Prediction Game")
            st.write("Use the menu on the left to get started.")
        elif page == "📅 View Matches":
            st.write("🧩 Coming soon: Match predictions UI")
        elif page == "📊 My Scores":
            st.write("📈 Coming soon: Score summary UI")
        elif page == "🛠️ Admin Panel":
            st.write("🛠️ Coming soon: Admin functions")

        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
