# Ubiquitous Language

The one vocabulary for this project: code, docs, tickets and conversation all use it. ocre-jelly treats every **Term** as a protected name and rewrites every alias to avoid into its Term.

Group terms by bounded context, one table per context. Use one row per concept. Separate aliases with commas, and put notes in parentheses: `Line item (too generic)`. Write `—` when there are no aliases. You can add columns (for example `UI label (fr-CA)`), as long as the table keeps a column named `Term` and one named `Aliases to avoid`.

## <Context name>

| Term | Definition | Aliases to avoid |
| ---- | ---------- | ---------------- |
| **<Term>** | <What it is, in one or two sentences.> | <alias>, <alias> (<why>) |

## Relationships

- A **<Term>** has many **<Term>**s

## Flagged ambiguities

- **"<word>"**: <which Term it means in which context>
