"""
SPA backend — Flask JSON REST API.

Auth: JWT (returned to the client, which stores it in localStorage).
This file contains several DELIBERATE weaknesses used by the case-study demos;
each is marked `# DEMO:`. Do not treat this as a best-practice reference.
"""
import datetime as dt
import functools

import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash

from db import get_db, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "spa-demo-secret-not-for-production"
CORS(app)  # DEMO: wide-open CORS so the Vite dev origin can call the API

JWT_ALGO = "HS256"


# ---------------------------------------------------------------- auth helpers
def make_token(user):
    payload = {
        "uid": user["id"],
        "username": user["username"],
        "role": user["role"],
        "exp": dt.datetime.utcnow() + dt.timedelta(hours=8),
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm=JWT_ALGO)


def current_user():
    """Decode the Bearer token from the Authorization header, or return None."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        return jwt.decode(auth[7:], app.config["SECRET_KEY"], algorithms=[JWT_ALGO])
    except jwt.PyJWTError:
        return None


def require_auth(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify(error="unauthorized"), 401
        request.user = user
        return fn(*args, **kwargs)

    return wrapper


def task_to_dict(row):
    # DEMO (issue 2 — over-fetch): returns EVERY column, including internal_notes
    # and other users' data. The Vue UI hides some of this, but the API ships it all.
    return {k: row[k] for k in row.keys()}


# --------------------------------------------------------------------- routes
@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    con = get_db()
    row = con.execute(
        "SELECT * FROM users WHERE username = ?", (data.get("username"),)
    ).fetchone()
    con.close()
    if not row or not check_password_hash(row["password_hash"], data.get("password", "")):
        return jsonify(error="invalid credentials"), 401
    return jsonify(
        token=make_token(row),
        user={"id": row["id"], "username": row["username"], "role": row["role"]},
    )


@app.get("/api/me")
@require_auth
def me():
    u = request.user
    return jsonify(id=u["uid"], username=u["username"], role=u["role"])


@app.get("/api/tasks")
@require_auth
def list_tasks():
    con = get_db()
    # DEMO (issues 2 & 4): no per-user filtering — every task from every user is
    # returned. The SPA decides client-side what to show; the server over-shares.
    rows = con.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    con.close()
    return jsonify([task_to_dict(r) for r in rows])


@app.get("/api/tasks/<int:task_id>")
@require_auth
def get_task(task_id):
    con = get_db()
    row = con.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    con.close()
    if not row:
        return jsonify(error="not found"), 404
    return jsonify(task_to_dict(row))


@app.post("/api/tasks")
@require_auth
def create_task():
    d = request.get_json(silent=True) or {}
    con = get_db()
    cur = con.execute(
        """INSERT INTO tasks (title, description, internal_notes, status, assignee_id, owner_id, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            d.get("title", "(untitled)"),
            # DEMO (issue 1): description stored verbatim — no sanitization here.
            d.get("description", ""),
            d.get("internal_notes", ""),
            d.get("status", "todo"),
            d.get("assignee_id"),
            request.user["uid"],
            dt.date.today().isoformat(),
        ),
    )
    con.commit()
    row = con.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    con.close()
    return jsonify(task_to_dict(row)), 201


@app.put("/api/tasks/<int:task_id>")
@require_auth
def update_task(task_id):
    d = request.get_json(silent=True) or {}
    con = get_db()
    # DEMO (issue 4): no ownership/role check — any authenticated user can edit any task.
    con.execute(
        "UPDATE tasks SET status = COALESCE(?, status), title = COALESCE(?, title), description = COALESCE(?, description) WHERE id = ?",
        (d.get("status"), d.get("title"), d.get("description"), task_id),
    )
    con.commit()
    row = con.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    con.close()
    if not row:
        return jsonify(error="not found"), 404
    return jsonify(task_to_dict(row))


@app.delete("/api/tasks/<int:task_id>")
@require_auth
def delete_task(task_id):
    con = get_db()
    # DEMO (issue 4): the "Delete" button is hidden client-side for non-admins,
    # but the server enforces NOTHING here — the client guard is not a real control.
    con.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    con.commit()
    con.close()
    return jsonify(ok=True)


if __name__ == "__main__":
    init_db()
    print("== SPA API on http://localhost:5001 ==")
    app.run(port=5001, debug=True)
