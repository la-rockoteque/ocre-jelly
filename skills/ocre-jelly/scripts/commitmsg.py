#!/usr/bin/env python3
"""Check a commit message: its shape (subject, blank line, wrap, convention) and the prose of its body.

Reads the message the way git leaves it: `#` comment lines and everything
below the scissors line are ignored. Merge, revert and fixup!/squash!/amend!
messages skip the shape checks, since git or a tool wrote their subject.

Checks:
  commit-empty            no message                                     hard
  commit-subject-length   over commits.subject_max (72)                   hard
                          over commits.subject_target (50)                soft
  commit-subject-period   subject ends with a period                      soft
  commit-blank-line       line 2 is not blank                             hard
  commit-body-wrap        a body line over commits.body_wrap (72)          soft
  commit-format           subject doesn't follow the convention           hard
  commit-type             Conventional Commits type not in commits.types  hard
  commit-imperative       subject starts with "Added", "Fixes", ...       soft
  + every prose check from scan.py on the body (trailers and code excluded)

The convention comes from commits.convention: conventional | gitmoji | none | auto.
auto follows the conventional-commits and gitmoji modules (modules.py list).

Usage:
  commitmsg.py [FILE]                 check FILE, or stdin; print findings; exit 0
  commitmsg.py --hook FILE            git commit-msg hook: obey commits.enforce
  commitmsg.py --enforce block FILE   exit 1 when a hard finding remains
  commitmsg.py --selftest

commits.enforce: off (print nothing), warn (print, never block), block (print, exit 1 on hard).
Security posture: stdlib only, no network, no subprocess. Reads the message and the config.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import scan  # noqa: E402

DEFAULT_TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert"]
CONVENTIONAL = re.compile(r"^(?P<type>[a-z][a-z0-9-]*)(?:\((?P<scope>[^()\n]+)\))?(?P<bang>!)?: (?P<desc>\S.*)$")
GITMOJI = re.compile(r"^(?::[a-z0-9_+-]+:|[←-⯿☀-➿\U0001f000-\U0001faff]️?)\s+\S")
SKIP_SHAPE = re.compile(r"^(?:Merge |Revert \"|fixup! |squash! |amend! )")
SCISSORS = re.compile(r"^# -+ >8 -+$", re.M)
TRAILER = re.compile(r"^(?:[A-Za-z][\w-]*|BREAKING CHANGE): \S", re.M)
NOT_IMPERATIVE = re.compile(
    r"^(?:added|adds|adding|fixed|fixes|fixing|updated|updates|updating|removed|removes|removing|changed|changes|"
    r"changing|improved|improves|improving|created|creates|creating|implemented|implements|implementing|refactored|"
    r"refactors|refactoring|moved|moves|moving|renamed|renames|renaming|deleted|deletes|deleting)\b", re.I)


def clean(message: str) -> list[str]:
    """Message lines as git will store them: no comments, nothing below the scissors, no trailing blanks."""
    cut = SCISSORS.search(message)
    if cut:
        message = message[:cut.start()]
    lines = [ln.rstrip() for ln in message.split("\n") if not ln.startswith("#")]
    while lines and not lines[-1]:
        lines.pop()
    while lines and not lines[0]:
        lines.pop(0)
    return lines


def convention_for(cfg: dict, active: dict[str, bool]) -> str:
    choice = cfg.get("convention", "auto")
    if choice != "auto":
        return choice
    if active.get("gitmoji"):
        return "gitmoji"
    return "conventional" if active.get("conventional-commits") else "none"


def body_prose(body: list[str]) -> str:
    """Body text for the prose checks: trailers and indented or fenced code are blanked, lines kept."""
    out, fenced = [], False
    for ln in body:
        if ln.lstrip().startswith("```"):
            fenced = not fenced
            out.append("")
        elif fenced or ln.startswith(("    ", "\t")) or TRAILER.match(ln):
            out.append("")
        else:
            out.append(ln)
    return "\n".join(out)


def check(message: str, settings: dict, convention: str, scan_kwargs: dict | None = None) -> list[dict]:
    lines = clean(message)
    hits: list[dict] = []

    def hit(line: int, sev: str, cat: str, match: str) -> None:
        hits.append({"line": line, "severity": sev, "category": cat, "match": match})

    if not lines:
        hit(1, "hard", "commit-empty", "the message is empty")
        return hits
    subject = lines[0]
    if not SKIP_SHAPE.match(subject):
        if len(subject) > settings["subject_max"]:
            hit(1, "hard", "commit-subject-length", f"{len(subject)} characters (max {settings['subject_max']})")
        elif len(subject) > settings["subject_target"]:
            hit(1, "soft", "commit-subject-length", f"{len(subject)} characters (aim for {settings['subject_target']})")
        if subject.endswith(".") and not subject.endswith("..."):
            hit(1, "soft", "commit-subject-period", subject[-30:])
        desc = subject
        if convention == "conventional":
            m = CONVENTIONAL.match(subject)
            if not m:
                hit(1, "hard", "commit-format", f"{subject[:40]!r}: expected type(scope)!: summary")
            else:
                desc = m.group("desc")
                types = settings.get("types") or DEFAULT_TYPES
                if m.group("type") not in types:
                    hit(1, "hard", "commit-type", f"{m.group('type')!r} is not one of {', '.join(types)}")
        elif convention == "gitmoji":
            if not GITMOJI.match(subject):
                hit(1, "hard", "commit-format", f"{subject[:40]!r}: expected a gitmoji first")
            desc = re.sub(r"^\S+\s+", "", subject)
        if NOT_IMPERATIVE.match(desc):
            hit(1, "soft", "commit-imperative", f"{desc.split()[0]!r}: use the imperative (add, fix, remove)")
    if len(lines) > 1 and lines[1]:
        hit(2, "hard", "commit-blank-line", "leave line 2 blank between the subject and the body")

    body = lines[2:] if len(lines) > 1 and not lines[1] else lines[1:]
    first_body = len(lines) - len(body) + 1
    fenced = False
    for i, ln in enumerate(body):
        if ln.lstrip().startswith("```"):
            fenced = not fenced
            continue
        long_ok = fenced or ln.startswith(("    ", "\t")) or "://" in ln or TRAILER.match(ln)
        if len(ln) > settings["body_wrap"] and not long_ok:
            hit(first_body + i, "soft", "commit-body-wrap", f"{len(ln)} characters (wrap at {settings['body_wrap']})")
    if body:
        prose = body_prose(body)
        for h in scan.scan(prose, **(scan_kwargs or {})):
            hits.append({**h, "line": h["line"] + first_body - 1})
    return sorted(hits, key=lambda h: (h["line"], h["severity"]))


def load(no_config: bool) -> tuple[dict, dict, dict]:
    """(commits settings, whole config, scan kwargs) from the layered config."""
    import config
    cfg = scan.load_settings(no_config)
    settings = {**config.DEFAULTS["commits"], **(cfg.get("commits") or {})}
    kwargs = {"locales": cfg.get("locales") or None, "protected_terms": cfg.get("protected_terms")}
    glossary = scan.default_glossary(cfg)
    if glossary:
        kwargs["aliases"] = scan.load_glossary(Path(glossary).read_text(encoding="utf-8"))
    return settings, cfg, kwargs


def active_modules(cfg: dict) -> dict[str, bool]:
    if not cfg.get("_root"):
        return {}
    import modules
    mods = modules.all_modules()
    return {n: on for n, (on, _) in modules.resolve(mods, Path(cfg["_root"]), modules.installed_plugins()).items()}


def selftest() -> None:
    s = {"subject_max": 72, "subject_target": 50, "body_wrap": 72, "types": []}
    cats = lambda msg, conv="conventional": {h["category"] for h in check(msg, s, conv)}  # noqa: E731

    good = "feat(api): add retry with backoff\n\nCalls to CMiC fail about once an hour, so retry three times.\n\nRefs: #42\n"
    assert check(good, s, "conventional") == [], check(good, s, "conventional")
    assert cats("") == {"commit-empty"}
    assert cats("# only a comment\n") == {"commit-empty"}
    assert "commit-format" in cats("Add retry")
    assert "commit-type" in cats("feature: add retry")
    assert cats("Add retry", "none") == set()
    assert "commit-subject-length" in cats("fix: " + "x" * 70)
    assert [h["severity"] for h in check("fix: " + "x" * 50, s, "conventional")] == ["soft"]
    assert "commit-subject-period" in cats("fix: add retry.")
    assert "commit-blank-line" in cats("fix: add retry\nno blank line")
    assert "commit-body-wrap" in cats("fix: add retry\n\n" + "word " * 20)
    assert "commit-body-wrap" not in cats("fix: add retry\n\nSee https://example.com/" + "x" * 80)
    assert "commit-imperative" in cats("fix: added retry")
    assert "commit-imperative" in cats("Added retry", "none")
    assert cats("Merge branch 'main' into feature", "conventional") == set()
    assert cats("fixup! feat: add retry") == set()
    assert "throat-clearing" in cats("fix: add retry\n\nHere's the thing: it failed.")
    assert "throat-clearing" not in cats("fix: add retry\n\n    Here's the thing: code block\n")
    scissors = "fix: add retry\n\n# ------------------------ >8 ------------------------\ndiff --git a b\n" + "y" * 200
    assert check(scissors, s, "conventional") == []
    assert "commit-format" not in cats("✨ add retry", "gitmoji") and "commit-format" in cats("add retry", "gitmoji")
    assert "commit-format" not in cats(":sparkles: add retry", "gitmoji")
    assert convention_for({"convention": "auto"}, {"conventional-commits": True}) == "conventional"
    assert convention_for({"convention": "auto"}, {}) == "none"
    assert convention_for({"convention": "gitmoji"}, {"conventional-commits": True}) == "gitmoji"
    assert exit_code([{"severity": "hard"}], "block") == 1 and exit_code([{"severity": "hard"}], "warn") == 0
    assert exit_code([{"severity": "soft"}], "block") == 0
    print("selftest ok")


def exit_code(hits: list[dict], enforce: str) -> int:
    return 1 if enforce == "block" and any(h["severity"] == "hard" for h in hits) else 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", help="message file (git passes .git/COMMIT_EDITMSG); default stdin")
    ap.add_argument("--hook", action="store_true", help="run as the commit-msg hook: obey commits.enforce")
    ap.add_argument("--enforce", choices=("off", "warn", "block"), help="override commits.enforce")
    ap.add_argument("--convention", choices=("auto", "conventional", "gitmoji", "none"), help="override commits.convention")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-config", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    settings, cfg, kwargs = load(args.no_config)
    enforce = args.enforce or (settings["enforce"] if args.hook else "warn")
    if enforce == "off" or not cfg.get("enabled", True):
        return
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            message = scan.read_capped(f)
    else:
        message = scan.read_capped(sys.stdin)
    convention = convention_for({**settings, **({"convention": args.convention} if args.convention else {})},
                                active_modules(cfg))
    started = time.perf_counter()
    hits = check(message, settings, convention, kwargs)
    if cfg.get("severity"):
        import config
        hits = config.apply_severity(hits, cfg["severity"])
    if not args.no_config:
        import telemetry
        telemetry.record("commitmsg", started, hits, convention=convention, enforce=enforce,
                         hook=args.hook, blocked=bool(exit_code(hits, enforce)))

    out = sys.stderr if args.hook else sys.stdout  # git shows a hook's stderr to the committer
    if args.json:
        print(json.dumps(hits, indent=2), file=out)
    elif hits:
        print(f"ocre-jelly: commit message ({convention} convention, enforce={enforce})", file=out)
        for h in hits:
            print(f"  L{h['line']:<3} {h['severity']:<4} {h['category']:<22} {h['match']}", file=out)
        code = exit_code(hits, enforce)
        if code:
            print("ocre-jelly: commit blocked. Fix the hard findings, or commit with --no-verify.", file=out)
    sys.exit(exit_code(hits, enforce))


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        scan._record_error(e)
        sys.exit(f"commitmsg.py: {e}")
    except Exception as e:
        scan._record_error(e)
        raise
