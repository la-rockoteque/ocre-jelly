---
kind: rules
when: commits, PRs, or memory files like CLAUDE.md
default: auto
detect: caveman
description: Split with caveman, caveman-commit and caveman-compress
---
## With caveman
- caveman governs chat replies. Never audit a terse chat reply for fragments or missing articles.
- caveman already writes commits and PRs normally. Ocre-jelly governs those.
- caveman-commit (or the repo's commit convention) owns the commit subject line. Ocre-jelly edits only the body.
- caveman-compress compresses memory files (`CLAUDE.md` and similar) on purpose. Don't audit or expand them. Never run caveman-compress on the ubiquitous-language file or on docs written to STE100: compression strips the register they are held to.
