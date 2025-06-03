import streamlit as st
# Page config at top-level:
st.set_page_config(page_title="Football Game", page_icon="⚽", layout="wide")

# Import Admin Cup 
from views.cup_view import cup_view
from views.login_view import login_view
from views.players_view import players_view
from admin_app import under_update

from views.matches_view import matches_view 
from views.predictions_view import predictions_view
from views.leaderboard_view import leaderboard_view
from views.achievement_view import achievement_view

from players_views.leaderboard_players_view import leaderboard_view_player
from players_views.predictions_players_view import prediction_view_player
from players_views.cup_players_view import cup_view_player

# stub for under development
def under_dev_view():
    return under_update.under_update_view

TABS = {
    "admin": {
        "Players": players_view,
        "Matches": matches_view,
        "Predictions": predictions_view,
        "Leaderboard": leaderboard_view,
        "Achievements": achievement_view,
        "Cup": under_dev_view(),
        "Power-Ups": under_dev_view(),
    },
    "user": {
        "My Predictions": prediction_view_player,
        "Leaderboard": leaderboard_view_player,
        "Cup": cup_view_player,
        "Achievements": achievement_view,
    }
}

def show_sidebar(user):
    st.sidebar.title("⚽ Football Game")
    st.sidebar.markdown(f"👤 **Logged in as:** `{user['username']}`")
    st.sidebar.markdown(f"🔐 **Role:** `{user['role']}`")
    st.sidebar.markdown("---")

    role_tabs = TABS.get(user["role"], {})
    if not role_tabs:
        st.sidebar.warning("🚫 No features available for your role.")
        return

    selected = st.sidebar.radio("📂 Menu", list(role_tabs.keys()))
    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.pop("user", None)
        st.rerun()

    view_function = role_tabs[selected]
    view_function()  # call function here, not during TABS definition



def main():
    user = st.session_state.get("user")
    if not user:
        login_view()
    else:
        show_sidebar(user)

if __name__ == "__main__":
    main()
