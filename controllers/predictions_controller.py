import sqlite3

DB_NAME = "football_game.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def get_all_players():
    with get_connection() as conn:
        return conn.execute("SELECT id, name FROM players WHERE role = 'user'").fetchall()

def get_all_round_names():
    with get_connection() as conn:
        query = "SELECT DISTINCT name FROM rounds ORDER BY name"
        return [row[0] for row in conn.execute(query).fetchall()]

def get_matches_by_round_name(round_name):
    with get_connection() as conn:
        query = """
        SELECT 
            matches.id,
            ht.name AS home_team,
            at.name AS away_team,
            matches.home_score,
            matches.away_score
        FROM matches
        JOIN rounds ON matches.round_id = rounds.id
        JOIN teams ht ON matches.home_team_id = ht.id
        JOIN teams at ON matches.away_team_id = at.id
        WHERE rounds.name = ?
        ORDER BY matches.match_datetime ASC
        """
        return conn.execute(query, (round_name,)).fetchall()

def get_predictions_by_round_name(round_name):
    with get_connection() as conn:
        query = """
        SELECT p.player_id, p.match_id, p.predicted_home_score, p.predicted_away_score
        FROM predictions p
        JOIN matches m ON m.id = p.match_id
        JOIN rounds r ON m.round_id = r.id
        WHERE r.name = ?
        """
        rows = conn.execute(query, (round_name,)).fetchall()
        return {(row[0], row[1]): (row[2], row[3]) for row in rows}

def save_predictions_and_scores(round_name, match_results, predictions):
    with get_connection() as conn:
        cursor = conn.cursor()

        # Update actual match results and set status to 'finished' if actual results exist
        for match_id, (home, away) in match_results.items():
            cursor.execute(
                "UPDATE matches SET home_score = ?, away_score = ?, status = ? WHERE id = ?",
                (home, away, "finished", match_id)
            )

        # Update or insert predictions
        for (player_id, match_id), (phs, pas) in predictions.items():
            cursor.execute(""" 
                INSERT INTO predictions (player_id, match_id, predicted_home_score, predicted_away_score)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(player_id, match_id) DO UPDATE SET
                    predicted_home_score=excluded.predicted_home_score,
                    predicted_away_score=excluded.predicted_away_score
            """, (player_id, match_id, phs, pas))
        conn.commit()


def calculate_and_store_points(round_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        # Get all predictions for that round (by round name)
        cursor.execute("""
            SELECT p.id, p.player_id, p.match_id, p.predicted_home_score, p.predicted_away_score,
                   m.home_score, m.away_score
            FROM predictions p
            JOIN matches m ON p.match_id = m.id
            JOIN rounds r ON m.round_id = r.id
            WHERE r.name = ?
        """, (round_name,))

        updates = []
        for row in cursor.fetchall():
            pred_id, _, _, phs, pas, ahs, aas = row
            if ahs is None or aas is None:
                continue  # Match not played yet
            if phs == ahs and pas == aas:
                points = 3
            elif (phs > pas and ahs > aas) or (phs < pas and ahs < aas) or (phs == pas and ahs == aas):
                points = 1
            else:
                points = 0
            updates.append((points, pred_id))

        cursor.executemany("UPDATE predictions SET points_awarded = ? WHERE id = ?", updates)
        conn.commit()
