#!/usr/bin/env python3
"""PreToolUse guard: keeps regex out of refactors, and bounds Bash wall time.

Two doors lead to the same mistake. Bash reaches for stream editors; serena's
replace_in_files takes mode="regex". Measured on one real class rename across 28
files, the regex path corrupted 3 of 72 sites — a log message, a test assertion
and a comment — then burned 12 extra turns finding and repairing them, for 2.4x
the tokens and 45% more wall time than rename_symbol. Both doors are guarded.

Every verdict is a deny, never an updatedInput rewrite. Other PreToolUse hooks
rewrite Bash too (rtk emits updatedInput to prefix commands), and two hooks
rewriting one call have undefined precedence — the loser is dropped silently. A
deny composes with anyone else's rewrite.

Fails open. Any unexpected payload or exception exits 0 with empty stdout, so a
broken guard degrades to no guard rather than to a broken session.
"""

import json
import re
import sys

MAX_TIMEOUT_MS = 60000
ESCAPE = "# mayhem:allow"

# In-place stream edits: sed -i / -i.bak / --in-place, and perl -i / -pi / -i.bak
INPLACE = re.compile(
    r"\bsed\b[^|;&\n]*?\s-i(?![a-zA-Z])"
    r"|\bsed\b[^|;&\n]*?\s--in-place"
    r"|\bperl\b[^|;&\n]*?\s-[a-zA-Z]{0,3}i(?![a-zA-Z])"
)

INPLACE_REASON = (
    "Blocked: in-place regex edit. A regex that half-matches corrupts the file "
    "silently. Use the Edit tool for a few exact sites, serena rename_symbol to "
    "rename, or ast-grep for a structural rewrite."
)

REGEX_REPLACE_REASON = (
    "Blocked: regex replacement across files — the same mistake as a stream "
    "editor, through a different door. Measured on a real rename, this path "
    "corrupted a log message, a test assertion and a comment, then cost 2.4x the "
    "tokens repairing them. Use rename_symbol to rename a symbol; mode='literal' "
    "for an exact string; dry_run=true to preview."
)

# Commands that routinely run for minutes and are the usual cause of a frozen agent
SLOW = re.compile(
    r"\b(?:"
    r"npm\s+(?:i|install|ci|test|run\s+build)"
    r"|yarn(?:\s+install)?"
    r"|pnpm\s+(?:i|install)"
    r"|pip3?\s+install"
    r"|brew\s+(?:install|upgrade|update)"
    r"|cargo\s+(?:build|test)"
    r"|go\s+(?:build|test)"
    r"|docker\s+(?:build|pull|compose\s+up)"
    r"|git\s+clone"
    r"|mvn|gradle|make|pytest|jest|tsc"
    r")\b"
)

SLOW_REASON = (
    "Blocked: long-running command with no explicit timeout. Either set timeout "
    "to {} or less, or pass run_in_background: true and poll.".format(MAX_TIMEOUT_MS)
)


def deny(reason, escapable=True):
    if escapable:
        reason += " Append '{}' to the command to override.".format(ESCAPE)
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )


def guard_replace_in_files(tool_input):
    # A preview writes nothing, so it is always allowed
    if tool_input.get("dry_run"):
        return
    if str(tool_input.get("mode") or "").lower() == "regex":
        deny(REGEX_REPLACE_REASON, escapable=False)


def guard_bash(tool_input):
    command = tool_input.get("command") or ""
    if not isinstance(command, str) or ESCAPE in command:
        return

    if INPLACE.search(command):
        deny(INPLACE_REASON)
        return

    # Background work cannot freeze the agent, so the ceiling does not apply to it
    if tool_input.get("run_in_background"):
        return

    timeout = tool_input.get("timeout")
    if isinstance(timeout, (int, float)) and timeout > MAX_TIMEOUT_MS:
        deny(
            "Blocked: timeout {}ms exceeds the {}ms ceiling. Re-run with timeout {} "
            "or less, or pass run_in_background: true and poll.".format(
                int(timeout), MAX_TIMEOUT_MS, MAX_TIMEOUT_MS
            )
        )
        return

    if timeout is None and SLOW.search(command):
        deny(SLOW_REASON)


def main():
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input") or {}
    if str(payload.get("tool_name") or "").endswith("replace_in_files"):
        guard_replace_in_files(tool_input)
    else:
        guard_bash(tool_input)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
