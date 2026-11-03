# AGENTS.md

Guide for AI agents (and humans) changing this repo.

## What this is
Skills for coding agents plus one stdlib-only helper:
- `skills/<name>/SKILL.md` — the product. Instructions an agent follows: `map`, `map-rcm`, `map-set`, `map-check`, `map-rule`, `ui-effects-glossary`.
- `skills/map/scripts/mapskills.py` — deterministic work the skills call (`MS …`): scan, install, link, check, usage.
- `skills/map/registry.json` — curated third-party skills, pinned commits, overlap groups.
- `skills/map/agents.json` — where each coding agent reads skills (from vercel-labs/skills docs/agents.md).
- `install.sh` — thin wrapper around `mapskills.py self-install`.

## Invariants (do not break)
1. Never edit, move or delete anything the user already has. Only add symlinks; only remove links recorded in `~/.mapskills/state.json`.
2. All state lives in `~/.mapskills` (`MAPSKILLS_HOME`). No network except `git` to repos in the registry. No telemetry.
3. Logs keep skill names, tags and counts only — never prompt text, file contents or paths.
4. No personal data in the repo: no home paths, emails, hostnames, tokens. `scripts/privacy-check.sh` must pass.
5. Python standard library only; must run on the system `python3`.
6. Skills change nothing without user approval; they show a plan or a risk report first.

## Before you finish
```bash
python3 -m unittest discover -s tests            # offline, ~0.5s
MAPSKILLS_NET=1 python3 -m unittest discover -s tests   # also fetches one pinned skill
./scripts/privacy-check.sh
claude plugin validate .                         # if Claude Code is available
```

## Common changes
- **Add a registry skill**: entry with `id`, `name`, `category`, `repo`, 40-char `commit`, `path` (or `paths.claude` / `paths.codex` for per-agent copies), `license`, one-line `ko`, optional `group`, `core`, `notes`. Non-git items use `type: tool | claude-plugin | mcp` with `install` (and `requires`). Read the skill's files at that commit first; mention downloads, hooks or credentials in `notes`.
- **Add an agent**: `agents.json` entry with `id`, `label`, global `skills` folder, `detect` dirs. Agents sharing a folder go in one entry via `aliases`.
- **Change a skill's behaviour**: keep SKILL.md short and imperative; put deterministic steps in `mapskills.py` with a test.
