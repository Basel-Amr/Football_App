import streamlit as st
from controllers import predictions_controller as pc
import pandas as pd

def predictions_view():
    st.title("⚽ Predictions Dashboard")

    # Step 1: Load all unique round names (e.g. "Round 1", "Round 2", ...)
    round_names = pc.get_all_round_names()
    selected_round_name = st.selectbox("Select Round", round_names)

    # Step 2: Load matches and players for this round name (across competitions)
    matches = pc.get_matches_by_round_name(selected_round_name)
    players = pc.get_all_players()
    predictions = pc.get_predictions_by_round_name(selected_round_name)

    player_ids = [p[0] for p in players]
    player_names = [p[1] for p in players]

    st.subheader("📋 Predictions Table")

    # Step 3: Build editable table data
    table_data = []
    for match in matches:
        match_id, home_team, away_team, actual_home, actual_away = match
        row = {
            "Match": f"{home_team} vs {away_team}",
        }
        for player_id, player_name in zip(player_ids, player_names):
            pred = predictions.get((player_id, match_id), (None, None))
            if pred[0] is not None and pred[1] is not None:
                row[player_name] = f"{pred[0]}-{pred[1]}"
            else:
                row[player_name] = ""

        # Actual result last column
        if actual_home is not None and actual_away is not None:
            row["Actual Result"] = f"{actual_home}-{actual_away}"
        else:
            row["Actual Result"] = ""

        table_data.append(row)

    df = pd.DataFrame(table_data)

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        key="predictions_editor"
    )

    # Step 4: Save & Calculate points on button press
    if st.button("💾 Save & Calculate Points"):
        match_results = {}
        prediction_inputs = {}

        for i, match in enumerate(matches):
            match_id = match[0]

            # Parse actual result
            try:
                actual_str = edited_df.at[i, "Actual Result"]
                actual_home, actual_away = map(int, actual_str.strip().split("-"))
                match_results[match_id] = (actual_home, actual_away)
            except:
                continue  # invalid or empty

            # Parse predictions per player
            for player_id, player_name in zip(player_ids, player_names):
                try:
                    pred_str = edited_df.at[i, player_name]
                    phs, pas = map(int, pred_str.strip().split("-"))
                    prediction_inputs[(player_id, match_id)] = (phs, pas)
                except:
                    continue  # invalid or empty

        # Save to DB and calculate points
        pc.save_predictions_and_scores(selected_round_name, match_results, prediction_inputs)
        pc.calculate_and_store_points(selected_round_name)
        st.success("✅ Predictions and scores saved. Points calculated!")
