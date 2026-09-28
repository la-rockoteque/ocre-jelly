#!/usr/bin/env python3
"""Back end of the /ocre-jelly setup wizard.

  wizard.py detect             facts about this repo, as JSON: languages, locales in resource
                               paths, glossary, commit tooling, hook managers, doc formats,
                               active modules and the current config. The wizard proposes
                               answers from these instead of asking everything.
  wizard.py apply PLAN.json    write the whole plan in one step, then run its exports.
  wizard.py apply - < PLAN     (plan on stdin)
  wizard.py --selftest

A plan is:
  {
    "user":    { ...config keys... },     # ~/.claude/ocre-jelly.json
    "project": { ...config keys... },     # <repo>/.claude/ocre-jelly.json (commit it)
    "local":   { ...config keys... },     # <repo>/.claude/ocre-jelly.local.json (kept out of git)
    "exports": ["agents-md", "git-hook", ...],
    "dry_run": false
  }
Each layer is validated as a whole before anything is written; objects merge key by key
into what the layer already has. `updates.mode` in the user or local layer also sets
Claude Code's native marketplace auto-update (see update.py).

Security posture: stdlib only, no network. detect walks the repo (bounded, skips
dependency and build folders) and reads only names, never file contents, except the
few config files it names in its output.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import config  # noqa: E402

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", "bin", "obj", "target", ".venv", "venv", "__pycache__",
             ".next", ".nuxt", "coverage", ".gradle", ".idea", ".vs", "Pods", ".terraform", ".omc"}
MAX_FILES = 20000  # ponytail: a bounded walk; a huge monorepo gets a partial but useful picture
LANG_CODES = set("en fr es de it pt nl ja zh ko ru pl sv da nb nn no fi cs sk hu ro bg el tr he ar hi th vi id ms uk ca eu gl".split())
LOCALE_DIR = re.compile(r"^([a-z]{2})(?:[-_]([A-Za-z]{2}))?$")
LOCALE_FILE = re.compile(r"(?:^|[._-])([a-z]{2})(?:[-_]([A-Z]{2}))?\.(?:json|resx|po|properties|strings|xlf|xliff|arb|ya?ml)$")
LANG_BY_EXT = {".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript",
               ".cs": "C#", ".java": "Java", ".kt": "Kotlin", ".py": "Python", ".go": "Go", ".rs": "Rust",
               ".swift": "Swift", ".php": "PHP", ".rb": "Ruby", ".c": "C", ".h": "C", ".cpp": "C++", ".hpp": "C++",
               ".md": "Markdown", ".mdx": "Markdown", ".rst": "reStructuredText", ".feature": "Gherkin"}
COMMIT_TOOLS = ["commitlint.config.js", "commitlint.config.cjs", "commitlint.config.mjs", "commitlint.config.ts",
                ".commitlintrc", ".commitlintrc.json", ".commitlintrc.yml", ".czrc", ".cz.toml", ".cz.json",
                ".releaserc", ".releaserc.json", "release-please-config.json", ".versionrc", ".gitmojirc.json"]


def walk(root: Path):
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".cache")]
        for name in filenames:
            count += 1
            if count > MAX_FILES:
                return
            yield Path(dirpath), name


def detect(root: Path) -> dict:
    root = root.resolve()
    exts, locales, i18n_dirs = collections.Counter(), collections.Counter(), set()
    truncated = False
    n = 0
    for dirpath, name in walk(root):
        n += 1
        ext = Path(name).suffix.lower()
        if ext in LANG_BY_EXT:
            exts[LANG_BY_EXT[ext]] += 1
        m = LOCALE_DIR.match(dirpath.name)
        if m and m.group(1) in LANG_CODES and ext in (".json", ".po", ".yml", ".yaml", ".properties", ".arb", ".strings", ".xlf"):
            tag = m.group(1) + (f"-{m.group(2).upper()}" if m.group(2) else "")
            locales[tag] += 1
            i18n_dirs.add(str(dirpath.parent.relative_to(root)))
        m = LOCALE_FILE.search(name)
        if m and m.group(1) in LANG_CODES:
            locales[m.group(1) + (f"-{m.group(2)}" if m.group(2) else "")] += 1
    truncated = n >= MAX_FILES

    git = root / ".git"
    git_config = (git / "config").read_text(encoding="utf-8", errors="replace") if (git / "config").is_file() else ""
    glossary = config.find_glossary(root)
    import modules as M
    mods = M.all_modules()
    active = M.resolve(mods, root, M.installed_plugins())
    cfg = config.load(root)
    sources = cfg.pop("_sources")
    cfg.pop("_root")
    layers = {layer: config.layer_path(layer, root).exists() for layer in config.LAYERS}
    import update
    return {
        "root": root.name,
        "files_scanned": n, "truncated": truncated,
        "languages": dict(exts.most_common(8)),
        "locales_found": dict(locales.most_common(8)),
        "i18n_folders": sorted(i18n_dirs)[:5],
        "glossary": str(glossary.relative_to(root)) if glossary else None,
        "commit_tooling": [f for f in COMMIT_TOOLS if (root / f).exists()],
        "hook_manager": ("husky" if (root / ".husky").is_dir() else "lefthook" if any((root / f).exists() for f in ("lefthook.yml", ".lefthook.yml"))
                         else "pre-commit" if (root / ".pre-commit-config.yaml").exists()
                         else "core.hooksPath" if re.search(r"(?im)^\s*hookspath\s*=", git_config) else "git" if git.is_dir() else None),
        "git_worktree": git.is_file(),
        "pr_template": any((root / p).exists() for p in (".github/PULL_REQUEST_TEMPLATE.md", ".github/pull_request_template.md",
                                                          ".gitlab/merge_request_templates", "PULL_REQUEST_TEMPLATE.md")),
        "changelog": any((root / p).exists() for p in ("CHANGELOG.md", "CHANGELOG")),
        "adr_folder": next((p for p in ("docs/adr", "docs/adrs", "docs/decisions", "doc/adr", "adr") if (root / p).is_dir()), None),
        "other_agents": [a for a, p in (("cursor", ".cursor"), ("windsurf", ".windsurf"), ("cline", ".clinerules"),
                                         ("kiro", ".kiro"), ("agents-md", "AGENTS.md")) if (root / p).exists()],
        "vale": (root / ".vale.ini").exists(), "cspell": any((root / p).exists() for p in ("cspell.json", ".cspell.json", "cspell.config.yaml")),
        "modules_active": sorted(n for n, (on, _) in active.items() if on),
        "modules_available": {n: {"kind": m["kind"], "default": m["default"], "description": m.get("description", "")} for n, m in mods.items()},
        "config": cfg, "config_set_by": sources, "config_files": layers,
        "updates_installed": update.installed().get("gitCommitSha", "")[:7] or None,
        "marketplace_source": (update.marketplace().get("source") or {}).get("source"),
    }


def apply(plan: dict, root: Path) -> list[str]:
    if not isinstance(plan, dict):
        raise ValueError("the plan must be a JSON object")
    unknown = set(plan) - {"user", "project", "local", "exports", "dry_run"}
    if unknown:
        raise ValueError(f"unknown plan keys: {', '.join(sorted(unknown))}")
    dry = bool(plan.get("dry_run"))
    out = []
    # validate every layer first, so a bad answer writes nothing
    for layer in config.LAYERS:
        changes = plan.get(layer) or {}
        if not isinstance(changes, dict):
            raise ValueError(f"plan.{layer} must be an object")
        merged = config.merge(config.read_layer(config.layer_path(layer, root)), changes)
        errors = config.validate(merged, layer)
        if errors:
            raise ValueError("; ".join(errors))
    for layer in config.LAYERS:
        changes = plan.get(layer) or {}
        if not changes:
            continue
        if dry:
            out.append(f"would write {layer}: {json.dumps(changes, ensure_ascii=False)}")
            continue
        path = config.update_layer(layer, root, lambda d, c=changes: d.update(config.merge(d, c)))
        out.append(f"wrote {layer}: {path}")
        mode = (changes.get("updates") or {}).get("mode")
        if mode and layer in ("user", "local"):
            import update
            try:
                update.set_native_auto_update(mode == "silent")
                out.append(f"Claude Code auto-update for ocre-jelly: {'on' if mode == 'silent' else 'off'}")
            except RuntimeError as e:
                out.append(f"native auto-update not changed: {e}")
    exports = plan.get("exports") or []
    if exports:
        if dry:
            out.append(f"would export: {', '.join(exports)}")
        else:
            import io
            from contextlib import redirect_stdout
            import modules as M
            buf = io.StringIO()
            cwd = Path.cwd()
            try:
                os.chdir(root)
                with redirect_stdout(buf):
                    M.run_export(list(exports), None, False, False)
            except SystemExit as e:
                buf.write(f"export stopped: {e}\n")
            finally:
                os.chdir(cwd)
            out += buf.getvalue().strip().splitlines()
    return out


def selftest() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        os.environ["CLAUDE_CONFIG_DIR"] = str(tmp / "home")
        root = tmp / "repo"
        for p in ("web/src/i18n/locales/fr-CA/nav.json", "web/src/i18n/locales/en-CA/nav.json", "web/tsconfig.json",
                  "api/Api.csproj", "api/Users.cs", "api/Strings.fr.resx", "docs/adr/0001-x.md", "node_modules/x/y.js",
                  "commitlint.config.js", "CHANGELOG.md", ".husky/commit-msg"):
            (root / p).parent.mkdir(parents=True, exist_ok=True)
            (root / p).write_text("{}")
        (root / ".git").mkdir()
        facts = detect(root)
        assert facts["locales_found"].get("fr-CA") == 1 and facts["locales_found"].get("en-CA") == 1, facts["locales_found"]
        assert facts["locales_found"].get("fr") == 1
        assert facts["languages"].get("JavaScript") == 1, "node_modules was walked"  # only commitlint.config.js
        (root / "db").mkdir()
        (root / "db" / "seed.json").write_text("{}")
        assert "db" not in detect(root)["locales_found"], "a db folder counted as a locale"
        assert facts["commit_tooling"] == ["commitlint.config.js"] and facts["hook_manager"] == "husky"
        assert facts["adr_folder"] == "docs/adr" and facts["changelog"] and "adr" in facts["modules_active"]
        assert "web/src/i18n/locales" in facts["i18n_folders"]

        plan = {"project": {"locales": ["en-CA", "fr-CA"], "modules": {"conventional-commits": "on"}},
                "local": {"severity": {"em-dash": "off"}}, "user": {"telemetry": {"enabled": True}}}
        out = apply(plan, root)
        assert any(o.startswith("wrote project") for o in out), out
        cfg = config.load(root)
        assert cfg["locales"] == ["en-CA", "fr-CA"] and cfg["modules"]["conventional-commits"] == "on"
        assert cfg["severity"] == {"em-dash": "off"} and cfg["telemetry"]["enabled"] is True

        before = config.layer_path("project", root).read_text()
        try:
            apply({"project": {"locales": ["en-CA"]}, "local": {"commits": {"enforce": "maybe"}}}, root)
            raise AssertionError("bad plan accepted")
        except ValueError:
            pass
        assert config.layer_path("project", root).read_text() == before, "a failed plan wrote a layer"
        assert any("would write" in o for o in apply({"project": {"inject": "full"}, "dry_run": True}, root))
        assert config.load(root)["inject"] == "index"
        try:
            apply({"projects": {}}, root)
            raise AssertionError("unknown plan key accepted")
        except ValueError:
            pass
    print("selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", nargs="?", choices=("detect", "apply"))
    ap.add_argument("plan", nargs="?", help="plan file for apply, or - for stdin")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    root = config.project_root()
    if args.action == "detect":
        return print(json.dumps(detect(root), indent=2, ensure_ascii=False))
    if args.action == "apply":
        if not args.plan:
            sys.exit("usage: wizard.py apply PLAN.json (or - for stdin)")
        text = sys.stdin.read() if args.plan == "-" else Path(args.plan).read_text(encoding="utf-8")
        try:
            print("\n".join(apply(json.loads(text), root)))
        except (ValueError, json.JSONDecodeError) as e:
            sys.exit(f"nothing written: {e}")
        return
    ap.print_help()


if __name__ == "__main__":
    main()
