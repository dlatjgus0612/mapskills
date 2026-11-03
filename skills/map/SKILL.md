---
name: map
description: "1 Web · 2 App · 3 Video · 4 Code · 5 Security · 6 AI · 7 Docs · 8 Tokens · 9 Other → your installed skills as /name - description / example. For task-based picks use /map-rcm. Also for \"what skills do I have\"."
argument-hint: "[1-9 | category]"
---

# map

Skill map for Claude Code and Codex. If the argument starts with `rcm`, follow the map-rcm skill (`<this skill's directory>/../map-rcm/SKILL.md`) instead. Answer in the user's language (Korean if they write Korean).

`MS` = `python3 <this skill's directory>/scripts/mapskills.py`. Registry (curated, not necessarily installed) = `<this skill's directory>/registry.json`.

## Refresh the index
Run `MS scan --json` once per session (or when `~/.mapskills/index.json` is missing or older than a day). Work only from its output: every installed skill with name, description, agents, category, and git info. Never list skills from memory.

## /map (no argument)
Print only this line and wait:
`1 웹  2 앱  3 영상  4 코드  5 보안  6 AI  7 문서  8 토큰  9 기타` (use English labels for English users)

## /map <number or category>
Show that category's installed skills, one per line, nothing else:
```
1. /hyperframes - HTML·GSAP 장면을 영상으로 렌더링 / 예: "우리 앱 소개 15초 영상 만들어줘"
```
- `/name` exactly as invoked (plugin skills keep their `plugin:` prefix). When not every selected agent has it, add the agents that do, e.g. `(Claude Code)`.
- Description: one short phrase, at most ~40 characters (Korean) or ~8 words, in the user's language. Cut detail; the details view has it.
- Example: one concrete request that would trigger it.
End with one line: pick a number or name to see details.

## Details for one skill
Read its SKILL.md (path from the index). Show: what (1–2 sentences), when to use (2–3), how to call (Claude `/name …`, Codex `$name …`, respecting argument-hint), cautions (cost, API keys, downloads, hooks, overlap with a similar installed skill). Do not run it.

## Privacy
Everything stays in `~/.mapskills`. Do not print or store the user's prompt text, file contents, or paths outside the current project in logs. `MS config usage off` disables usage counting and logging.
