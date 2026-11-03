---
name: map-set
description: "Install curated top skills by category (one core skill per category by default) for Claude Code and Codex without touching existing skills or rules. /map-set, /map-set <id|category>, /map-set core."
argument-hint: "[core | <category> | <skill id>...]"
---

# map-set

Install skills from the curated registry. Answer in the user's language.

`MS` = `python3 <this skill's directory>/../map/scripts/mapskills.py`. Registry = `<this skill's directory>/../map/registry.json`.

## Hard rules
- Never modify, move or delete existing skills, CLAUDE.md, AGENTS.md or settings. mapskills only adds symlinks into `~/.claude/skills` and `~/.agents/skills` and keeps fetched repos in `~/.mapskills/vendor`. `MS link` refuses existing names; report those as "already have one" and move on.
- Install nothing before the user confirms the final list.
- Third-party code: show the risk report before linking and call out downloads, hooks, package installs and credential handling.

## Flow
1. `MS scan` to see what the user already has.
2. Build the plan from the argument:
   - none or `core`: the registry entries with `"core": true` (one per category).
   - a category (`web`, `app`, `video`, `code`, `security`, `ai`, `docs`, `token`): every entry in it.
   - ids: those entries, plus anything in their `with` list.
3. Mark each planned entry: **new**, **already installed** (same name in the index), or **overlaps** (an installed skill in the same `group`, or an installed skill doing the same job by its description). Recommend skipping overlaps and say which one the user already has.
4. Show the plan as a table (name · category · what it does in one line · status · license · notes) and ask once to confirm or edit.
5. For confirmed `git` entries: `MS install <id> --dry-run` first, show the RISK lines in plain words, then `MS install <id>` after the user agrees. For `tool` and `claude-plugin` entries, show the `install` command and `notes`, and run it only after the user agrees (these may install CLIs or plugins; graphify edits CLAUDE.md, so ask whether to remove the lines it adds).
6. `MS scan` again and report what is now available, split by agent (Claude, Codex). Tell the user a new session may be needed for the agent to load new skills.

## Removing
`MS unlink <name>` removes only links mapskills created. `MS status` lists them.
