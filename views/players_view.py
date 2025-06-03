import streamlit as st
import pandas as pd
from controllers.players_controller import (
    get_all_players, add_player, update_player,
    delete_player, get_audit_logs
)

def players_view():
    admin_id = st.session_state["user"]["id"]
    st.title("👥 Admin: Manage Players")

    # 🔍 Search Bar
    search_term = st.text_input("Search players by name", "")

    # ➕ Add New Player
    with st.expander("➕ Add New Player"):
        with st.form("add_player_form"):
            new_name = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["user", "admin"])
            submitted = st.form_submit_button("Add Player")
            if submitted:
                add_player(new_name, new_password, new_role, admin_id)
                st.success("✅ Player added.")
                st.rerun()

    # 📋 Load Players Data
    players = get_all_players(search_term)

    if not players:
        st.info("No players found.")
        return

    st.subheader("📄 Player List")

    # Keep track of which player is being edited
    if "editing_player_id" not in st.session_state:
        st.session_state.editing_player_id = None

    for player in players:
        player_id, name, pw_hash, role = player
        is_editing = st.session_state.editing_player_id == player_id

        cols = st.columns([3, 3, 2, 1, 1])
        cols[0].markdown(f"**{name}**")
        cols[1].markdown(f"🔒 Password set")
        cols[2].markdown(f"🔘 {role}")

        if cols[3].button("📝", key=f"edit_{player_id}"):
            st.session_state.editing_player_id = player_id
            st.rerun()

        if cols[4].button("🗑️", key=f"delete_{player_id}"):
            delete_player(player_id, admin_id)
            st.warning(f"❌ Deleted {name}")
            st.rerun()

        if is_editing:
            with st.expander(f"✏️ Edit Player: {name}", expanded=True):
                with st.form(f"edit_form_{player_id}"):
                    updated_name = st.text_input("New Username", value=name, key=f"name_{player_id}")
                    updated_password = st.text_input("New Password (leave blank to keep current)", key=f"pw_{player_id}")
                    updated_role = st.selectbox("Role", ["user", "admin"], index=0 if role == "user" else 1, key=f"role_{player_id}")
                    confirm = st.form_submit_button("Save")
                    if confirm:
                        password_to_use = updated_password if updated_password else pw_hash
                        update_player(player_id, updated_name, password_to_use, updated_role, admin_id)
                        st.success("✅ Player updated.")
                        st.session_state.editing_player_id = None
                        st.rerun()

    # 📝 Audit Log
    with st.expander("🧾 Admin Action Log"):
        logs = get_audit_logs()
        if logs:
            df = pd.DataFrame(logs, columns=["Timestamp", "Admin", "Action", "Target ID"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No actions yet.")
