# Keep ocre-jelly up to date

ocre-jelly can follow the `main` branch of its marketplace, at session start, in one of two ways. Both are off by default, and only you can turn them on.

| Mode | At session start | You do |
|---|---|---|
| `silent` | Claude Code's own marketplace auto-update pulls the new version. It says "Plugin updated · Run /reload-plugins to apply". | Run `/reload-plugins`, or start a new session. |
| `prompt` | ocre-jelly tells you "an update is available (abc1234 -> def5678 on main)", and Claude asks whether to update now. | Say yes or no. On yes, Claude updates, and you run `/reload-plugins`. |
| `off` (default) | Nothing. | `claude plugin update ocre-jelly@ocre-jelly` when you want. |

## Choose a mode

```bash
python3 $OJ/update.py mode silent    # or: prompt, off
```

Or ask Claude: "update ocre-jelly silently" or "ask me before updating ocre-jelly".

- `mode` writes `updates.mode` in your user config (`~/.claude/ocre-jelly.json`).
- `silent` also sets `autoUpdate: true` for the ocre-jelly marketplace in `~/.claude/settings.json`, and keeps a backup (`settings.json.ocre-jelly.bak`). The other modes set it to `false`.
- You can also toggle Claude Code's auto-update yourself: `/plugin`, then **Marketplaces**, **ocre-jelly**, **Enable auto-update**.

## How prompt mode works

1. At session start, the hook reads the last check. It never waits on the network.
2. When a check is due (every `updates.check_hours`, 24 by default), the hook starts `update.py check` in the background. It runs `git ls-remote` on the marketplace's source to read the latest commit of `updates.branch`. It reads only; no credential prompts appear, and it stops after 10 seconds.
3. When that commit differs from the installed one, the **next** session start shows the notice, and Claude asks you with a question.
4. On yes, Claude runs `update.py apply`, which runs `claude plugin marketplace update ocre-jelly` and `claude plugin update ocre-jelly@ocre-jelly`. Then run `/reload-plugins`.

A new commit on `main` therefore shows up at most one day later (by default), one session after the check. To check right away:

```bash
python3 $OJ/update.py check --now
python3 $OJ/update.py status
```

## Requirements

- ocre-jelly installed from a marketplace with a git source: the server URL (`claude plugin marketplace add https://git.nexapptech.com/vbernier/ocre-jelly.git`), or a local clone. From a local clone, "main" means the clone's own `main`. Pull or commit there, and the check sees it.
- Read access to the repo without a password prompt: a credential helper or an SSH key. Without one, the check fails quietly, and `update.py status` shows the error.

## Team rules

A committed `.claude/ocre-jelly.json` can't choose a mode for teammates, because updates reach the network. It can only force updates off:

```json
{ "updates": { "mode": "off" } }
```

## Check the state

```bash
python3 $OJ/update.py status
```

```
mode: prompt (branch main, check every 24 h)
installed: 0.1.0 (b4019b0)
marketplace source: {"source": "git", "url": "https://git.nexapptech.com/vbernier/ocre-jelly.git"}, native auto-update: off
last check: 2026-09-28T12:18:04+00:00 (latest ca767f4)
update available: b4019b0 -> ca767f4
```
