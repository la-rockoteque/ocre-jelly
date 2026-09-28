---
type: llm
weight: 1
---

The response passes when all of these hold:
- The rewrite keeps exactly: "v2.1.0", "$47.3M", "23%", "Q3 2024", "https://api.example.com/v2", "3x faster" (or equivalent wording that keeps "3x" and the comparison with v1).
- It removes or replaces "We are thrilled to announce", "stands as a testament to our commitment to excellence" and "The future looks bright!".
- It adds no new claims, numbers or promises.
Score 1.0 when all hold, 0 when any fact is lost or changed, 0.5 when facts are kept but one slop phrase remains.
