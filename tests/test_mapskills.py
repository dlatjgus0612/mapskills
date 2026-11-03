"""Offline tests for mapskills. Every test runs in a throwaway HOME.

    python3 -m unittest discover -s tests          # offline
    MAPSKILLS_NET=1 python3 -m unittest discover -s tests   # + fetch from GitHub
"""
import json, os, re, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MS = REPO / "skills" / "map" / "scripts" / "mapskills.py"
REGISTRY = json.loads((REPO / "skills" / "map" / "registry.json").read_text())
AGENTS = json.loads((REPO / "skills" / "map" / "agents.json").read_text())


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.env = {**os.environ, "HOME": str(self.home)}
        self.env.pop("MAPSKILLS_HOME", None)

    def tearDown(self):
        self.tmp.cleanup()

    def ms(self, *args, ok=True):
        r = subprocess.run([sys.executable, str(MS), *args], env=self.env, capture_output=True, text=True)
        if ok:
            self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def skill(self, folder, name, desc="x"):
        d = self.home / folder / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {desc}\n---\nbody\n")
        return d


class Data(unittest.TestCase):
    def test_registry_schema(self):
        ids = [s["id"] for s in REGISTRY["skills"]]
        self.assertEqual(len(ids), len(set(ids)), "duplicate ids")
        for s in REGISTRY["skills"]:
            self.assertIn(s["category"], REGISTRY["categories"], s["id"])
            self.assertTrue(s.get("ko"), f"{s['id']} needs a short description")
            if "group" in s:
                self.assertIn(s["group"], REGISTRY["groups"], s["id"])
            if s.get("type", "git") == "git":
                self.assertRegex(s["commit"], r"^[0-9a-f]{40}$", s["id"])
                self.assertTrue(s.get("path") or s.get("paths"), s["id"])
                self.assertRegex(s["repo"], r"^[\w.-]+/[\w.-]+$", s["id"])
            else:
                self.assertTrue(s.get("install"), f"{s['id']} needs install steps")

    def test_every_category_but_other_has_a_core_skill(self):
        for cat in REGISTRY["categories"]:
            if cat != "other":
                self.assertTrue(any(s.get("core") and s["category"] == cat for s in REGISTRY["skills"]), cat)

    def test_readme_lists_core_skills(self):
        readme = (REPO / "README.md").read_text()
        for s in REGISTRY["skills"]:
            if s.get("core"):
                self.assertIn(s["id"], readme)

    def test_agents_schema(self):
        ids = [a["id"] for a in AGENTS["agents"]] + [x for a in AGENTS["agents"] for x in a.get("aliases", [])]
        self.assertEqual(len(ids), len(set(ids)), "duplicate agent ids/aliases")
        for a in AGENTS["agents"]:
            self.assertTrue(a["skills"].startswith("~/") and a["skills"].endswith("skills"), a["id"])
        for d in AGENTS["default"]:
            self.assertIn(d, ids)

    def test_bundled_skills_have_frontmatter(self):
        for d in (REPO / "skills").iterdir():
            text = (d / "SKILL.md").read_text()
            self.assertRegex(text, rf"^---\nname: {re.escape(d.name)}\ndescription: ", d.name)


class Install(Base):
    def test_self_install_skips_existing_and_removes_cleanly(self):
        mine = self.skill(".claude/skills", "map", "my own map")
        out = self.ms("self-install")
        self.assertIn("SKIP", out)
        self.assertEqual((mine / "SKILL.md").read_text().count("my own map"), 1)
        for folder in (".claude/skills", ".agents/skills"):
            self.assertTrue((self.home / folder / "map-rcm").is_symlink(), folder)
        self.assertTrue((self.home / ".agents/skills/map").is_symlink())
        self.ms("self-install", "--remove")
        links = [p for p in self.home.rglob("*") if p.is_symlink()]
        self.assertEqual(links, [])
        self.assertTrue((mine / "SKILL.md").exists())

    def test_agents_aliases_dedupe_and_custom_path(self):
        cfg = json.loads(self.ms("config", "agents", f"claude,codex,zed,cursor,mine={self.home}/mine/skills"))
        self.assertEqual(cfg["agents"][:3], ["claude-code", "codex", "cursor"])  # zed shares codex's folder
        self.ms("self-install")
        for folder in (".claude/skills", ".agents/skills", ".cursor/skills", "mine/skills"):
            self.assertTrue((self.home / folder / "map").is_symlink(), folder)

    def test_unlink_refuses_user_skills(self):
        self.skill(".claude/skills", "caveman")
        out = self.ms("unlink", "caveman")
        self.assertIn("not created by mapskills", out)
        self.assertTrue((self.home / ".claude/skills/caveman/SKILL.md").exists())

    def test_check_reports_user_owned_and_new(self):
        self.skill(".claude/skills", "ponytail")
        rows = {r["id"]: r["status"] for r in json.loads(self.ms("check", "ponytail", "caveman", "graphify"))}
        self.assertEqual(rows, {"ponytail": "user-owned", "caveman": "new", "graphify": "manual"})


class Scan(Base):
    def test_scan_indexes_and_classifies(self):
        self.skill(".claude/skills", "landing-helper", "Build a React landing page with animation")
        self.skill(".agents/skills", "shared", "Write pytest tests and debug failures")
        self.skill(".agents/skills", "회의록", "회의 노트를 문서로 정리")
        idx = json.loads(self.ms("scan", "--json"))
        cats = {s["name"]: s["category"] for s in idx["skills"]}
        self.assertEqual(cats, {"landing-helper": "web", "shared": "code", "회의록": "docs"})

    def test_frontmatter_folded_description(self):
        d = self.home / ".claude/skills/folded"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("---\nname: folded\ndescription: >\n  line one\n  line two\n---\n")
        idx = json.loads(self.ms("scan", "--json"))
        self.assertEqual(idx["skills"][0]["description"], "line one line two")

    def test_project_detects_monorepo_parts(self):
        proj = self.home / "proj"
        (proj / "web").mkdir(parents=True)
        (proj / "web/package.json").write_text(json.dumps({"dependencies": {"react": "18", "gsap": "3"}}))
        (proj / "api").mkdir()
        (proj / "api/requirements.txt").write_text("fastapi\ntorch\n")
        out = json.loads(self.ms("project", str(proj)))
        self.assertEqual(out["parts"], {"api": ["fastapi", "python", "torch"], "web": ["gsap", "node", "react"]})


class Usage(Base):
    def test_counts_real_uses_not_mentions(self):
        claude = self.home / ".claude/projects/p"
        claude.mkdir(parents=True)
        (claude / "s.jsonl").write_text("\n".join(json.dumps(x) for x in [
            {"message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": "impeccable"}}]}},
            {"message": {"content": [{"type": "text", "text": "skills/impeccable/SKILL.md is listed here"}]}},
        ]) + "\n")
        codex = self.home / ".codex/sessions/2026"
        codex.mkdir(parents=True)
        (codex / "r.jsonl").write_text("\n".join(json.dumps(x) for x in [
            {"type": "response_item", "payload": {"type": "custom_tool_call", "input": "cat ~/.agents/skills/example-skill/SKILL.md"}},
            {"type": "session_meta", "payload": {"text": "skills/impeccable/SKILL.md skills/example-skill/SKILL.md"}},
        ]) + "\n")
        counts = json.loads(self.ms("usage"))["counts"]
        self.assertEqual(counts, {"impeccable": 1, "example-skill": 1})

    def test_usage_off_writes_nothing(self):
        self.ms("config", "usage", "off")
        self.ms("log", "--tags", "web", "--skills", "x")
        self.assertFalse((self.home / ".mapskills/usage.jsonl").exists())
        self.assertEqual(json.loads(self.ms("usage")), {"usage": "off"})

    def test_log_stores_no_prompt_text(self):
        self.ms("log", "--tags", "web,improve", "--skills", "impeccable")
        rec = json.loads((self.home / ".mapskills/usage.jsonl").read_text())
        self.assertEqual(set(rec), {"ts", "tags", "skills"})


@unittest.skipUnless(os.environ.get("MAPSKILLS_NET"), "set MAPSKILLS_NET=1 to fetch from GitHub")
class Network(Base):
    def test_install_pinned_then_up_to_date(self):
        self.assertIn("FETCHED", self.ms("install", "ponytail"))
        self.assertTrue((self.home / ".claude/skills/ponytail/SKILL.md").exists())
        self.assertEqual(json.loads(self.ms("check", "ponytail"))[0]["status"], "up-to-date")
        self.assertIn("UP-TO-DATE", self.ms("install", "ponytail"))


if __name__ == "__main__":
    unittest.main()
