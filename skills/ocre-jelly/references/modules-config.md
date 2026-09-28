# Modules, locales and config

## Locales and config

Settings come from layered JSON: `~/.claude/ocre-jelly.json` (you), `<repo>/.claude/ocre-jelly.json` (committed, team) and `<repo>/.claude/ocre-jelly.local.json` (personal, kept out of git). Later files win. `locales` (for example `["en-CA", "fr-CA"]`) sets the regional spelling, terms and typography for each language. The scanners pick the locale per paragraph, and per file for `fr-CA/…` resource paths. Write new prose in the configured locale. Run `modules.py config show` to see the merged settings, and `config set KEY VALUE [--project|--local]` to change one. The scanners read the same config, so you don't pass `--locale` or `--glossary` when it is set.

Ask whether a config change is for the team (`--project`, committed), for this clone only (`--local`) or for every repo (the default user layer).

## Modules

Compatibility with other tools lives in `modules/`, one file per tool, and each can be switched on or off:

```bash
python3 <this-skill-dir>/scripts/modules.py list                  # state and why
python3 <this-skill-dir>/scripts/modules.py enable vale [--project]
python3 <this-skill-dir>/scripts/modules.py disable caveman [--project]
python3 <this-skill-dir>/scripts/modules.py reset caveman [--project]   # back to the default
python3 <this-skill-dir>/scripts/modules.py export [NAME ...] [--dry-run]
```

- **rules** modules (ponytail, caveman, omc, ecc, atlassian, and the doc-comment conventions) use progressive disclosure. While a module is on, the session and subagent hooks inject only one index line with its `when:` trigger. Before work that matches the trigger, read `modules/<name>.md` (or run `modules.py rules <name>`). A module with `inject: always` is inlined instead. `auto` means on when the related plugin or project file is found. When the hooks are off, run `modules.py rules` for the same index.
- **export** modules (agents-md, cursor, windsurf, cline, kiro, vale, cspell) write files for other tools into the project. They never overwrite a file that ocre-jelly didn't generate unless `--force` is set. Run `export` only when the user asks, and show the `--dry-run` output first.
- `--project` writes `<repo>/.claude/ocre-jelly.json`, which overrides the user file `~/.claude/ocre-jelly.json`.
- To add a module, add `modules/<name>.md` with `kind`, `default`, `detect` or `detect_files`, a `when:` trigger for rules modules, and a body. An export module also sets `target`, and can have an optional `<name>.py` with `render(ctx)`. `modules.py --selftest` checks every module.

When the user says "enable/disable <module>" or "turn off the caveman integration", run the matching command.
