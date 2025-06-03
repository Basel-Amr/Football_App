from utils.db import get_connection

def get_player_title_summary():
    """
    Returns a list of players with the count of cups and leagues they've won.
    Achievement names are 'League Winner' and 'Cup Winner' (per your DB).
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        p.name,
        a.name AS achievement_name,
        COUNT(ua.id) AS count
    FROM players p
    LEFT JOIN user_achievements ua ON p.id = ua.user_id
    LEFT JOIN achievements a ON ua.achievement_id = a.id
    GROUP BY p.id, a.name
    ORDER BY p.name;
    """

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    achievements_dict = {}

    for name, achievement, count in results:
        if name not in achievements_dict:
            achievements_dict[name] = {'League Winner': 0, 'Cup Winner': 0}
        if achievement:
            achievements_dict[name][achievement] = count

    # Convert dict to list of dicts for easier use in views
    summary_list = []
    for player, ach in achievements_dict.items():
        summary_list.append({
            "player_name": player,
            "leagues_won": ach.get("League Winner", 0),
            "cups_won": ach.get("Cup Winner", 0)
        })

    return summary_list


def get_league_winners():
    """
    Return detailed league winners per year with achievement name 'League Winner'.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        ua.year,
        p.name AS player_name,
        a.name AS achievement_name,
        a.description
    FROM user_achievements ua
    JOIN players p ON ua.user_id = p.id
    JOIN achievements a ON ua.achievement_id = a.id
    WHERE a.name = 'League Winner'
    ORDER BY ua.year DESC;
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "year": r[0],
            "player_name": r[1],
            "achievement_name": r[2],
            "description": r[3]
        }
        for r in rows
    ]
