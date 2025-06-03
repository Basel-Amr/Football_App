import sqlite3

def get_connection():
    return sqlite3.connect("football_game.db", check_same_thread=False)
