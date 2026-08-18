PROJECT MAYHEM ACTIVE — operational efficiency rules. These govern how tool calls
and context get spent. They do not govern prose style or code style.

## Finding code

- Locate with Grep/Glob or symbol tools. Read only to confirm. Never Read a file in order to search it.
- Symbols and their references: serena `find_symbol` / `find_referencing_symbols` where available — it loads the project itself. The built-in `LSP` tool only covers the session's working directory and returns partial results outside it without saying so.
- "What implements this": `ast-grep -p 'def <name>'`. Python language servers cannot answer it at all.
- grep is complete but textual — on a common name roughly a tenth of hits are comments or strings. Verify a hit is real code before acting on it.
- Read the slice: pass `offset`/`limit` once the region is known. Whole-file reads are for small files or when the whole file genuinely matters.
- Fan-out searches go to a subagent. The conclusion returns, the file dumps do not.
- Never re-read a file to verify a successful Edit/Write. The tool errors if it failed.

## Changing code

- Edits go through the Edit tool. Never in-place regex edits on source: exact-match fails loudly, a half-matching regex corrupts silently. (hook-enforced)
- A rename is a refactor, not a search-and-replace: serena `rename_symbol`, or `gopls rename` for Go. Never grep, never ast-grep.
- Python: zero references on a method that overrides an interface is a trap, not a green light — polymorphic call sites never name the implementation. Enumerate implementations with ast-grep, then rename the interface and all of them, or none.
- `ast-grep` narrows, it never completes: a pattern finds only what it describes. Use it for structural rewrites, not renames.
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
