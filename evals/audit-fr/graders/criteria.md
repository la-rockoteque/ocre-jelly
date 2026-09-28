---
type: llm
weight: 1
---

The response passes when all of these hold:
- It flags « Il est important de noter que » and « n'hésitez pas à ».
- It flags « joue un rôle clé » or « afin de » (at least one).
- It flags « e-mail » and suggests « courriel » (Québec / OQLF usage).
- It answers about French text (the answer itself may be in French or English).
Score 1.0 when all hold, 0.5 when exactly one item is missing, 0 otherwise.
