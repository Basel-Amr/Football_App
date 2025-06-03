import streamlit as st
import pandas as pd
from streamlit_lottie import st_lottie
import requests
from controllers import leaderboard_controller as lc


def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None


def leaderboard_view():
    # ---------------------- Page Header ---------------------- #
    st.markdown("## 🏆 **Leaderboard Dashboard**")
    st.markdown("Welcome to the Football Prediction Leaderboard! Keep track of who’s leading and how everyone's doing week by week.")

    # Load Lottie animation
    lottie_url = "https://assets5.lottiefiles.com/packages/lf20_zrqthn6o.json"  # football player animation
    lottie_football = load_lottie_url(lottie_url)

    if lottie_football:
        st_lottie(lottie_football, height=200, key="football")
    else:
        st.info("⚽ (Animation couldn't load, but the game is still on!)")

    # ------------------- Overall Leaderboard ------------------- #
    st.markdown("---")
    st.markdown("### 🏅 **Overall Points**")

    overall_scores = lc.get_overall_points()
    overall_df = pd.DataFrame(overall_scores, columns=["Player", "Total Points"])
    overall_df["Total Points"] = pd.to_numeric(overall_df["Total Points"], errors='coerce').fillna(0)
    overall_df.sort_values(by="Total Points", ascending=False, inplace=True)
    overall_df.reset_index(drop=True, inplace=True)

    # Add medals and crown for top players + owl for last player
    medals = ["👑🥇", "🥈", "🥉"]
    total_rows = len(overall_df)

    def add_medals(row):
        idx = row.name
        if idx < 3:
            return f"{medals[idx]} {row['Player']}"
        elif idx == total_rows - 1:
            return f"🦉 {row['Player']}"
        else:
            return row['Player']

    overall_df["Player"] = [add_medals(row) for _, row in overall_df.iterrows()]

    # Medal colors for top 3 & last player highlight
    def highlight_rows(row):
        idx = row.name
        n = total_rows
        if idx == 0:
            color = "#FFD700"  # Gold
        elif idx == 1:
            color = "#C0C0C0"  # Silver
        elif idx == 2:
            color = "#CD7F32"  # Bronze
        elif idx == n - 1:
            color = "#8B4513"  # Dark brown for last player
        else:
            color = ""
        return [f'background-color: {color}' if color else '' for _ in row]

    # Apply consistent color for whole row for top 3 and last player
    styled_df = (
        overall_df.style
        .apply(highlight_rows, axis=1)
        .set_properties(**{'padding-left': '15px', 'font-size': '16px'})
        .set_table_styles([
            {'selector': 'th', 'props': [('font-size', '18px'), ('text-align', 'center')]},
            {'selector': 'td', 'props': [('font-size', '16px'), ('padding', '8px 12px')]},
            {'selector': 'thead tr th', 'props': [('background-color', '#1f77b4'), ('color', 'white')]},
        ])
        .format({"Total Points": "{:.0f}"})
        .set_properties(subset=["Total Points"], **{'text-align': 'center'})
    )

    st.dataframe(styled_df, use_container_width=True)

    # ------------------ Round-specific Leaderboard ------------------ #
    st.markdown("---")
    st.markdown("### 📅 **Round Predictions & Results**")

    # Get rounds and let user select
    rounds = lc.get_all_rounds()
    round_options = {r[1]: r[0] for r in rounds}
    selected_round_label = st.selectbox("🔁 Select Round", list(round_options.keys()))
    selected_round_id = round_options[selected_round_label]

    # Fetch data for selected round
    players = lc.get_all_players()
    matches = lc.get_matches_by_round(selected_round_id)
    predictions = lc.get_predictions_and_points(selected_round_id)
    actual_results = lc.get_actual_results(selected_round_id)

    player_ids = [p[0] for p in players]
    player_names = [p[1] for p in players]

    # Build table showing all players even if no prediction
    table_data = []
    for match in matches:
        match_id, home_team, away_team = match
        row = {"Match": f"⚔️ {home_team} vs {away_team}"}

        for player_id, player_name in zip(player_ids, player_names):
            pred, pts = predictions.get((player_id, match_id), ("-", 0))
            row[player_name] = f"{pred} ({pts})"

        row["Actual Result"] = f"✅ {actual_results.get(match_id, '-')}"
        table_data.append(row)

    df = pd.DataFrame(table_data)

    # Reorder columns to place 'Match' first, then players, then 'Actual Result'
    cols = ["Match"] + player_names + ["Actual Result"]
    df = df[cols]

    st.subheader(f"📝 Round: {selected_round_label}")
    st.dataframe(df, use_container_width=True)

    # ------------------- Footer ------------------- #
    st.markdown("---")
