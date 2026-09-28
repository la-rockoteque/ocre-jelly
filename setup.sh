#!/usr/bin/env bash
# Install ocre-jelly as a Claude Code plugin from this folder (a local marketplace).
#   ./setup.sh                       install for your user
#   ./setup.sh --scope project       install for the current repo (shared via .claude/settings.json)
#   ./setup.sh --scope local         install for the current repo, this machine only
#   ./setup.sh --uninstall [--scope ...]
#   ./setup.sh --check               run every self-test, install nothing
#   ./setup.sh --wizard [--repo DIR] run the setup wizard after installing, without asking
#   ./setup.sh --no-wizard           install only
# Runs only the claude CLI and the self-tests. No network, no sudo.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCOPE=user
UNINSTALL=0
CHECK=0
WIZARD=ask
REPO="$PWD"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope) SCOPE="${2:?--scope needs user, project or local}"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    --check) CHECK=1; shift ;;
    --wizard) WIZARD=yes; shift ;;
    --no-wizard) WIZARD=no; shift ;;
    --repo) REPO="${2:?--repo needs a directory}"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
[[ $SCOPE =~ ^(user|project|local)$ ]] || { echo "bad scope: $SCOPE" >&2; exit 2; }

selftests() {
  command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 1; }
  for t in config scan codedoc commitmsg feedback telemetry update wizard modules; do
    printf '%-10s ' "$t"
    python3 "$SRC/skills/ocre-jelly/scripts/$t.py" --selftest 2>/dev/null || { echo "FAILED: $t" >&2; exit 1; }
  done
  printf '%-10s ' docs
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
echo "installed. Disable the always-on mode with OCRE_JELLY=off."

# The setup wizard runs inside Claude Code, which a fresh process loads with the new plugin.
if [[ $WIZARD == ask ]]; then
  if [[ -t 0 && -t 1 ]]; then
    read -r -p "Run the setup wizard now? [Y/n] " answer
    [[ ${answer:-y} =~ ^[Yy] ]] && WIZARD=yes || WIZARD=no
    if [[ $WIZARD == yes ]]; then
      read -r -p "Repo to configure [$REPO]: " picked
      REPO="${picked:-$REPO}"
    fi
  else
    WIZARD=no  # not interactive (CI, piped): never start a session
  fi
fi
if [[ $WIZARD == yes ]]; then
  REPO="${REPO/#\~/$HOME}"
  [[ -d $REPO ]] || { echo "not a directory: $REPO" >&2; exit 1; }
  if [[ $(cd "$REPO" && pwd) == "$SRC" ]]; then
    echo "note: this configures the ocre-jelly repo itself. Pass --repo DIR to configure another repo."
  fi
  echo "starting Claude Code in $REPO ..."
  cd "$REPO" && exec claude "Run the ocre-jelly setup wizard (/ocre-jelly setup) for this repo."
else
  echo "to configure a repo later: open it in Claude Code and run /ocre-jelly setup"
fi
