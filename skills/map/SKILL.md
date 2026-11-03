---
name: map
description: "1 Web · 2 App · 3 Video · 4 Code · 5 Security · 6 AI · 7 Docs · 8 Tokens · 9 Other → skill list | rcm <task> → best skills + a refined prompt. Also for \"which skill should I use\", \"what skills do I have\"."
argument-hint: "[1-9 | rcm <task>]"
---

# map

Skill map and recommender for Claude Code and Codex. Answer in the user's language (Korean if they write Korean).

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
- `/name` exactly as invoked (plugin skills keep their `plugin:` prefix). Add `(Claude)` or `(Codex)` when only one agent has it.
- Description: 20–40 plain words in the user's language, from the skill's own description.
- Example: one concrete request that would trigger it.
End with one line: pick a number or name to see details.

## Details for one skill
Read its SKILL.md (path from the index). Show: what (1–2 sentences), when to use (2–3), how to call (Claude `/name …`, Codex `$name …`, respecting argument-hint), cautions (cost, API keys, downloads, hooks, overlap with a similar installed skill). Do not run it.

## /map rcm <task>
Recommend; do not do the task.

1. **Context.** `MS project` for the current directory's stack tags. If usage is on, `MS usage --days 30` for local invocation counts.
2. **Parse the task** into: domain (web/app/video/…), action (create · improve · review · debug · research · learn), target (file, URL, screen, model), stack, and hard constraints.
3. **Retrieve.** From the index, shortlist up to 10 candidates by matching name, description and trigger phrases against the parsed task and stack tags. Include plugin skills.
4. **Read and rank.** Open the first ~40 lines of each candidate's SKILL.md. Score by: fits the action (create vs refine vs review), fits the stack, specificity (a specialized skill beats a general one), and real usage (used recently = slight boost; installed but never used = no penalty). Drop skills whose own description says not to use them for this case.
5. **Resolve overlaps.** If two picks are in the same registry `group`, keep one and say why in one clause.
6. **Order** 1–3 skills in the sequence they would be used (plan → build → check).
7. **Gap fill.** If nothing installed fits well, look in registry.json for a matching skill that is not installed and suggest it with `/map-set <id>`. If no skill helps, say a plain request is enough.
8. **Output**, in this shape:
   - **추천 스킬**: `/name - why` per line, in order.
   - **다듬은 프롬프트**: one code block the user can paste. First line invokes the first skill. Then: target, desired result, constraints (stack from step 1, what not to touch), and how to verify done. Fill facts you detected; never invent paths, URLs, repo ids or numbers — leave `<빈칸>` placeholders.
   - **빈칸 안내**: one line per placeholder.
9. **Clipboard.** Put only the code block's text on the clipboard with a heredoc: macOS `pbcopy`, Linux `wl-copy` or `xclip -selection clipboard`, Windows `clip.exe`. On success end with "📋 클립보드에 복사했어요. 빈칸만 채워 붙여넣으세요". If no tool works, skip silently.
10. **Log.** `MS log --tags <domain,action,stack> --skills <picked,names>` (no prompt text is stored; it is a no-op when usage is off).

## Privacy
Everything stays in `~/.mapskills`. Do not print or store the user's prompt text, file contents, or paths outside the current project in logs. `MS config usage off` disables usage counting and logging.
