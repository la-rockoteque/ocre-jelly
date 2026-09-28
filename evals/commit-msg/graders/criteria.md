---
type: llm
weight: 1
---

The response passes when all of these hold:
- It notes the subject is not in Conventional Commits form (missing a type such as `feat:` or `fix:`).
- It notes at least two of: past tense instead of imperative ("Added"), the trailing period, the missing blank line between subject and body.
- The proposed message has a subject like `feat(billing): add retry to the CMiC client` (imperative, no period, a type), a blank line, and a body that keeps the reason (1 call in 50, three retries).
Score 1.0 when all hold, 0.5 when the fix is right but the diagnosis misses items, 0 otherwise.
