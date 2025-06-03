import sqlite3

DB_NAME = "football_game.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def get_all_players():
    with get_connection() as conn:
        return conn.execute("SELECT id, name FROM players WHERE role = 'user'").fetchall()

def get_all_rounds():
    with get_connection() as conn:
        query = """
        SELECT rounds.id, rounds.name
        FROM rounds
        GROUP BY rounds.name
        ORDER BY rounds.name
        """
        return conn.execute(query).fetchall()

def get_round_ids_by_name(round_name):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM rounds WHERE name = ?", (round_name,))
        return [r[0] for r in c.fetchall()]

def get_matches_by_round(round_id):
    with get_connection() as conn:
        c = conn.cursor()

        # Get round name by ID
        c.execute("SELECT name FROM rounds WHERE id = ?", (round_id,))
        row = c.fetchone()
        if not row:
            return []
        round_name = row[0]

        # Get all round IDs with this name (ignore competition)
        round_ids = get_round_ids_by_name(round_name)
        placeholders = ",".join("?" * len(round_ids))

        query = f"""
        SELECT m.id, ht.name, at.name
        FROM matches m
        JOIN teams ht ON m.home_team_id = ht.id
        JOIN teams at ON m.away_team_id = at.id
        WHERE m.round_id IN ({placeholders})
        ORDER BY m.match_datetime ASC
        """
        c.execute(query, round_ids)
        return c.fetchall()

def get_predictions_and_points(round_id):
    with get_connection() as conn:
        c = conn.cursor()

        # Get round name by ID
        c.execute("SELECT name FROM rounds WHERE id = ?", (round_id,))
        row = c.fetchone()
        if not row:
            return {}
        round_name = row[0]

        # Get all round IDs with this name
        round_ids = get_round_ids_by_name(round_name)
        placeholders = ",".join("?" * len(round_ids))

        query = f"""
        SELECT p.player_id, p.match_id,
               p.predicted_home_score || '-' || p.predicted_away_score AS prediction,
               p.points_awarded
        FROM predictions p
        JOIN matches m ON p.match_id = m.id
        WHERE m.round_id IN ({placeholders})
        """
        c.execute(query, round_ids)
        rows = c.fetchall()
        return {(row[0], row[1]): (row[2], row[3]) for row in rows}

def get_actual_results(round_id):
    with get_connection() as conn:
        c = conn.cursor()

        # Get round name by ID
        c.execute("SELECT name FROM rounds WHERE id = ?", (round_id,))
        row = c.fetchone()
        if not row:
            return {}
        round_name = row[0]

        # Get all round IDs with this name
        round_ids = get_round_ids_by_name(round_name)
        placeholders = ",".join("?" * len(round_ids))

        query = f"""
        SELECT m.id,
               CASE WHEN m.home_score IS NOT NULL AND m.away_score IS NOT NULL
                    THEN m.home_score || '-' || m.away_score
                    ELSE '-'
               END as actual_result
        FROM matches m
        WHERE m.round_id IN ({placeholders})
        """
        c.execute(query, round_ids)
        rows = c.fetchall()
        return {row[0]: row[1] for row in rows}

def get_overall_points():
    with get_connection() as conn:
        c = conn.cursor()
        query = """
        SELECT pl.name, SUM(p.points_awarded) AS total_points
        FROM predictions p
        JOIN players pl ON p.player_id = pl.id
        GROUP BY pl.id
        ORDER BY total_points DESC
        """
        c.execute(query)
        return c.fetchall()
