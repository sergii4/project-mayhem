PROJECT MAYHEM ACTIVE — operational efficiency rules. These govern how tool calls
and context get spent. They do not govern prose style or code style.

## Tool discipline

- Locate with Grep/Glob/LSP. Read only to confirm. Never Read a file in order to search it.
- Callers of a symbol: `LSP findReferences` or `incomingCalls`, not `grep -r`. AST has no false hits in comments and strings.
- Symbol by name: `LSP workspaceSymbol`, not glob guessing.
- LSP needs a server for the file type and errors out without one. Then fall back to Grep, and check each hit is real code rather than a comment or a string — that check is what the language server was doing for you.
- Read the slice: pass `offset`/`limit` once the region is known. Whole-file reads are for small files or when the whole file genuinely matters.
- Edits go through the Edit tool. Never `sed -i` or `perl -pi` on source: exact-match fails loudly, a half-matching regex corrupts silently. (hook-enforced)
- Structural rewrite across many files: `ast-grep -p '<pattern>' -r '<rewrite>'`. It matches syntax, so it cannot hit comments or strings the way a regex loop does.
- Fan-out searches go to a subagent. The conclusion returns, the file dumps do not.
- Never re-read a file to verify a successful Edit/Write. The tool errors if it failed.
- Bash gets an explicit `timeout` of 60000 or less. Anything longer runs with `run_in_background`. (hook-enforced)

## Context discipline

- Quote the decisive line of an error, not the whole log.
- Relay a subagent's conclusion, not its raw output.
- Do not re-derive facts already established in this conversation.

## Time discipline

- About 60 seconds per unit of work. Not finished means report what is done and what
  is left, explicitly marked partial. Never keep digging silently past the budget.

## Where not to economise

- Thrift never shortens comprehension. Trace the real flow before editing. A small
  diff in the wrong place is a second bug, not a saving.
- Never change shared behaviour without checking its callers first.

Off only: "stop mayhem".
