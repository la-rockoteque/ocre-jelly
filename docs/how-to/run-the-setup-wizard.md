# Run the setup wizard

The wizard configures ocre-jelly for a repo in one guided pass. It takes two or three minutes.

```
/ocre-jelly setup
```

You can also say "configure ocre-jelly" or "run the ocre-jelly wizard". When you install from a clone, `./setup.sh` offers to start it for you: it asks which repo to configure, then opens Claude Code there with the wizard. `./setup.sh --wizard --repo DIR` skips the questions.

## What it does

1. **Looks at the repo.** It reads file names, not contents. It finds languages, locale folders (`locales/fr-CA/`, `Strings.fr.resx`), the glossary, commit tooling (commitlint, commitizen, release tools), the hook manager (git, husky, lefthook, pre-commit), the ADR folder, the PR template, other agents' rule folders, and any existing ocre-jelly config.
2. **Asks five short rounds of questions,** with answers proposed from what it found:

   | Round | Questions |
   |---|---|
   | Scope and language | Where team settings live (project, local or user), locales, glossary |
   | Checks | Strictness (standard, relaxed or strict), opinionated doc modules, opt-in conventions, session injection |
   | Commits | Convention, enforcement (warn or block), installing the commit-msg hook |
   | Other tools | Exports (AGENTS.md, Cursor, Windsurf, Cline, Kiro, Vale, cspell), sibling integrations |
   | Personal | Updates, usage statistics, feedback form |

3. **Shows the plan,** file by file. You apply it, dry-run it, change it, or cancel.
4. **Writes it in one step.** Every file is validated first, so a bad answer writes nothing. Then it runs the chosen exports and creates the glossary if you asked for one.
5. **Tells you what to commit,** and what stays local.

## Where answers go

- **Team settings** go where you chose in round 1. The recommended place is `.claude/ocre-jelly.json`, which you commit.
- **Personal settings** (updates, usage statistics) always go to your user file, `~/.claude/ocre-jelly.json`. A committed file can't turn those on for teammates.
- The wizard updates existing files and keeps the keys you don't change.

## Run it again

Run `/ocre-jelly setup` any time: after you add a locale, adopt Conventional Commits, or start using Cursor. It starts from the current config, so you only change what's new.

## Without the wizard

Every answer maps to a config key. See [Configuration](../reference/configuration.md), and set keys one by one with `modules.py config set`. To script a setup, write a plan file and run `wizard.py apply plan.json`. See [Command line](../reference/cli.md#wizardpy-the-setup-wizards-back-end).
