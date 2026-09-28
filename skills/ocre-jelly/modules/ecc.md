---
kind: rules
when: output of doc-updater, /update-docs or /update-codemaps
default: auto
detect: everything-claude-code
description: everything-claude-code - doc-updater, /update-docs, /update-codemaps
---
## With everything-claude-code
- Output from the `doc-updater` agent, `/update-docs` and `/update-codemaps` counts as prose artifacts, so these rules apply.
- Codemaps are generated structure. Apply the rules to their prose sections only. Never reorder or rename the generated entries.
