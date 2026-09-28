---
kind: rules
when: writing or reviewing a commit message
default: auto
detect_files: commitlint.config.*, .commitlintrc*, .czrc, .cz.toml, .cz.json, .releaserc*, release-please-config.json, .versionrc*
description: Conventional Commits (with Angular types, commitlint and the 50/72 rule)
---
## Conventional Commits
- Subject: `type(scope)!: summary`. Types: feat, fix, docs, refactor, perf, test, build, ci, chore, revert, or the ones in the repo's commitlint config. When caveman-commit is active, it owns the subject line.
- Write the summary in the imperative, lowercase after the colon (unless the repo capitalizes), with no period. Keep it to 50 characters or fewer, and never more than 72.
- Leave a blank line after the subject. Wrap the body at 72 characters. The body says why, not what: the diff already shows what.
- Breaking changes: add `!` after the type or scope, and a `BREAKING CHANGE: <what breaks and how to migrate>` footer.
- Footers go last, one per line, as `Token: value` (`Refs: #42`, `Co-authored-by: …`). Never put footers in the body.
- The body follows the prose rules (STE100, no slop). The subject follows this convention, not STE sentence rules.
- Before you commit, check the message: `commitmsg.py <file>` (or stdin). The repo may run it as a commit-msg hook; with `commits.enforce: block`, fix every hard finding.
