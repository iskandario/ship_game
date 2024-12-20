import sqlite3

def init_db():
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        shots_fired INTEGER,
        ships_destroyed INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    conn.commit()
    conn.close()

def get_or_create_user(name):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (name) VALUES (?)", (name,))
    conn.commit()
    cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
    user_id = cursor.fetchone()[0]
    conn.close()
    return user_id

def save_result(user_id, shots_fired, ships_destroyed):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO results (user_id, shots_fired, ships_destroyed)
    VALUES (?, ?, ?)
    """, (user_id, shots_fired, ships_destroyed))
    conn.commit()
    conn.close()

def get_results(user_id):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT shots_fired, ships_destroyed FROM results WHERE user_id = ?
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

init_db()
