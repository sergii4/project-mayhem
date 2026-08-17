#!/usr/bin/env python3
"""SubagentStop: warn when a subagent blew the 60s budget.

SubagentStop carries no duration, but it does carry agent_transcript_path, and
that file's birth-to-last-write span is the agent's wall time. So no start-side
bookkeeping and no state file are needed.

Fails open, and stays silent when the agent was within budget.
"""

import json
import os
import sys

BUDGET_SECONDS = 60

try:
    payload = json.load(sys.stdin)
    stat = os.stat(payload["agent_transcript_path"])
    started = getattr(stat, "st_birthtime", stat.st_ctime)
    seconds = int(stat.st_mtime - started)
    if seconds > BUDGET_SECONDS:
        agent = payload.get("agent_type", "subagent")
        print(json.dumps({"systemMessage": "mayhem: {} ran {}s, over the {}s budget "
              "— split the next one or have it report partial results".format(
                  agent, seconds, BUDGET_SECONDS)}))
except Exception:
    pass
