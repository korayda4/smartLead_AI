import sqlite3
from config import Config
from app.models.lead import Lead


class LeadRepository:
    def __init__(self, db_path: str | None = None):
        self._db_path = db_path or Config.DATABASE_PATH

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        with self._connect() as conn:
            conn.execute("""
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

    def ekle(self, lead: Lead) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO leads (isim, telefon, mesaj) VALUES (?, ?, ?)",
                (lead.isim.strip(), lead.telefon.strip(), (lead.mesaj or "").strip())
            )
            conn.commit()
            return cur.lastrowid

    def hepsini_getir(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, isim, telefon, mesaj, status, created_at FROM leads ORDER BY id DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def sifirla(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM leads")
            conn.execute("DELETE FROM sqlite_sequence WHERE name='leads'")
            conn.commit()
