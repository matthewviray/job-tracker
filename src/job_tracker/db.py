import sqlite3
from pathlib import Path


def get_connection() -> sqlite3.Connection:
    db_dir = Path.home() / ".jobs"
    db_dir.mkdir(exist_ok=True)
    return sqlite3.connect(db_dir / "applications.db")


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY,
                company TEXT,
                role TEXT,
                status TEXT DEFAULT 'applied',
                url TEXT,
                notes TEXT,
                applied_date TEXT,
                next_action TEXT
            );
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY,
                application_id INTEGER,
                name TEXT,
                role TEXT,
                email TEXT
            );
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY,
                application_id INTEGER,
                timestamp TEXT,
                note TEXT
            );
        """)
