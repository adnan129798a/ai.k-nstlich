import sqlite3
from contextlib import closing

from config import DEFAULT_COINS


DB_NAME = "bot.db"


def init_db():
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                language TEXT,
                coins INTEGER DEFAULT 20,
                referred_by INTEGER
            )
        """)
        conn.commit()


def create_or_update_user(user_id: int, username: str | None, first_name: str | None, language: str):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()

        if row:
            cur.execute("""
                UPDATE users
                SET username = ?, first_name = ?, language = ?
                WHERE user_id = ?
            """, (username, first_name, language, user_id))
        else:
            cur.execute("""
                INSERT INTO users (user_id, username, first_name, language, coins, referred_by)
                VALUES (?, ?, ?, ?, ?, NULL)
            """, (user_id, username, first_name, language, DEFAULT_COINS))

        conn.commit()


def get_user_language(user_id: int) -> str | None:
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else None


def set_user_language(user_id: int, language: str):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
        conn.commit()


def get_user_coins(user_id: int) -> int:
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else DEFAULT_COINS


def get_referred_by(user_id: int) -> int | None:
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT referred_by FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row and row[0] is not None else None


def apply_referral(user_id: int, referrer_id: int) -> bool:
    if user_id == referrer_id:
        return False

    with closing(sqlite3.connect(DB_NAME)) as conn:
        cur = conn.cursor()

        cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        user_exists = cur.fetchone()
        if not user_exists:
            return False

        cur.execute("SELECT user_id FROM users WHERE user_id = ?", (referrer_id,))
        ref_exists = cur.fetchone()
        if not ref_exists:
            return False

        cur.execute("SELECT referred_by FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()

        if not row or row[0] is not None:
            return False

        cur.execute(
            "UPDATE users SET referred_by = ? WHERE user_id = ? AND referred_by IS NULL",
            (referrer_id, user_id)
        )
        conn.commit()
        return cur.rowcount > 0


def get_referral_count(user_id: int) -> int:
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users WHERE referred_by = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else 0