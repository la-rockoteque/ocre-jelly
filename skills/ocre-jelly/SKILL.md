---
name: ocre-jelly
description: Find and remove AI writing patterns from prose. Two modes - audit (flag tells, change nothing) and rewrite (minimal repair, facts preserved). Use when the user invokes ocre-jelly or asks to "unslop" prose, "humanize", "make it sound human", "remove AI patterns", says text "sounds like ChatGPT" or "sounds robotic", or wants drafted docs, READMEs, commit bodies or PR descriptions cleaned up before publishing. Also audits and rewrites code comments and doc comments (JSDoc, TSDoc, Javadoc, KDoc, .NET XML docs, docstrings, godoc, rustdoc, Doxygen, PHPDoc, Swift, YARD), including GhostDoc and other generated stubs. Prose only: for code slop use ai-slop-cleaner or ponytail-review.
user-invocable: true
argument-hint: "[audit|rewrite|docs|modules] <text, file or folder>"
---

# Ocre Jelly

Repair concrete AI-writing defects. Leave everything else alone. A no-op beats an uncertain edit.

**Prose authority, per language.** English follows ASD-STE100 Simplified Technical English ([references/ste100.md](references/ste100.md)). French follows [references/ste-fr.md](references/ste-fr.md) (ISO 24495-1 plain language, Français Rationalisé principles, OQLF usage). Read the one for the text's language before every audit or rewrite. It decides what counts as clear prose and how to repair it. Only the preservation rules below outrank it.

**Locales and config.** Settings come from layered JSON: `~/.claude/ocre-jelly.json` (you), `<repo>/.claude/ocre-jelly.json` (committed, team) and `<repo>/.claude/ocre-jelly.local.json` (personal, kept out of git). Later files win. `locales` (for example `["en-CA", "fr-CA"]`) sets the regional spelling, terms and typography for each language. The scanners pick the locale per paragraph, and per file for `fr-CA/…` resource paths. Write new prose in the configured locale. Run `modules.py config show` to see the merged settings, and `config set KEY VALUE [--project|--local]` to change one. The scanners read the same config, so you don't pass `--locale` or `--glossary` when it is set.

## Modes

- `audit` (also: "review", "just flag it", "don't change anything"): report findings, never rewrite.
- `rewrite` (default when no mode word is given): diagnose, then make the smallest repairs.
- `docs [audit] <files>`: the same two passes, on the comments and doc comments of source files. See [Code docs](#code-docs).
- `modules ...`: list, enable, disable or export modules. See [Modules](#modules).
- `commit [message or file]`: check a commit message's shape and prose with `scripts/commitmsg.py`. See [Commits and PRs](#commits-and-prs).
- `feedback [text]`: send a feature request, a bug or a comment to the ocre-jelly author. See [Feedback](#feedback).
- `stats [summary|send|clear]`: the user's opt-in usage statistics. See [Usage statistics](#usage-statistics-opt-in).
- `update [status|mode off|prompt|silent|apply]`: keep ocre-jelly current with its main branch. See [Updates](#updates).
- `config ...`: show or change settings (`show`, `path`, `init`, `set`). Ask whether a change is for the team (`--project`, committed), for this clone only (`--local`) or for every repo (the default user layer).

Input is inline text or a file path the user gives. Only read files the user named. Never go looking for writing samples elsewhere on disk.

## Pass 0: ubiquitous language

1. Find the project root: `git rev-parse --show-toplevel`, or the current directory outside git. Look, case-insensitively, for `docs/ubiquitous-language.md`, then `UBIQUITOUS-LANGUAGE.md` at the root.
2. If you find it, read it. It is a set of markdown tables, grouped by context, each with a **Term** column and an **Aliases to avoid** column (other columns, such as a UI label, are allowed). A Term is a protected technical name (STE100 allows these): never simplify, rename or synonym-cycle it. An alias to avoid is a finding: replace it with its Term. Where an alias maps to several Terms, the **Flagged ambiguities** section decides which one applies. Each `##` section is a bounded context. An alias from one context is a finding only in text about that context, so check the section before you replace anything. Words in a **UI label** column are valid.
3. If you find none, ask the user (AskUserQuestion when available) where to create it:
   - **Committed** (recommended for a shared repo): `docs/ubiquitous-language.md`. Write it, but don't commit it; the user commits it.
   - **Local only**: `UBIQUITOUS-LANGUAGE.md` at the root, plus a `UBIQUITOUS-LANGUAGE.md` line appended to `.git/info/exclude`. That file ignores it for this clone only; don't touch `.gitignore`.
   - **Skip**: run without a glossary this time.
   Build it from [references/UBIQUITOUS-LANGUAGE.template.md](references/UBIQUITOUS-LANGUAGE.template.md). Seed it with the domain terms the input uses, and fill in the aliases when the input uses two words for one concept. Tell the user to review it.

## Pass 1: diagnose

1. Read every sentence yourself first, headings and endings included. Note what each sentence contributes.
2. Then run the scanner for anything you missed. It reads stdin only; pipe the text in:
   ```bash
   python3 <this-skill-dir>/scripts/scan.py < input.txt
   ```
   Write inline text to a scratch file first. Never interpolate user text into a shell command line.
   If the project has a glossary, add `--glossary <path>` to every scan so avoided aliases are flagged.
3. Load [references/patterns.md](references/patterns.md) for the full catalog and the protection rules. Check the text against its language's prose authority too, at full strength for technical text and vocabulary/clarity only for other registers. French has its own AI tells (« Il est important de noter que », « N'hésitez pas à », « Plongeons dans »); the scanner knows them.
4. Classify each candidate as **confirmed** (a real defect in this context) or **protected** (literal, quoted, domain-valid, attributed, or natural for the genre), with a one-line reason. A scanner hit is a candidate, not a verdict. Phrase lists are incomplete, so also catch paraphrased scaffolding by what it does.

## Pass 2: rewrite (rewrite mode only)

- Edit only sentences with confirmed findings. Copy every other sentence byte-for-byte, same order, same paragraphs.
- No confirmed findings: return the source unchanged and say so.
- Write every repaired sentence to STE100: simple words, active voice, one topic, length limits.
- Delete empty framing rather than swapping in new filler. Don't overcorrect into choppy staccato.
- Preserve exactly: numbers, dates, names, quotes, citations, code, URLs, units, version numbers, file paths.
- Never touch code, or tool markers in comments: `ponytail:`, `TODO:`, `FIXME:`, `NOTE:`, `HACK:`, `noqa`, `eslint-disable`, `@ts-`, `type: ignore`. Only the prose after a marker is in scope. The words after `ponytail:` stay as they are, because they name a ceiling and an upgrade path.
- Preserve meaning: negations, conditions, scope ("most", "73%"), uncertainty, attribution, causal strength, register.
- Keep force-bearing "never", "must", "all" in safety, security, legal and technical rules.
- Add nothing: no new claims, advice, anecdotes, personality, certainty or conclusions.
- Don't fact-check or treat missing evidence as an AI tell.

## Validate (rewrite mode only)

1. Re-scan the output with `scan.py`. Any **hard** hit you introduced blocks; fix it.
2. Run `python3 <this-skill-dir>/scripts/scan.py --preserve original.txt < rewritten.txt`. Any `MISSING` token blocks; restore it.
3. Re-read negations, conditions and scope side by side with the original.

## Output

Rewrite: return the cleaned text only. Add a short change list only if the user asks for one.

Audit: one line per finding, in the same shape as ponytail-review and caveman-review, so all three can go in one review:

```
L<line>: <category> "<smallest span>". <fix>.
```

Use `<file>:L<line>:` for several files. Tags are the scanner categories (`throat-clearing`, `ste-length`, `glossary-alias`, ...). After the findings, list protected spans as `L<line>: keep "<span>". <reason>.` End with one verdict line: `clean`, `light touch`, or `heavy rewrite`.

## Code docs

For `docs` mode, and whenever the user asks to review or fix comments or doc comments in source files:

1. Read [references/code-docs.md](references/code-docs.md), and follow the active doc-convention modules (`modules.py rules`).
2. Scan the files the user named. For a folder, list its source files first and confirm the list with the user if it has more than 20 files:
   ```bash
   python3 <this-skill-dir>/scripts/codedoc.py FILE [FILE ...]
   ```
   It scans only the prose of comments, and the user-facing values of string resources (i18n JSON, `.po`, `.resx`, `.properties`, `.strings`, `.xlf`), with placeholders like `{{count}}` masked. Files under `ignore_paths` are skipped. Tags, types, parameter names, XML elements and code examples are masked. It adds the doc checks `echo-doc`, `param-echo`, `returns-echo`, `generated-doc` and `this-method` to the prose checks.
3. Classify each candidate as in Pass 1. In audit mode, report with `<file>:L<line>:` lines.
4. In rewrite mode, edit comment text only, then verify that the code didn't change:
   ```bash
   python3 <this-skill-dir>/scripts/codedoc.py --same-code original.ext rewritten.ext
   ```
   Keep a copy of each original in a scratch directory for this check. Any answer except `code unchanged` blocks: undo the edit.

## Commits and PRs

- Before you run `git commit`, write the message to a scratch file and check it with `python3 <this-skill-dir>/scripts/commitmsg.py <file>`. Fix the hard findings, and weigh the soft ones. The convention (Conventional Commits, gitmoji or none), the limits and the enforcement come from the `commits` config.
- When the repo runs the hook with `commits.enforce: block`, a commit with a hard finding fails. Read the hook's output, fix the message, and commit again. Never bypass it with `--no-verify` unless the user asks.
- To install the hook: `modules.py export git-hook` writes `.git/hooks/commit-msg`. With husky, lefthook or the pre-commit framework, follow `docs/how-to/check-commit-messages.md` in the ocre-jelly repo instead.
- PR and MR descriptions: fill the repo's template (the `pr-template` module), then scan the body with `scan.py` like any prose. To audit an existing PR, fetch the body with the repo's CLI (`gh pr view --json body -q .body`, `glab mr view`), then scan it.

## Feedback

When the user asks for something ocre-jelly doesn't do (a language, a locale, a convention, a doc format, a tool integration, a check), say so plainly first. Name the closest thing that exists, if any. Then offer, with AskUserQuestion, to send a feature request to the author. For `/ocre-jelly feedback`, skip the offer.

1. Draft the text: one line for the request, one for why the user needs it, and any detail they gave. Use the ocre-jelly writing rules.
2. Leave out code, file contents, file paths, repo, product and customer names, people's names and anything secret, unless the user explicitly adds them.
3. Show the exact text, and ask the user to confirm or edit it. Ask whether to add a contact (an email or a name) and whether to include the context line (version, locales, Python version).
4. After they confirm, run:
   ```bash
   python3 <this-skill-dir>/scripts/feedback.py --kind feature|bug|feedback --message "<text>" [--why "<use case>"] [--contact "<contact>"] [--no-context] --open
   ```
   Pass the text as an argument or on stdin, never interpolated unquoted into the shell. The script opens the form in the browser, pre-filled. Tell the user that nothing is sent until they click **Submit** there.
5. Never submit the form yourself, and never send feedback without the user's confirmation. If `feedback.enabled` is false in the config, say that feedback is turned off in this repo.

## Usage statistics (opt-in)

Telemetry is off unless the user turned it on in their user or local config (`telemetry.enabled`); `telemetry.py status` says which. When it is on, the scanners and hooks record counts by themselves. Two things are yours:

- After you classify an audit's candidates, record the verdicts in one call: `python3 <this-skill-dir>/scripts/telemetry.py verdicts '{"<category>":{"confirmed":N,"protected":M}}'`. Skip it when telemetry is off.
- When the user asks to see or share their statistics, run `telemetry.py summary`. To share, run `telemetry.py send`, show the user the exact text it prints, and ask for confirmation (AskUserQuestion). Only then run it with `--open`; the user submits the form themselves. Never send the debug log, and never turn telemetry on for the user: tell them the command instead.

## Updates

- `updates.mode` is off unless the user chose `prompt` or `silent` for themselves: `python3 <this-skill-dir>/scripts/update.py mode prompt|silent|off`. Explain the choice first: `silent` turns on Claude Code's own marketplace auto-update (it edits `~/.claude/settings.json`, after a backup); `prompt` checks in the background and asks before updating. Get the user's OK before you change the mode.
- When the session context says an ocre-jelly update is available, ask the user once with AskUserQuestion. On yes, run `update.py apply`, then tell them to run `/reload-plugins`. On no, don't ask again this session.
- `update.py status` shows the installed and latest commits.

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
