---
name: map-set
description: "Install or update curated top skills for Claude Code, Codex, Cursor, Gemini CLI and other agents: new → install, already installed by mapskills → update if newer, yours → left alone. Never touches existing skills or rules. /map-set, /map-set <category|id>."
argument-hint: "[core | <category> | <skill id>...] [--latest]"
---

# map-set

Install or update skills from the curated registry. Answer in the user's language.

`MS` = `python3 <this skill's directory>/../map/scripts/mapskills.py`. Registry = `<this skill's directory>/../map/registry.json`.

## Hard rules
- Never modify, move or delete existing skills, CLAUDE.md, AGENTS.md or settings. mapskills only adds symlinks into `~/.claude/skills` and `~/.agents/skills` and keeps fetched repos in `~/.mapskills/vendor`.
- Install or update nothing before the user confirms the final list.
- Third-party code: show the risk report before linking and call out downloads, hooks, package installs and credential handling.

## 0. Where to install (first run only)
Run `MS config`. If `first_run` is true, ask two questions in one go (a picker if the agent has one, otherwise a numbered list), then save with `MS config root <dir>` / `MS config agents <list>`:
1. **Where the skill files live**
   - Default (recommended): files in `~/.mapskills/vendor`, and each skill appears in `~/.claude/skills` / `~/.agents/skills` as a link, like any other skill.
   - A folder you choose for keeping skills organized (e.g. `~/skills`): files there, same links in the agent folders.
   Explain that each agent only reads its own skills folder (e.g. `~/.claude/skills`, `~/.agents/skills`, `~/.cursor/skills`), so the links are always created there; the choice is only where the real files sit.
2. **Which agents**: run `MS agents` (detected on this machine) and let the user pick several. Default: Claude Code + Codex. Note that `~/.agents/skills` is shared by Codex, Cline, Warp, Zed, Kimi Code CLI, Pi and others, so one choice covers them all. Unlisted tools: `name=/path/to/skills`. `MS agents --all` shows the ~65 known agents.
   Save with `MS config agents claude-code,codex,cursor,…`.
Mention they can change it later with the same commands; existing installs stay where they are.

## 1. Plan
1. Pick entries from the argument: none or `core` → entries with `"core": true`; a category (`web`, `app`, `video`, `code`, `security`, `ai`, `docs`, `token`) → all its entries; ids → those plus their `with` list.
2. `MS check <ids>` gives each entry's status:
   - `new` → **install**
   - `update` (mapskills installed an older commit) → **update** to the pinned commit
   - `up-to-date` → nothing to do
   - `user-owned` (you already have a skill with that name) → **keep yours**; if it is a git checkout, show `git -C <path> log -1 --format=%cs` and suggest `git -C <path> pull` for the user to run
   - `manual` (`tool`, `claude-plugin`, `mcp`) → show `install`, `requires` and `notes`
3. For `mcp` entries, check `requires` first (e.g. for ghidra-mcp: a Ghidra install and `java -version`). If missing, list it as "skipped: needs X" and do not offer it.
4. Also flag **overlaps**: an installed skill in the same registry `group`, or one doing the same job by its description.
5. Show one table: name · category · what it does · action (install / update / keep yours / skip) · license · notes. Ask once to confirm or edit. `--latest` means use the upstream HEAD instead of the pinned commit; say that it is unreviewed.

## 2. Apply
- install / update: `MS install <ids> --dry-run` → explain RISK lines in plain words → after OK, `MS install <ids>` (add `--latest` if asked).
- manual entries: run the shown command only after the user agrees. graphify appends lines to CLAUDE.md: ask whether to remove them afterwards.

## 3. Activate
Installing is not the same as using. Tell the user, briefly:
- Start a **new session** (Claude Code and Codex load skills at session start).
- Most skills switch on by themselves when the request matches their description. **Mode skills** (ponytail, caveman, …) only run when called: `/ponytail`, `$ponytail`.
- To make the agent look for skills on its own before starting work, offer `/map-rule`, which can propose a one-line skill-routing rule for their CLAUDE.md / AGENTS.md (applied only with approval).
- `/map-rcm <task>` picks the right ones for a task.

Finish with `MS scan` and a summary split by agent: installed, updated, kept, skipped.

## Removing
`MS unlink <name>` removes only links mapskills created. `MS status` lists them.
