from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

DB_PATH = "/data/app.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    conn = get_db_connection()
    row = conn.execute("SELECT message FROM test LIMIT 1").fetchone()
    conn.close()
    return jsonify({"message": row["message"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8181)
