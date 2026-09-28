---
kind: rules
when: writing code review comments or PR review feedback
default: on
description: Conventional Comments labels for review feedback (with Google eng-practices)
---
## Conventional Comments
- Start every review comment with a label: `praise:`, `nitpick:`, `suggestion:`, `issue:`, `todo:`, `question:`, `thought:`, `chore:`, `note:`.
- Add a decoration when it changes what the author must do: `issue (blocking):`, `suggestion (non-blocking):`, `nitpick (non-blocking):`.
- After the label, write one sentence about the subject, then the reason. For `issue` and `suggestion`, give the concrete fix.
- Keep praise specific: say what is good and why. Never "Great job!".
- Comment on the code, not the person. Ask a real question with `question:`, not a rhetorical one.
