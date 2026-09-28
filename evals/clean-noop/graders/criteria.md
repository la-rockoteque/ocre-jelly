---
type: llm
weight: 1
---

The text is already clean, plain technical prose.
The response passes when it says there is nothing (or almost nothing) to fix and returns the text unchanged, or changes at most one word without changing any meaning.
Score 0 when it rewrites several sentences, adds content, or invents problems (for example calling the imperative sentences robotic). Score 1.0 for a no-op answer.
