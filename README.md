# mapskills

Skill map, recommender and installer for **Claude Code** and **Codex**.
Your own agent does the work: mapskills ships skills and a small helper script, not a black-box installer.

| Command | What it does |
|---|---|
| `/map` | Pick a category → `/skill - description / example prompt` for every installed skill |
| `/map rcm <task>` | Best 1–3 skills for the task, in order, plus a refined prompt copied to your clipboard |
| `/map-set` | Install curated top skills, one core skill per category (or a whole category, or by id) |
| `/map-check` | Review all your skills: overlaps, unused, outdated, better alternatives → cleanup plan |

In Codex use `$map`, `$map-set`, `$map-check`. Installed as a Claude plugin, the commands are namespaced (`/mapskills:map`).

## Install

**git clone (Claude Code + Codex)**
```bash
git clone https://github.com/dlatjgus0612/mapskills.git ~/.mapskills-repo
~/.mapskills-repo/install.sh          # remove: ~/.mapskills-repo/install.sh --remove
```

**Claude Code plugin**
```
/plugin marketplace add dlatjgus0612/mapskills
/plugin install mapskills@mapskills
```

Then open a new session and run `/map-set` (or `/map` to see what you already have).

## Promises

1. **Your existing setup is not touched.** mapskills only adds symlinks to `~/.claude/skills` and `~/.agents/skills`. A name that already exists is skipped. It never edits `CLAUDE.md`, `AGENTS.md` or settings. `rules/example-rules.md` is a reference you can copy yourself.
2. **Curated, pinned sources.** `skills/map/registry.json` lists popular skills per category with the upstream repo, a pinned commit, license and overlap group. Skills are fetched from the original repos into `~/.mapskills/vendor`; nothing third-party is copied into this repo.
3. **You see the risk first.** Before linking, `/map-set` shows a report of downloads, hooks, package installs and credential handling found in the skill's files, and waits for your OK.
4. **Local only.** The index, usage counts and logs live in `~/.mapskills`. No telemetry, no prompt text stored. Turn usage counting off with `python3 skills/map/scripts/mapskills.py config usage off`.

## How `/map rcm` chooses

1. Indexes every installed skill (personal, mapskills, plugins) from its `SKILL.md`.
2. Detects your project's stack (`package.json`, `pyproject.toml`, `Package.swift`, …).
3. Parses the task into domain, action (create, improve, review, debug, research), target and constraints.
4. Shortlists ~10 candidates, reads each `SKILL.md`, ranks by fit, specificity and your recent use.
5. Resolves overlaps with registry groups, orders the picks (plan → build → check).
6. Suggests an uninstalled registry skill when nothing installed fits.
7. Writes a paste-ready prompt with your stack filled in and `<blanks>` for anything it does not know.

## Categories in the registry

| Category | Core skill (installed by `/map-set`) | Others |
|---|---|---|
| Web | taste-skill | impeccable, hallmark, ui-ux-pro-max, react-best-practices, web-design-guidelines, gsap-scrolltrigger, motion-foundations, motion-patterns, accessibility, webapp-testing, react-three-fiber, threejs-webgl |
| App | react-native-skills | react-native-patterns, swiftui-ui-patterns, swift-concurrency-expert |
| Video | hyperframes (+ cli, registry, media-use) | reverse-any-video, hypit |
| Code | systematic-debugging | test-driven-development, writing-plans, ponytail, ponytail-review, python-patterns, python-testing, docker-patterns, reverse-engineer-anything |
| Security | security-audit | software-security, differential-review, supply-chain-risk-auditor, fp-check |
| AI·ML | hf-cli | huggingface-local-models, huggingface-llm-trainer, trl-training, pytorch-patterns, mcp-builder |
| Docs | graphify | agent-reach, claude-seo (plugin) |
| Tokens | caveman | |

Bundled: `ui-effects-glossary` — turns "make it react to the mouse" into effect names (custom cursor, 3D tilt, magnetic button, scroll reveal…) and how to build them.

All listed skills belong to their authors under their own licenses (see `license` in the registry).

## Contributing

Add or update a registry entry (repo, path, pinned commit, license, category, group). Run `scripts/privacy-check.sh` before committing.

---

## 한국어 요약

Claude Code와 Codex에서 같이 쓰는 스킬 지도·추천·설치 도구입니다.

- `/map`: 분야를 고르면 `/스킬 - 설명 / 예시 프롬프트`로 보여줍니다.
- `/map rcm <작업>`: 작업에 맞는 스킬 1~3개를 쓰는 순서대로 추천하고, 다듬은 프롬프트를 클립보드에 복사합니다.
- `/map-set`: 분야별 대표 스킬을 설치합니다. 기존 스킬과 규칙 파일은 건드리지 않습니다.
- `/map-check`: 겹치는 스킬, 안 쓰는 스킬, 오래된 스킬, 더 나은 대안을 찾아 정리안을 줍니다. 승인 전에는 아무것도 바꾸지 않습니다.

모든 데이터는 `~/.mapskills`에만 저장되고 외부로 보내지 않습니다.
