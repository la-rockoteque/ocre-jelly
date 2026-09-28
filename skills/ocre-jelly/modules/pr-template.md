---
kind: rules
when: writing a pull request or merge request description
default: auto
detect_files: .github/PULL_REQUEST_TEMPLATE.md, .github/pull_request_template.md, PULL_REQUEST_TEMPLATE.md, .gitlab/merge_request_templates, docs/pull_request_template.md
description: Fill the repo's PR/MR template instead of free-form descriptions
---
## PR template
- Read the repo's template and fill in every section. Keep its headings and checkboxes exactly as they are.
- Write "N/A" and a reason for a section that doesn't apply. Never delete the section.
- Tick a checkbox only when it's true for this change.
- Summary: what changed and why, in two or three sentences. Test plan: the commands run and what they showed.
