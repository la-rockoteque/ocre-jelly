---
type: llm
weight: 1
---

The response passes when all of these hold:
- It flags the first doc comment: the summary only restates the name ("Gets the user name."), and "@param userId The user id." and "@returns The result." add nothing.
- It does NOT flag the second doc comment (retry) as a problem; it may praise it or leave it out.
- It does not propose changing the code itself.
Score 1.0 when all hold, 0.5 when the first comment is only partly flagged, 0 when the retry comment is reported as defective.
