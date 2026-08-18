# project-mayhem

A single guard that keeps regex out of refactors.

Renaming a symbol with a regex looks like it works. The code compiles, the tests still pass, and three comments now say something false. This plugin refuses that operation and pushes the work onto a tool that understands the syntax tree.

## What it does

One `PreToolUse` hook, `hooks/guard.py`, on two tools:

```
sed -i / sed --in-place / perl -pi          deny
replace_in_files  mode=regex                deny
replace_in_files  mode=regex, dry_run=true  pass   preview writes nothing
replace_in_files  mode=literal              pass   exact string, no hazard
rename_symbol                               pass   the path the numbers favour
Bash timeout above 60000ms                  deny
slow command with no timeout                deny
```

Two doors lead to the same mistake — Bash reaches for a stream editor, serena's `replace_in_files` takes `mode="regex"` — so both are guarded. `rename_symbol` is left alone, which is the point.

Append `# mayhem:allow` to any Bash command to skip every check, so a block is never a dead end.

## Why — the measurement

One class rename across 28 files of a real Python codebase, six runs, grouped by the tool each run actually used:

| path | tokens | time | turns | silent corruptions |
|---|---|---|---|---|
| `rename_symbol` | 128k – 915k | 9 – 104s | 2 – 20 | 0 |
| regex | 1.30M – 1.45M | 147 – 187s | 26 – 27 | 3 |

**2.4× fewer tokens, 45% less time, no corruption.** There is no overlap between the groups: the worst `rename_symbol` run beat the best regex run on tokens, on time, and on turns.

The three corruptions were a log message, a test assertion, and a comment. On that corpus, 3 of 72 occurrences of the symbol name live in comments or strings — invisible to a syntax check and to a reference count, which is exactly why they ship. The extra turns in the regex group are spent discovering and repairing that damage, so the correctness failure *is* the cost.

## What it deliberately does not do

Earlier versions injected a ruleset into every session — search discipline, sliced reads, subagent delegation, a 60-second budget. It was measured across 12 A/B runs on a code search task and produced no attributable behavioural change: no whole-file reads in either arm, no subagent delegations, near-identical tool counts. The one replicated difference, −33% input tokens, lived entirely in `cache_read` and was bimodal — a prompt-cache artifact, not better tool use. An injection costing 687 tokens per session whose effect cannot be traced to any of its rules does not earn its place, so it was deleted.

What survives is the part that demonstrably changes an outcome.

## Known limitations

- **The stream-editor rule matches the raw command string.** Any command that merely *mentions* `sed -i` is refused, including writing documentation about it. Simple, no shell parsing, and a genuine false-positive class. Use `# mayhem:allow`.
- **The timeout rules are unmeasured.** They never fired in any benchmark run. They rest on argument, not evidence.
- **One task, one symbol, one repo.** The measurement above is a single well-characterised case, not a suite.

## Install

This repo is its own marketplace, so no separate catalog is needed:

```shell
/plugin marketplace add sergii4/project-mayhem
/plugin install project-mayhem@project-mayhem
```

Requires `python3`. Claude Code only — the whole plugin is a hook. Restart after installing or updating; the hook registers at session start.

Iterate locally with `claude --plugin-dir .`

The `rename_symbol` and `replace_in_files` tools come from [serena](https://github.com/oraios/serena), configured per project. Without it the guard still blocks stream editors, and `gopls rename` covers Go from the shell.
