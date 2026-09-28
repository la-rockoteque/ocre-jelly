"""ocre-jelly configuration: one JSON shape, four layers, later wins.

  1. built-in DEFAULTS
  2. ~/.claude/ocre-jelly.json                  user (all your repos)
  3. <repo>/.claude/ocre-jelly.json             project, committed and shared with the team
  4. <repo>/.claude/ocre-jelly.local.json       personal override, kept out of git

Objects merge key by key; other values replace. Env vars beat every file:
OCRE_JELLY=off, OCRE_JELLY_SUBAGENT_MATCHER=<regex>.

Security posture: stdlib only, reads these four files, writes only the layer asked for.
"""
from __future__ import annotations

import copy
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

STATES = ("on", "off", "auto")
SEVERITIES = ("hard", "soft", "off")
LAYERS = ("user", "project", "local")
TAG_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")  # same rule as scan.TAG_RE
GLOSSARY_NAMES = ("docs/ubiquitous-language.md", "ubiquitous-language.md")

DEFAULTS = {
    "enabled": True,
    "locales": [],                 # e.g. ["en-CA", "fr-CA"]; empty = detect en/fr, no regional checks
    "glossary": None,              # path from the repo root; None = docs/ubiquitous-language.md or UBIQUITOUS-LANGUAGE.md
    "modules": {},                 # name -> on | off | auto
    "inject": "index",             # index (progressive disclosure) | full
    "subagents": {"inject": True, "matcher": None},
    "thresholds": {
        "sentence_words": 25,       # STE descriptive limit
        "instruction_words": 20,    # STE procedure limit (judged by the agent)
        "em_dash_per_paragraph": 3,
        "length_hits_per_file": 3,
    },
    "severity": {},                # category -> hard | soft | off, e.g. {"em-dash": "off"}
    "ignore_paths": [],            # globs from the repo root that docs mode and codedoc skip
    "protected_terms": [],         # extra words never flagged or respelled (brand names, code names)
    "commits": {                   # commitmsg.py and the commit-msg hook
        "enforce": "warn",          # off | warn (print, never block) | block (exit 1 on hard findings)
        "convention": "auto",       # auto (from the modules) | conventional | gitmoji | none
        "subject_max": 72,
        "subject_target": 50,
        "body_wrap": 72,
        "types": [],                # allowed Conventional Commits types; empty = the standard list
    },
    "feedback": {                  # feedback.py: pre-fills a form; the user submits it in the browser
        "enabled": True,
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSdnhduOn5MnbEBo6Dp44mNfiXvTkNj2PKmJE-5opP9_MwlYDg/viewform",
        "entry": "1018508464",      # the form's paragraph field (entry.<id>)
    },
    "telemetry": {                 # telemetry.py: opt-in, local-only counts; see its docstring
        "enabled": False,           # only the user and local layers can turn it on
        "debug": False,             # also keep error tracebacks in ~/.claude/ocre-jelly/debug.log
        "retention_days": 30,
    },
}

TYPES = {"enabled": bool, "locales": list, "glossary": (str, type(None)), "modules": dict, "inject": str,
         "subagents": dict, "thresholds": dict, "severity": dict, "ignore_paths": list, "protected_terms": list,
         "commits": dict, "feedback": dict, "telemetry": dict}


def claude_dir() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def project_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for d in (here, *here.parents):
        if (d / ".git").exists():
            return d
    return here


def layer_path(layer: str, root: Path) -> Path:
    return {"user": claude_dir() / "ocre-jelly.json",
            "project": root / ".claude" / "ocre-jelly.json",
            "local": root / ".claude" / "ocre-jelly.local.json"}[layer]


def validate(data: dict, where: str) -> list[str]:
    errors = []
    for key, value in data.items():
        if key == "$schema":
            continue
        if key not in TYPES:
            errors.append(f"{where}: unknown key {key!r}")
        elif not isinstance(value, TYPES[key]):
            errors.append(f"{where}: {key!r} has the wrong type")
    for name, state in (data.get("modules") or {}).items():
        if state not in STATES:
            errors.append(f"{where}: modules.{name} must be one of {STATES}")
    for cat, sev in (data.get("severity") or {}).items():
        if sev not in SEVERITIES:
            errors.append(f"{where}: severity.{cat} must be one of {SEVERITIES}")
    for key, value in (data.get("thresholds") or {}).items():
        if key not in DEFAULTS["thresholds"] or not isinstance(value, int) or value < 1:
            errors.append(f"{where}: thresholds.{key} must be a known key with a positive integer")
    for tag in data.get("locales") if isinstance(data.get("locales"), list) else []:
        if not isinstance(tag, str) or not TAG_RE.match(tag):
            errors.append(f"{where}: locales entry {tag!r} must look like en, en-CA or fr-FR")
    sub = data.get("subagents") or {}
    for key, value in sub.items():
        if key == "inject" and not isinstance(value, bool):
            errors.append(f"{where}: subagents.inject must be true or false")
        elif key == "matcher" and not isinstance(value, (str, type(None))):
            errors.append(f"{where}: subagents.matcher must be a string or null")
        elif key not in ("inject", "matcher"):
            errors.append(f"{where}: unknown key subagents.{key}")
    for key in ("ignore_paths", "protected_terms"):
        if any(not isinstance(x, str) for x in data.get(key) or []):
            errors.append(f"{where}: {key} must be a list of strings")
    commits = data.get("commits") or {}
    choices = {"enforce": ("off", "warn", "block"), "convention": ("auto", "conventional", "gitmoji", "none")}
    for key, value in commits.items():
        if key in choices:
            if value not in choices[key]:
                errors.append(f"{where}: commits.{key} must be one of {choices[key]}")
        elif key in ("subject_max", "subject_target", "body_wrap"):
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                errors.append(f"{where}: commits.{key} must be a positive integer")
        elif key == "types":
            if not isinstance(value, list) or any(not isinstance(t, str) for t in value):
                errors.append(f"{where}: commits.types must be a list of strings")
        else:
            errors.append(f"{where}: unknown key commits.{key}")
    for key, value in (data.get("feedback") or {}).items():
        if key == "enabled" and not isinstance(value, bool):
            errors.append(f"{where}: feedback.enabled must be true or false")
        elif key == "form_url" and not (isinstance(value, str) and value.startswith("https://")):
            errors.append(f"{where}: feedback.form_url must be an https URL")
        elif key == "entry" and not (isinstance(value, str) and value.isdigit()):
            errors.append(f"{where}: feedback.entry must be the numeric field id, as a string")
        elif key not in ("enabled", "form_url", "entry"):
            errors.append(f"{where}: unknown key feedback.{key}")
    for key, value in (data.get("telemetry") or {}).items():
        if key in ("enabled", "debug") and not isinstance(value, bool):
            errors.append(f"{where}: telemetry.{key} must be true or false")
        elif key == "retention_days" and (not isinstance(value, int) or isinstance(value, bool) or value < 1):
            errors.append(f"{where}: telemetry.retention_days must be a positive integer")
        elif key not in ("enabled", "debug", "retention_days"):
            errors.append(f"{where}: unknown key telemetry.{key}")
    if data.get("inject") not in (None, "index", "full"):
        errors.append(f"{where}: inject must be index or full")
    return errors


def read_layer(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as e:
        print(f"ocre-jelly: ignoring unreadable config {path}: {e}", file=sys.stderr)
        return {}
    if not isinstance(data, dict):
        print(f"ocre-jelly: ignoring {path}: top level must be an object", file=sys.stderr)
        return {}
    errors = validate(data, str(path))
    for err in errors:
        print(f"ocre-jelly: {err}", file=sys.stderr)
    return {} if errors else data


def merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def load(root: Path | None = None) -> dict:
    """Merged config, plus "_sources": which layer set each top-level key."""
    root = root or project_root()
    cfg, sources = copy.deepcopy(DEFAULTS), {}
    consent = {}  # telemetry on/off per layer
    for layer in LAYERS:
        data = read_layer(layer_path(layer, root))
        data.pop("$schema", None)
        cfg = merge(cfg, data)
        sources.update({k: layer for k in data})
        consent[layer] = (data.get("telemetry") or {})
    # Consent is personal: only the user or local layer can turn telemetry (or debug) on.
    # A committed project layer can only turn it off.
    for key in ("enabled", "debug"):
        personal = consent["local"].get(key, consent["user"].get(key, False))
        cfg["telemetry"][key] = bool(personal) and consent["project"].get(key) is not False
    if os.environ.get("OCRE_JELLY", "").lower() == "off":
        cfg["enabled"], sources["enabled"] = False, "env"
    if os.environ.get("OCRE_JELLY_SUBAGENT_MATCHER"):
        cfg["subagents"]["matcher"], sources["subagents"] = os.environ["OCRE_JELLY_SUBAGENT_MATCHER"], "env"
    cfg["_sources"] = sources
    cfg["_root"] = str(root)
    return cfg


def module_layers(root: Path) -> list[tuple[str, dict]]:
    """(layer, modules map) in precedence order, for `modules.py list` to explain a state."""
    return [(layer, read_layer(layer_path(layer, root)).get("modules", {})) for layer in LAYERS]


def update_layer(layer: str, root: Path, change) -> Path:
    """Apply change(dict) to one layer file and write it atomically."""
    path = layer_path(layer, root)
    data = read_layer(path)
    change(data)
    errors = validate(data, str(path))
    if errors:
        raise ValueError("; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    if layer == "local":
        exclude_locally(root, path)
    return path


def exclude_locally(root: Path, path: Path) -> None:
    """Keep the local layer out of git for this clone only, without touching .gitignore."""
    exclude = root / ".git" / "info" / "exclude"
    if not exclude.parent.is_dir():
        return
    entry = str(path.relative_to(root))
    lines = exclude.read_text(encoding="utf-8").splitlines() if exclude.exists() else []
    if entry not in lines:
        exclude.write_text("\n".join(lines + [entry]) + "\n", encoding="utf-8")


def find_glossary(root: Path, cfg: dict | None = None) -> Path | None:
    configured = (cfg or {}).get("glossary")
    if configured:  # a committed config must never make us read outside the repo
        path = (root / configured).resolve()
        return path if path.is_file() and root.resolve() in path.parents else None
    lower = {}
    for d in (root, root / "docs"):
        if d.is_dir():
            lower.update({str(p.relative_to(root)).lower(): p for p in d.iterdir() if p.is_file()})
    return next((lower[n] for n in GLOSSARY_NAMES if n in lower), None)


def ignored(path: str, root: Path, patterns: list[str]) -> bool:
    try:
        rel = Path(path).resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return any(fnmatch.fnmatch(rel.as_posix(), pat) for pat in patterns)  # fnmatch's * also crosses /


def apply_severity(hits: list[dict], overrides: dict[str, str]) -> list[dict]:
    """Re-rank or drop hits per the `severity` map."""
    out = []
    for h in hits:
        sev = overrides.get(h["category"], h["severity"])
        if sev != "off":
            out.append({**h, "severity": sev})
    return out


def selftest() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        os.environ["CLAUDE_CONFIG_DIR"] = str(tmp / "home")
        root = tmp / "repo"
        (root / ".git" / "info").mkdir(parents=True)
        cfg = load(root)
        assert cfg["enabled"] and cfg["thresholds"]["sentence_words"] == 25 and cfg["_sources"] == {}

        update_layer("user", root, lambda d: d.update({"locales": ["en-US"], "thresholds": {"sentence_words": 30}}))
        update_layer("project", root, lambda d: d.update({"locales": ["en-CA", "fr-CA"], "modules": {"vale": "on"}}))
        update_layer("local", root, lambda d: d.update({"severity": {"em-dash": "off"}}))
        cfg = load(root)
        assert cfg["locales"] == ["en-CA", "fr-CA"] and cfg["_sources"]["locales"] == "project"
        assert cfg["thresholds"] == {**DEFAULTS["thresholds"], "sentence_words": 30}, cfg["thresholds"]
        assert cfg["severity"] == {"em-dash": "off"} and cfg["modules"] == {"vale": "on"}
        assert ".claude/ocre-jelly.local.json" in (root / ".git/info/exclude").read_text()

        try:
            update_layer("project", root, lambda d: d.update({"modules": {"vale": "maybe"}}))
            raise AssertionError("bad state accepted")
        except ValueError:
            pass
        (root / ".claude" / "ocre-jelly.json").write_text('{"locales": "en-CA"}')
        assert load(root)["locales"] == ["en-US"], "invalid layer must be ignored, not half-applied"

        assert validate({"commits": {"enforce": "maybe"}}, "t") and not validate({"commits": {"enforce": "block", "types": ["feat"]}}, "t")
        assert load(root)["commits"]["enforce"] == "warn"
        update_layer("project", root, lambda d: d.update({"telemetry": {"enabled": True, "debug": True}}))
        assert load(root)["telemetry"]["enabled"] is False, "a committed config turned telemetry on"
        update_layer("local", root, lambda d: d.update({"telemetry": {"enabled": True}}))
        assert load(root)["telemetry"]["enabled"] is True and load(root)["telemetry"]["debug"] is False
        update_layer("project", root, lambda d: d.update({"telemetry": {"enabled": False}}))
        assert load(root)["telemetry"]["enabled"] is False, "the project layer must be able to turn it off"
        update_layer("project", root, lambda d: d.pop("telemetry"))
        update_layer("local", root, lambda d: d.pop("telemetry"))
        assert validate({"feedback": {"form_url": "http://evil"}}, "t") and validate({"feedback": {"entry": "x1"}}, "t")
        assert not validate({"feedback": {"enabled": False, "form_url": "https://f.example/form", "entry": "42"}}, "t")
        assert validate({"locales": ["../../etc/passwd"]}, "t") and validate({"subagents": {"inject": "yes", "x": 1}}, "t")
        (tmp / "secret.md").write_text("s")
        assert find_glossary(root, {"glossary": "../secret.md"}) is None, "glossary escaped the repo"

        os.environ["OCRE_JELLY"] = "off"
        assert load(root)["enabled"] is False
        del os.environ["OCRE_JELLY"]

        hits = [{"category": "em-dash", "severity": "soft"}, {"category": "anglicism", "severity": "soft"}]
        assert apply_severity(hits, {"em-dash": "off", "anglicism": "hard"}) == [{"category": "anglicism", "severity": "hard"}]
        (root / "gen").mkdir()
        assert ignored(str(root / "gen" / "a.g.cs"), root, ["gen/*"]) and not ignored(str(root / "a.cs"), root, ["gen/*"])
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--selftest"]):
        sys.exit("config.py only runs its self-test; use modules.py config ...")
    selftest()
