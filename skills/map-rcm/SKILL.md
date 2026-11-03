---
name: map-rcm
description: "/map-rcm <task> → the 1-3 installed skills that fit, in order, plus a refined paste-ready prompt (copied to clipboard). Also for \"which skill should I use for …\"."
argument-hint: "<task in your own words>"
---

# map-rcm

Reply in the user's language: the language of their message, or if the invocation has no words (e.g. just `/map-check`), the language of their earlier messages or global rules; fall back to `$LANG`.

`MS` = `python3 <this skill's directory>/../map/scripts/mapskills.py`. Registry = `<this skill's directory>/../map/registry.json`.
Refresh the index with `MS scan --json` if `~/.mapskills/index.json` is missing or older than a day, and work only from it.

Recommend skills for a task; do not do the task.

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
Do not store the prompt text. `MS log` keeps only tags and skill names, and does nothing when usage is off (`MS config usage off`).
