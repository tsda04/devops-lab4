import sqlite3

DB_FILE = "/data/data.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Удаляем старую таблицу, если есть
cur.execute("DROP TABLE IF EXISTS users")

# Создаем таблицу заново
cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

# Добавим одного дефолтного пользователя
cur.execute("INSERT INTO users(name) VALUES ('Admin')")

conn.commit()
conn.close()

print("DB initialized.")
