# SPA Task Tracker

A Flask + Vue.js single-page application demonstrating SPA-specific security and privacy characteristics. Built as a teaching prototype to compare against an HDA (Hypermedia-Driven App) equivalent.

## What this demos

| Demo point | Where to observe |
|---|---|
| JWT stored in localStorage | DevTools → Application → Local Storage |
| JWT payload readable by JS | DevTools Console on login |
| XSS token theft | Enter `<img src=x onerror="alert(localStorage.getItem('access_token'))">` in a task's Notes field |
| Admin code in JS bundle | DevTools → Network → JS file, search "AdminView" |
| Client-side guard bypass | Edit `user.is_admin` to `true` in localStorage → guard passes, API returns 403 |
| No server-side revocation | Copy token, logout, use token in curl — still valid until expiry |
| CORS required | Flask must emit `Access-Control-Allow-Origin` because frontend and API are different origins |
| CORS misconfiguration | Change `origins` to `"*"` in `backend/app.py` → browser rejects wildcard + credentials |
| State desync | Optimistic update in task store does not roll back on error |

## Stack

- **Backend:** Flask, flask-jwt-extended, flask-cors, SQLAlchemy (SQLite), bcrypt
- **Frontend:** Vue 3 (Composition API), Vite, Pinia, Vue Router, axios

## Prerequisites on macOS

- Install Node.js first if `npm` is not available. The quickest option is Homebrew:

```bash
brew install node
```

- Python 3 is required for the Flask backend.

## Running

### macOS / Linux

**Terminal 1 — Flask API (port 5000)**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask run --port 5000
```

**Terminal 2 — Vite dev server (port 5173)**

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### Windows

If you're on Windows, use PowerShell and activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

The rest of the commands are the same.

## First-time setup

1. Register an account via the login page.
2. To make a user admin:

```powershell
cd backend
python make_admin.py <username>
```

## Project structure

```
spa-task-tracker/
├── backend/
│   ├── app.py              # Flask factory, CORS config, blueprint registration
│   ├── models.py           # User, Task (SQLAlchemy)
│   ├── auth.py             # /api/auth/* endpoints + /api/debug/me
│   ├── make_admin.py       # CLI: promote a user to admin
│   ├── routes/
│   │   ├── tasks.py        # /api/tasks CRUD
│   │   └── admin.py        # /api/admin/tasks
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── api/client.js           # axios instance + JWT interceptor
        ├── router/index.js         # client-side routes (history mode)
        ├── stores/
        │   ├── auth.js             # token, user, login, logout
        │   └── tasks.js            # task list, optimistic updates
        └── views/
            ├── LoginView.vue       # login + register + JWT debug panel
            ├── TasksView.vue       # task CRUD + v-html XSS surface
            └── AdminView.vue       # all tasks + debug/me output
```

## Key implementation notes

- **No Vite proxy** — keeping Flask and Vite on separate origins makes CORS headers visible in DevTools. A proxy would hide them.
- **JWT in localStorage** (not httpOnly cookie) — the common SPA pattern; makes XSS token theft possible.
- **Static import of `AdminView`** — the component lands in the main JS bundle for all users. The route guard is UX, not security.
- **15-minute JWT expiry** — short enough to demonstrate token expiry. Change `JWT_ACCESS_TOKEN_EXPIRES` in `backend/.env` for longer demo sessions.
- **XSS payload:** `<script>` tags injected via `v-html` do not execute in modern browsers. Use `<img src=x onerror="...">` instead.
