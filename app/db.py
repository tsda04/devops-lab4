import sqlite3, os

DB_PATH = "/data/app.db"

os.makedirs("/data", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, message TEXT)")
conn.execute("INSERT INTO test (message) VALUES ('Hello from DB!')")
conn.commit()
conn.close()

print("DB initialized:", DB_PATH)
