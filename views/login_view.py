import streamlit as st
from controllers.auth_controller import login, signup

def login_view():
    st.title("🔐 Login to Football Game")

    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    # Login Tab
    with login_tab:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            user = login(username, password)
            if user:
                st.session_state["user"] = user
                st.success(f"Welcome, {user['username']}!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    # Sign Up Tab
    with signup_tab:
        new_username = st.text_input("New Username", key="signup_username")
        new_password = st.text_input("New Password", type="password", key="signup_password")
        admin_code = st.text_input("Admin Code (optional)", type="password", key="signup_admin_code")

        if st.button("Sign Up"):
            success, message = signup(new_username, new_password, admin_code)
            if success:
                st.success(message)
            else:
                st.error(message)
