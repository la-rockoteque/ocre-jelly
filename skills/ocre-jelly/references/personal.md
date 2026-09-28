# Personal settings: usage statistics and updates

## Usage statistics (opt-in)

Telemetry is off unless the user turned it on in their user or local config (`telemetry.enabled`); `telemetry.py status` says which. When it is on, the scanners and hooks record counts by themselves. Two things are yours:

- After you classify an audit's candidates, record the verdicts in one call: `python3 <this-skill-dir>/scripts/telemetry.py verdicts '{"<category>":{"confirmed":N,"protected":M}}'`. Skip it when telemetry is off.
- When the user asks to see or share their statistics, run `telemetry.py summary`. To share, run `telemetry.py send`, show the user the exact text it prints, and ask for confirmation (AskUserQuestion). Only then run it with `--open`; the user submits the form themselves. Never send the debug log, and never turn telemetry on for the user: tell them the command instead.

## Updates

- `updates.mode` is off unless the user chose `prompt` or `silent` for themselves: `python3 <this-skill-dir>/scripts/update.py mode prompt|silent|off`. Explain the choice first: `silent` turns on Claude Code's own marketplace auto-update (it edits `~/.claude/settings.json`, after a backup); `prompt` checks in the background and asks before updating. Get the user's OK before you change the mode.
- When the session context says an ocre-jelly update is available, ask the user once with AskUserQuestion. On yes, run `update.py apply`, then tell them to run `/reload-plugins`. On no, don't ask again this session.
- `update.py status` shows the installed and latest commits.
