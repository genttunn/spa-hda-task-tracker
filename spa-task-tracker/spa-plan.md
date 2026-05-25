SPA Prototype — Task Tracker (Flask + Vue.js)
Purpose
Demonstrate SPA-specific security and privacy characteristics compared to the HDA equivalent. The app is a simple multi-user task tracker — enough surface area to expose real architectural differences without scope creep.

Scope (contained)
Features only:

Register / login (JWT-based)
Create, complete, delete tasks
View your own task list
One "admin" role that can see all users' tasks

That's it. No file uploads, no search, no notifications.

Architecture
Flask (API only — JSON responses)
  └── /api/auth/register   POST
  └── /api/auth/login      POST  → returns JWT
  └── /api/tasks           GET, POST
  └── /api/tasks/<id>      PUT, DELETE
  └── /api/admin/tasks     GET (admin only)

Vue.js (served as static files, separate from Flask)
  └── router (client-side, hash or history mode)
  └── Pinia store (auth token, task state)
  └── axios (all API calls, attaches JWT via interceptor)
Flask serves the Vue bundle as static files or you run them on separate ports (e.g. :5000 for Flask, :5173 for Vite dev server). The latter is better for the demo — it makes the CORS requirement visible and explicit.

Security/Privacy Surface to Expose
These are the things your prototype should make observable — not just functional:
1. JWT stored in localStorage
Store the token in localStorage (not httpOnly cookie). This is the common SPA pattern and the one that exposes XSS token theft. Your demo can include a trivial XSS injection field to show the token can be read by JS.
2. Client-side route guarding
The /admin route is hidden in the nav for regular users, but the route and its Vue component are present in the downloaded JS bundle. Show that curl-ing the bundle or opening DevTools reveals admin route logic. The real guard is the API — but the logic is exposed.
3. State duplication
The Pinia store holds a local copy of tasks. Show that the client state can desync from the server (e.g. optimistic update that doesn't roll back cleanly). This is a correctness/privacy concern — stale data displayed after a permissions change.
4. CORS required
Because the Vue app and Flask API are separate origins, Flask must emit CORS headers. Demo what happens if CORS is misconfigured (* origin + credentials). This is an attack surface that simply doesn't exist in the HDA.
5. Token expiry / no revocation
Issue a short-lived JWT. Show there's no server-side session to invalidate — logging out on the client doesn't invalidate the token. If someone sniffs the token, it's valid until expiry.

File Structure
spa/
├── backend/
│   ├── app.py              # Flask app factory
│   ├── models.py           # User, Task (SQLite via SQLAlchemy)
│   ├── auth.py             # Register, login, JWT helpers
│   ├── routes/
│   │   ├── tasks.py        # CRUD endpoints
│   │   └── admin.py        # Admin-only endpoint
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── main.js
    │   ├── router/index.js         # client-side routes
    │   ├── stores/auth.js          # Pinia: token, user
    │   ├── stores/tasks.js         # Pinia: task list
    │   ├── views/
    │   │   ├── Login.vue
    │   │   ├── Tasks.vue
    │   │   └── Admin.vue
    │   └── api/client.js           # axios instance + JWT interceptor
    └── vite.config.js

Key Implementation Notes
Backend:

Use flask-jwt-extended for tokens
Use flask-cors — configure it explicitly, don't just CORS(app) with defaults
SQLite is fine — single file, easy to inspect/reset between demos
Passwords: bcrypt, nothing fancy
Admin flag: simple boolean column on User

Frontend:

Vue 3 + Composition API
Vite for dev server
Pinia for state
Vue Router in history mode (shows client-side routing clearly)
Store JWT in localStorage deliberately — this is the demo point, not a mistake

Demo hooks (small additions that make the security story visible):

A GET /api/debug/me endpoint that returns everything Flask knows about the current token — useful for showing what's actually being validated server-side
A text field in the UI labeled "Notes (unsafe)" that renders raw HTML — your XSS demo surface
A browser console log that prints the decoded JWT payload on login — makes the "client can see the token" point obvious