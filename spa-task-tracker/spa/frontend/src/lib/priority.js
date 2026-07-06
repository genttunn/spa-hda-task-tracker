// -------------------------------------------------------------------------
// Proprietary task-priority scoring algorithm.
//
// DEMO (issue 5): in the SPA this logic runs in the browser, so it ships inside
// the JS bundle and is fully readable by anyone via DevTools — even minified,
// it is trivially reverse-engineered. The HDA app computes the identical score
// on the SERVER and sends only the resulting badge, so this never leaves the box.
// -------------------------------------------------------------------------

const STATUS_WEIGHT = { todo: 10, in_progress: 30, blocked: 50, done: 0 }

export function priorityScore(task) {
  const base = STATUS_WEIGHT[task.status] ?? 10
  const ageDays = Math.floor((Date.now() - new Date(task.created_at).getTime()) / 86400000)
  let score = base + Math.min(ageDays * 2, 40)   // older = more urgent, capped
  if (task.assignee_id == null) score += 15       // unassigned penalty
  return score
}

export function priorityLabel(task) {
  const s = priorityScore(task)
  if (s >= 60) return 'urgent'
  if (s >= 40) return 'high'
  if (s >= 20) return 'normal'
  return 'low'
}
