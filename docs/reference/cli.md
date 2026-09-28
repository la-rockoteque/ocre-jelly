# Command line

In Claude Code, you rarely run these yourself: the skill runs them, or you ask Claude. They are plain Python 3 scripts with no dependencies.

In these docs, `$OJ` is the scripts folder:

```bash
OJ=~/.claude/plugins/marketplaces/ocre-jelly/skills/ocre-jelly/scripts   # installed from the marketplace
OJ=/path/to/ocre-jelly/skills/ocre-jelly/scripts                         # from a clone
```

All the scripts read the [configuration](configuration.md) of the repo you run them in. `--no-config` turns that off.

## scan.py: prose

Reads text on stdin and prints findings.

```bash
python3 $OJ/scan.py < README.md
python3 $OJ/scan.py --locale en-CA,fr-CA --json < page.md
python3 $OJ/scan.py --preserve original.md < rewritten.md
```

| Option | Meaning |
|---|---|
| `--locale TAGS` | Comma list, for example `en-CA,fr-CA`. Default: `locales` from the config, else `en,fr`. |
| `--glossary MD` | Glossary file. Default: from the config, else the standard names. |
| `--include-quoted` | Also scan quotes, « guillemets », blockquotes and code. They are masked by default. |
| `--preserve ORIGINAL` | Don't scan: list every number, URL, code span, version and multi-word name from ORIGINAL that is missing from stdin. Exit 1 when one is missing. |
| `--json` | JSON output. |
| `--no-config` | Ignore the config layers. |
| `--list-locales` | List the locale files and their summaries. |
| `--selftest` | Run the self-test. |

Output: `L<line> <severity> <category> '<match>'`, then a count line. Exit 0 when the scan ran, whatever it found.

## codedoc.py: comments, doc comments and string resources

```bash
python3 $OJ/codedoc.py src/api/*.ts
python3 $OJ/codedoc.py --json --all src/**/*.cs
python3 $OJ/codedoc.py --lang .py < snippet.py
python3 $OJ/codedoc.py --same-code original.ts rewritten.ts
```

| Option | Meaning |
|---|---|
| `FILE ...` | Files to scan. The extension picks the parser. See [Audit code docs and UI strings](../how-to/audit-code-docs-and-ui-strings.md). |
| `--lang EXT` | Extension for stdin input, for example `.ts`. |
| `--locale TAGS` | As in `scan.py`. A locale in a resource file's path wins. |
| `--glossary MD` | As in `scan.py`. |
| `--all` | List every long sentence and every alias use, instead of a summary per file. |
| `--same-code ORIGINAL REWRITTEN` | Exit 0 and print `code unchanged` only when the two files differ in comments alone. Exit 1 otherwise. |
| `--json`, `--no-config`, `--selftest` | As in `scan.py`. |

Output: `<file>:L<line> <severity> <category> '<match>'` for several files, `L<line> …` for one.

## commitmsg.py: commit messages

```bash
python3 $OJ/commitmsg.py .git/COMMIT_EDITMSG
git log -1 --format=%B | python3 $OJ/commitmsg.py
python3 $OJ/commitmsg.py --hook "$1"          # inside a commit-msg hook
```

| Option | Meaning |
|---|---|
| `FILE` | The message file. Default: stdin. |
| `--hook` | Run as the commit-msg hook: obey `commits.enforce`, and print to stderr so git shows it. |
| `--enforce off\|warn\|block` | Override `commits.enforce`. Without `--hook` and without this option, the script uses `warn`. |
| `--convention auto\|conventional\|gitmoji\|none` | Override `commits.convention`. |
| `--json`, `--no-config`, `--selftest` | As in `scan.py`. |

Exit 1 only with `block` and a hard finding. See [Check commit messages and PR descriptions](../how-to/check-commit-messages.md).

## feedback.py: feedback to the author

```bash
python3 $OJ/feedback.py --kind feature --message "Support es-MX" --why "Half our docs are Spanish" --open
echo "The glossary parser misses my 5-column tables" | python3 $OJ/feedback.py --kind bug
```

| Option | Meaning |
|---|---|
| `--kind feature\|bug\|feedback` | The first word of the text. Default: `feedback`. |
| `--message TEXT` | The request or comment. Default: stdin. |
| `--why TEXT` | The use case. |
| `--contact TEXT` | Optional: how the author can reach you. |
| `--no-context` | Leave out the line with the ocre-jelly version, the configured locales and the Python version. |
| `--open` | Open the pre-filled form in the browser. Without it, the script only prints the text and the link. |
| `--selftest` | Run the self-test. |

The script never sends anything; the browser talks to the form when you click Submit. Text too long for a link opens the empty form, and prints the text to paste.

## telemetry.py: opt-in usage statistics

| Command | Does |
|---|---|
| `status` | On or off, the retention, and where the files are. |
| `summary [--days N] [--json]` | Aggregated statistics. |
| `verdicts JSON` | Record confirmed/protected counts per category, for example `'{"ste-length":{"confirmed":1,"protected":4}}'`. |
| `send [--open]` | Print the summary as feedback text, and build the pre-filled form link. `--open` opens it; you submit it. |
| `clear` | Delete the usage file and the debug log. |
| `--selftest` | Run the self-test. |

See [Collect usage statistics](../how-to/collect-usage-statistics.md).

## update.py: updates

| Command | Does |
|---|---|
| `status` | Mode, installed commit, latest known commit, last check, native auto-update state. |
| `mode off\|prompt\|silent` | Set your mode (user layer). `silent` also turns Claude Code's marketplace auto-update on; the other modes turn it off. |
| `check [--now]` | Refresh the latest-commit cache. The hook runs it in the background when a check is due. |
| `apply` | `claude plugin marketplace update ocre-jelly`, then `claude plugin update ocre-jelly@ocre-jelly`. |
| `--selftest` | Run the self-test (offline). |

See [Keep ocre-jelly up to date](../how-to/keep-up-to-date.md).

## wizard.py: the setup wizard's back end

| Command | Does |
|---|---|
| `detect` | JSON facts about the repo: languages, locales found in resource paths, glossary, commit tooling, hook manager, ADR folder, PR template, other agents' folders, active modules and the current config. It reads names, not file contents, and skips dependency and build folders (at most 20,000 files). |
| `apply PLAN.json` (or `-` for stdin) | Write a plan: `{"user": {…}, "project": {…}, "local": {…}, "exports": […], "dry_run": false}`. Every layer is validated before anything is written. Objects merge into what each layer already has. |
| `--selftest` | Run the self-test. |

The questions themselves live in `skills/ocre-jelly/references/wizard.md`; `/ocre-jelly setup` asks them.

## modules.py: modules, config and hooks

| Command | Does |
|---|---|
| `list` | Every module, its state and why. |
| `rules [NAME] [--full]` | The text the session receives, one module's rules, or everything inlined. |
| `enable NAME`, `disable NAME`, `reset NAME` | Set a module to `on` or `off`, or remove the setting. Add `--project` or `--local`; the default is the user layer. |
| `config show\|path\|init\|set` | See [Configuration](configuration.md#commands). |
| `export [NAME ...] [--glossary MD] [--dry-run] [--force]` | Write the files of the named export modules, or of every enabled one. |
| `hook session-start\|subagent-start` | Used by the plugin hooks. Reads the hook JSON on stdin. It never fails the session: errors go to stderr. |
| `--selftest` | Run the self-test. |

## gen_docs.py: generated reference pages

```bash
python3 $OJ/gen_docs.py           # rewrite docs/reference/modules.md, locales.md and checks.md
python3 $OJ/gen_docs.py --check   # exit 1 if one of them is out of date
```

## setup.sh

Run it from a clone.

| Command | Does |
|---|---|
| `./setup.sh` | Self-tests, validate, add the marketplace and install the plugin (user scope). Then it asks whether to run the setup wizard, and for which repo (default: the current folder). |
| `./setup.sh --wizard [--repo DIR]` | Same, then start the wizard in DIR without asking. |
| `./setup.sh --no-wizard` | Install only. A non-interactive run (CI, piped input) also skips the wizard. |
| `./setup.sh --scope project` or `--scope local` | Same, for the current repo. |
| `./setup.sh --check` | Every self-test and the docs check. Installs nothing. |
| `./setup.sh --uninstall [--scope …]` | Uninstall the plugin. |
