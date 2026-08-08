import sqlite3
from config import Config


def get_db():
    """
    Creates and returns a SQLite database connection with row factory configured.
    """
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the SQLite database schema if tables do not exist.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                telefon TEXT NOT NULL,
                mesaj TEXT,
                status TEXT DEFAULT 'Yeni',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def db_sifirla():
    """
    Resets/clears all lead records from the database table.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM leads")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='leads'")
        conn.commit()


def lead_ekle(isim: str, telefon: str, mesaj: str = "") -> int:
    """
    Inserts a new contact lead into the database safely using parameterized SQL queries.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO leads (isim, telefon, mesaj) VALUES (?, ?, ?)",
            (isim.strip(), telefon.strip(), mesaj.strip() if mesaj else "")
        )
        conn.commit()
        return cursor.lastrowid


def tum_leadler() -> list[dict]:
    """
    Fetches all recorded leads from the database ordered by creation date descending.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, isim, telefon, mesaj, status, created_at FROM leads ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
