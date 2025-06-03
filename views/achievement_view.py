import streamlit as st
import pandas as pd
from controllers.achievement_controller import get_player_title_summary, get_league_winners
from streamlit_lottie import st_lottie
import requests

def load_lottie_url(url: str):
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return None
        return res.json()
    except:
        return None

def achievement_view():
    st.title("🏆 Football Prediction Game Achievements")

    user = st.session_state.get("user", {}).get("username", "")

    st.header("🎖️ Summary: Titles Won by Players")
    summary = get_player_title_summary()

    league_emoji = "🥇"
    cup_emoji = "🏆"
    crown = "👑"

    if summary:
        df_summary = pd.DataFrame(summary)
        df_summary = df_summary.rename(columns={
            "player_name": "Player",
            "cups_won": "Cups Won",
            "leagues_won": "Leagues Won"
        })

        df_summary["Total"] = df_summary["Cups Won"] + df_summary["Leagues Won"]
        df_summary = df_summary.sort_values(by=["Leagues Won", "Cups Won"], ascending=False)

        top_player = df_summary.iloc[0]["Player"]

        cols = st.columns(len(df_summary))
        for idx, row in df_summary.iterrows():
            is_user = row['Player'] == user
            is_leader = row['Player'] == top_player

            glow = "0 0 20px 5px gold" if is_user else "none"
            border = "4px solid #FFD700" if is_user else "2px solid #ccc"
            emoji_prefix = crown if is_user else ("🥇" if is_leader else "⚽")

            with cols[idx]:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
                    border-radius: 15px;
                    padding: 20px;
                    text-align:center;
                    box-shadow: {glow};
                    border: {border};
                    transition: all 0.3s ease-in-out;
                ">
                    <h2 style="color:#8B4513;">{emoji_prefix} {row['Player']}</h2>
                    <p style="font-size:18px; color:#2F4F4F; margin-bottom:10px;">
                        {league_emoji} <strong style='color:#FFD700;'>{row['Leagues Won']}</strong> Leagues<br>
                        {cup_emoji} <strong style='color:#DAA520;'>{row['Cups Won']}</strong> Cups
                    </p>
                </div>
                """, unsafe_allow_html=True)

        # 🎯 Show achievement animation if user has any titles
        if user in df_summary["Player"].values:
            st.subheader("🏅 You're a Champion!")
            st.markdown("Celebrate your victories with this animated badge of honor!")

            # Achievement / Trophy animation
            # 🏆 Trophy animation for champions
            animation_url = "https://assets10.lottiefiles.com/packages/lf20_touohxv0.json"
            animation = load_lottie_url(animation_url)

            if animation:
                st_lottie(animation, height=300, speed=1, loop=False)
            else:
                st.warning("Could not load achievement animation.")
    else:
        st.info("No achievements found yet.")

    st.markdown("---")
    st.header("🏅 Detailed League Winners by Year")

    winners = get_league_winners()

    if winners:
        for winner in winners:
            is_user = winner["player_name"] == user
            bg = "#FFF5E1" if is_user else "#FFFAF0"
            border_color = "#FFD700" if is_user else "#F5DEB3"
            box_shadow = "0 4px 16px rgba(255,215,0,0.4)" if is_user else "0 4px 12px rgba(255,215,0,0.2)"
            ribbon = "🎖️" if is_user else "🎉"

            st.markdown(f"""
                <div style="
                    background-color:{bg};
                    border-left: 6px solid {border_color};
                    margin-bottom: 20px;
                    padding: 15px 20px;
                    border-radius: 10px;
                    box-shadow: {box_shadow};
                ">
                    <h3 style="color:#B8860B;">
                        {ribbon} {winner['year']} League Winner: 
                        <span style="color:#DAA520;">{winner['player_name']}</span>
                    </h3>
                    <p style="font-style: italic; color:#555;">
                        {winner['description'] if winner['description'] else 'No description available.'}
                    </p>
                </div>
            """, unsafe_allow_html=True)

        st.snow()
    else:
        st.info("No league winners recorded yet.")
