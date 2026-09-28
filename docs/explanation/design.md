# Design

This page explains how ocre-jelly is built, and the trade-offs behind each choice.

## Two parts: always-on rules and an on-demand skill

- **Hooks** (`SessionStart` and `SubagentStart`) inject a short set of rules into every session and subagent. They shape the prose the agent writes from the start: docs, commits, PRs, comments.
- **The skill** (`/ocre-jelly …`) audits and rewrites existing text. It runs the scanners, and it follows the full contract in `SKILL.md`.

Without the hooks, the agent would clean text only when asked. Without the skill, there would be no way to check the text or prove that facts survived.

## Progressive disclosure

Every token injected at session start costs context in every turn. ocre-jelly keeps the injection small:

1. A core of about 90 words: the rules that apply to all prose.
2. One locale line, when locales are set.
3. One index line per active module: its name and its `when:` trigger.

The agent reads a module's full rules only when the work matches the trigger. In a repo with ten active modules, a session receives about 180 words instead of about 700. `inject: always` (per module) and `"inject": "full"` (per config) switch back to inlining for rules that must be in force on every turn.

Exports to other agents always inline everything, because those tools can't read this machine's plugin folder.

## Modules

Each integration or convention is one markdown file. Adding support for a tool means adding a file, not changing code. A module:

- has a state (`on`, `off` or `auto`), set per user, per repo or per clone;
- turns itself on (`auto`) from an installed plugin or a file in the repo. Only shallow globs are allowed, so session start stays fast in large repos;
- is either rules (text for the agent) or an export (a file written for another tool).

Opinionated modules (GhostDoc, doc generators, user stories, standard-readme, RFC 2119, Diátaxis) are `off` by default. A team opts in.

## Config layers

The layers copy Claude Code's own `settings.json` / `settings.local.json` split: user, then committed project, then personal local. A team agrees on the committed file. A person overrides locally without touching git. Invalid layers are ignored whole, never half-applied, so a typo can't produce a strange mix.

## Sharing work with other tools

ocre-jelly governs prose. It hands everything else to the tool that owns it:

| Tool | Owns | ocre-jelly's part |
|---|---|---|
| ponytail | What code to write | The words around the code. `ponytail:` comments stay verbatim. |
| caveman | Chat replies (terse on purpose) | Commits, PRs and docs, which caveman already writes normally. Never audits a terse chat reply. |
| caveman-commit, commitlint | The commit subject line | The commit body. |
| caveman-compress | Compressed memory files | Doesn't audit or expand them, and keeps compression away from the glossary and STE docs. |
| ai-slop-cleaner (OMC), ponytail-review | Code slop | Prose slop. Never rewrites code to fix prose. |

Each of these rules is a module, so a team that doesn't use the tool can turn the rule off.

## Security posture

The unslop project that inspired ocre-jelly harvested chat transcripts, opened pull requests and fetched from the network. ocre-jelly does none of that:

- Standard-library Python only. The scanners, hooks and config make no network calls and run no programs.
- One exception, opt-in and personal: in `prompt` mode, `update.py` runs `git ls-remote` in the background (read-only, no credential prompts, 10 s timeout), and `update.py apply` runs the claude CLI's own update commands after you say yes. `silent` mode only switches on Claude Code's native marketplace auto-update.
- The scanners read stdin, the files you name, the glossary and the config layers. Nothing else.
- Writes go only to the config layers and to export targets. Every export target must resolve inside the repo, and the glossary path must too.
- Exports never overwrite a file that ocre-jelly didn't generate, without `--force`.
- Every regex is bounded. The self-tests run 200 KB worst cases.
- The hooks catch every error. A broken module or config can't break session start.
- Usage statistics are off by default, local only, and counts only (never text, matches, paths or repo names). Only the person can turn them on; a committed config can only turn them off. Sharing sends an aggregated summary, shown in full first, through the form the person submits.
- `--same-code` guards doc rewrites with two independent checks, so one parser mistake can't hide a code change.

## Generated reference

The pages that list modules, locales and checks are generated from the code (`gen_docs.py`), and `setup.sh --check` fails when they are stale. The lists can't drift from what the tool does.
