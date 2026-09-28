---
kind: rules
when: writing or editing an architecture decision record (ADR)
default: auto
detect_files: docs/adr, docs/adrs, docs/decisions, doc/adr, adr, decisions
description: ADRs (MADR and Nygard templates)
---
## Architecture decision records
- Follow the template the folder already uses (MADR or Nygard). The Nygard sections are Title, Status, Context, Decision, Consequences.
- The title names the decision, not the problem: "Use QuestPDF for server-side PDFs", not "PDF generation".
- Context states forces and constraints as facts. Decision starts with "We will …". Consequences lists the good and the bad.
- An accepted ADR is immutable. To change a decision, write a new ADR and set the old one to "Superseded by ADR-NNNN". Never rewrite the old decision.
- Number with the folder's scheme (`0013-…md`), and link related ADRs by number.
