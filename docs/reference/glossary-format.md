# Glossary format

This page describes exactly what the parser in `scripts/scan.py` (`glossary_rows`, `load_glossary`) reads. To write a glossary step by step, see [Write a ubiquitous-language glossary](../how-to/write-a-glossary.md).

## Where it looks

1. The `glossary` path from the [configuration](configuration.md), if set. It must be inside the repo.
2. `docs/ubiquitous-language.md`, in any case.
3. `ubiquitous-language.md` at the repo root, in any case (so `UBIQUITOUS-LANGUAGE.md` works).

## Tables

- A table starts at a line that begins with `|` and ends at the first line that doesn't.
- Its first row is the header. The parser needs a header cell that contains `term` and one that contains `avoid`, in any case, at any position. Tables without both are skipped. That lets you keep other tables (for example a `Term | Definition` table of UI labels) in the same file.
- A header cell that contains `label` marks a label column. Its values are valid words.
- The separator row (`|---|---|`) is skipped.
- The avoid column is read from the end of the row. A `|` inside an earlier cell (for example in inline code) doesn't shift it.

## Term cells

| Cell | Terms read |
|---|---|
| `**Requisition**` | Requisition |
| `**Backorder** / **Backordered**` | Backorder, Backordered |
| `**Assumption** (Hypothèse)` | Assumption |
| `Requisition` (no bold) | Requisition |

## Alias cells

| Cell | Aliases read | Why |
|---|---|---|
| `Order, Request` | Order, Request | Commas separate aliases. `;`, ` / ` and ` or ` do too. |
| `Line item (too generic)` | Line item | Parenthesized notes are dropped. |
| `` `#1042` _(the former form)_ `` | #1042 | Italic notes are dropped, and backticks are stripped. |
| `"Supervisor", "Approver"` | Supervisor, Approver | Only the quoted words are read. |
| `"login page" is fine, not "portal"` | portal | A segment that says `is fine`, `is ok` or `allowed` is acceptable, not an alias. |
| `« Retirer »` | Retirer | Guillemets work like quotes. |
| `—` | (none) | No aliases. |

## How aliases become findings

- An alias that is also a Term, or a word in a label column, is dropped. It is valid in its own context.
- An alias listed under several Terms maps to all of them: `transport -> VehicleLender | Shipment`. The **Flagged ambiguities** section decides which one applies.
- `protected_terms` from the config removes aliases too.
- Matching is case-insensitive and whole-word. Every hit is a soft `glossary-alias` finding.
- `codedoc.py` folds repeated hits of one alias in one file into a single line: `ligne -> Item (x99, first at L12)`.

## Other sections

The parser reads only tables. Headings, **Relationships**, **Business rules**, **Example dialogue** and **Flagged ambiguities** are for people and for Claude, which reads the whole file before it replaces an alias.
