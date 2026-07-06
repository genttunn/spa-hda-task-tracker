"""SQLite setup + seed for the SPA backend. DB is persisted to app.db (a file)."""
import os
import sqlite3
from werkzeug.security import generate_password_hash

BASE = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE, "app.db")
SEED_SQL = os.path.join(BASE, "..", "..", "shared", "seed.sql")

# username, plaintext password, role. Passwords are hashed on insert.
SEED_USERS = [
    ("admin", "admin123", "admin"),
    ("alice", "alice123", "member"),
    ("bob", "bob123", "member"),
]


def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db(force=False):
    """Create + seed the DB file if it doesn't exist yet (or force a rebuild)."""
    if force and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists(DB_PATH):
        return
    con = get_db()
    with open(SEED_SQL) as f:
        con.executescript(f.read())          # schema + task rows
    for username, password, role in SEED_USERS:
        con.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password, method="pbkdf2:sha256"), role),
        )
    con.commit()
    con.close()


if __name__ == "__main__":
    init_db(force=True)
    print("Rebuilt", DB_PATH)
