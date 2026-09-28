---
kind: rules
when: writing a commit message in a gitmoji repo
default: auto
detect_files: .gitmojirc.json, .gitmoji*
description: gitmoji commit prefixes
---
## gitmoji
- The leading emoji (or `:code:`) is the commit type, so it's never decoration. Don't flag it or remove it.
- Use one gitmoji per commit, from the gitmoji.dev list. Don't also add a Conventional Commits type, unless the repo combines both.
