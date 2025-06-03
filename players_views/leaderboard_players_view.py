import streamlit as st
import pandas as pd
from players_controllers import leaderboard_players_controller as lpc
from streamlit_lottie import st_lottie
from utils.lottie_loader import load_lottie_url

def leaderboard_view_player():
    st.markdown("<h2 style='color:#FFD700;'>🏆 Global Leaderboard</h2>", unsafe_allow_html=True)
    st.markdown("See how you rank among other legends of prediction!")

    # 🔄 Top Lottie Animation
    anim_url = "https://lottie.host/5e833fc5-0620-4e7d-8fd1-4dfbc7582b7b/aWy5uQ6DJu.json"
    lottie = load_lottie_url(anim_url)
    if lottie:
        st_lottie(lottie, height=180, speed=1.2, key="leaderboard_lottie")

    scores = lpc.get_players_leaderboard()
    user = st.session_state.get("user")
    player_name = user["username"] if user else None

    df = pd.DataFrame(scores, columns=["Player", "Total Points"])
    df["Rank"] = df["Total Points"].rank(method="min", ascending=False).astype(int)
    df = df.sort_values(by=["Total Points", "Player"], ascending=[False, True]).reset_index(drop=True)

    # 🎖️ Medals
    medals = ["👑", "🥈", "🥉"]
    df["Player"] = df.apply(
        lambda row: f"{medals[row['Rank']-1]} {row['Player']}" if row["Rank"] <= 3 
        else ("😔 " + row["Player"] if row["Player"] == player_name and row['Rank'] > 3 else row["Player"]), axis=1
    )

    # 📣 Personal Highlight
    my_row = df[df["Player"].str.contains(player_name, case=False, na=False)].iloc[0]
    my_rank = my_row["Rank"]
    my_points = my_row["Total Points"]

    # 🌈 Custom style
    st.markdown("""
        <style>
        .gradient-box {
            background: linear-gradient(to right, #ffd700, #ff8c00, #ffa500);
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0px 0px 12px 4px rgba(255, 215, 0, 0.7);
            margin-bottom: 1.5rem;
            text-align: center;
            color: black;
            font-size: 1.5rem;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # 🎉 Personal Result Card
    st.markdown(f"""
        <div class='gradient-box'>
            🔥 <span style='font-size:2rem;'>Your Rank:</span> <span style='font-size:2.2rem;'>#{my_rank}</span><br>
            🌟 <span style='font-size:1.5rem;'>Total Points:</span> <span style='font-size:1.5rem;'>{my_points}</span><br>
            {"🥳 You're in the top 3! Keep it up!" if my_rank <= 3 else "🚀 Keep pushing to reach the top!"}
        </div>
    """, unsafe_allow_html=True)

    # 💎 Highlight row function
    def highlight_user(row):
        player_raw = row["Player"]
        if player_name and player_name.lower() in player_raw.lower():
            return ['background-color: #44475a; color: #f1fa8c; font-weight: bold;'] * len(row)
        else:
            return [''] * len(row)

    # 💎 Display Leaderboard with styling
    styled_df = df[["Rank", "Player", "Total Points"]].style

    styled_df = styled_df.applymap(
        lambda val: 'color: gold; font-weight: bold;' if isinstance(val, str) and '👑' in val else ''
    ).applymap(
        lambda val: 'color: silver;' if isinstance(val, str) and '🥈' in val else ''
    ).applymap(
        lambda val: 'color: #cd7f32;' if isinstance(val, str) and '🥉' in val else ''
    ).applymap(
        lambda val: 'color: gray; font-style: italic;' if isinstance(val, str) and '😔' in val else ''
    ).apply(highlight_user, axis=1)

    st.dataframe(styled_df, use_container_width=True)
