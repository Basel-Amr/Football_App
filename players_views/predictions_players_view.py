import streamlit as st
from players_controllers.predictions_players_controller import (
    get_upcoming_matches_grouped_by_round,
    save_predictions_batch
)

def prediction_view_player():
    st.title("📝 My Predictions")
    st.markdown("### 🔮 Predict Upcoming Matches Round by Round")
    st.info("📌 **Format:** `2-1` (home score - away score). You can only edit matches that haven’t started.")
    st.markdown("---")

    user = st.session_state.get("user")
    if not user:
        st.error("❌ You must be logged in to view this page.")
        return

    player_id = user["id"]
    grouped_matches = get_upcoming_matches_grouped_by_round(player_id)

    if not grouped_matches:
        st.success("✅ No upcoming matches. You’re all caught up!")
        return

    prediction_inputs = {}

    # Match card styles
    st.markdown("""
        <style>
            .match-block {
                background-color: #1e1e1e;
                padding: 1rem;
                border-radius: 12px;
                margin-bottom: 1.2rem;
                border: 1px solid #333;
            }
            .match-title {
                font-size: 1.4rem;
                font-weight: bold;
                color: #00ffff;
            }
            .match-meta {
                font-size: 0.9rem;
                color: #ccc;
                margin-top: 0.3rem;
                margin-bottom: 0.4rem;
            }
            .perfect {
                background-color: #004d00;
                color: #00ff00;
                padding: 0.4rem 0.8rem;
                border-radius: 8px;
                font-weight: bold;
            }
            .good {
                background-color: #4d3b00;
                color: #ffc107;
                padding: 0.4rem 0.8rem;
                border-radius: 8px;
                font-weight: bold;
            }
            .wrong {
                background-color: #330000;
                color: #ff4d4d;
                padding: 0.4rem 0.8rem;
                border-radius: 8px;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)

    def evaluate_prediction(actual_home, actual_away, predicted_home, predicted_away):
        if actual_home == predicted_home and actual_away == predicted_away:
            return "perfect"
        elif (actual_home - actual_away) * (predicted_home - predicted_away) > 0 or \
             (actual_home == actual_away and predicted_home == predicted_away):
            return "good"
        else:
            return "wrong"

    status_display = {
        "not played": '<span style="background-color:#005f73; color:white; padding:4px 10px; border-radius:6px;">⏳ Not Played</span>',
        "finished": '<span style="background-color:#007f5f; color:white; padding:4px 10px; border-radius:6px;">✅ Finished</span>',
        "live": '<span style="background-color:#ffb703; color:black; padding:4px 10px; border-radius:6px;">📺 Live Now</span>',
        "cancelled": '<span style="background-color:#9e2a2b; color:white; padding:4px 10px; border-radius:6px;">🚫 Cancelled</span>',
        "postponed": '<span style="background-color:#6a0572; color:white; padding:4px 10px; border-radius:6px;">⏸️ Postponed</span>'
    }

    for round_name, matches in grouped_matches.items():
        with st.expander(f"🗓️ Round: {round_name}", expanded=False):
            for match in matches:
                match_id = match["match_id"]
                home_team = match["home_team"]
                away_team = match["away_team"]
                match_datetime = match["match_datetime"]
                status = match["status"]
                predicted_home = match["predicted_home"]
                predicted_away = match["predicted_away"]
                actual_home = match.get("home_score")
                actual_away = match.get("away_score")
                earned_points = match.get("earned_points")

                st.markdown('<div class="match-block">', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="match-title">⚽ {home_team} <span style="color:#999">vs</span> {away_team}</div>',
                    unsafe_allow_html=True
                )
                st.markdown(f'<div class="match-meta">🕒 {match_datetime}</div>', unsafe_allow_html=True)

                status_html = status_display.get(status.lower(), f'<span style="color:gray;">{status}</span>')
                st.markdown(f'<div class="match-meta">📌 Status: {status_html}</div>', unsafe_allow_html=True)

                if status == "not played":
                    default = f"{predicted_home}-{predicted_away}" if predicted_home is not None else ""
                    prediction = st.text_input(
                        f"✍️ Your Prediction for {home_team} vs {away_team}",
                        value=default,
                        placeholder="e.g., 2-1",
                        key=f"prediction_{match_id}"
                    )
                    prediction_inputs[match_id] = prediction
                else:
                    if predicted_home is not None:
                        st.markdown(f"**📝 Your Prediction:** `{predicted_home}-{predicted_away}`")
                        if actual_home is not None and actual_away is not None:
                            st.markdown(f"**🎯 Final Score:** `{actual_home}-{actual_away}`")
                            result_type = evaluate_prediction(actual_home, actual_away, predicted_home, predicted_away)
                            result_msg = {
                                "perfect": f'<div class="perfect">🎯 Perfect Prediction! +{earned_points} pts</div>',
                                "good": f'<div class="good">👍 Good Try! +{earned_points} pts</div>',
                                "wrong": f'<div class="wrong">❌ Missed Prediction. +{earned_points} pts</div>'
                            }
                            st.markdown(result_msg[result_type], unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ This match is marked as finished, but no final score is available yet.")
                    else:
                        st.warning("⚠️ You didn’t submit a prediction for this match.")

                st.markdown('</div>', unsafe_allow_html=True)

    if prediction_inputs:
        if st.button("✅ Submit All Predictions", use_container_width=True):
            # ✅ Only keep non-empty predictions
            cleaned_inputs = {k: v for k, v in prediction_inputs.items() if v.strip()}
            if not cleaned_inputs:
                st.warning("⚠️ You didn’t enter any predictions to submit.")
            else:
                results = save_predictions_batch(player_id, cleaned_inputs)
                if all(success for success, _ in results):
                    st.balloons()
                    st.success("🎉 All predictions saved successfully!")
                else:
                    for success, msg in results:
                        if not success:
                            st.warning(msg)
