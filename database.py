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
                coins INTEGER DEFAULT 20
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
                INSERT INTO users (user_id, username, first_name, language, coins)
                VALUES (?, ?, ?, ?, ?)
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