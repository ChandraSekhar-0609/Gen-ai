import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "history.db"

def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                language TEXT NOT NULL,
                prompt TEXT,
                code TEXT,
                answer TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_history(action, language, prompt, code, answer):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO history (action, language, prompt, code, answer)
               VALUES (?, ?, ?, ?, ?)""",
            (action, language, prompt, code, answer),
        )
        conn.commit()

def get_history(limit=30):
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT id, action, language, prompt, code, answer, created_at
               FROM history ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]

def clear_history():
    with get_connection() as conn:
        conn.execute("DELETE FROM history")
        conn.commit()
