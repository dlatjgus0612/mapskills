# mapskills

Skill map, recommender and installer for **Claude Code**, **Codex** and other coding agents (Cursor, Gemini CLI, Copilot, OpenCode, Windsurf, … ~65 known).
Your own agent does the work: mapskills ships skills and a small helper script, not a black-box installer.

| Command | What it does |
|---|---|
| `/map` | Pick a category → `/skill - description / example prompt` for every installed skill |
| `/map-rcm <task>` | Best 1–3 skills for the task, in order, plus a refined prompt copied to your clipboard |
| `/map-set` | Install or update curated skills: new → install, older → update, yours → kept. Core set, a category, or by id |
| `/map-check` | Review all your skills: overlaps, unused, outdated, better alternatives → cleanup plan |
| `/map-rule` | Propose a tighter CLAUDE.md / AGENTS.md (English, fewer tokens, synced, optional skill-routing line). Originals kept unless you approve |

In Codex use `$map`, `$map-rcm`, `$map-set`, `$map-check`, `$map-rule`; other agents use their own skill syntax. Installed as a Claude plugin, the commands are namespaced (`/mapskills:map`).

## Install

**git clone (any agent)**
```bash
git clone https://github.com/dlatjgus0612/mapskills.git ~/.mapskills-repo
~/.mapskills-repo/install.sh --list                                  # agents detected here
~/.mapskills-repo/install.sh                                         # Claude Code + Codex (default)
~/.mapskills-repo/install.sh --agents claude-code,codex,cursor,gemini-cli
~/.mapskills-repo/install.sh --remove                                # undo
```

**Claude Code plugin**
```
/plugin marketplace add dlatjgus0612/mapskills
/plugin install mapskills@mapskills
```

Then open a new session and follow the steps below.

## Where skills go

Each agent reads skills from its own folder: Claude Code `~/.claude/skills`, Codex (and Cline, Warp, Zed, Kimi, Pi…) `~/.agents/skills`, Cursor `~/.cursor/skills`, Gemini CLI `~/.gemini/skills`, and so on (`skills/map/agents.json`, from the vercel-labs/skills agent table). Every skill mapskills installs shows up there like any other skill. On the first `/map-set` you choose:

- **where the real files live**: `~/.mapskills/vendor` (default) or a folder you pick to keep skills organized (`config root <dir>`); the agent folders hold links to it.
- **which agents**: detected ones are suggested; pick any number (`config agents claude-code,codex,cursor`), or add your own `name=/path/to/skills`.

## First setup when you already have skills and rules

mapskills never edits or deletes what you already have, so you can run this on a busy setup.

1. **Install** (above). `install.sh` prints `skip` for any name you already use. If you already have a skill called `map`, either rename yours or use the plugin install, whose commands are namespaced (`/mapskills:map`).
2. **Look**: `/map` shows everything you have, grouped into 9 categories, including your own skills and plugins.
3. **Audit what you have**: `/map-check`. It reports overlaps, unused (0 uses in 30 days), outdated (no upstream commit in 9 months) and skills that repeat your CLAUDE.md / AGENTS.md rules. It changes nothing; for your own skills it gives you the command to run.
4. **Fill gaps**: `/map-set`. It plans the core set and marks each item *install*, *update* (a newer pinned commit), *keep yours* (same name already installed by you) or *overlaps with X*. You confirm the list, see a risk report (downloads, hooks, package installs) per skill, then it links them for Claude Code and Codex.
5. **Tidy the combined set**: `/map-check` again, now that old and new sit side by side. Apply only the changes you approve.
6. **Make them get used**: start a new session. Most skills trigger on their own when a request matches; mode skills (ponytail, caveman) need to be called. `/map-rule route` can add one rule line so the agent checks skills before starting work.
7. **Rules (optional)**: `/map-rule` proposes a shorter, English, synced version of your rules and saves it beside them; nothing changes until you approve (with a backup). `rules/example-rules.md` is a reference set.
8. **Daily use**: `/map-rcm <what you want to do>` → skills in order + a prompt on your clipboard.

**Update**: `git -C ~/.mapskills-repo pull`, then `/map-set` (installed skills move to the newly pinned commits) or `/map-set <id> --latest` for upstream HEAD (unreviewed).
**Uninstall**: `~/.mapskills-repo/install.sh --remove`, `python3 ~/.mapskills-repo/skills/map/scripts/mapskills.py unlink <name>` for skills `/map-set` added (`... status` lists them), then delete `~/.mapskills`.

## Promises

1. **Your existing setup is not touched.** mapskills only adds symlinks to `~/.claude/skills` and `~/.agents/skills`. A name that already exists is skipped. It never edits `CLAUDE.md`, `AGENTS.md` or settings. `rules/example-rules.md` is a reference you can copy yourself.
2. **Curated, pinned sources.** `skills/map/registry.json` lists popular skills per category with the upstream repo, a pinned commit, license and overlap group. Skills are fetched from the original repos into `~/.mapskills/vendor`; nothing third-party is copied into this repo.
3. **You see the risk first.** Before linking, `/map-set` shows a report of downloads, hooks, package installs and credential handling found in the skill's files, and waits for your OK.
4. **Local only.** The index, usage counts and logs live in `~/.mapskills`. No telemetry, no prompt text stored. Turn usage counting off with `python3 skills/map/scripts/mapskills.py config usage off`.

## How `/map-rcm` chooses

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
| Code | systematic-debugging, karpathy-guidelines, ponytail, reverse-engineer-anything | test-driven-development, writing-plans, ponytail-review, python-patterns, python-testing, docker-patterns, ghidra-mcp (MCP, needs Ghidra) |
| Security | security-audit, software-security | differential-review, supply-chain-risk-auditor, fp-check |
| AI·ML | hf-cli | huggingface-local-models, huggingface-llm-trainer, trl-training, pytorch-patterns, mcp-builder |
| Docs | graphify | agent-reach, claude-seo (plugin) |
| Tokens | caveman | |

Bundled: `ui-effects-glossary` — turns "make it react to the mouse" into effect names (custom cursor, 3D tilt, magnetic button, scroll reveal…) and how to build them.

All listed skills belong to their authors under their own licenses (see `license` in the registry).

## Contributing

See [AGENTS.md](AGENTS.md) (written for AI agents, works for humans): invariants, how to add a registry skill or an agent, and the checks to run:

```bash
python3 -m unittest discover -s tests && ./scripts/privacy-check.sh
```

---

## 한국어 요약

Claude Code와 Codex에서 같이 쓰는 스킬 지도·추천·설치 도구입니다.

- `/map`: 분야를 고르면 `/스킬 - 설명 / 예시 프롬프트`로 보여줍니다.
- `/map-rcm <작업>`: 작업에 맞는 스킬 1~3개를 쓰는 순서대로 추천하고, 다듬은 프롬프트를 클립보드에 복사합니다.
- `/map-set`: 분야별 대표 스킬(1~2개)을 설치합니다. 기존 스킬과 규칙 파일은 건드리지 않습니다.
- `/map-check`: 겹치는 스킬, 안 쓰는 스킬, 오래된 스킬, 더 나은 대안을 찾아 정리안을 줍니다. 승인 전에는 아무것도 바꾸지 않습니다.
- `/map-rule`: CLAUDE.md·AGENTS.md를 영문화·압축·동기화한 제안본을 따로 만들어 보여줍니다. 승인하면 백업 후 적용합니다.
- 설치 위치: 처음 `/map-set` 때 실제 파일을 둘 곳(기본 `~/.mapskills/vendor` 또는 직접 정한 폴더)과 연결할 에이전트를 묻습니다. 이 컴퓨터에서 감지된 에이전트(Claude Code, Codex, Cursor, Gemini CLI 등 약 65종 중)를 추천하고 여러 개를 고를 수 있으며, 목록에 없는 도구는 `이름=경로`로 추가합니다. 각 에이전트는 자기 스킬 폴더만 읽으므로 그곳에 링크가 생깁니다.

처음 설정 순서 (기존 스킬·규칙이 있을 때): 설치 → `/map`으로 현황 보기 → `/map-check`로 기존 스킬 점검 → `/map-set`으로 설치·업데이트 → `/map-check`로 합쳐진 상태 정리 → 새 세션 열기(필요하면 `/map-rule route`) → 평소엔 `/map-rcm <작업>`. 기존 스킬과 CLAUDE.md·AGENTS.md는 어느 단계에서도 수정하지 않습니다.

모든 데이터는 `~/.mapskills`에만 저장되고 외부로 보내지 않습니다.
