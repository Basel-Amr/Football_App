# players_controllers/leaderboard_players_controller.py

from utils.db import get_connection

def get_players_leaderboard():
    """
    Returns the leaderboard with each user's total points.
    
    Returns:
        List of tuples: (player_name, total_points)
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            pl.name AS player_name,
            COALESCE(SUM(p.points_awarded), 0) AS total_points
        FROM players pl
        LEFT JOIN predictions p ON p.player_id = pl.id
        WHERE pl.role = 'user'
        GROUP BY pl.id
        ORDER BY total_points DESC, pl.name ASC
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results
