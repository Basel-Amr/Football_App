# controllers/cup_controller.py

import sqlite3
from utils.db import get_connection


def get_current_cup_round_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM rounds WHERE is_current = 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_round_name(round_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM rounds WHERE id = ?", (round_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else f"Round {round_id}"


def get_player_points(player_id, cup_round_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT COALESCE(SUM(p.points_awarded), 0)
        FROM predictions p
        JOIN matches m ON p.match_id = m.id
        WHERE p.player_id = ?
    """

    params = [player_id]

    if cup_round_id:
        query += " AND m.cup_round_id = ?"
        params.append(cup_round_id)

    cursor.execute(query, tuple(params))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0


def get_cup_matchups_with_points(cup_round_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cm.id, 
               p1.id, p1.name,
               p2.id, p2.name,
               cm.winner_id
        FROM cup_matchups cm
        LEFT JOIN players p1 ON cm.player1_id = p1.id
        LEFT JOIN players p2 ON cm.player2_id = p2.id
        WHERE cm.cup_round_id = ?
          AND (cm.player1_id IS NOT NULL OR cm.player2_id IS NOT NULL)
        ORDER BY cm.id
    """, (cup_round_id,))

    matchups = []
    for row in cursor.fetchall():
        _, p1_id, p1_name, p2_id, p2_name, winner_id = row

        player1 = {'id': p1_id, 'name': p1_name, 'points': get_player_points(p1_id, cup_round_id)} if p1_id else None
        player2 = {'id': p2_id, 'name': p2_name, 'points': get_player_points(p2_id, cup_round_id)} if p2_id else None

        matchups.append({'player1': player1, 'player2': player2, 'winner_id': winner_id})

    conn.close()
    return matchups
