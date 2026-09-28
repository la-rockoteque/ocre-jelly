# Configuration

ocre-jelly reads one JSON shape from four layers. Later layers win. Objects (`modules`, `thresholds`, `severity`, `subagents`, `commits`, `feedback`, `telemetry`, `updates`) merge key by key, except that `telemetry.enabled`, `telemetry.debug` and `updates.mode` follow the personal-consent rule (only the user and local layers turn them on); every other value replaces the one before it.

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
| `register` | `"formal"`, `"neutral"`, `"casual"`, or an object | `null` (neutral) | How formal new prose is. One value, or `{"default": …, "<lang>": …, "contexts": {"<context>": value or {"<lang>": value}}}`. Contexts: `docs`, `comments`, `strings`, `commits`, `pr`, `tickets`, `chat`. First match wins: context and language, context, language, `default`, `neutral`. `casual` turns off the fr-CA `anglicism` check; `formal` adds soft `register-informal` findings. AI-tell checks stay on in every register. See [Configure locales](../how-to/configure-locales.md#set-a-register). |
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
| `commits.enforce` | `"off"`, `"warn"`, `"block"` | `"warn"` | The commit-msg hook: print nothing, print and never block, or print and reject the commit on a hard finding. See [Check commit messages](../how-to/check-commit-messages.md). |
| `commits.convention` | `"auto"`, `"conventional"`, `"gitmoji"`, `"none"` | `"auto"` | The subject rule. `auto` follows the `conventional-commits` and `gitmoji` modules. |
| `commits.subject_max` | integer ≥ 1 | `72` | Over this, the subject is a hard finding. |
| `commits.subject_target` | integer ≥ 1 | `50` | Over this, the subject is a soft finding. |
| `commits.body_wrap` | integer ≥ 1 | `72` | Body lines over this are soft findings. URLs, code and trailers are exempt. |
| `feedback.enabled` | boolean | `true` | `false` makes `/ocre-jelly feedback` refuse, and stops Claude from offering it. |
| `feedback.form_url` | https URL | the ocre-jelly form | The form's `viewform` URL. Point it at your team's own form if you like. |
| `feedback.entry` | digits, as a string | `"1018508464"` | The id of the form's paragraph field, from a pre-filled link (`entry.<id>=`). |
| `telemetry.enabled` | boolean | `false` | Record local usage statistics. **Only the user and local layers can turn it on**; the project layer can only turn it off. See [Collect usage statistics](../how-to/collect-usage-statistics.md). |
| `telemetry.debug` | boolean | `false` | Also keep error tracebacks in `~/.claude/ocre-jelly/debug.log`. Same consent rule. |
| `telemetry.retention_days` | integer ≥ 1 | `30` | Older events are dropped. |
| `updates.mode` | `"off"`, `"prompt"`, `"silent"` | `"off"` | Follow the marketplace's main branch at session start. **Only the user and local layers can choose a mode**; the project layer can only force `"off"`. See [Keep ocre-jelly up to date](../how-to/keep-up-to-date.md). |
| `updates.branch` | branch name | `"main"` | The branch that prompt mode compares with the installed commit. |
| `updates.check_hours` | integer ≥ 1 | `24` | Prompt mode runs at most one background check per this many hours. |
| `commits.types` | list of strings | `[]` | Allowed Conventional Commits types. Empty: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert. |

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
  "protected_terms": ["MoFlex", "CMiC", "Brix"],
  "commits": { "enforce": "block", "convention": "conventional" }
}
```

A personal override, `.claude/ocre-jelly.local.json`:

```json
{
  "severity": { "em-dash": "off" },
  "subagents": { "matcher": "writer|doc" },
  "commits": { "enforce": "warn" }
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
