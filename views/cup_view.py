# views/cup_view.py
import streamlit as st
from controllers.cup_controller import get_cup_matchups_with_points

def display_matchup(player1, player2):
    col1, col2, col3 = st.columns([4, 1, 4])

    def format_player(player, highlight=False):
        if not player or not player.get("name"):
            # Waiting / bye placeholder
            return """
            <div style="background-color:#f0f0f0; border-radius:15px; padding:20px; text-align:center; 
                        font-weight:bold; color:#6c757d; box-shadow: inset 2px 2px 5px #bbb;">
                🎁 Waiting for opponent<br>Points: 🎯 0
            </div>
            """
        bg_color = "#d1e7dd" if highlight else "#e7f3ff"
        return f"""
        <div style="background-color:{bg_color}; border-radius:15px; padding:20px; text-align:center;
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.1); font-size:1.1em;">
            ⚽ <strong>{player['name']}</strong><br>
            <span style="font-size:1.2em; color:#0d6efd;">Points: 🎯 {player['points']}</span>
        </div>
        """

    with col1:
        st.markdown(format_player(player1, highlight=True), unsafe_allow_html=True)

    with col2:
        st.markdown("<h3 style='text-align:center; color:#dc3545; margin-top:40px;'>VS</h3>", unsafe_allow_html=True)

    with col3:
        st.markdown(format_player(player2), unsafe_allow_html=True)


def cup_view():
    st.title("🔥 Current Cup Matchups & Player Points 🔥")

    # TODO: get current cup round ID dynamically, for example:
    current_cup_round_id = 1  # replace with real logic to get current round

    matchups = get_cup_matchups_with_points(current_cup_round_id)

    if not matchups:
        st.info("No matchups found for the current cup round.")
        return

    for matchup in matchups:
        display_matchup(matchup['player1'], matchup['player2'])
        st.markdown("---")
