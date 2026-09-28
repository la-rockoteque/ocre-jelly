# Manage modules and exports

A module adds rules for one tool or convention. There are two kinds:

- **rules** modules add their rules to the session. Examples: ponytail, caveman, Conventional Commits, TSDoc, ADRs.
- **export** modules write a file for another tool. Examples: AGENTS.md, Cursor, Vale, cspell.

The generated [Modules](../reference/modules.md) page lists all 39.

## See the state

```bash
python3 $OJ/modules.py list
```

```
on   rules  tsdoc              default:auto (*/tsconfig.json)   TSDoc and TypeDoc conventions for TypeScript
off  rules  ghostdoc           default                          Opinions for GhostDoc-generated .NET XML docs
on   rules  caveman            project                          Split with caveman, caveman-commit and caveman-compress
```

The third column says why: the module's default, an `auto` match (and what matched), or the config layer that set it.

## Turn a module on or off

```bash
python3 $OJ/modules.py enable ghostdoc --project     # for the team (commit .claude/ocre-jelly.json)
python3 $OJ/modules.py disable caveman --local       # for you, in this clone only
python3 $OJ/modules.py enable rfc2119                # for you, in every repo
python3 $OJ/modules.py reset caveman --project       # back to the module's default
```

Or ask Claude: "turn off the caveman integration for this repo." The states are `on`, `off` and `auto`. `auto` means on when the named plugin is installed or a listed file exists at the repo root or one folder down.

## See a module's rules

```bash
python3 $OJ/modules.py rules tsdoc          # one module
python3 $OJ/modules.py rules                # what the session gets: the core and the index
python3 $OJ/modules.py rules --full         # every active module inlined
```

## Export to other tools

```bash
python3 $OJ/modules.py export --dry-run                 # every enabled export module
python3 $OJ/modules.py export agents-md cursor vale     # named ones, enabled or not
```

| Export | Writes | For |
|---|---|---|
| `agents-md` | a marked block in `AGENTS.md` | Codex, Gemini CLI, OpenCode, Copilot |
| `cursor` | `.cursor/rules/ocre-jelly.mdc` | Cursor |
| `windsurf` | `.windsurf/rules/ocre-jelly.md` | Windsurf |
| `cline` | `.clinerules/ocre-jelly.md` | Cline |
| `kiro` | `.kiro/steering/ocre-jelly.md` | Kiro |
| `vale` | `.vale/styles/OcreJelly/UbiquitousLanguage.yml` | Vale (add `OcreJelly` to `BasedOnStyles`) |
| `cspell` | `.cspell/ubiquitous-language.txt` | cspell (add it to `dictionaryDefinitions`) |
| `git-hook` | `.git/hooks/commit-msg` (executable, never committed) | git: checks each commit message. See [Check commit messages](check-commit-messages.md). |

Safety rules:

- An export never overwrites a file that ocre-jelly didn't generate, unless you pass `--force`.
- `agents-md` edits only the block between `<!-- ocre-jelly:start -->` and `<!-- ocre-jelly:end -->`, and it keeps the rest of `AGENTS.md`.
- Every target must be inside the repo.
- Exported rule files contain the full rules. Other agents can't read this machine's plugin folder, so an index line wouldn't work for them.

Run the export again after you change the glossary or the modules. When nothing changed, it reports `same`.

To write your own module, see [Add a module](add-a-module.md).
