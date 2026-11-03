#!/usr/bin/env python3
"""mapskills helper. Standard library only.

All state lives in ~/.mapskills (override with MAPSKILLS_HOME). Nothing is sent
over the network except `git` calls to the public repos listed in registry.json.

Commands:
  scan [--json]                 index installed skills -> ~/.mapskills/index.json
  project [DIR]                 detect the stack of a project directory
  usage [--days N]              count local skill invocations (if usage is on)
  log --tags a,b --skills x,y   append an rcm record to usage.jsonl (if usage is on)
  check [ID...] [--upstream]    per registry entry: new | up-to-date | update | latest | user-owned | manual
                                (--upstream also reports the upstream HEAD)
  install ID [ID...] [--latest] [--dry-run]
                                fetch pinned (or upstream HEAD) commit, update if older, risk report, link
  unlink NAME [NAME...]         remove links that mapskills created
  status                        links mapskills created
  agents [--all]                known agents (detected / selected), from agents.json
  self-install [--remove]       link the bundled mapskills skills into the chosen agents
  config [KEY VALUE]            usage on|off · root <dir> · agents claude-code,codex,cursor,name=/path
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

HOME = Path.home()
MS_HOME = Path(os.environ.get("MAPSKILLS_HOME", HOME / ".mapskills"))
REGISTRY = Path(__file__).resolve().parent.parent / "registry.json"
AGENTS_FILE = Path(__file__).resolve().parent.parent / "agents.json"
BUNDLED = ["map", "map-rcm", "map-set", "map-check", "map-rule", "ui-effects-glossary"]
READ_ONLY_DIRS = {"codex-legacy": HOME / ".codex" / "skills"}
PLUGIN_GLOB = HOME / ".claude" / "plugins" / "cache"
RISK = [
    (r"curl[^\n|]*\|\s*(ba|z)?sh", "pipes a download into a shell"),
    (r"\b(curl|wget)\b", "downloads from the network"),
    (r"\b(pip|pip3|npm|pnpm|yarn|uv|brew|cargo)\s+(install|add|tool install)", "installs packages"),
    (r"\beval\b|\bexec\(", "dynamic code execution"),
    (r"rm\s+-rf", "recursive delete"),
    (r"\"hooks\"|PreToolUse|PostToolUse|SessionStart", "registers agent hooks"),
    (r"(api[_-]?key|token|secret)\s*[:=]", "handles credentials"),
]


def load_json(p, default):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return default


def save_json(p, data):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def known_agents():
    """id -> {label, skills Path, detect [Path], aliases} from agents.json."""
    doc = load_json(AGENTS_FILE, {"agents": [], "default": ["claude-code", "codex"]})
    out = {}
    for a in doc["agents"]:
        out[a["id"]] = {"label": a["label"], "skills": Path(a["skills"].replace("~", str(HOME), 1)),
                        "detect": [Path(x.replace("~", str(HOME), 1)) for x in a.get("detect", [])],
                        "aliases": a.get("aliases", [])}
    return out, doc.get("default", ["claude-code", "codex"])


def resolve_agent(name):
    agents, _ = known_agents()
    name = {"claude": "claude-code"}.get(name, name)
    if name in agents:
        return name
    for aid, a in agents.items():
        if name in a["aliases"]:
            return aid
    return None


def config():
    _, default = known_agents()
    return {"usage": True, "agents": default, **load_json(MS_HOME / "config.json", {})}


def vendor_dir():
    """Where fetched repos live: config 'root' (user-chosen folder) or ~/.mapskills/vendor."""
    root = config().get("root")
    return Path(root).expanduser() if root else MS_HOME / "vendor"


def targets():
    """Chosen agents -> skills folder. Entries can be ids/aliases or custom 'name=/path'. Same folder only once."""
    agents, _ = known_agents()
    out, seen = {}, set()
    for entry in config()["agents"]:
        if "=" in entry:
            name, path = entry.split("=", 1)
            folder = Path(path).expanduser()
        else:
            name = resolve_agent(entry)
            if not name:
                continue
            folder = agents[name]["skills"]
        if folder not in seen:
            seen.add(folder)
            out[name] = folder
    return out


def is_claude(agent):
    return agent == "claude-code"


def registry():
    return load_json(REGISTRY, {"skills": [], "categories": {}})


def frontmatter(skill_md):
    try:
        text = skill_md.read_text(errors="ignore")
    except OSError:
        return {}
    m = re.match(r"---\s*\n(.*?)\n---", text, re.S)
    out = {}
    if not m:
        return out
    lines = m.group(1).splitlines()
    i = 0
    while i < len(lines):
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", lines[i])
        if km:
            key, val = km.group(1), km.group(2).strip()
            if val in (">", ">-", "|", "|-", ""):
                buf = []
                while i + 1 < len(lines) and (lines[i + 1].startswith(" ") or not lines[i + 1].strip()):
                    i += 1
                    buf.append(lines[i].strip())
                val = " ".join(b for b in buf if b)
            out[key] = val.strip().strip('"').strip("'")
        i += 1
    return out


def classify(name, desc, reg_by_name, cats):
    if name in reg_by_name:
        return reg_by_name[name]["category"]
    text = f"{name} {desc}".lower()
    best, score = "other", 0
    for cat, info in cats.items():
        s = sum(1 for k in info.get("keywords", []) if re.search(r"\b" + re.escape(k), text))
        if s > score:
            best, score = cat, s
    return best


_GIT_CACHE = {}


def git_info(path):
    """Origin URL and last commit date of the repo containing path (cached per repo)."""
    top = next((d for d in (path, *path.parents) if (d / ".git").exists()), None)
    if top is None:
        return {}
    if top not in _GIT_CACHE:
        run = lambda *a: subprocess.run(["git", "-C", str(top), *a], capture_output=True, text=True, timeout=5).stdout.strip()
        try:
            url = re.sub(r"^https://[^@/]+@", "https://", run("remote", "get-url", "origin"))  # never keep credentials
            _GIT_CACHE[top] = {"repo": url, "updated": run("log", "-1", "--format=%cs")}
        except (OSError, subprocess.SubprocessError):
            _GIT_CACHE[top] = {}
    return _GIT_CACHE[top]


def iter_skill_dirs():
    agents, _ = known_agents()
    folders, seen = {}, set()
    for aid, a in agents.items():
        if a["skills"] not in seen:
            seen.add(a["skills"])
            folders[aid] = a["skills"]
    for name, d in {**folders, **targets(), **READ_ONLY_DIRS}.items():
        if d.is_dir():
            for p in sorted(d.iterdir()):
                if (p / "SKILL.md").is_file():
                    yield name, p
    if PLUGIN_GLOB.is_dir():
        for p in sorted(PLUGIN_GLOB.glob("*/*/*/skills/*")):
            if (p / "SKILL.md").is_file():
                yield "claude-plugin:" + p.parts[-5], p


def cmd_scan(args):
    reg = registry()
    by_name = {s["name"]: s for s in reg["skills"]}
    by_name.update({n: {"category": c} for n, c in reg.get("bundled", {}).items()})
    state = load_json(MS_HOME / "state.json", {"links": {}})
    skills = {}
    for agent, p in iter_skill_dirs():
        fm = frontmatter(p / "SKILL.md")
        name = p.name if not agent.startswith("claude-plugin") else f"{agent.split(':')[1]}:{fm.get('name', p.name)}"
        real = p.resolve()
        e = skills.setdefault(name, {
            "name": name, "description": fm.get("description", "")[:400],
            "hint": fm.get("argument-hint", ""), "agents": [],
            "category": classify(fm.get("name", p.name), fm.get("description", ""), by_name, reg["categories"]),
            "managed": name in state["links"], "path": str(real), **git_info(real)})
        base = agent.split(":")[0]
        if base not in e["agents"]:
            e["agents"].append(base)
    order = {c: i for i, c in enumerate(reg["categories"])}
    index = {"generated": time.strftime("%Y-%m-%d %H:%M"),
             "skills": sorted(skills.values(), key=lambda s: (order.get(s["category"], 99), s["name"]))}
    save_json(MS_HOME / "index.json", index)
    if "--json" in args:
        print(json.dumps(index, ensure_ascii=False, indent=1))
        return
    by_cat = {}
    for s in index["skills"]:
        by_cat.setdefault(s["category"], []).append(s)
    for cat, items in by_cat.items():
        label = reg["categories"].get(cat, {}).get("label", cat)
        print(f"## {label} ({len(items)})")
        for s in items:
            print(f"- {s['name']} [{','.join(s['agents'])}]{' *mapskills' if s['managed'] else ''}")
    print(f"\nindex: {MS_HOME / 'index.json'} ({len(index['skills'])} skills)")


def project_tags(d):
    tags = set()
    pkg = load_json(d / "package.json", None)
    if pkg:
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        tags.add("node")
        for dep, tag in [("react", "react"), ("next", "nextjs"), ("expo", "expo"), ("react-native", "react-native"),
                         ("three", "threejs"), ("@react-three/fiber", "r3f"), ("gsap", "gsap"), ("motion", "motion"),
                         ("framer-motion", "motion"), ("vue", "vue"), ("svelte", "svelte"), ("tailwindcss", "tailwind"),
                         ("@playwright/test", "playwright"), ("@capacitor/core", "capacitor"), ("hyperframes", "hyperframes")]:
            if dep in deps:
                tags.add(tag)
    py = " ".join((d / f).read_text(errors="ignore").lower() for f in ("pyproject.toml", "requirements.txt") if (d / f).is_file())
    if py:
        tags.add("python")
        for k in ("torch", "transformers", "fastapi", "django", "flask", "pytest", "xarray", "numpy"):
            if k in py:
                tags.add(k)
    for f, tag in [("Package.swift", "swift"), ("Dockerfile", "docker"), ("docker-compose.yml", "docker"),
                   ("Cargo.toml", "rust"), ("go.mod", "go"), ("pubspec.yaml", "flutter")]:
        if (d / f).exists():
            tags.add(tag)
    if any(d.glob("*.xcodeproj")):
        tags.add("swift")
    return tags


def cmd_project(args):
    d = Path(args[0]).expanduser() if args else Path.cwd()
    if not d.is_dir():
        sys.exit(json.dumps({"error": f"not a directory: {d.name}"}))
    skip = {"node_modules", "dist", "build", "vendor", "venv", ".venv"}
    dirs = [d] + [x for x in sorted(d.iterdir()) if x.is_dir() and not x.name.startswith(".") and x.name not in skip]
    for mono in ("apps", "packages"):
        if (d / mono).is_dir():
            dirs += [x for x in sorted((d / mono).iterdir()) if x.is_dir()]
    parts = {}
    for x in dirs[:40]:
        tags = project_tags(x)
        if tags:
            parts[str(x.relative_to(d)) or "."] = sorted(tags)
    print(json.dumps({"dir": d.name, "tags": sorted({t for v in parts.values() for t in v}), "parts": parts}))


def _skill_names(obj):
    """Yield skill names from one transcript record: a real use, not a mention."""
    if not isinstance(obj, dict):
        return
    msg = obj.get("message") if isinstance(obj.get("message"), dict) else {}
    for c in msg.get("content", []) if isinstance(msg.get("content"), list) else []:
        if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "Skill":
            name = (c.get("input") or {}).get("skill")
            if name:
                yield name  # Claude Code: Skill tool call
    payload = obj.get("payload") if isinstance(obj.get("payload"), dict) else {}
    if obj.get("type") == "response_item" and payload.get("type") in ("custom_tool_call", "function_call"):
        raw = json.dumps(payload.get("input") or payload.get("arguments") or "")
        yield from re.findall(r"skills/([\w.-]+)/SKILL\.md", raw)  # Codex: shell reads a SKILL.md


def cmd_usage(args):
    if not config()["usage"]:
        print(json.dumps({"usage": "off"}))
        return
    days = int(args[args.index("--days") + 1]) if "--days" in args else 30
    since = time.time() - days * 86400
    counts = {}
    for root in (HOME / ".claude" / "projects", HOME / ".codex" / "sessions"):
        if not root.is_dir():
            continue
        for f in root.rglob("*.jsonl"):
            try:
                if f.stat().st_mtime < since:
                    continue
                with open(f, errors="ignore") as fh:
                    for line in fh:
                        if '"Skill"' not in line and "SKILL.md" not in line:
                            continue
                        try:
                            obj = json.loads(line)
                        except ValueError:
                            continue
                        for name in set(_skill_names(obj)):
                            counts[name] = counts.get(name, 0) + 1
            except OSError:
                continue
    out = {"days": days, "counts": dict(sorted(counts.items(), key=lambda kv: -kv[1]))}
    save_json(MS_HOME / "usage-counts.json", out)  # skill names and counts only, no prompt text
    print(json.dumps(out, ensure_ascii=False))


def cmd_log(args):
    if not config()["usage"]:
        return
    get = lambda k: args[args.index(k) + 1].split(",") if k in args else []
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M"), "tags": get("--tags"), "skills": get("--skills")}
    MS_HOME.mkdir(parents=True, exist_ok=True)
    with open(MS_HOME / "usage.jsonl", "a") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def link(src, name, only=None):
    src = Path(src).expanduser().resolve()
    if not (src / "SKILL.md").is_file():
        sys.exit(f"no SKILL.md in {src}")
    state = load_json(MS_HOME / "state.json", {"links": {}})
    done = []
    for agent, d in targets().items():
        # registry variants: "claude" -> Claude Code only, "codex" -> every other agent
        if only == "claude" and not is_claude(agent) or only == "codex" and is_claude(agent):
            continue
        dst = d / name
        if dst.is_symlink() and dst.resolve() == src:
            done.append(str(dst))
            continue
        if dst.exists() or dst.is_symlink():
            print(f"SKIP {dst} already exists (not touched)")
            continue
        d.mkdir(parents=True, exist_ok=True)
        dst.symlink_to(src)
        done.append(str(dst))
    if done:
        state["links"].setdefault(name, {"src": str(src), "dst": []})
        state["links"][name]["dst"] = sorted(set(state["links"][name]["dst"]) | set(done))
        save_json(MS_HOME / "state.json", state)
        print(f"LINKED {name}: {', '.join(done)}")


def cmd_unlink(args):
    state = load_json(MS_HOME / "state.json", {"links": {}})
    for name in args:
        rec = state["links"].get(name)
        if not rec:
            print(f"SKIP {name}: not created by mapskills")
            continue
        for dst in rec["dst"]:
            p = Path(dst)
            if p.is_symlink() and str(p.resolve()) == rec["src"]:
                p.unlink()
                print(f"UNLINKED {p}")
        del state["links"][name]
    save_json(MS_HOME / "state.json", state)


def risk_report(root):
    hits = []
    for f in root.rglob("*"):
        if not f.is_file() or ".git" in f.parts or f.stat().st_size > 400_000:
            continue
        if f.suffix not in (".sh", ".py", ".js", ".mjs", ".cjs", ".ts", ".json", ".md", ".ps1", "") or f.name == "LICENSE":
            continue
        text = f.read_text(errors="ignore")
        for pat, why in RISK:
            if re.search(pat, text, re.I):
                hits.append(f"{f.relative_to(root)}: {why}")
    bins = [str(f.relative_to(root)) for f in root.rglob("*") if f.is_file() and os.access(f, os.X_OK) and ".git" not in f.parts]
    return hits, bins


def _git(repo_dir, *a):
    return subprocess.run(["git", "-C", str(repo_dir), *a], check=True, capture_output=True, text=True).stdout.strip()


def _upstream_head(repo):
    try:
        out = subprocess.run(["git", "ls-remote", f"https://github.com/{repo}.git", "HEAD"],
                             capture_output=True, text=True, timeout=20).stdout.split()
    except (OSError, subprocess.SubprocessError):
        return ""
    return out[0] if out else ""


def _checkout(repo_dir, commit):
    """Shallow-fetch one commit into repo_dir (created if needed) and check it out."""
    if not (repo_dir / ".git").exists():
        repo_dir.mkdir(parents=True, exist_ok=True)
        _git(repo_dir, "init", "-q")
        _git(repo_dir, "remote", "add", "origin", f"https://github.com/{repo_dir.name.replace('__', '/', 1)}.git")
    _git(repo_dir, "fetch", "-q", "--depth", "1", "origin", commit)
    _git(repo_dir, "checkout", "-q", "FETCH_HEAD")


def _status(s, state):
    """One registry entry -> new | managed (up-to-date / update) | user-owned (same name, not ours)."""
    if s.get("type", "git") != "git":
        return {"id": s["id"], "status": "manual", "how": s.get("install", "")}
    repo_dir = vendor_dir() / s["repo"].replace("/", "__")
    ours = s["name"] in state["links"]
    present = [a for a, d in targets().items() if (d / s["name"]).exists()]
    if ours and repo_dir.is_dir():
        cur = _git(repo_dir, "rev-parse", "HEAD")
        if state["links"][s["name"]].get("latest"):
            status = "latest"  # user chose upstream HEAD; do not pull them back to the pin
        else:
            status = "up-to-date" if cur.startswith(s["commit"][:12]) else "update"
        return {"id": s["id"], "status": status, "current": cur[:12], "pinned": s["commit"][:12], "agents": present}
    if present:
        return {"id": s["id"], "status": "user-owned", "agents": present,
                "note": "same name already installed by you; mapskills will not touch it"}
    return {"id": s["id"], "status": "new"}


def cmd_check(args):
    reg = {s["id"]: s for s in registry()["skills"]}
    state = load_json(MS_HOME / "state.json", {"links": {}})
    ids = [a for a in args if not a.startswith("--")] or list(reg)
    rows = []
    for i in ids:
        row = _status(reg[i], state) if i in reg else {"id": i, "status": "unknown"}
        if "--upstream" in args and reg.get(i, {}).get("type", "git") == "git":
            head = _upstream_head(reg[i]["repo"])
            row["upstream"] = head[:12] or "unreachable"
            row["newer_upstream"] = bool(head) and not head.startswith(reg[i]["commit"][:12])
        rows.append(row)
    print(json.dumps(rows, ensure_ascii=False))


def cmd_install(args):
    reg = {s["id"]: s for s in registry()["skills"]}
    latest = "--latest" in args
    for sid in [a for a in args if not a.startswith("--")]:
        s = reg.get(sid)
        if not s:
            print(f"UNKNOWN {sid}")
            continue
        if s.get("type", "git") != "git":
            print(f"MANUAL {sid}: {s.get('install', 'see registry notes')}")
            continue
        repo_dir = vendor_dir() / s["repo"].replace("/", "__")
        target = _upstream_head(s["repo"]) if latest else s["commit"]
        if not target:
            print(f"ERROR {sid}: could not reach upstream")
            continue
        cur = subprocess.run(["git", "-C", str(repo_dir), "rev-parse", "-q", "--verify", "HEAD"],
                             capture_output=True, text=True).stdout.strip() if repo_dir.is_dir() else ""
        dry = "--dry-run" in args
        if cur.startswith(target[:12]):
            print(f"UP-TO-DATE {sid} @{target[:12]}")
        elif not dry or not cur:  # a dry run on a fresh repo still needs the files to report risk
            _checkout(repo_dir, target)
            if not dry:
                print(f"{'UPDATED' if cur else 'FETCHED'} {sid} {cur[:12] or '-'} -> {target[:12]}")
        paths = s.get("paths") or {"both": s["path"]}
        for agent, rel in paths.items():
            src = repo_dir / rel
            hits, bins = risk_report(src)
            print(f"== {sid} ({s['repo']}@{target[:12]}, {s.get('license', '?')}) -> {rel}")
            for h in sorted(set(hits))[:25]:
                print(f"  RISK {h}")
            if bins:
                print(f"  EXECUTABLES {', '.join(bins[:10])}")
            if not dry:
                link(src, s["name"], None if agent == "both" else agent)
        if not dry:
            state = load_json(MS_HOME / "state.json", {"links": {}})
            if s["name"] in state["links"]:
                state["links"][s["name"]].update({"commit": target[:12], "latest": latest})
                save_json(MS_HOME / "state.json", state)


def cmd_status(args):
    state = load_json(MS_HOME / "state.json", {"links": {}})
    for name, rec in sorted(state["links"].items()):
        print(f"{name} -> {rec['src']} ({len(rec['dst'])} links)")
    if not state["links"]:
        print("no links created by mapskills")


def cmd_agents(args):
    """List known agents: detected on this machine, selected in config."""
    agents, _ = known_agents()
    chosen = set(targets().values())
    rows = []
    for aid, a in agents.items():
        detected = any(d.exists() for d in a["detect"]) or a["skills"].is_dir()
        if detected or a["skills"] in chosen or "--all" in args:
            rows.append({"id": aid, "label": a["label"], "skills": str(a["skills"]).replace(str(HOME), "~", 1),
                         "detected": detected, "selected": a["skills"] in chosen})
    print(json.dumps(rows, ensure_ascii=False, indent=1))


def cmd_self_install(args):
    """Link (or with --remove, unlink) the bundled mapskills skills into the chosen agents' folders."""
    root = Path(__file__).resolve().parent.parent.parent
    if "--remove" in args:
        cmd_unlink([n for n in BUNDLED if n in load_json(MS_HOME / "state.json", {"links": {}})["links"]])
        return
    for name in BUNDLED:
        link(root / name, name)
    print("Agents: " + ", ".join(f"{k} ({str(v).replace(str(HOME), '~', 1)})" for k, v in targets().items()))


def cmd_config(args):
    """config usage on|off · config root <dir> · config agents claude-code,codex,name=/path"""
    cfg = config()
    if len(args) == 2:
        key, val = args
        if key == "usage":
            cfg[key] = val.lower() in ("on", "true", "1", "yes")
        elif key == "root":
            cfg[key] = str(Path(val).expanduser())
        elif key == "agents":
            picked = []
            for a in val.split(","):
                a = a.strip()
                if "=" in a or resolve_agent(a):
                    picked.append(a if "=" in a else resolve_agent(a))
                else:
                    print(f"unknown agent {a} (see: agents --all, or use name=/path)", file=sys.stderr)
            cfg[key] = list(dict.fromkeys(picked)) or known_agents()[1]
        else:
            sys.exit(f"unknown key {key}")
        save_json(MS_HOME / "config.json", cfg)
    print(json.dumps({**cfg, "home": str(MS_HOME), "vendor_dir": str(vendor_dir()), "first_run": not (MS_HOME / "config.json").exists()}))


COMMANDS = {"scan": cmd_scan, "project": cmd_project, "usage": cmd_usage, "log": cmd_log, "check": cmd_check,
            "install": cmd_install, "unlink": cmd_unlink, "status": cmd_status, "agents": cmd_agents,
            "self-install": cmd_self_install, "config": cmd_config}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.exit(__doc__)
    COMMANDS[sys.argv[1]](sys.argv[2:])
