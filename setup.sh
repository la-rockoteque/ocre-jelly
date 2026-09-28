#!/usr/bin/env bash
# Install ocre-jelly as a Claude Code plugin from this folder (a local marketplace).
#   ./setup.sh                       install for your user
#   ./setup.sh --scope project       install for the current repo (shared via .claude/settings.json)
#   ./setup.sh --scope local         install for the current repo, this machine only
#   ./setup.sh --uninstall [--scope ...]
#   ./setup.sh --check               run every self-test, install nothing
# Runs only the claude CLI and the scanner self-check. No network, no sudo.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCOPE=user
UNINSTALL=0
CHECK=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope) SCOPE="${2:?--scope needs user, project or local}"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    --check) CHECK=1; shift ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
[[ $SCOPE =~ ^(user|project|local)$ ]] || { echo "bad scope: $SCOPE" >&2; exit 2; }

selftests() {
  command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 1; }
  for t in config scan codedoc modules; do
    printf '%-8s ' "$t"
    python3 "$SRC/skills/ocre-jelly/scripts/$t.py" --selftest 2>/dev/null || { echo "FAILED: $t" >&2; exit 1; }
  done
  printf '%-8s ' docs
  python3 "$SRC/skills/ocre-jelly/scripts/gen_docs.py" --check || exit 1
}

if [[ $CHECK -eq 1 ]]; then selftests; exit 0; fi
command -v claude >/dev/null || { echo "claude CLI is required" >&2; exit 1; }

if [[ $UNINSTALL -eq 1 ]]; then
  claude plugin uninstall ocre-jelly@ocre-jelly --scope "$SCOPE"
  exit 0
fi

selftests
claude plugin validate "$SRC"
claude plugin marketplace add "$SRC" --scope "$SCOPE"
claude plugin install ocre-jelly@ocre-jelly --scope "$SCOPE"
echo "restart Claude Code, then: /ocre-jelly audit <text or file>. Disable the always-on mode with OCRE_JELLY=off."
