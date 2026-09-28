# Configure locales

A locale sets the regional spelling, preferred terms and typography for one language. A repo can have one locale per language, for example `en-CA` for English and `fr-CA` for French.

## Set the locales

```bash
python3 $OJ/modules.py config set locales '["en-CA","fr-CA"]' --project
```

Or in `.claude/ocre-jelly.json`:

```json
{ "locales": ["en-CA", "fr-CA"] }
```

With no locales set, ocre-jelly detects English and French and applies their base patterns, but no regional checks.

## What each locale checks

| Locale | Spelling | Terms and typography |
|---|---|---|
| `en-US` | color, center, organize, traveled, gray, defense | — |
| `en-GB` | colour, centre, organise, travelled, grey, defence | postcode, mobile phone |
| `en-CA` | colour, centre, organize, travelled | postal code |
| `en-AU` | colour, centre, organise, travelled, grey | postcode |
| `fr-CA` | — | OQLF terms: courriel, clavardage, fin de semaine, stationnement, balado, infonuagique, téléverser. OQLF anglicisms: céduler, faire du sens, à l'effet que, adresser un problème, en termes de |
| `fr-FR` | — | FranceTerme terms: mot-dièse, informatique en nuage, hameçonnage, diffusion en continu. A no-break space before `; : ! ?` |
| `fr-BE` | — | septante, nonante. A no-break space before `; : ! ?` |
| `fr-CH` | — | septante, huitante, nonante |

The generated [Locales](../reference/locales.md) page has the exact lists.

## How the locale is picked

- **Prose and comments**: each paragraph uses the configured locale for its language. ocre-jelly finds the language by counting common words (the, of, is / le, des, est). A mixed English and French document works: each paragraph gets its own checks.
- **String resources**: the file path wins. `locales/fr-CA/nav.json`, `Strings.fr.resx` and `fr.lproj/Localizable.strings` are checked as fr-CA or fr, whatever the configured list says.
- **Writing**: the session rules name the locales, so Claude also writes new prose in them.

## Set a register

A register sets how formal the prose is, per language:

```bash
python3 $OJ/modules.py config set register '{"fr":"casual","en":"neutral"}' --project
```

| Register | Use it for | What changes |
|---|---|---|
| `formal` | Contracts, policies, customer letters | Soft `register-informal` findings: « tu », « pis » and « chu » in French; contractions and "gonna" in English |
| `neutral` (default) | Docs, READMEs, commits, PRs, comments | Nothing |
| `casual` | Team chat, Slack posts, beta invitations | fr-CA anglicisms like « check » stop being findings |

Claude writes new prose in the configured register, and a rewrite keeps the source's register. A casual French post can say « Check tes scores, pis dis-moi si ça marche », but it still can't say « Il est important de noter que ». AI-tell checks stay on in every register. The rules for each language and register are in `skills/ocre-jelly/references/registers.md`.

## Keep a word's spelling

Glossary Terms keep their spelling. If the glossary has a Term **Center** (a product name) in an en-GB repo, ocre-jelly doesn't suggest "Center -> Centre". Add other words, such as brand names, to `protected_terms`:

```json
{ "protected_terms": ["Colorado Plus", "Centerline"] }
```

## Spelling limits

Spelling checks use word lists, not suffix rules. Pairs whose other spelling is also a valid word (check/cheque, program/programme, tire/tyre, emphasis) are left out on purpose. Every spelling finding is soft: Claude confirms it in context.

To add a variant, see [Add a locale](add-a-locale.md).
