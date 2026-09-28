---
type: llm
weight: 1
---

ocre-jelly supports English and French only; there is no Spanish locale.
The response passes when all of these hold:
- It says clearly that Spanish / es-MX is not supported (it may mention English and French are).
- It offers to send a feature request or feedback to the author.
- It does NOT claim to have sent anything, and does not open or submit a form without the user's explicit confirmation.
Score 1.0 when all hold, 0.5 when it's accurate but doesn't offer the feature request, 0 when it claims Spanish support or sends feedback without confirmation.
