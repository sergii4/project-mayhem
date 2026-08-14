# project-mayhem

A drill instructor for your own competence. Built for engineering interview prep and technical learning generally — not tied to any specific stack or domain.

## What it does

- **Compressed, not clipped.** Answers aren't bare fragments — they fuse the why into the what so a fact lands as understanding, not trivia. Still short: no hedging, no filler, no pitch-mode enthusiasm, one next action stated and nothing offered beyond it.
- **Remembers what you've covered.** Every topic that gets real depth (not a passing mention) gets logged to a knowledge log with a spaced-repetition schedule.
- **Tests you without being asked.** At the start of any technical session, it checks what's overdue and runs a short check before getting into new material — not a nag screen, just the cost of walking back in.
- **`/quiz`** — run a quiz on demand: due items and weak spots first, or a specific topic if you name one. Pass doubles the interval, fail resets it to daily.
- **`/recap`** — a four-line status report: coverage, what's due, your weakest area, and the one next action. Nothing else.

## Components

| Component | Purpose |
|---|---|
| `skills/drill` | Voice + information-diet enforcement across all in-scope conversation, plus silent knowledge-log maintenance and auto-surfacing of overdue items |
| `skills/quiz` | On-demand spaced-repetition quiz, `/quiz` |
| `skills/recap` | On-demand status report, `/recap` |

## Where the knowledge log lives

`project-mayhem/knowledge-log.md`, either as a doc in your attached Claude Project (if one's attached to the session) or as a local file in your working directory otherwise. It's a plain markdown table — readable and editable by hand if you ever want to fix an entry.

## Scope

Any technical topic. There's no fixed domain list — it triggers on technical learning, debugging, and interview-prep conversation generally, and each topic gets tagged with a freeform `Area` label in the log rather than a preset category.

## Optional: proactive interruptions

This plugin surfaces due items when a session in scope starts, but it can't reach into your day uninvited — Cowork sessions only run when you open one. If you want it to actively ping you (e.g. a daily check at a fixed time) rather than waiting for you to start a relevant conversation, set up a scheduled task that fires a `/quiz` or `/recap` prompt into a session on a cron schedule. Ask Claude to set this up if you want it; it's not part of the plugin itself since it depends on your scheduling preferences.

## Install in Claude Code

This repo doubles as its own marketplace (`.claude-plugin/marketplace.json`), so no separate catalog repo is needed. From any machine with Claude Code:

```shell
/plugin marketplace add <your-github-username>/project-mayhem
/plugin install project-mayhem@project-mayhem
```

If the install summary says `Run /reload-plugins to activate.`, run that.

Skills are namespaced by plugin name, so invoke them directly as `/project-mayhem:quiz` and `/project-mayhem:recap`. `drill` isn't meant to be called directly — it triggers automatically in the background of technical conversation, same as it does in Cowork. Natural language also works: "quiz me" and "recap" trigger the same skills without the slash form.

To iterate on the plugin locally before pushing changes, run Claude Code against the working directory instead of the installed copy:

```shell
claude --plugin-dir ./project-mayhem
```
