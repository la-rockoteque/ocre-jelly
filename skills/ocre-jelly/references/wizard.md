# /ocre-jelly setup: the configuration wizard

Walk the user through the full configuration in five short rounds of questions, then write it all in one step. Use AskUserQuestion for every round: at most four questions per call, and the recommended option first, labelled "(Recommended)". Propose answers from what `detect` found, so the user mostly confirms.

## 0. Detect

```bash
python3 <this-skill-dir>/scripts/wizard.py detect
```

Tell the user, in three or four lines, what you found: languages, locales in resource paths, the glossary, commit tooling and hook manager, ADR folder, PR template, other agents' rule folders, and any existing ocre-jelly config (`config_files`, `config_set_by`). If a config exists, say that the wizard updates it and keeps other keys.

## 1. Scope and language

1. **Where should team settings live?** Options:
   - Project, committed, shared with the team (Recommended in a repo with teammates).
   - Local, this clone only.
   - User, all my repos.

   Personal settings (updates, statistics) always go to the user layer, whatever the answer. Say so.
2. **Locales.** Offer the combination that `locales_found` suggests first (for example "en-CA + fr-CA (found in moship-web/src/i18n/locales)"), then single common choices (en-US, en-GB, en-CA, fr-CA, fr-FR), and "None: detect English and French only". Accept Other for any combination. Valid tags come from `scan.py --list-locales`.
3. **Register** per language: "Neutral for everything (Recommended)", "Casual French (team chat, fr-CA)", "Formal", or Other for a map like `{"fr": "casual", "en": "neutral"}`. Ask this only when the repo writes messages, posts or customer text; docs-only repos keep neutral.
4. **Glossary.** If `glossary` was found: "Use docs/ubiquitous-language.md (Recommended)" or "Skip". If none: "Create docs/ubiquitous-language.md, committed", "Create UBIQUITOUS-LANGUAGE.md, local only", or "Skip for now".

## 2. Checks

1. **How strict?**
   - Standard, the defaults (Recommended).
   - Relaxed: `severity` `{"em-dash": "off", "ste-length": "off", "locale-spelling": "off"}`, and `thresholds.sentence_words` 30.
   - Strict: `severity` `{"ste-length": "hard", "ste-wordy": "hard", "promotional": "hard"}`.
2. **Opinionated doc-comment modules** (multiSelect): `ghostdoc` (offer it first when C# or `.NET` was found), `doc-generators`. Leaving both unticked keeps them off.
3. **Opt-in writing conventions** (multiSelect): `user-stories`, `standard-readme`, `rfc2119`, `diataxis`. Mention which `auto` modules are already on (`modules_active`) and don't ask about those.
4. **Session injection:**
   - Index, one line per module (Recommended).
   - Index, with subagents limited to doc writers (`subagents.matcher` "writer|doc").
   - Full, every module inlined.

## 3. Commits

Skip this round when the user says the repo has no commits they care about.

1. **Commit convention:**
   - Auto: follow the modules (Recommended). Say what auto resolves to here: conventional when `commit_tooling` has a commitlint, commitizen or release config; otherwise none.
   - Conventional Commits.
   - gitmoji.
   - None.
2. **Enforcement:** "Warn, never block (Recommended)", "Block on hard findings", "Off".
3. **Install the commit-msg hook**, matched to `hook_manager`:
   - `git`: "Install .git/hooks/commit-msg (Recommended)" (the `git-hook` export).
   - `husky` or `lefthook`: "Show me the line to add" (from `docs/how-to/check-commit-messages.md`).
   - `pre-commit`: "Show me the .pre-commit-config.yaml entry".
   - Always also offer "Not now".
   - If `git_worktree` is true, say that the hook must be installed from the main clone.

## 4. Other tools

1. **Exports** (multiSelect): `agents-md`, `cursor`, `windsurf`, `cline`, `kiro`, `vale`, `cspell`. Tick the ones that `other_agents` found, plus `vale` and `cspell` when their config exists. Only offer `vale` and `cspell` when a glossary exists or will be created.
2. **Sibling integrations:** only if `modules_active` includes ponytail, caveman, omc, ecc or atlassian. Ask "Keep the integrations for the tools you have installed? (Recommended: keep)". Offer to turn one off only if the user wants that.

## 5. Personal (always the user layer)

1. **Updates:** "Ask me when main has a new version" (prompt), "Update silently" (silent: Claude Code's auto-update), or "Off". Say that silent edits `~/.claude/settings.json`, after a backup.
2. **Usage statistics:** "Off (Recommended)", "On, local counts only", or "On, with the local debug log". Say what is and isn't recorded, in one line.
3. **Feedback:** "Keep the ocre-jelly form (Recommended)", "Use our own form" (then ask for its viewform URL and the entry id; see `docs/how-to/send-feedback.md`), or "Turn feedback off". Team forms go to the team layer; turning it off for yourself goes to the user layer.

## 6. Review and write

Build the plan. Put team answers in the chosen layer; put updates, telemetry and personal feedback choices in `user`:

```json
{
  "project": {"locales": ["en-CA", "fr-CA"], "modules": {"ghostdoc": "on"}, "severity": {},
              "commits": {"convention": "auto", "enforce": "warn"}},
  "local": {},
  "user": {"updates": {"mode": "prompt"}, "telemetry": {"enabled": false}},
  "exports": ["git-hook", "agents-md"]
}
```

Leave out keys the user left at the default, so the files stay small. Show the plan as a short bullet list per file, not as raw JSON, and ask a last question:
- Apply (Recommended).
- Dry run first.
- Change something.
- Cancel.

Then write the plan to a scratch file and run:

```bash
python3 <this-skill-dir>/scripts/wizard.py apply <plan.json>
```

`apply` validates every layer before it writes anything. If it answers `nothing written: …`, fix that answer with the user and run it again.

If the user chose to create a glossary, create it now, following **Pass 0** in SKILL.md.

## 7. Finish

- Run `modules.py config show` and `modules.py list`, and summarize the result in a few lines.
- List the files to commit (`.claude/ocre-jelly.json`, the glossary, and exported files like `AGENTS.md` or `.cursor/rules/ocre-jelly.mdc`), and the ones that stay local (`.claude/ocre-jelly.local.json`, `.git/hooks/commit-msg`).
- For husky, lefthook or pre-commit, print the exact snippet to add.
- Say that the new settings apply from the next session. Run `/reload-plugins` to reload now.
