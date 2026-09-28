---
kind: rules
when: editing CHANGELOG.md or writing release notes
default: auto
detect_files: CHANGELOG.md, CHANGELOG, HISTORY.md, changelog.md
description: Keep a Changelog format
---
## Keep a Changelog
- Keep an `## [Unreleased]` section at the top. A release is `## [1.2.0] - 2026-09-28` (ISO date).
- Use only these groups, in this order: Added, Changed, Deprecated, Removed, Fixed, Security.
- Each entry is one line for a user of the software, not a developer. Say what changed for them; don't paste commit subjects.
- Put breaking changes first in their group, and say how to migrate.
- Keep the compare links at the bottom up to date.
