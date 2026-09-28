#!/usr/bin/env python3
"""Keep ocre-jelly up to date with the main branch of its marketplace.

Two modes, both at session startup, both opt-in (updates.mode, user or local layer only):

  silent   Claude Code's own marketplace auto-update does the work. `mode silent`
           turns on autoUpdate for the ocre-jelly marketplace in ~/.claude/settings.json.
           Claude Code then updates at startup and says "Run /reload-plugins to apply".
  prompt   At most every updates.check_hours, a background `git ls-remote` reads the
           latest commit of updates.branch. When it differs from the installed commit,
           the next session start tells you, and Claude asks whether to update now.
  off      Neither (the default).

Usage:
  update.py status                  mode, installed commit, latest known commit, last check
  update.py mode off|prompt|silent  set the mode for you (user layer) and the native flag
  update.py check [--now]           refresh the latest-commit cache (the hook runs this in the background)
  update.py apply                   update now: claude plugin marketplace update + claude plugin update
  update.py --selftest

Security posture: this is the only ocre-jelly script that touches the network or runs
programs, and only when you opt in. The check runs `git ls-remote` (read-only, no
prompts, 10 s timeout). `apply` runs the claude CLI's own update commands. `mode`
edits only extraKnownMarketplaces.ocre-jelly in ~/.claude/settings.json, after a backup.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import config  # noqa: E402

PLUGIN = "ocre-jelly"
MARKETPLACE = "ocre-jelly"
PLUGIN_ID = f"{PLUGIN}@{MARKETPLACE}"


def cache_file() -> Path:
    return config.claude_dir() / "ocre-jelly" / "update-check.json"


def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def installed() -> dict:
    """The installed ocre-jelly record from Claude Code's registry, or {}."""
    data = read_json(config.claude_dir() / "plugins" / "installed_plugins.json")
    entries = (data.get("plugins") or {}).get(PLUGIN_ID) or []
    return entries[0] if entries and isinstance(entries[0], dict) else {}


def marketplace() -> dict:
    return read_json(config.claude_dir() / "plugins" / "known_marketplaces.json").get(MARKETPLACE) or {}


def remote_url(source: dict) -> str | None:
    """A git URL to read the branch from, or None when the source can't be checked."""
    kind = source.get("source")
    if kind == "github" and source.get("repo"):
        return f"https://github.com/{source['repo']}.git"
    if kind == "git" and str(source.get("url", "")).startswith(("https://", "ssh://", "git@")):
        return source["url"]
    path = source.get("path") or source.get("directory")
    if path and (Path(path) / ".git").exists():
        return str(Path(path))  # a local clone: ls-remote reads its own refs (after you pull or commit)
    return None


def ls_remote(url: str, branch: str, timeout: int = 10) -> str | None:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "echo", "SSH_ASKPASS": "echo"}
    proc = subprocess.run(["git", "ls-remote", "--heads", "--", url, f"refs/heads/{branch}"],
                          capture_output=True, text=True, timeout=timeout, env=env, stdin=subprocess.DEVNULL)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else f"git exited {proc.returncode}")
    line = proc.stdout.strip().split("\n")[0]
    return line.split()[0] if line else None


def settings() -> dict:
    return config.load()["updates"]


def check(force: bool = False) -> dict:
    """Refresh the cache when it's due. Returns the cache. Records failures; never raises."""
    upd = settings()
    cache = read_json(cache_file())
    if upd["mode"] != "prompt" and not force:
        return cache
    last = cache.get("checked_at")
    if not force and last:
        try:
            age = now() - dt.datetime.fromisoformat(last)
            if age < dt.timedelta(hours=upd["check_hours"]):
                return cache
        except ValueError:
            pass
    cache = {"checked_at": now().isoformat(timespec="seconds"), "branch": upd["branch"]}
    url = remote_url(marketplace().get("source") or {})
    try:
        if not url:
            raise RuntimeError("the ocre-jelly marketplace has no git source to check")
        cache["latest"] = ls_remote(url, upd["branch"])
        cache["ok"] = True
    except (RuntimeError, OSError, subprocess.SubprocessError) as e:
        cache["ok"], cache["error"] = False, str(e)[:200]
    cache_file().parent.mkdir(parents=True, exist_ok=True)
    cache_file().write_text(json.dumps(cache, indent=2) + "\n", encoding="utf-8")
    return cache


def pending(cache: dict | None = None) -> tuple[str, str] | None:
    """(installed short sha, latest short sha) when main moved past the installed commit."""
    cache = read_json(cache_file()) if cache is None else cache
    current = installed().get("gitCommitSha")
    latest = cache.get("latest")
    if cache.get("ok") and current and latest and latest != current:
        return current[:7], latest[:7]
    return None


def hook_notice() -> tuple[str, str] | None:
    """For the SessionStart hook: (message for the user, instruction for Claude), or None.
    Also starts a background check when one is due, so the hook never waits on the network."""
    upd = settings()
    if upd["mode"] != "prompt":
        return None
    cache = read_json(cache_file())
    due = True
    if cache.get("checked_at"):
        try:
            due = now() - dt.datetime.fromisoformat(cache["checked_at"]) >= dt.timedelta(hours=upd["check_hours"])
        except ValueError:
            pass
    if due:
        subprocess.Popen([sys.executable, str(HERE / "update.py"), "check"], stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    change = pending(cache)
    if not change:
        return None
    old, new = change
    user = f"ocre-jelly: an update is available ({old} -> {new} on {cache.get('branch', 'main')})."
    agent = (f"ocre-jelly update available: installed {old}, {cache.get('branch', 'main')} is at {new}. "
             "Before your first answer, ask the user with AskUserQuestion whether to update ocre-jelly now. "
             f"If yes, run `python3 {HERE / 'update.py'} apply`, then tell them to run /reload-plugins. "
             "If no, don't ask again this session.")
    return user, agent


def set_native_auto_update(on: bool) -> Path:
    """Set extraKnownMarketplaces.ocre-jelly.autoUpdate in ~/.claude/settings.json (backup first)."""
    path = config.claude_dir() / "settings.json"
    data = read_json(path) if path.exists() else {}
    if path.exists() and not data:
        raise RuntimeError(f"{path} isn't valid JSON; not touching it")
    source = marketplace().get("source")
    markets = data.setdefault("extraKnownMarketplaces", {})
    entry = markets.setdefault(MARKETPLACE, {})
    if "source" not in entry:
        if not source:
            raise RuntimeError("install ocre-jelly from its marketplace first (claude plugin marketplace add …)")
        entry["source"] = source
    entry["autoUpdate"] = on
    if path.exists():
        shutil.copy2(path, path.with_name(path.name + ".ocre-jelly.bak"))
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


def set_mode(mode: str) -> list[str]:
    done = [f"updates.mode = {mode} in {config.update_layer('user', config.project_root(), lambda d: d.setdefault('updates', {}).update({'mode': mode}))}"]
    try:
        path = set_native_auto_update(mode == "silent")
        done.append(f"Claude Code auto-update for the ocre-jelly marketplace: {'on' if mode == 'silent' else 'off'} ({path})")
    except RuntimeError as e:
        done.append(f"native auto-update not changed: {e}")
    return done


def apply() -> int:
    if not shutil.which("claude"):
        print("the claude CLI isn't on PATH", file=sys.stderr)
        return 1
    for cmd in (["claude", "plugin", "marketplace", "update", MARKETPLACE], ["claude", "plugin", "update", PLUGIN_ID]):
        print("$ " + " ".join(cmd))
        proc = subprocess.run(cmd, stdin=subprocess.DEVNULL, timeout=180)
        if proc.returncode != 0:
            return proc.returncode
    if cache_file().exists():
        cache_file().unlink()  # the next check starts fresh against the new install
    print("updated. Run /reload-plugins, or start a new session, to use the new version.")
    return 0


def status() -> None:
    upd, inst, cache = settings(), installed(), read_json(cache_file())
    print(f"mode: {upd['mode']} (branch {upd['branch']}, check every {upd['check_hours']} h)")
    print(f"installed: {inst.get('version', 'not installed from a marketplace')} "
          f"({(inst.get('gitCommitSha') or '?')[:7]})")
    print(f"marketplace source: {json.dumps(marketplace().get('source') or 'unknown')}, "
          f"native auto-update: {'on' if marketplace().get('autoUpdate') else 'off'}")
    if cache:
        state = f"latest {cache.get('latest', '?')[:7]}" if cache.get("ok") else f"failed: {cache.get('error')}"
        print(f"last check: {cache.get('checked_at')} ({state})")
    change = pending(cache)
    print(f"update available: {change[0]} -> {change[1]}" if change else "no update pending")


def selftest() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        os.environ["CLAUDE_CONFIG_DIR"] = str(tmp / "home")
        plugins = tmp / "home" / "plugins"
        plugins.mkdir(parents=True)
        # a local git "server" with a main branch
        remote = tmp / "remote"
        subprocess.run(["git", "init", "-q", "-b", "main", str(remote)], check=True)
        subprocess.run(["git", "-C", str(remote), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                        "--allow-empty", "-m", "one"], check=True)
        head = subprocess.run(["git", "-C", str(remote), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        (plugins / "known_marketplaces.json").write_text(json.dumps({MARKETPLACE: {"source": {"source": "directory", "path": str(remote)}}}))
        (plugins / "installed_plugins.json").write_text(json.dumps({"plugins": {PLUGIN_ID: [{"gitCommitSha": "0" * 40, "version": "0.1.0"}]}}))

        assert remote_url({"source": "github", "repo": "a/b"}) == "https://github.com/a/b.git"
        assert remote_url({"source": "git", "url": "file:///etc"}) is None
        assert ls_remote(str(remote), "main") == head
        assert settings()["mode"] == "off" and hook_notice() is None

        root = config.project_root()
        config.update_layer("user", root, lambda d: d.update({"updates": {"mode": "prompt"}}))
        cache = check(force=True)
        assert cache["ok"] and cache["latest"] == head, cache
        assert pending(cache) == ("0000000", head[:7])
        user, agent = hook_notice()
        assert head[:7] in user and "AskUserQuestion" in agent and "update.py" in agent

        (plugins / "installed_plugins.json").write_text(json.dumps({"plugins": {PLUGIN_ID: [{"gitCommitSha": head}]}}))
        assert pending(cache) is None and hook_notice() is None

        (plugins / "known_marketplaces.json").write_text(json.dumps({MARKETPLACE: {"source": {"source": "directory", "path": str(tmp / "nowhere")}}}))
        failed = check(force=True)  # no network: an unknown source fails before git runs
        assert failed["ok"] is False and failed["error"] and pending(failed) is None

        settings_json = tmp / "home" / "settings.json"
        settings_json.write_text(json.dumps({"theme": "dark", "extraKnownMarketplaces": {"other": {"source": {"source": "github", "repo": "x/y"}}}}))
        set_native_auto_update(True)
        data = json.loads(settings_json.read_text())
        assert data["theme"] == "dark" and "other" in data["extraKnownMarketplaces"]
        assert data["extraKnownMarketplaces"][MARKETPLACE]["autoUpdate"] is True
        assert data["extraKnownMarketplaces"][MARKETPLACE]["source"]["source"] == "directory"
        assert (tmp / "home" / "settings.json.ocre-jelly.bak").exists()

        config.update_layer("project", root, lambda d: d.update({"updates": {"mode": "prompt"}}))
        config.update_layer("user", root, lambda d: d.update({"updates": {"mode": "off"}}))
        assert settings()["mode"] == "off", "a committed config turned updates on"
        (root / ".claude" / "ocre-jelly.json").unlink()
    print("selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", nargs="?", choices=("status", "mode", "check", "apply"), default="status")
    ap.add_argument("value", nargs="?", choices=("off", "prompt", "silent"))
    ap.add_argument("--now", action="store_true", help="check: ignore check_hours")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.action == "status":
        return status()
    if args.action == "mode":
        if not args.value:
            sys.exit("usage: update.py mode off|prompt|silent")
        return print("\n".join(set_mode(args.value)))
    if args.action == "check":
        cache = check(force=args.now)
        if sys.stdout.isatty() or args.now:
            status()
        return None if cache.get("ok", True) else sys.exit(1)
    if args.action == "apply":
        sys.exit(apply())


if __name__ == "__main__":
    main()
