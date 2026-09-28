# Collect usage statistics

ocre-jelly can keep statistics about how you use it, on your machine only. They show which checks fire, which ones Claude protects as false positives, how fast the tools run, and which errors happen. You can share a summary with the author to help improve the tool.

It is **off by default**, and only you can turn it on.

## Turn it on

For yourself, in every repo:

```bash
python3 $OJ/modules.py config set telemetry '{"enabled":true}'
```

For yourself, in one clone only:

```bash
python3 $OJ/modules.py config set telemetry '{"enabled":true}' --local
```

A committed project config can't turn it on for teammates: consent is personal. A project can turn it off for everyone, with `"telemetry": {"enabled": false}` in `.claude/ocre-jelly.json`.

Check the state at any time:

```bash
python3 $OJ/telemetry.py status
```

## What is recorded

One line per run in `~/.claude/ocre-jelly/usage.jsonl`:

| Recorded | Example |
|---|---|
| The tool and its duration | `scan`, 10 ms |
| Finding counts per category and severity | `throat-clearing: 1`, `hard: 2` |
| Claude's verdicts per category | `ste-length`: 1 confirmed, 4 protected |
| File types and counts | `.ts: 3` |
| Locales | `en-CA` |
| Hook size | 177 words, 10 modules active |
| Commit checks | convention, enforcement, blocked or not |
| Rewrite gates | `--preserve` and `--same-code`: passed or failed, and how many facts went missing |
| Error types | `ValueError` |

**Never recorded:** the text, the matches, file names, folders, repo names, people, or anything you typed.

Events older than `telemetry.retention_days` (30 by default) are dropped. The file never grows past about 1 MB.

## Debug mode

```bash
python3 $OJ/modules.py config set telemetry '{"enabled":true,"debug":true}'
```

Debug mode also writes full error tracebacks to `~/.claude/ocre-jelly/debug.log`. Tracebacks contain file paths, so this log stays on your machine: `send` never includes it. Attach parts of it to a bug report yourself only if you want to.

## See your statistics

```bash
python3 $OJ/telemetry.py summary
python3 $OJ/telemetry.py summary --days 7 --json
```

Or ask Claude: "show my ocre-jelly statistics."

## Share them with the author

```bash
python3 $OJ/telemetry.py send          # prints the exact text to share
python3 $OJ/telemetry.py send --open   # opens the feedback form, pre-filled
```

From Claude Code, ask "share my ocre-jelly statistics". Claude shows you the text, asks you to confirm, then opens the form.

What is shared: the aggregated summary only (totals, medians, top categories, verdict ratios), never the raw events and never the debug log. Nothing is sent until you click **Submit** in the form. The form comes from the `feedback` config, so a team can route it to its own form, or turn it off.

## Delete everything

```bash
python3 $OJ/telemetry.py clear
```

This deletes the usage file and the debug log. To stop recording, set `"enabled": false`.
