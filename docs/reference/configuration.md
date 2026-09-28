# Configuration

ocre-jelly reads one JSON shape from four layers. Later layers win. Objects (`modules`, `thresholds`, `severity`, `subagents`) merge key by key; every other value replaces the one before it.

| # | Layer | File | Commit it? | Written by |
|---|---|---|---|---|
| 1 | defaults | built into `scripts/config.py` | | |
| 2 | user | `~/.claude/ocre-jelly.json` (or `$CLAUDE_CONFIG_DIR/ocre-jelly.json`) | no | `config set …`, `enable …` |
| 3 | project | `<repo>/.claude/ocre-jelly.json` | yes, it's shared with the team | `… --project` |
| 4 | local | `<repo>/.claude/ocre-jelly.local.json` | no; added to `.git/info/exclude` | `… --local` |

The repo is the nearest parent folder that contains `.git`. The JSON Schema is `ocre-jelly.schema.json` at the root of the ocre-jelly repo.

## Keys

| Key | Type | Default | Meaning |
|---|---|---|---|
| `$schema` | string | — | Optional. Points editors at the schema. Ignored by ocre-jelly. |
| `enabled` | boolean | `true` | `false` stops the session and subagent hooks from injecting rules. The skill still works when you call it. |
| `locales` | list of tags | `[]` | For example `["en-CA", "fr-CA"]`. Each tag is `ll` or `ll-RR`. Empty: detect English and French, with no regional checks. See [Locales](locales.md). |
| `glossary` | string or `null` | `null` | Path of the ubiquitous-language file, from the repo root. It must stay inside the repo. `null`: `docs/ubiquitous-language.md`, then `UBIQUITOUS-LANGUAGE.md` (in any case). |
| `modules` | object | `{}` | Module name to `on`, `off` or `auto`. A missing name uses the module's default. See [Modules](modules.md). |
| `inject` | `"index"` or `"full"` | `"index"` | `index`: one line per active module, and the agent reads the file on demand. `full`: inline every active module. |
| `subagents.inject` | boolean | `true` | Inject the rules into subagents (SubagentStart). |
| `subagents.matcher` | string or `null` | `null` | Regex on the subagent type, case-insensitive. Only matching subagents get the rules. A bad regex injects into all of them. |
| `thresholds.sentence_words` | integer ≥ 1 | `25` | `ste-length` limit. |
| `thresholds.instruction_words` | integer ≥ 1 | `20` | Limit for procedural sentences, judged by the agent. |
| `thresholds.em_dash_per_paragraph` | integer ≥ 1 | `3` | `em-dash` fires at this count in one paragraph. |
| `thresholds.length_hits_per_file` | integer ≥ 1 | `3` | Long sentences listed per file by `codedoc.py` before the summary line. |
| `severity` | object | `{}` | Category to `hard`, `soft` or `off`. See [Checks](checks.md). |
| `ignore_paths` | list of globs | `[]` | Paths from the repo root that `codedoc.py` skips. `*` also crosses `/`. |
| `protected_terms` | list of strings | `[]` | Words never flagged as aliases and never respelled. Glossary Terms are protected already. |

## Environment variables

They beat every file.

| Variable | Effect |
|---|---|
| `OCRE_JELLY=off` | Same as `"enabled": false`. |
| `OCRE_JELLY_SUBAGENT_MATCHER=<regex>` | Same as `subagents.matcher`. |
| `CLAUDE_CONFIG_DIR` | Moves the user layer (and the installed-plugins registry) with Claude Code's own setting. |

## Validation

- `config set` validates the whole layer before it saves, and refuses invalid values.
- A layer file with any invalid value is ignored as a whole, with a message on stderr. The other layers still apply. ocre-jelly never half-applies a layer.
- Unknown top-level keys are errors, so a typo doesn't pass silently.

## Examples

A bilingual team repo, `.claude/ocre-jelly.json`:

```json
{
  "locales": ["en-CA", "fr-CA"],
  "glossary": "docs/ubiquitous-language.md",
  "modules": { "conventional-commits": "on", "ghostdoc": "on" },
  "ignore_paths": ["**/*.generated.cs", "moship-web/src/api/generated/*"],
  "protected_terms": ["MoFlex", "CMiC", "Brix"]
}
```

A personal override, `.claude/ocre-jelly.local.json`:

```json
{
  "severity": { "em-dash": "off" },
  "subagents": { "matcher": "writer|doc" }
}
```

A user default for every repo, `~/.claude/ocre-jelly.json`:

```json
{ "locales": ["en-CA"], "modules": { "caveman": "off" } }
```

## Commands

```bash
modules.py config show                      # the merged result; stderr says which layer set each key
modules.py config path                      # the four files and whether each one exists
modules.py config init [--project|--local]  # write a starter file (refuses to overwrite)
modules.py config set KEY VALUE [--project|--local]
```

`KEY` can be dotted (`thresholds.sentence_words`). `VALUE` is JSON (`30`, `true`, `'["en-CA"]'`, `'{"em-dash":"off"}'`); a bare word is a string (`config set inject full`).
