# players_controllers/predictions_players_controller.py

from utils.db import get_connection

def get_rounds_for_predictions():
    """
    Returns a list of all rounds for which matches exist, ordered by round ID descending.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT r.id, r.name
        FROM rounds r
        JOIN matches m ON m.round_id = r.id
        GROUP BY r.id
        ORDER BY r.id DESC
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def get_user_predictions_by_round(player_id, round_id):
    """
    Get the user's predictions for matches in a specific round.
    
    Args:
        player_id (int): ID of the logged-in player
        round_id (int): ID of the selected round
    
    Returns:
        List of tuples: (home_team, away_team, user_pred, actual_score, points)
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            t1.name AS home_team,
            t2.name AS away_team,
            p.predicted_home_score || '-' || p.predicted_away_score AS prediction,
            CASE 
                WHEN m.status = 'finished' THEN 
                    COALESCE(m.home_score, '-') || '-' || COALESCE(m.away_score, '-')
                ELSE 'Pending'
            END AS actual_result,
            COALESCE(p.points_awarded, 0) AS points
        FROM predictions p
        JOIN matches m ON p.match_id = m.id
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        WHERE p.player_id = ? AND m.round_id = ?
        ORDER BY m.match_datetime
    """
    cursor.execute(query, (player_id, round_id))
    results = cursor.fetchall()
    conn.close()
    return results

def get_upcoming_matches():
    """
    Fetch all matches that have not been played yet (status = 'not played').

    Returns:
        List of tuples: (match_id, round_name, home_team, away_team, match_datetime)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            m.id,
            r.name AS round_name,
            th.name AS home_team,
            ta.name AS away_team,
            m.match_datetime
        FROM matches m
        JOIN teams th ON m.home_team_id = th.id
        JOIN teams ta ON m.away_team_id = ta.id
        JOIN rounds r ON m.round_id = r.id
        WHERE m.status = 'not played'
        ORDER BY m.match_datetime ASC
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


def save_prediction(player_id, match_id, prediction_str):
    """
    Save the prediction for a specific match by a player.
    
    Format of prediction_str must be 'X-Y', e.g. '2-1'
    
    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        predicted_home_score, predicted_away_score = map(int, prediction_str.strip().split("-"))
    except ValueError:
        return False, "❌ Invalid format! Please enter predictions as 'X-Y', e.g. '2-1'."

    conn = get_connection()
    cursor = conn.cursor()

    # Check if prediction already exists
    cursor.execute("""
        SELECT 1 FROM predictions WHERE player_id = ? AND match_id = ?
    """, (player_id, match_id))
    if cursor.fetchone():
        conn.close()
        return False, "⚠️ You have already submitted a prediction for this match."

    # Insert prediction
    cursor.execute("""
        INSERT INTO predictions (player_id, match_id, predicted_home_score, predicted_away_score)
        VALUES (?, ?, ?, ?)
    """, (player_id, match_id, predicted_home_score, predicted_away_score))

    conn.commit()
    conn.close()
    return True, "✅ Prediction saved successfully!"

def get_upcoming_matches_grouped_by_round(player_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            m.id AS match_id,
            t1.name AS home_team,
            t2.name AS away_team,
            m.match_datetime,
            m.status,
            r.name AS round_name,
            p.predicted_home_score AS predicted_home,
            p.predicted_away_score AS predicted_away,
            m.home_score,
            m.away_score,
            p.points_awarded
        FROM matches m
        JOIN rounds r ON m.round_id = r.id
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        LEFT JOIN predictions p ON m.id = p.match_id AND p.player_id = ?
        WHERE m.status IN ('not played', 'finished', 'live')
        ORDER BY m.match_datetime ASC
    """


    cursor.execute(query, (player_id,))
    rows = cursor.fetchall()
    conn.close()

    grouped = {}
    for row in rows:
        match = {
            "match_id": row[0],
            "home_team": row[1],
            "away_team": row[2],
            "match_datetime": row[3],
            "status": row[4],
            "predicted_home": row[6],
            "predicted_away": row[7],
            "home_score": row[8],
            "away_score": row[9],
            "earned_points": row[10]  # ✅ Correct column name
        }
        round_name = row[5]
        grouped.setdefault(round_name, []).append(match)

    return grouped



def save_predictions_batch(player_id, prediction_inputs):
    from datetime import datetime
    import re
    conn = get_connection()
    cursor = conn.cursor()

    results = []

    for match_id, value in prediction_inputs.items():
        match_id = int(match_id)
        value = value.strip()

        if not re.match(r"^\d+-\d+$", value):
            results.append((False, f"Invalid format for match {match_id}. Use format '2-1'."))
            continue

        try:
            predicted_home, predicted_away = map(int, value.split("-"))
        except ValueError:
            results.append((False, f"Failed to parse prediction for match {match_id}."))
            continue

        cursor.execute("SELECT status FROM matches WHERE id = ?", (match_id,))
        row = cursor.fetchone()
        if not row or row[0] != "not played":
            results.append((False, f"Match {match_id} is already played or doesn't exist."))
            continue

        cursor.execute("SELECT id FROM predictions WHERE player_id = ? AND match_id = ?", (player_id, match_id))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE predictions
                SET predicted_home_score = ?, predicted_away_score = ?
                WHERE player_id = ? AND match_id = ?
            """, (predicted_home, predicted_away, player_id, match_id))
        else:
            cursor.execute("""
                INSERT INTO predictions (player_id, match_id, predicted_home_score, predicted_away_score)
                VALUES (?, ?, ?, ?)
            """, (player_id, match_id, predicted_home, predicted_away))

        results.append((True, f"Prediction saved for match {match_id}"))

    conn.commit()
    conn.close()
    return results