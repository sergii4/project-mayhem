# project-mayhem

An operational efficiency enforcer for Claude Code. It bounds how the agent spends tool calls, context, and wall time — not how it writes prose or code.

That scope is deliberate. Terse output and minimal code are already well covered by other plugins; what nothing enforces is the operational layer, where the waste actually is: a whole file read to find one function, `grep -r` returning hits in comments, a subagent's raw output dumped into main context, a foreground command that hangs for ten minutes.

## What it enforces

Everything is delivered through hooks, so it is active from the first message rather than waiting for the model to decide to load a skill. `SessionStart` injects the ruleset in `hooks/rules.md`, and `SubagentStart` injects the same file again because `SessionStart` context does not reach subagents.

### Hard limits (the Bash guard)

`hooks/bash-guard.py` inspects every Bash call and acts on three cases:

- **In-place regex edits are denied.** `sed -i`, `sed --in-place`, `perl -pi` and friends. A regex that half-matches corrupts the file silently; the `Edit` tool matches an exact string and fails loudly instead. `ast-grep` is the escalation for structural multi-file rewrites.
- **Timeouts over 60s are denied**, with the ceiling and both escapes named in the reason.
- **Slow commands with no timeout are denied** — `npm install`, `docker build`, `mvn`, `pytest` and similar. The reason names both escapes: set a timeout, or run it in the background and poll.

Every check is skipped if the command contains `# mayhem:allow`, so a block is never a dead end.

Every verdict is a deny rather than a silent rewrite, and that is deliberate. `PreToolUse` also supports `updatedInput`, which would let the guard clamp an oversized timeout in place instead of refusing the call. But other plugins rewrite Bash through the same field — rtk prefixes commands that way — and two hooks rewriting one call have undefined precedence, so one of them is dropped with no error. A guard that silently loses is worse than one that makes you retype the timeout.

The guard fails open. An unparseable payload or any exception exits cleanly with no output — a broken guard degrades to no guard, never to a broken session.

### Soft limits (the ruleset)

The injected rules cover what a hook cannot check: locate with `Grep`/`Glob`/`LSP` and read only to confirm, use `LSP findReferences` rather than `grep -r` for callers, read a slice rather than a whole file, send fan-out searches to a subagent so only the conclusion returns, never re-read a file to verify an edit that already succeeded.

They also close with the rule that keeps the rest from doing damage: thrift never shortens comprehension. A small diff in the wrong place is a second bug, not a saving.

## The 60-second budget, honestly

Hooks cannot preempt a running subagent — `SubagentStart` and `SubagentStop` only fire at the boundaries, and the `Agent` tool has no timeout parameter. So the budget splits three ways by what is actually achievable:

- **Enforced** on Bash, where `PreToolUse` can deny and rewrite. This is where ten-minute freezes usually come from.
- **A contract** for subagents: the ruleset tells them to return partial results marked as such rather than dig silently past the budget. The model self-polices this.
- **Measured** after the fact. `SubagentStop` carries no duration, but it does carry the agent's transcript path, and that file's birth-to-last-write span is its wall time. Over 60 seconds, you get a warning; under, silence.

## Install

This repo doubles as its own marketplace (`.claude-plugin/marketplace.json`), so no separate catalog repo is needed:

```shell
/plugin marketplace add sergii4/project-mayhem
/plugin install project-mayhem@project-mayhem
```

If the install summary says `Run /reload-plugins to activate.`, run that.

Requires `python3` and `jq`, both standard on macOS with Homebrew. Claude Code only — the whole plugin is hooks, and hosts without hook support have nothing to load.

To iterate locally instead of on the installed copy:

```shell
claude --plugin-dir .
```

## Turning it off

Say "stop mayhem" and the injected rules stop applying for the rest of the session. There is no flag file and no state to reset, because nothing re-injects after `SessionStart`. The Bash guard is a hook rather than an instruction, so it keeps running — use `# mayhem:allow` for individual commands, or disable the plugin.
