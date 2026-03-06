import sqlite3

DB = "bot.db"


def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        referred_by INTEGER
    )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, username):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO users (user_id, username, referred_by) VALUES (?, ?, NULL)",
        (user_id, username)
    )

    conn.commit()
    conn.close()


def set_referral(user_id, referrer):
    if user_id == referrer:
        return

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET referred_by=? WHERE user_id=? AND referred_by IS NULL",
        (referrer, user_id)
    )

    conn.commit()
    conn.close()


def get_referrals(user_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users WHERE referred_by=?", (user_id,))
    count = cur.fetchone()[0]

    conn.close()
    return count