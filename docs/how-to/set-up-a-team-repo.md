# Set up a team repo

This guide makes ocre-jelly part of a repo, so every teammate gets the same plugin and the same settings.

## 1. Declare the plugin in the repo

In the repo root, run:

```bash
claude plugin marketplace add https://git.nexapptech.com/vbernier/ocre-jelly.git --scope project
claude plugin install ocre-jelly@ocre-jelly --scope project
```

Both commands write `.claude/settings.json`. Commit that file. When a teammate opens the repo and trusts the folder, Claude Code offers to install the plugin.

Use `--scope local` instead if you want the plugin in this clone only, without changing the shared settings.

## 2. Create the shared config

```bash
OJ=~/.claude/plugins/marketplaces/ocre-jelly/skills/ocre-jelly/scripts
python3 $OJ/modules.py config init --project
```

This writes `.claude/ocre-jelly.json` with a starter shape. Then set what the team agrees on, for example:

```bash
python3 $OJ/modules.py config set locales '["en-CA","fr-CA"]' --project
python3 $OJ/modules.py config set protected_terms '["MoFlex","CMiC"]' --project
python3 $OJ/modules.py enable conventional-commits --project
```

You can also edit the file by hand. [Configuration](../reference/configuration.md) lists every key. For editor completion, add the schema reference at the top of the file:

```json
{ "$schema": "https://git.nexapptech.com/vbernier/ocre-jelly/raw/branch/main/ocre-jelly.schema.json" }
```

Check the raw-file URL format on your git server: Gitea uses `/raw/branch/main/`, and GitLab uses `/-/raw/main/`.

## 3. Add a glossary (recommended)

Create `docs/ubiquitous-language.md`, or ask Claude to create it when it first needs one. See [Write a ubiquitous-language glossary](write-a-glossary.md).

## 4. Commit

```bash
git add .claude/settings.json .claude/ocre-jelly.json docs/ubiquitous-language.md
git commit -m "chore: set up ocre-jelly for the team"
```

Don't commit `.claude/ocre-jelly.local.json`. `config set --local` adds it to `.git/info/exclude` for you.

## 5. Export the rules to other agents (optional)

If some teammates use Cursor, Windsurf, Cline, Kiro, Codex or Gemini CLI, export the same rules into the files those tools read:

```bash
python3 $OJ/modules.py export agents-md cursor --dry-run
python3 $OJ/modules.py export agents-md cursor
```

See [Manage modules and exports](manage-modules-and-exports.md).

## Personal overrides

A teammate who wants different settings uses the local layer, which stays out of git:

```bash
python3 $OJ/modules.py config set severity '{"em-dash":"off"}' --local
```
