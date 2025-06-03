import sqlite3

DB_NAME = "football_game.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def list_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    return [row[0] for row in cursor.fetchall()]

def get_table_record_count(cursor, table):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    return cursor.fetchone()[0]

def show_table_contents(cursor, table):
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]

    if not rows:
        print("⚠️ Table is empty.")
    else:
        print("\n📄 Table Contents:")
        print(" | ".join(col_names))
        print("-" * 60)
        for row in rows:
            print(" | ".join(str(cell) for cell in row))

def delete_table_data(cursor, conn, table):
    cursor.execute(f"DELETE FROM {table}")
    conn.commit()
    print(f"✅ All data from '{table}' has been deleted.")

def drop_entire_table(cursor, conn, table):
    cursor.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    print(f"🗑️ Table '{table}' has been dropped from the database.")

def interactive_table_manager():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Get all table names
        tables = list_tables(cursor)

        if not tables:
            print("❌ No tables found in the database.")
            return

        print("\n📊 Tables and Record Counts:")
        for table in tables:
            count = get_table_record_count(cursor, table)
            print(f"   - {table}: {count} records")

        selected_table = input("\n📥 Enter the name of the table you want to inspect:\n>> ").strip()

        if selected_table not in tables:
            print(f"❌ Table '{selected_table}' does not exist.")
            return

        print(f"\n✅ Table '{selected_table}' selected.")
        print("Choose an action:")
        print("   1. Show contents")
        print("   2. Delete all data from this table")
        print("   3. Delete the entire table")

        choice = input(">> ").strip()

        if choice == '1':
            show_table_contents(cursor, selected_table)
        elif choice == '2':
            confirm = input(f"⚠️ Are you sure you want to delete ALL data from '{selected_table}'? (yes/no): ").strip().lower()
            if confirm == 'yes':
                delete_table_data(cursor, conn, selected_table)
            else:
                print("❌ Deletion cancelled.")
        elif choice == '3':
            confirm = input(f"⚠️ Are you sure you want to DROP the ENTIRE table '{selected_table}'? This cannot be undone. (yes/no): ").strip().lower()
            if confirm == 'yes':
                drop_entire_table(cursor, conn, selected_table)
            else:
                print("❌ Drop table cancelled.")
        else:
            print("❌ Invalid choice.")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()



import sqlite3
from datetime import datetime

DB_NAME = "football_game.db"

def generate_standard_league_name():
    while True:
        season = input("📆 Enter the season (e.g., 2024/2025): ").strip()
        if "/" not in season or len(season) < 7:
            print("⚠️ Invalid format. Try again.")
            continue
        break

    while True:
        portion = input("🕒 Is it First Half, Second Half, or Full? ").strip().lower()
        if portion in ["first half", "second half", "full"]:
            break
        print("⚠️ Please enter 'First Half', 'Second Half', or 'Full'.")

    name = f"Premier Prediction League {season} {portion.title()}"
    return name, int(season.split("/")[0])  # Use first year as the season year


def ensure_achievement_exists(cursor, name="League Winner", description="Won the prediction league"):
    cursor.execute("SELECT id FROM achievements WHERE name = ?", (name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    cursor.execute("INSERT INTO achievements (name, description) VALUES (?, ?)", (name, description))
    return cursor.lastrowid


def record_league_winner():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Show players
    print("👥 All Players:")
    cursor.execute("SELECT id, name FROM players")
    for row in cursor.fetchall():
        print(f"ID: {row[0]} | Name: {row[1]}")

    while True:
        try:
            player_id = int(input("🏆 Enter the ID of the player who won the league: "))
            cursor.execute("SELECT name FROM players WHERE id = ?", (player_id,))
            row = cursor.fetchone()
            if not row:
                print("❌ Invalid player ID.")
                continue
            player_name = row[0]
            break
        except ValueError:
            print("⚠️ Please enter a number.")

    # Generate League Name & Season
    league_name, year = generate_standard_league_name()
    print(f"✨ League Title: {league_name}")

    # Ensure "League Winner" achievement exists
    achievement_id = ensure_achievement_exists(cursor)

    # Check if already awarded
    cursor.execute("""
        SELECT id FROM user_achievements
        WHERE user_id = ? AND achievement_id = ? AND year = ?
    """, (player_id, achievement_id, year))
    if cursor.fetchone():
        print("⚠️ Player already awarded this achievement for the selected year.")
    else:
        cursor.execute("""
            INSERT INTO user_achievements (user_id, achievement_id, year)
            VALUES (?, ?, ?)
        """, (player_id, achievement_id, year))
        print(f"✅ Recorded: {player_name} is the {league_name} Winner!")

    conn.commit()
    conn.close()

import sqlite3

def show_player_achievements():
    conn = sqlite3.connect("football_game.db")
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

    achievements_dict = {}

    for name, achievement, count in results:
        if name not in achievements_dict:
            achievements_dict[name] = {'League Winner': 0, 'Cup Winner': 0}
        if achievement:
            achievements_dict[name][achievement] = count

    print("\n🏅 Player Achievements Summary:")
    print("-" * 40)
    for player, ach in achievements_dict.items():
        print(f"👤 {player}")
        print(f"   🏆 Leagues Won: {ach.get('League Winner', 0)}")
        print(f"   🏅 Cups Won   : {ach.get('Cup Winner', 0)}")
        print("-" * 40)

    conn.close()

# if __name__ == "__main__":
#     show_player_achievements()


# if __name__ == "__main__":
#     record_league_winner()

# Run the manager
interactive_table_manager()