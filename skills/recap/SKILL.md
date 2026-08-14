---
name: recap
description: Produces a compressed status report from the Project Mayhem knowledge log — what's been covered, what's overdue, the weakest area, and one next action. Trigger when the user says "/recap", "recap", "where am I", "status check", "what's outstanding", or asks for a summary of their learning progress on any technical topic they've been logging.
---

# Recap

A status report, not a retrospective. Four lines, no more, unless the user explicitly asks to drill into one of them.

## Finding the log

Same location logic as `drill` and `quiz`: project doc `project-mayhem/knowledge-log.md` via the Projects tool if attached, else the local file at `./project-mayhem/knowledge-log.md`. If it doesn't exist, say there's nothing logged yet in one line and stop.

## What to report

Compute from the log and state exactly this, each on its own line, nothing extra:

1. **Coverage** — count of topics logged, broken down by `Area` in a single compact clause (e.g. "14 topics: 7 networking, 4 auth, 3 storage" — using whatever area labels are actually in the log).
2. **Due** — count of rows with `Next Due` on or before today. If more than 3, name only the count; if 1-3, name them.
3. **Weakest** — the single row with the lowest `Consecutive Passes` (ties broken by shortest `Interval`), named specifically, not just its area.
4. **Next action** — one imperative sentence. If anything is due, it's "run /quiz." If nothing is due and nothing is weak, it's the next topic worth opening given what's already covered and what's thin (say which, in one clause).

Do not list every row in the log. Do not add commentary about progress, effort, or encouragement. If the user wants the full table, they'll ask for it — then show it as-is.
