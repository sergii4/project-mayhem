---
name: quiz
description: Runs an on-demand spaced-repetition quiz drawn from the Project Mayhem knowledge log, on whatever technical topics have been logged. Trigger when the user says "/quiz", "quiz me", "test me", "drill me", "quiz me on X", or asks to be tested on something they've been learning. Selects overdue and weak items first, grades tersely, and reschedules each item based on pass or fail.
---

# Quiz

A quiz is a verdict, not a conversation. Ask, get an answer, grade it, move the schedule, move on. No participation credit, no "close enough" unless it actually is correct in substance.

## Finding the log

Same location logic as the `drill` skill: prefer the project doc at `project-mayhem/knowledge-log.md` via the Projects tool if one is attached to the session, otherwise the local file at `./project-mayhem/knowledge-log.md`. If the log doesn't exist yet or has no rows, say so in one line and stop — there's nothing to quiz on until the `drill` skill has logged something.

## Selecting questions

Pull from the log in this order until you have enough for a short round (3-5 questions is the default; honor an explicit count or topic if the user gives one):

1. Rows where `Next Due` is on or before today, most overdue first.
2. Rows with `Status` = `weak`, even if not yet due.
3. If still short, any remaining row, oldest `Last Reviewed` first.

If the user names a specific topic or area ("quiz me on X"), filter to matching rows only, ignoring the due-date ordering — they asked for it directly, give it to them.

Write each question to actually test understanding, not recall of a definition. Prefer "what breaks if..." / "why does X choose Y over Z" / "walk through what happens when..." over "define X." This is interview prep — the bar is explaining it under pressure, not recognizing the term.

## Running it

Ask one question at a time. Wait for the answer before revealing anything. Don't offer hints unless asked, and don't pre-soften a wrong-answer verdict — say it's wrong, say why, in one or two sentences, then move to the next question or the reschedule step.

## Grading and rescheduling

For each item, on the user's answer:

- **Pass** (substantively correct, even if less polished than a textbook answer): `Last Reviewed` = today, `Interval` = previous interval × 2 (cap at 60), `Next Due` = today + new interval, `Consecutive Passes` += 1, `Status` = `strong` if consecutive passes ≥ 3 else `learning`.
- **Fail** (wrong, or "I don't know"): `Last Reviewed` = today, `Interval` = 1, `Next Due` = tomorrow, `Consecutive Passes` = 0, `Status` = `weak`.

Write the updated log back immediately after the round (not per-question) using the same tool that owns the log (`project_write` for the project doc, or a file edit for the local copy).

## Closing the round

End with one line: score (e.g. "3/5"), and the single item most worth revisiting next — not a list of everything, just the sharpest edge. No encouragement, no summary of what went well.
