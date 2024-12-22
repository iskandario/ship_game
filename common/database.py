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
    if shots_fired <= 0 and ships_destroyed <= 0:
        print("Попытка сохранить пустой результат. Сохранение пропущено.")
        return  # Игнорируем пустые результаты
    conn = sqlite3.connect("game_results.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results (username, shots_fired, ships_destroyed) VALUES (?, ?, ?)",
        (username, shots_fired, ships_destroyed)
    )
    conn.commit()
    conn.close()
    print(f"Результат сохранен: {username}, выстрелы: {shots_fired}, уничтожено: {ships_destroyed}")

    
def get_results(username):
    conn = sqlite3.connect("game_results.db")
    cursor = conn.cursor()
    cursor.execute("SELECT shots_fired, ships_destroyed FROM results WHERE username = ? ORDER BY id DESC", (username,))
    results = cursor.fetchall()
    conn.close()
    return results
