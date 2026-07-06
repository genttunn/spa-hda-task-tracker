-- Shared schema + task seed data for BOTH the SPA and HDA apps.
-- Users are inserted programmatically by db.py (so passwords get properly hashed).
-- Tasks are seeded here so both apps start from an identical data set.

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'member'   -- 'admin' | 'member'
);

CREATE TABLE IF NOT EXISTS tasks (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    title          TEXT NOT NULL,
    description    TEXT NOT NULL DEFAULT '',        -- rich text -> the XSS vector (demo 1)
    internal_notes TEXT NOT NULL DEFAULT '',        -- private field the UI hides -> over-fetch leak (demo 2)
    status         TEXT NOT NULL DEFAULT 'todo',    -- todo | in_progress | blocked | done
    assignee_id    INTEGER,                         -- NULL = unassigned
    owner_id       INTEGER NOT NULL,
    created_at     TEXT NOT NULL,                   -- ISO date; feeds the priority-score algorithm (demo 5)
    FOREIGN KEY (assignee_id) REFERENCES users(id),
    FOREIGN KEY (owner_id)    REFERENCES users(id)
);

-- Seed tasks. owner/assignee ids: 1=admin, 2=alice, 3=bob (see db.py user seed).
INSERT INTO tasks (title, description, internal_notes, status, assignee_id, owner_id, created_at) VALUES
    ('Set up CI pipeline',       'Configure GitHub Actions for the repo.',        'Budget approved: $4k for runners.',           'in_progress', 2, 2, '2026-06-20'),
    ('Design landing page',      'Hero, features, pricing sections.',             'Reuse assets from the abandoned Q1 rebrand.', 'todo',        3, 2, '2026-06-28'),
    ('Fix login rate limiting',  'Users locked out after 3 tries; loosen it.',    'Incident INC-2231 root cause, keep private.',  'blocked',     2, 3, '2026-06-15'),
    ('Write API docs',           'Document the public endpoints.',                'Legal wants a disclaimer added first.',        'todo',        NULL, 3, '2026-07-01'),
    ('Migrate to Postgres',      'Move off SQLite before launch.',                'Vendor quote: $1.2k/mo managed DB.',           'todo',        3, 2, '2026-07-04'),
    ('Ship onboarding emails',   'Welcome + day-3 nudge sequence.',               'A/B test winner from last cohort: variant B.', 'done',        2, 3, '2026-05-30');
