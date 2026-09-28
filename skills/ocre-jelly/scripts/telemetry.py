#!/usr/bin/env python3
"""Opt-in, local-only usage statistics and debug logging for ocre-jelly.

Off by default. Turn it on for yourself (user or local config layer):
  modules.py config set telemetry '{"enabled":true}'
A committed project config can turn it off, but never on: consent is personal.

What is recorded, one JSON line per run in ~/.claude/ocre-jelly/usage.jsonl:
  the tool, its duration, finding counts per category and severity, the locales,
  file extensions and counts, the number of active modules, the words the hook
  injected, the agent's confirmed/protected verdicts per category, and error types.
What is never recorded: text, matches, file names or paths, repo names, people.

With "debug": true, error tracebacks also go to ~/.claude/ocre-jelly/debug.log (local only).

Usage:
  telemetry.py status                 on or off, and where the files are
  telemetry.py summary [--days N]     aggregated statistics
  telemetry.py verdicts JSON          record the agent's verdicts: '{"ste-length":{"confirmed":1,"protected":4}}'
  telemetry.py send [--open]          show the summary as feedback text and open the pre-filled form
  telemetry.py clear                  delete the usage file and the debug log
  telemetry.py --selftest

Security posture: stdlib only, no network. Writes only under ~/.claude/ocre-jelly/.
"send" prints the summary and builds a link; the user reviews and submits it in the browser.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import config  # noqa: E402

MAX_BYTES = 1_000_000  # ponytail: when the file passes this, the oldest half is dropped
_settings: dict | None = None


def data_dir() -> Path:
    return config.claude_dir() / "ocre-jelly"


def usage_file() -> Path:
    return data_dir() / "usage.jsonl"


def debug_file() -> Path:
    return data_dir() / "debug.log"


def settings() -> dict:
    """telemetry settings for the current repo, loaded once per process. Never raises."""
    global _settings
    if _settings is None:
        try:
            _settings = config.load()["telemetry"]
        except Exception:  # noqa: BLE001 - statistics must never break a tool
            _settings = {"enabled": False, "debug": False, "retention_days": 30}
    return _settings


def version() -> str:
    try:
        return json.loads((HERE.parent.parent.parent / ".claude-plugin" / "plugin.json").read_text()).get("version", "?")
    except (OSError, ValueError):
        return "?"


def _append(event: dict) -> None:
    path = usage_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
    if path.stat().st_size > MAX_BYTES:
        lines = path.read_text(encoding="utf-8").splitlines()
        path.write_text("\n".join(lines[len(lines) // 2:]) + "\n", encoding="utf-8")


def record(tool: str, started: float | None = None, hits: list[dict] | None = None, **fields) -> None:
    """Append one event when telemetry is on. Counts only; never raises."""
    try:
        if not settings().get("enabled"):
            return
        event = {"ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "v": version(), "tool": tool}
        if started is not None:
            event["ms"] = round((time.perf_counter() - started) * 1000)
        if hits is not None:
            event["counts"] = dict(collections.Counter(h["category"] for h in hits))
            event["severity"] = dict(collections.Counter(h["severity"] for h in hits))
        event.update({k: v for k, v in fields.items() if v is not None})
        _append(event)
    except Exception:  # noqa: BLE001
        pass


def extensions(paths: list[str]) -> dict[str, int]:
    """File-type counts only: {'.ts': 3}. Names and folders are dropped."""
    return dict(collections.Counter(Path(p).suffix.lower() or "(none)" for p in paths))


def error(tool: str, exc: BaseException) -> None:
    """Record the error type; with debug on, also the traceback in the local debug log."""
    record(tool, result="error", error=type(exc).__name__)
    try:
        if settings().get("debug"):
            debug_file().parent.mkdir(parents=True, exist_ok=True)
            with debug_file().open("a", encoding="utf-8") as f:
                stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
                f.write(f"--- {stamp} {tool} ocre-jelly {version()}\n")
                f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
    except Exception:  # noqa: BLE001
        pass


# ---- reading -----------------------------------------------------------------

def events(days: int | None = None) -> list[dict]:
    try:
        lines = usage_file().read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    cutoff = None
    if days:
        cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if isinstance(e, dict) and (cutoff is None or e.get("ts", "") >= cutoff):
            out.append(e)
    return out


def prune(days: int) -> None:
    """Drop events older than the retention period."""
    kept = events(days)
    if usage_file().exists():
        usage_file().write_text("".join(json.dumps(e, ensure_ascii=False, separators=(",", ":")) + "\n" for e in kept),
                                encoding="utf-8")


def summarize(evts: list[dict]) -> dict:
    runs = collections.Counter(e.get("tool") for e in evts)
    counts, severity, errors = collections.Counter(), collections.Counter(), collections.Counter()
    exts, locales, ms = collections.Counter(), collections.Counter(), collections.defaultdict(list)
    verdicts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    words, blocked = [], 0
    gates: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for e in evts:
        counts.update(e.get("counts", {}))
        severity.update(e.get("severity", {}))
        exts.update(e.get("ext", {}))
        locales.update(e.get("locales") or [])
        if "ms" in e:
            ms[e.get("tool")].append(e["ms"])
        if e.get("error"):
            errors[e["error"]] += 1
        if "words" in e:
            words.append(e["words"])
        blocked += bool(e.get("blocked"))
        if e.get("gate"):
            gates[e["gate"]]["passed" if e.get("ok") else "failed"] += 1
        for cat, v in (e.get("verdicts") or {}).items():
            verdicts[cat].update({k: n for k, n in v.items() if k in ("confirmed", "protected") and isinstance(n, int)})
    precision = {cat: {"confirmed": v["confirmed"], "protected": v["protected"],
                       "confirmed_rate": round(v["confirmed"] / (v["confirmed"] + v["protected"]), 2)}
                 for cat, v in verdicts.items() if v["confirmed"] + v["protected"]}
    first = min((e.get("ts", "") for e in evts), default="")
    last = max((e.get("ts", "") for e in evts), default="")
    return {
        "period": f"{first[:10]} to {last[:10]}" if evts else "no data",
        "versions": sorted({e.get("v", "?") for e in evts}),
        "runs": dict(runs),
        "median_ms": {t: sorted(v)[len(v) // 2] for t, v in ms.items()},
        "findings_by_category": dict(counts.most_common(20)),
        "findings_by_severity": dict(severity),
        "verdicts": precision,
        "file_types": dict(exts.most_common(10)),
        "locales": dict(locales),
        "hook_words_median": sorted(words)[len(words) // 2] if words else None,
        "commits_blocked": blocked,
        "rewrite_gates": {g: dict(c) for g, c in gates.items()},
        "errors": dict(errors),
    }


def summary_text(s: dict) -> str:
    """The exact text `send` pre-fills. Aggregates only."""
    def kv(d: dict) -> str:
        return ", ".join(f"{k} {v}" for k, v in d.items()) or "none"
    lines = [f"[Usage statistics] ocre-jelly {', '.join(s['versions']) or '?'}, {s['period']}",
             f"Runs: {kv(s['runs'])}",
             f"Median ms: {kv(s['median_ms'])}",
             f"Findings by severity: {kv(s['findings_by_severity'])}",
             f"Top findings: {kv(s['findings_by_category'])}"]
    if s["verdicts"]:
        lines.append("Verdicts (confirmed/protected): " + ", ".join(
            f"{c} {v['confirmed']}/{v['protected']}" for c, v in sorted(s["verdicts"].items())))
    lines += [f"File types: {kv(s['file_types'])}", f"Locales: {kv(s['locales'])}",
              f"Hook words (median): {s['hook_words_median'] if s['hook_words_median'] is not None else 'n/a'}",
              f"Commits blocked: {s['commits_blocked']}",
              "Rewrite gates (passed/failed): " + (", ".join(f"{g} {c.get('passed', 0)}/{c.get('failed', 0)}"
                                                           for g, c in sorted(s.get("rewrite_gates", {}).items())) or "none"),
              f"Errors: {kv(s['errors'])}"]
    return "\n".join(lines)


# ---- cli ---------------------------------------------------------------------

def selftest() -> None:
    import tempfile
    global _settings
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["CLAUDE_CONFIG_DIR"] = tmp
        _settings = {"enabled": False, "debug": False, "retention_days": 30}
        record("scan", hits=[{"category": "em-dash", "severity": "soft"}])
        assert not usage_file().exists(), "recorded while off"

        _settings = {"enabled": True, "debug": True, "retention_days": 30}
        t = time.perf_counter()
        record("scan", started=t, hits=[{"category": "throat-clearing", "severity": "hard", "match": "SECRET TEXT"},
                                        {"category": "em-dash", "severity": "soft"}], locales=["en-CA"])
        record("codedoc", ext=extensions(["/Users/me/acme/src/Billing.cs", "a/b.ts", "c.ts"]))
        record("verdict", verdicts={"em-dash": {"confirmed": 1, "protected": 3}})
        record("commitmsg", blocked=True)
        record("gate", gate="preserve", ok=False, missing=2)
        record("gate", gate="preserve", ok=True, missing=0)
        try:
            raise KeyError("boom")
        except KeyError as e:
            error("scan", e)
        raw = usage_file().read_text()
        assert "SECRET TEXT" not in raw and "acme" not in raw and "Billing" not in raw, raw
        s = summarize(events())
        assert s["rewrite_gates"] == {"preserve": {"failed": 1, "passed": 1}}, s["rewrite_gates"]
        assert "preserve 1/1" in summary_text(s)
        assert s["runs"]["scan"] == 2 and s["findings_by_category"] == {"throat-clearing": 1, "em-dash": 1}
        assert s["file_types"] == {".cs": 1, ".ts": 2} and s["commits_blocked"] == 1 and s["errors"] == {"KeyError": 1}
        assert s["verdicts"]["em-dash"] == {"confirmed": 1, "protected": 3, "confirmed_rate": 0.25}
        text = summary_text(s)
        assert text.startswith("[Usage statistics]") and "em-dash 1/3" in text and "/Users" not in text
        assert "KeyError" in debug_file().read_text()

        old = {"ts": "2000-01-01T00:00:00Z", "tool": "scan"}
        with usage_file().open("a") as f:
            f.write(json.dumps(old) + "\nnot json\n")
        prune(30)
        assert all(e["ts"] > "2001" for e in events()) and len(events()) == 7
        _settings = None
    print("selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", nargs="?", choices=("status", "summary", "verdicts", "send", "clear"))
    ap.add_argument("value", nargs="?", help="JSON for verdicts")
    ap.add_argument("--days", type=int, help="summary window (default: telemetry.retention_days)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--open", action="store_true", help="send: open the pre-filled form")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    tel = settings()
    days = args.days or tel.get("retention_days", 30)

    if args.action in (None, "status"):
        state = "on" if tel.get("enabled") else "off"
        print(f"telemetry: {state} (debug {'on' if tel.get('debug') else 'off'}, keeps {tel.get('retention_days', 30)} days)")
        print(f"usage file: {usage_file()} ({len(events())} events)")
        print(f"debug log:  {debug_file()}")
        if state == "off":
            print('turn it on for yourself: modules.py config set telemetry \'{"enabled":true}\'')
        return
    if args.action == "verdicts":
        try:
            data = json.loads(args.value or "")
            assert isinstance(data, dict)
        except (ValueError, AssertionError):
            sys.exit('verdicts needs JSON like \'{"ste-length":{"confirmed":1,"protected":4}}\'')
        return record("verdict", verdicts=data)
    if args.action == "clear":
        for path in (usage_file(), debug_file()):
            if path.exists():
                path.unlink()
        return print("cleared")

    prune(tel.get("retention_days", 30))
    s = summarize(events(days))
    if args.action == "summary":
        return print(json.dumps(s, indent=2, ensure_ascii=False) if args.json else summary_text(s))
    if args.action == "send":
        import feedback
        fb = config.load()["feedback"]
        if not fb.get("enabled", True):
            sys.exit("feedback is turned off in this repo's config, so statistics can't be sent")
        if not events(days):
            sys.exit("no statistics recorded yet")
        text = summary_text(s)
        link, prefilled = feedback.form_link(fb["form_url"], fb["entry"], text)
        print("---- statistics to share (nothing is sent until you click Submit in the form) ----")
        print(text)
        print("----")
        host = link.split("/")[2]
        print(f"{'Pre-filled form' if prefilled else 'Too long to pre-fill; paste the text into the form'} on {host}:\n{link}")
        if args.open:
            import webbrowser
            webbrowser.open(link)


if __name__ == "__main__":
    main()
