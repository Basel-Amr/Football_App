import datetime
import sqlite3
from typing import List, Tuple, Optional
import streamlit as st
from utils.db import get_connection


def _get_or_create(cursor: sqlite3.Cursor, table: str, name: str) -> int:
    """
    Retrieve the ID of a record by name from a given table.
    If it doesn't exist, insert it and return the new ID.
    """
    cursor.execute(f"SELECT id FROM {table} WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(f"INSERT INTO {table} (name) VALUES (?)", (name,))
    return cursor.lastrowid


def _get_or_create_team(cursor: sqlite3.Cursor, team_name: str) -> int:
    """Get or create a team record by name."""
    return _get_or_create(cursor, "teams", team_name)


def _get_or_create_competition(cursor: sqlite3.Cursor, competition_name: str) -> int:
    """Get or create a competition record by name."""
    return _get_or_create(cursor, "competitions", competition_name)


def _get_or_create_round(cursor: sqlite3.Cursor, round_name: str, competition_id: int) -> int:
    """
    Get or create a round record by name and competition ID.
    """
    cursor.execute(
        "SELECT id FROM rounds WHERE name = ? AND competition_id = ?", 
        (round_name, competition_id)
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(
        "INSERT INTO rounds (name, competition_id) VALUES (?, ?)", 
        (round_name, competition_id)
    )
    return cursor.lastrowid


def add_match(
    competition_name: str,
    home_team_name: str,
    away_team_name: str,
    match_date: datetime.datetime,
    status: str,
    home_score: Optional[int],
    away_score: Optional[int],
    round_num: int,
) -> None:
    """
    Add or update a match in the database. If the match already exists in the round, update its details.
    Raises:
        ValueError: If home and away teams are the same.
    """
    if home_team_name == away_team_name:
        raise ValueError("Home and Away teams cannot be the same.")

    conn = get_connection()
    try:
        cursor = conn.cursor()

        competition_id = _get_or_create_competition(cursor, competition_name)
        home_team_id = _get_or_create_team(cursor, home_team_name)
        away_team_id = _get_or_create_team(cursor, away_team_name)
        round_name = f"Round {round_num}"
        round_id = _get_or_create_round(cursor, round_name, competition_id)

        # Check if match already exists (home vs away or reverse)
        cursor.execute(
            """
            SELECT id FROM matches
            WHERE round_id = ?
              AND (
                (home_team_id = ? AND away_team_id = ?)
                OR
                (home_team_id = ? AND away_team_id = ?)
              )
            """,
            (round_id, home_team_id, away_team_id, away_team_id, home_team_id),
        )
        existing_match = cursor.fetchone()

        if existing_match:
            # Update existing match
            cursor.execute(
                """
                UPDATE matches
                SET match_datetime = ?, status = ?, home_score = ?, away_score = ?
                WHERE id = ?
                """,
                (
                    match_date.strftime("%Y-%m-%d %H:%M:%S"),
                    status,
                    home_score,
                    away_score,
                    existing_match[0],
                ),
            )
        else:
            # Insert new match
            cursor.execute(
                """
                INSERT INTO matches (
                    round_id, competition_id, home_team_id, away_team_id,
                    match_datetime, status, home_score, away_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    round_id,
                    competition_id,
                    home_team_id,
                    away_team_id,
                    match_date.strftime("%Y-%m-%d %H:%M:%S"),
                    status,
                    home_score,
                    away_score,
                ),
            )
        conn.commit()

    except sqlite3.Error as e:
        raise RuntimeError(f"Database error occurred: {e}")
    finally:
        conn.close()


def get_rounds(competition_name: str) -> List[int]:
    """
    Retrieve all round numbers for a specified competition.
    Returns an empty list if competition not found.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM competitions WHERE name = ?", (competition_name,))
        comp = cursor.fetchone()
        if not comp:
            return []

        comp_id = comp[0]
        cursor.execute("SELECT name FROM rounds WHERE competition_id = ? ORDER BY id", (comp_id,))
        rounds = [
            int(name.split()[1])
            for (name,) in cursor.fetchall()
            if name.startswith("Round ")
        ]
        return rounds
    finally:
        conn.close()


def get_matches_by_round(competition_name: str, round_number: int) -> List[Tuple]:
    """
    Fetch match details for a specific round in a competition.
    Returns empty list if competition or round not found.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM competitions WHERE name = ?", (competition_name,))
        comp = cursor.fetchone()
        if not comp:
            return []

        comp_id = comp[0]
        round_name = f"Round {round_number}"
        cursor.execute(
            "SELECT id FROM rounds WHERE name = ? AND competition_id = ?", (round_name, comp_id)
        )
        round_row = cursor.fetchone()
        if not round_row:
            return []

        round_id = round_row[0]
        cursor.execute(
            """
            SELECT m.id, ht.name, at.name, m.match_datetime,
                   m.status, m.home_score, m.away_score
            FROM matches m
            JOIN teams ht ON m.home_team_id = ht.id
            JOIN teams at ON m.away_team_id = at.id
            WHERE m.round_id = ?
            ORDER BY m.match_datetime
            """,
            (round_id,),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def update_match(
    match_id: int,
    status: str,
    home_score: int,
    away_score: int,
    match_datetime: Optional[datetime.datetime] = None,
) -> None:
    """
    Update match details such as status, score, and optionally datetime.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if match_datetime:
            cursor.execute(
                """
                UPDATE matches
                SET status = ?, home_score = ?, away_score = ?, match_datetime = ?
                WHERE id = ?
                """,
                (status, home_score, away_score, match_datetime, match_id),
            )
        else:
            cursor.execute(
                """
                UPDATE matches
                SET status = ?, home_score = ?, away_score = ?
                WHERE id = ?
                """,
                (status, home_score, away_score, match_id),
            )
        conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error occurred: {e}")
    finally:
        conn.close()


def delete_match(match_id: int) -> None:
    """
    Delete a match and all related data (e.g. predictions) by match ID.
    If the match's round becomes empty, delete the round too.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Step 1: Get the round_id of the match to be deleted
        cursor.execute("SELECT round_id FROM matches WHERE id = ?", (match_id,))
        result = cursor.fetchone()

        if result is None:
            raise ValueError(f"No match found with ID {match_id}")
        round_id = result[0]

        # Step 2: Delete related predictions
        cursor.execute("DELETE FROM predictions WHERE match_id = ?", (match_id,))

        # Add other related deletions here if necessary
        # Example: cursor.execute("DELETE FROM scores WHERE match_id = ?", (match_id,))

        # Step 3: Delete the match
        cursor.execute("DELETE FROM matches WHERE id = ?", (match_id,))

        # Step 4: Check if the round has any matches left
        cursor.execute("SELECT COUNT(*) FROM matches WHERE round_id = ?", (round_id,))
        match_count = cursor.fetchone()[0]

        # Step 5: If no matches left in the round, delete the round
        if match_count == 0:
            cursor.execute("DELETE FROM rounds WHERE id = ?", (round_id,))

        conn.commit()

    except sqlite3.Error as e:
        raise RuntimeError(f"Database error occurred: {e}")
    finally:
        conn.close()




def get_matches_by_round_id(round_id: int) -> List[Tuple]:
    """
    Retrieve matches for a given round ID, including competition and team names.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT m.id, c.name, ht.name, at.name, m.match_datetime,
                   m.status, m.home_score, m.away_score
            FROM matches m
            JOIN competitions c ON m.competition_id = c.id
            JOIN teams ht ON m.home_team_id = ht.id
            JOIN teams at ON m.away_team_id = at.id
            WHERE m.round_id = ?
            ORDER BY m.match_datetime
            """,
            (round_id,),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_all_rounds():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM rounds ORDER BY name")
    rounds = cursor.fetchall()
    conn.close()
    return rounds



def get_latest_round_num() -> int:
    """
    Get the highest round number across all competitions.
    Returns 1 if no rounds are present.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT MAX(CAST(SUBSTR(name, 7) AS INTEGER)) FROM rounds
            WHERE name LIKE 'Round %'
            """
        )
        max_round = cursor.fetchone()[0]
        return int(max_round) if max_round else 1
    finally:
        conn.close()


def get_all_competitions() -> List[str]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM competitions ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def handle_add_match(teams_by_league: dict) -> None:
    st.subheader("Add or Update Match")

    league = st.selectbox("Select League", list(teams_by_league.keys()))
    teams = teams_by_league[league]["teams"]

    home_team = st.selectbox("Home Team", teams)
    away_team = st.selectbox("Away Team", teams)

    if home_team == away_team:
        st.warning("Home and Away teams cannot be the same.")
        return

    competition_name = st.text_input("Competition Name", value=league)
    round_num = st.number_input(
        "Round Number", min_value=1, max_value=100, value=get_latest_round_num()
    )

    # Initialize session state once
    if "match_date" not in st.session_state:
        st.session_state.match_date = datetime.date.today()
    if "match_time" not in st.session_state:
        st.session_state.match_time = datetime.datetime.now().time()

    # Use session state to persist the user's input
    match_date = st.date_input("Match Date", value=st.session_state.match_date)
    match_time = st.time_input("Match Time", value=st.session_state.match_time)

    # Update session state with the latest user input
    st.session_state.match_date = match_date
    st.session_state.match_time = match_time

    match_datetime = datetime.datetime.combine(match_date, match_time)

    status = st.selectbox("Status", ["not played", "live", "finished"])
    home_score = None
    away_score = None

    if status in ("live", "finished"):
        home_score = st.number_input("Home Score", min_value=0, max_value=100, value=0)
        away_score = st.number_input("Away Score", min_value=0, max_value=100, value=0)

    if st.button("Add Match"):
        try:
            add_match(
                competition_name=competition_name,
                home_team_name=home_team,
                away_team_name=away_team,
                match_date=match_datetime,
                status=status,
                home_score=home_score,
                away_score=away_score,
                round_num=round_num,
            )
            st.success("Match added or updated successfully!")
        except Exception as e:
            st.error(f"Error adding/updating match: {e}")


def get_match_count_by_round_id(cursor: sqlite3.Cursor, round_id: int) -> int:
    """
    Return count of matches for a given round_id.
    """
    cursor.execute("SELECT COUNT(*) FROM matches WHERE round_id = ?", (round_id,))
    return cursor.fetchone()[0]

from typing import List, Tuple

def get_matches_by_round_name(round_name: str) -> List[Tuple]:
    """
    Retrieve all matches from all competitions for a given round name.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT m.id, c.name AS competition, ht.name AS home_team, at.name AS away_team,
                   m.match_datetime, m.status, m.home_score, m.away_score
            FROM matches m
            JOIN competitions c ON m.competition_id = c.id
            JOIN teams ht ON m.home_team_id = ht.id
            JOIN teams at ON m.away_team_id = at.id
            JOIN rounds r ON m.round_id = r.id
            WHERE r.name = ?
            ORDER BY m.match_datetime
            """,
            (round_name,),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_all_round_names() -> List[str]:
    """
    Retrieve all unique round names across competitions.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT name FROM rounds ORDER BY name")
        round_names = [row[0] for row in cursor.fetchall()]
        return round_names
    finally:
        conn.close()





def handle_view_matches() -> None:
    """
    View, update, and delete matches by round name,
    showing matches in a colorful, compact, table-like layout with smaller fonts,
    with update/delete as small icons inline,
    and delete rounds automatically if no matches remain.
    """
    st.subheader("⚽ View and Manage Matches")

    conn = get_connection()
    try:
        cursor = conn.cursor()

        round_names = get_all_round_names()
        if not round_names:
            st.info("No rounds available.")
            return

        round_display = []
        for round_name in round_names:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM matches m
                JOIN rounds r ON m.round_id = r.id
                WHERE r.name = ?
                """,
                (round_name,),
            )
            count = cursor.fetchone()[0]
            round_display.append(f"{round_name} ({count} match{'es' if count != 1 else ''})")

        selected_round_display = st.selectbox("Select Round", round_display)
        selected_index = round_display.index(selected_round_display)
        selected_round_name = round_names[selected_index]

        matches = get_matches_by_round_name(selected_round_name)
        if not matches:
            st.info("No matches found for this round.")
            return

        status_colors = {
            "not played": "#adb5bd",
            "live": "#198754",
            "finished": "#0d6efd",
        }
        status_emojis = {
            "not played": "🕒",
            "live": "🔴",
            "finished": "✅",
        }

        font_style = "font-size:12px; padding:4px 6px;"

        # Table header
        header_cols = st.columns([2, 3, 2, 1, 1, 1, 1])
        headers = ["Competition", "Match", "Date & Time", "Status", "Home Score", "Away Score", "Actions"]
        header_bg_color = "#343a40"
        header_text_color = "white"
        for col, header in zip(header_cols, headers):
            col.markdown(
                f"<div style='background-color:{header_bg_color};color:{header_text_color};"
                f"font-weight:bold;{font_style}border-radius:4px;text-align:center'>{header}</div>",
                unsafe_allow_html=True,
            )

        for match in matches:
            (
                match_id,
                competition_name,
                home_team_name,
                away_team_name,
                match_datetime,
                status,
                home_score,
                away_score,
            ) = match

            cols = st.columns([2, 3, 2, 1, 1, 1, 1])

            cols[0].markdown(
                f"<div style='background:#6f42c1;color:white;{font_style}border-radius:4px;text-align:center;'>{competition_name}</div>",
                unsafe_allow_html=True,
            )

            cols[1].markdown(
                f"<div style='background:#0dcaf0;color:#000;{font_style}border-radius:4px;text-align:center;'>"
                f"{home_team_name} vs {away_team_name}</div>",
                unsafe_allow_html=True,
            )

            cols[2].markdown(
                f"<div style='background:#fd7e14;color:white;{font_style}border-radius:4px;text-align:center;'>{match_datetime}</div>",
                unsafe_allow_html=True,
            )

            status_color = status_colors.get(status, "#6c757d")
            status_text = status_emojis.get(status, "") + " " + status.capitalize()
            cols[3].markdown(
                f"<div style='background:{status_color};color:white;{font_style}font-weight:bold;border-radius:4px;text-align:center;'>"
                f"{status_text}</div>",
                unsafe_allow_html=True,
            )

            new_home_score = cols[4].number_input(
                label="",
                min_value=0,
                max_value=100,
                value=home_score if home_score is not None else 0,
                key=f"home_score_{match_id}",
                label_visibility="collapsed",
            )

            new_away_score = cols[5].number_input(
                label="",
                min_value=0,
                max_value=100,
                value=away_score if away_score is not None else 0,
                key=f"away_score_{match_id}",
                label_visibility="collapsed",
            )

            with cols[6]:
                new_status = st.selectbox(
                    "",
                    options=["not played", "live", "finished"],
                    index=["not played", "live", "finished"].index(status),
                    key=f"status_{match_id}",
                    label_visibility="collapsed",
                )

                # Small icon buttons for Update (pencil) and Delete (trash)
                update_clicked = st.button("✏️", key=f"update_{match_id}", help="Update Match")
                delete_clicked = st.button("🗑️", key=f"delete_{match_id}", help="Delete Match")

                if update_clicked:
                    with st.spinner("Updating match..."):
                        try:
                            update_match(match_id, new_status, new_home_score, new_away_score)
                            st.success("Match updated successfully.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating match: {e}")

                if delete_clicked:
                    with st.spinner("Deleting match..."):
                        try:
                            # Delete the match first
                            delete_match(match_id)

                            # Check if this round still has matches
                            cursor.execute(
                                """
                                SELECT r.id FROM rounds r WHERE r.name = ?
                                """,
                                (selected_round_name,),
                            )
                            round_row = cursor.fetchone()
                            if round_row:
                                round_id = round_row[0]
                                cursor.execute(
                                    """
                                    SELECT COUNT(*) FROM matches WHERE round_id = ?
                                    """,
                                    (round_id,),
                                )
                                count_matches = cursor.fetchone()[0]
                                if count_matches == 0:
                                    # Delete the round as no matches left
                                    cursor.execute(
                                        "DELETE FROM rounds WHERE id = ?", (round_id,)
                                    )
                                    conn.commit()
                                    st.info(f"Round '{selected_round_name}' deleted because it has no more matches.")

                            st.success("Match deleted successfully.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting match: {e}")

    finally:
        conn.close()



