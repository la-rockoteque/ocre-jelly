# Write a ubiquitous-language glossary

A ubiquitous-language glossary gives each concept of the project one name. The same name appears in code, docs, tickets and conversation. ocre-jelly protects each **Term** from rewording, and it flags each **alias to avoid**.

## 1. Choose where it lives

| Location | When |
|---|---|
| `docs/ubiquitous-language.md` | Recommended. Commit it; the whole team uses it. |
| `UBIQUITOUS-LANGUAGE.md` at the repo root | A root file is fine too. ocre-jelly finds both names in any case. |
| Any other path | Set `"glossary": "path/from/repo/root.md"` in the [configuration](../reference/configuration.md). |

When ocre-jelly needs a glossary and finds none, it asks whether to create it as committed (`docs/ubiquitous-language.md`) or local only (a root file, excluded from git).

## 2. Write one table per bounded context

A bounded context is a part of the domain where each word has one meaning. Give each context a `##` heading and a table:

```markdown
## Requisition lifecycle

| Term | Definition | Aliases to avoid |
| ---- | ---------- | ---------------- |
| **Requisition** | A request from a job site for material, equipment or tools. | Order, Request |
| **Requisition draft** | A saved, not yet submitted requisition. | Saved requisition (ambiguous with Submitted), Pending requisition |
| **Cancelled** | Terminal state set by the requestor before any fulfillment. | Aborted, Void, Deleted |
```

Rules the parser follows:

- The table needs a column whose header contains `Term`, and one whose header contains `avoid`. Other columns are allowed.
- Bold marks the Term. A cell can hold two Terms: `**Backorder** / **Backordered**`.
- Separate aliases with commas. Notes go in parentheses and are ignored: `Line item (too generic)`.
- Write `—` when a Term has no aliases.
- `"login page" is fine` marks an acceptable word. It is not an alias.

The full grammar is in [Glossary format](../reference/glossary-format.md).

## 3. Add a UI label column for translated products

```markdown
| Term | UI label (fr-CA) | Definition | Aliases to avoid |
| ---- | ---------------- | ---------- | ---------------- |
| **Status** | « Statut » | The badge a tracker carries. | State, Phase |
```

Words in a `label` column count as valid. ocre-jelly won't flag « Statut » in a French string, even if another context lists it as an alias.

## 4. Add the closing sections

- **Relationships**: one line per link between Terms ("A **Job** has many **Requisitions**").
- **Flagged ambiguities**: each word that means different things in different contexts, and which Term to use where. ocre-jelly reads this section when an alias maps to several Terms.

## 5. Check it

```bash
python3 $OJ/scan.py --glossary docs/ubiquitous-language.md < docs/some-page.md
```

Each alias use appears as `glossary-alias "basket -> Order"`. These findings are soft. An alias from one context is a defect only in text about that context, so Claude checks the section before it replaces a word.

## Export the glossary to other tools

- **Vale**: `modules.py export vale` writes a substitution rule that maps each alias to its Term.
- **cspell**: `modules.py export cspell` writes a word list of the Terms, so the spell checker stops flagging them.

See [Manage modules and exports](manage-modules-and-exports.md).
