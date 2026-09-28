---
type: llm
weight: 1
---

The response passes when all of these hold:
- It flags "Here's the thing" (throat-clearing), the "isn't just … It's a revolution" contrast, the ", showcasing …" tail, and "Let that sink in".
- It flags at least one of "In order to" or "utilize" as wordy.
- It does NOT present a rewritten paragraph as the answer (an optional one-line fix per finding is fine).
- It does not flag the fact "1,200 invoices per minute" as a problem.
Score 1.0 when all hold, 0.5 when it misses one or two AI patterns but meets the rest, 0 otherwise.
