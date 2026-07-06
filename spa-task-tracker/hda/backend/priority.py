"""
Proprietary task-priority scoring algorithm — SERVER SIDE.

DEMO (issue 5): this is the exact same algorithm the SPA ships to the browser
in its JS bundle. Here it runs on the server; the client only ever receives the
rendered badge (e.g. "urgent"), never the formula. View-source reveals nothing.
"""
import datetime as dt

STATUS_WEIGHT = {"todo": 10, "in_progress": 30, "blocked": 50, "done": 0}


def priority_score(task):
    base = STATUS_WEIGHT.get(task["status"], 10)
    created = dt.date.fromisoformat(task["created_at"])
    age_days = (dt.date.today() - created).days
    score = base + min(age_days * 2, 40)          # older = more urgent, capped
    if task["assignee_id"] is None:
        score += 15                               # unassigned penalty
    return score


def priority_label(task):
    s = priority_score(task)
    if s >= 60:
        return "urgent"
    if s >= 40:
        return "high"
    if s >= 20:
        return "normal"
    return "low"
