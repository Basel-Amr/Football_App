"""
Football Prediction Game - Database Setup Script
Author: Basel Amr Barakat
Email: baselamr52@gmail.com

This script creates the SQLite database with the following tables:
- players
- competitions
- rounds
- teams
- matches
- predictions
- audit_log
- cups
- cup_rounds
- cup_matches
- achievements
- user_achievements

Run this once to initialize your database.
"""

import sqlite3
import os

# Database file name
DB_NAME = "football_game.db"

# Optional: Uncomment to reset the database
# if os.path.exists(DB_NAME):
#     os.remove(DB_NAME)

# Connect to the database (it will be created if it doesn't exist)
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Step 1: Drop tables if needed (optional cleanup)
# cursor.executescript("""
# DROP TABLE IF EXISTS user_achievements;
# DROP TABLE IF EXISTS achievements;
# DROP TABLE IF EXISTS cup_matches;
# DROP TABLE IF EXISTS cup_rounds;
# DROP TABLE IF EXISTS cups;
# DROP TABLE IF EXISTS predictions;
# DROP TABLE IF EXISTS matches;
# DROP TABLE IF EXISTS teams;
# DROP TABLE IF EXISTS rounds;
# DROP TABLE IF EXISTS competitions;
# DROP TABLE IF EXISTS audit_log;
# DROP TABLE IF EXISTS players;
# """)

# Step 2: Create all tables
cursor.executescript("""

-- Players Table
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'user')) NOT NULL
);

-- Competitions Table (leagues or cups)
CREATE TABLE IF NOT EXISTS competitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Rounds Table (each week or stage in a competition)
CREATE TABLE IF NOT EXISTS rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    competition_id INTEGER NOT NULL,
    FOREIGN KEY (competition_id) REFERENCES competitions(id),
    UNIQUE(name, competition_id)
);

-- Teams Table
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Matches Table
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    round_id INTEGER,
    competition_id INTEGER NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    match_datetime TEXT NOT NULL,
    status TEXT CHECK(status IN ('not played', 'live', 'finished')) NOT NULL DEFAULT 'not played',
    home_score INTEGER DEFAULT NULL,
    away_score INTEGER DEFAULT NULL,
    FOREIGN KEY (round_id) REFERENCES rounds(id),
    FOREIGN KEY (competition_id) REFERENCES competitions(id),
    FOREIGN KEY (home_team_id) REFERENCES teams(id),
    FOREIGN KEY (away_team_id) REFERENCES teams(id)
);

-- Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    predicted_home_score INTEGER NOT NULL,
    predicted_away_score INTEGER NOT NULL,
    points_awarded INTEGER DEFAULT NULL,
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (match_id) REFERENCES matches(id),
    UNIQUE (player_id, match_id)
);

-- Audit Log Table
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER,
    action TEXT,
    target_player_id INTEGER,
    target_match_id INTEGER,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES players(id),
    FOREIGN KEY (target_player_id) REFERENCES players(id),
    FOREIGN KEY (target_match_id) REFERENCES matches(id)
);

-- Cups Table
CREATE TABLE IF NOT EXISTS cups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    competition_id INTEGER NOT NULL,
    start_round_id INTEGER NOT NULL,
    FOREIGN KEY (competition_id) REFERENCES competitions(id),
    FOREIGN KEY (start_round_id) REFERENCES rounds(id)
);

-- Cup Rounds Table
CREATE TABLE IF NOT EXISTS cup_rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cup_id INTEGER NOT NULL,
    name TEXT NOT NULL, -- e.g., Round of 16, Quarter Final
    order_number INTEGER NOT NULL,
    FOREIGN KEY (cup_id) REFERENCES cups(id),
    UNIQUE(cup_id, order_number)
);

-- Cup Matches Table (was cup_matchups)
CREATE TABLE IF NOT EXISTS cup_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cup_round_id INTEGER NOT NULL,
    player1_id INTEGER NOT NULL,
    player2_id INTEGER,         -- Nullable if it's a bye
    winner_id INTEGER,          -- Set after match played
    round_number INTEGER NOT NULL,  -- Corresponding gameweek or round
    FOREIGN KEY (cup_round_id) REFERENCES cup_rounds(id),
    FOREIGN KEY (player1_id) REFERENCES players(id),
    FOREIGN KEY (player2_id) REFERENCES players(id),
    FOREIGN KEY (winner_id) REFERENCES players(id)
);

-- Achievements Table
CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,         -- e.g., 'Cup', 'League'
    description TEXT
);

-- User Achievements Table
CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    cup_round_id INTEGER,             -- Nullable if achievement is not cup-related
    year INTEGER NOT NULL,            -- Year or season
    FOREIGN KEY (user_id) REFERENCES players(id),
    FOREIGN KEY (achievement_id) REFERENCES achievements(id),
    FOREIGN KEY (cup_round_id) REFERENCES cup_rounds(id)
);
""")

# Final Step: Confirmation
print("✅ Database and tables created successfully!")

# Commit and close connection
conn.commit()
conn.close()
