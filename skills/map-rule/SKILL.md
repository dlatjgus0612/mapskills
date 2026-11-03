---
name: map-rule
description: "Review your CLAUDE.md / AGENTS.md and propose a tighter version: English, fewer tokens, no duplicates with skills, Claude/Codex in sync, optional skill-routing line. Your files stay as they are unless you approve. /map-rule."
argument-hint: "[en | short | sync | route]"
---

# map-rule

Propose better global rules; never silently change them. Answer in the user's language.

`MS` = `python3 <this skill's directory>/../map/scripts/mapskills.py`. `HOME_DIR` = the `home` value from `MS config` (normally `~/.mapskills`).

## Read
1. Global rule files: `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` (note if either is a symlink and where it points, and whether they are identical). Also any `@import`ed files Claude loads.
2. `MS scan --json` for installed skills, to spot rules that a skill already covers.
3. Measure each file: lines, characters, and a rough token count (characters ÷ 4 for English, ÷ 1.5 for Korean/CJK).

## Propose
Build one proposed file and keep every rule's meaning. Options (argument picks one, none = all that apply):
- **en**: translate to concise English. English usually costs fewer tokens than Korean for the same meaning. Keep proper nouns, paths, commands and examples exactly.
- **short**: remove filler, merge repeated points, turn paragraphs into one-line bullets, drop examples that repeat the rule. Never drop a constraint.
- **sync**: if Claude and Codex files differ, merge them into one neutral file ("the agent", no product names where unnecessary) and suggest one source file symlinked to both paths.
- **route**: add one line so skills get used without being named, e.g. `Before starting a non-trivial task, check installed skills (/map-rcm) and use the one that fits.`
- **dedupe**: list rules that duplicate an installed skill (or vice versa) and suggest which side to keep.

Also flag, without fixing: contradictions, rules that reference missing files, skills or servers, and secrets or personal data that should not be in a rules file.

## Show
- Save the proposal to `HOME_DIR/rules/proposed-<date>.md`. Do not touch the originals.
- Show a before/after table (lines, characters, ~tokens, saved %) and a diff of the meaningful changes, grouped by type (translated, shortened, merged, added, flagged).

## Apply (only after explicit approval)
1. Back up each original to `HOME_DIR/rules/backup-<date>-<name>`.
2. If the target is a symlink, write the source file it points to, and say so.
3. Write the approved version, then show the restore command (`cp <backup> <original>`).
