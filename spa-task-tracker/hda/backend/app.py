"""
HDA backend — Flask + Jinja + htmx.

Every interaction is a server round-trip that returns HTML; htmx swaps the
fragment into the DOM. There is NO hand-written client JavaScript. Auth is a
signed, HttpOnly session cookie (not readable from JS).

The XSS-rendering behaviour is switchable so the demo can show the honest range:
    HDA_XSS_MODE=escape    (default) Jinja auto-escapes -> inert
    HDA_XSS_MODE=raw       trusts stored HTML  -> XSS FIRES (HDA is not auto-safe)
    HDA_XSS_MODE=sanitize  bleach-clean rich text -> safe
"""
import datetime as dt
import functools
import os

import bleach
from flask import (Flask, abort, redirect, render_template, request, session,
                   url_for)
from markupsafe import Markup
from werkzeug.security import check_password_hash

from db import get_db, init_db
from priority import priority_label

app = Flask(__name__, static_folder="../frontend/static", static_url_path="/static")
app.config.update(
    SECRET_KEY="hda-demo-secret-not-for-production",
    SESSION_COOKIE_HTTPONLY=True,   # DEMO (issue 2): cookie is invisible to JavaScript
    SESSION_COOKIE_SAMESITE="Lax",
)

XSS_MODE = os.environ.get("HDA_XSS_MODE", "escape")
ALLOWED_TAGS = ["b", "i", "em", "strong", "a", "code", "p", "br", "ul", "ol", "li"]


# ------------------------------------------------------------------- helpers
def current_user():
    uid = session.get("uid")
    if not uid:
        return None
    con = get_db()
    row = con.execute("SELECT id, username, role FROM users WHERE id = ?", (uid,)).fetchone()
    con.close()
    return row


def require_login(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            # htmx requests get a hard 401; plain navigations get redirected
            if request.headers.get("HX-Request"):
                abort(401)
            return redirect(url_for("login"))
        return fn(*args, **kwargs)

    return wrapper


def render_desc(description):
    """DEMO (issue 1): how the server renders a task description decides safety."""
    if XSS_MODE == "raw":
        return Markup(description)                                  # vulnerable
    if XSS_MODE == "sanitize":
        return Markup(bleach.clean(description, tags=ALLOWED_TAGS, strip=True))
    return description                                             # auto-escaped (safe)


def visible_tasks(user):
    con = get_db()
    if user["role"] == "admin":
        rows = con.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    else:
        # DEMO (issue 2): the SERVER filters. A member never receives other users'
        # tasks or the internal_notes column — it isn't put into the HTML at all.
        rows = con.execute(
            "SELECT * FROM tasks WHERE owner_id = ? OR assignee_id = ? ORDER BY id",
            (user["id"], user["id"]),
        ).fetchall()
    con.close()
    return rows


def one_task(task_id):
    con = get_db()
    row = con.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    con.close()
    return row


# make helpers available inside templates
app.jinja_env.globals.update(render_desc=render_desc, priority_label=priority_label)


@app.context_processor
def inject_user():
    return {"me": current_user()}


# -------------------------------------------------------------------- routes
@app.get("/login")
def login():
    if current_user():
        return redirect(url_for("index"))
    return render_template("login.html")


@app.post("/login")
def do_login():
    con = get_db()
    row = con.execute(
        "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
    ).fetchone()
    con.close()
    if not row or not check_password_hash(row["password_hash"], request.form.get("password", "")):
        return render_template("login.html", error="Invalid credentials"), 401
    session["uid"] = row["id"]
    return redirect(url_for("index"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/")
@require_login
def index():
    user = current_user()
    return render_template("tasks.html", tasks=visible_tasks(user))


@app.post("/tasks")
@require_login
def create_task():
    user = current_user()
    con = get_db()
    cur = con.execute(
        """INSERT INTO tasks (title, description, internal_notes, status, assignee_id, owner_id, created_at)
           VALUES (?, ?, '', 'todo', NULL, ?, ?)""",
        (
            request.form.get("title", "(untitled)"),
            request.form.get("description", ""),
            user["id"],
            dt.date.today().isoformat(),
        ),
    )
    con.commit()
    row = con.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    con.close()
    return render_template("_task.html", task=row)   # htmx appends this fragment


@app.post("/tasks/<int:task_id>/advance")
@require_login
def advance_task(task_id):
    user = current_user()
    nxt = {"todo": "in_progress", "in_progress": "blocked", "blocked": "done", "done": "todo"}
    row = one_task(task_id)
    if not row:
        abort(404)
    new_status = nxt[row["status"]]
    con = get_db()
    con.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    con.commit()
    con.close()
    # DEMO (issue 4): the server sees and logs every state change.
    app.logger.info("task %s advanced to %s by %s", task_id, new_status, user["username"])
    return render_template("_task.html", task=one_task(task_id))


@app.post("/tasks/<int:task_id>/delete")
@require_login
def delete_task(task_id):
    user = current_user()
    # DEMO (issue 4): the server is IN THE LOOP. Authorization is enforced here,
    # not by hiding a button. A forged delete from a non-admin is logged + rejected.
    app.logger.info("delete task %s requested by %s (%s)", task_id, user["username"], user["role"])
    if user["role"] != "admin":
        app.logger.warning("REJECTED delete of task %s: %s is not admin", task_id, user["username"])
        abort(403)
    con = get_db()
    con.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    con.commit()
    con.close()
    return ""   # htmx swaps the row's outerHTML with nothing -> it disappears


@app.get("/styles.css")
def shared_styles():
    # serve the same stylesheet the SPA uses (single source of truth)
    path = os.path.join(os.path.dirname(__file__), "..", "..", "shared", "styles.css")
    with open(path) as f:
        return app.response_class(f.read(), mimetype="text/css")


if __name__ == "__main__":
    init_db()
    print("== HDA app on http://localhost:5002  (XSS mode: %s) ==" % XSS_MODE)
    app.run(port=5002, debug=True)
