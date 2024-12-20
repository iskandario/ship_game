import sqlite3

def init_db():
    conn = sqlite3.connect("game_results.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            shots_fired INTEGER NOT NULL,
            ships_destroyed INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_result(username, shots_fired, ships_destroyed):
    conn = sqlite3.connect("game_results.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO results (username, shots_fired, ships_destroyed) VALUES (?, ?, ?)",
                   (username, shots_fired, ships_destroyed))
    conn.commit()
    conn.close()

def get_results(username):
    conn = sqlite3.connect("game_results.db")
    cursor = conn.cursor()
    cursor.execute("SELECT shots_fired, ships_destroyed FROM results WHERE username = ? ORDER BY id DESC", (username,))
    results = cursor.fetchall()
    conn.close()
    return results
