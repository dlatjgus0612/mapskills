---
name: map-check
description: "Review all installed skills (existing and mapskills-installed) for overlaps, unused or outdated skills and better alternatives, then propose a cleanup. Changes nothing without approval. /map-check."
argument-hint: "[category]"
---

# map-check

Audit the user's skills and propose a tidy setup. Answer in the user's language. Read-only until the user approves.

`MS` = `python3 <this skill's directory>/../map/scripts/mapskills.py`. Registry = `<this skill's directory>/../map/registry.json`.

## Gather
1. `MS scan --json` (all skills, agents, git repo and last commit date).
2. `MS usage --days 30` (local invocation counts; skip if usage is off).
3. `MS updates` (pinned commit vs upstream for repos mapskills fetched).
4. Read registry `groups` and `notes`.

## Analyse
For each category, find:
- **Overlaps**: two or more skills doing the same job. Use registry groups first, then compare descriptions; open both SKILL.md files before judging. Prefer the one that is more specific, deeper (reference files, examples), maintained more recently, and actually used.
- **Duplicates of rules**: a skill whose content is already in the user's global rules (CLAUDE.md / AGENTS.md). Read the rules, do not edit them.
- **Unused**: installed but zero uses in 30 days and not a core skill. Suggest disabling, not deleting.
- **Outdated**: last upstream commit older than 9 months, or `NEWER-UPSTREAM` from `MS updates`.
- **Agent gaps**: a skill only one agent has when the other could use it too.
- **Better options**: a registry entry clearly stronger than an installed skill for the same job. Explain the concrete difference.

## Report
One table per category: skill · verdict (keep / disable / replace with X / update / add) · one-line reason with evidence (file count, last commit, uses). Then a short ordered action list.

## Apply (only after approval)
- Links mapskills created: `MS unlink`, `MS install`, or re-install at a newer commit.
- Anything else (the user's own skills, plugins, other installers): give the exact command or step for the user to run. Never delete or edit it yourself.
- Finish with `MS scan` and a before/after count.
