# Add a locale

Locales are Python files in `skills/ocre-jelly/locales/`. A language file holds the patterns for that language. A regional file extends it.

## A regional variant (common case)

Create `skills/ocre-jelly/locales/en-NZ.py`:

```python
"""New Zealand English: British spelling, -ise."""
PARENT = "en"
SUMMARY = "en-NZ: colour, centre, organise, travelled, grey."
SPELLING_STYLE = {"our": "gb", "re": "gb", "ise": "gb", "ll": "gb", "misc": "gb"}
PREFER = {r"\bzip ?codes?\b": "postcode"}
```

| Name | Meaning |
|---|---|
| `PARENT` | The language tag it extends (`en`, `fr`). |
| `SUMMARY` | One line, starting with the tag. The session's locale line uses it. |
| `SPELLING_STYLE` | English only: for each class (`our`, `re`, `ise`, `ll`, `misc`), `us` or `gb`. Leave a class out when usage is mixed. |
| `PREFER` | Regex to preferred term. Each match becomes a soft `locale-term` finding with the suggestion. |
| `SOFT`, `HARD` | Extra category to regex patterns, like `anglicism` in `fr-CA.py` or `typography` in `fr-FR.py`. |

## A new language

Create `skills/ocre-jelly/locales/es.py` with:

- `SUMMARY` and `AUTHORITY` (the path of the prose-rules file, for example `references/ste-es.md`). Then write that file.
- `STOPWORDS`: about twenty common words. Language detection uses them.
- `HARD` and `SOFT`: category to regex. Reuse the English category names (`throat-clearing`, `chatbot-artifact`, `ste-wordy`, …) so reports stay consistent.

Regex rules:

- Keep every quantifier bounded (`{1,80}`, never `.*` across sentences). The self-test runs a 200 KB worst case.
- Match both `'` and `’` where the language uses apostrophes (see `A` in `fr.py`).
- Only put a pattern in `HARD` when it is almost never correct prose.

## Check it

```bash
./setup.sh --check                              # every locale compiles
python3 skills/ocre-jelly/scripts/gen_docs.py   # refresh docs/reference/locales.md and checks.md
echo "Your sample text" | python3 skills/ocre-jelly/scripts/scan.py --no-config --locale en-NZ
```

If a new check category appears, `gen_docs.py` asks you to describe it in its `CHECKS` table.
