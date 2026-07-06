# SPA vs HDA — a security case study

Two builds of the **same task-tracker app**, compared from a client-side security
angle:

- **`spa/`** — Single Page Application: Flask JSON API + Vue 3 (Vite) frontend.
  Auth is a **JWT held in `localStorage`**.
- **`hda/`** — Hypermedia-Driven Application: Flask + Jinja + **htmx**. The server
  returns HTML fragments; there is no hand-written client JavaScript. Auth is an
  **HttpOnly session cookie**.

Both apps run five identical, *actually exploitable* security demos. The point is
**not** to declare a winner up front — each demo fires the same attack at both
apps and records what really happens, including where HDA fails, only partly
helps, or just shifts the blast radius. See **[DEMOS.md](DEMOS.md)**.

> ⚠️ Both apps contain **deliberate vulnerabilities** (marked `# DEMO:` /
> `DEMO (issue …)`). This is teaching apparatus, not a best-practice reference.

## Layout

```
spa/backend    Flask JSON API      (port 5001)
spa/frontend   Vue 3 + Vite        (port 5173)
hda/backend    Flask + Jinja+htmx  (port 5002)
shared/        seed.sql, styles.css (shared look), attacker listener, malicious dep
```

Data lives in a SQLite **file** per app (`spa/backend/app.db`, `hda/backend/app.db`),
seeded identically from `shared/seed.sql`.

## Prerequisites

- Python 3.9+
- Node 18+ / npm

## Setup

```bash
# from the repo root — one shared virtualenv for both Flask backends + attacker
python3 -m venv .venv
./.venv/bin/pip install -r spa/backend/requirements.txt -r hda/backend/requirements.txt

# SPA frontend deps
cd spa/frontend && npm install && cd ../..
```

## Run

Open separate terminals (all commands from the repo root):

```bash
# 1) attacker listener — watches for stolen data      -> http://localhost:5999
./.venv/bin/python shared/attacker/listener.py

# 2) SPA backend                                       -> http://localhost:5001
./.venv/bin/python spa/backend/app.py

# 3) SPA frontend                                      -> http://localhost:5173
cd spa/frontend && npm run dev

# 4) HDA app (backend + frontend in one)               -> http://localhost:5002
./.venv/bin/python hda/backend/app.py
```

- **SPA:** open http://localhost:5173
- **HDA:** open http://localhost:5002

The HDA app's XSS rendering is switchable (see DEMOS.md):

```bash
HDA_XSS_MODE=raw      ./.venv/bin/python hda/backend/app.py   # XSS fires
HDA_XSS_MODE=sanitize ./.venv/bin/python hda/backend/app.py   # bleach-cleaned
# default is 'escape' (Jinja auto-escaping)
```

## Logins

| user  | password  | role   |
|-------|-----------|--------|
| admin | admin123  | admin  |
| alice | alice123  | member |
| bob   | bob123    | member |

## Rebuild / reset the databases

```bash
./.venv/bin/python spa/backend/db.py   # rebuilds spa/backend/app.db
./.venv/bin/python hda/backend/db.py   # rebuilds hda/backend/app.db
```

## The five demos

Full reproduction steps and observed results are in **[DEMOS.md](DEMOS.md)**:

1. XSS (stored, via task description)
2. Sensitive data exposure through client-side storage
3. Third-party script / dependency compromise
4. Monitoring & detection of client-side changes and data access
5. Exposure of client-side business logic & proprietary information
