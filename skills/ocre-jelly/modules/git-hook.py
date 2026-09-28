"""Render the commit-msg hook. It calls this machine's commitmsg.py, so it lives in .git/hooks (never committed)."""
import re
import shlex
from pathlib import Path


def render(ctx: dict) -> str:
    script = shlex.quote(f"{ctx['scripts_dir']}/commitmsg.py")
    git = Path(ctx["root"]) / ".git"
    line = f'python3 {script} --hook "$1"'
    if git.is_file():
        raise ValueError(f"this is a git worktree; install the hook in the main clone, or add `{line}` to your hook manager")
    cfg = git / "config"
    if cfg.is_file() and re.search(r"(?im)^\s*hookspath\s*=", cfg.read_text(encoding="utf-8", errors="replace")):
        raise ValueError(f"core.hooksPath is set (husky, lefthook?), so git ignores .git/hooks. Add `{line}` to that commit-msg hook")
    return f"""#!/bin/sh
# {ctx['mark']} (git-hook module). Re-export to update; delete this file to remove it.
# commits.enforce in the ocre-jelly config decides: off, warn (never blocks) or block.
command -v python3 >/dev/null 2>&1 || exit 0
if [ ! -f {script} ]; then
  echo "ocre-jelly: {script} not found; commit message not checked. Re-run: modules.py export git-hook" >&2
  exit 0
fi
exec python3 {script} --hook "$1"
"""
