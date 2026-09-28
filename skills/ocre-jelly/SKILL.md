---
name: ocre-jelly
description: Find and remove AI writing patterns in prose (audit, or minimal rewrite with facts preserved) under ASD-STE100 and French plain-language rules. Use for "unslop", "humanize", "sounds like ChatGPT", or cleaning docs, READMEs, commit messages, PR descriptions, code comments, doc comments (JSDoc, Javadoc, XML docs, docstrings...) and UI strings. Also setup, config, modules and feedback for ocre-jelly. Prose only; code slop goes to ai-slop-cleaner.
user-invocable: true
argument-hint: "[setup|audit|rewrite|docs|commit|modules|config|update|stats|feedback] <text, file or folder>"
---

# Ocre Jelly

Repair concrete AI-writing defects. Leave everything else alone. A no-op beats an uncertain edit.

**Prose authority, per language.** English follows ASD-STE100 Simplified Technical English ([references/ste100.md](references/ste100.md)). French follows [references/ste-fr.md](references/ste-fr.md) (ISO 24495-1 plain language, Français Rationalisé principles, OQLF usage). Read the one for the text's language before every audit or rewrite. It decides what counts as clear prose and how to repair it. Only the preservation rules below outrank it.

## Modes

- `setup` (also: "configure ocre-jelly", "run the wizard"): the configuration wizard. Read [references/wizard.md](references/wizard.md) and follow it.
- `audit` (also: "review", "just flag it", "don't change anything"): report findings, never rewrite.
- `rewrite` (default when no mode word is given): diagnose, then make the smallest repairs.
- `docs [audit] <files>`: the same passes on comments, doc comments and string resources.

Other modes load their own instructions: `docs` and code comments → [references/code-docs.md](references/code-docs.md) ("Running docs mode"); `commit` → [references/commits.md](references/commits.md); `feedback` → [references/feedback.md](references/feedback.md); `stats` and `update` → [references/personal.md](references/personal.md); `modules` and `config` → [references/modules-config.md](references/modules-config.md).

Settings (locales, glossary path, thresholds, severity) come from the layered config, and the scanners read it themselves. Write new prose in the configured locales (`modules.py config show`).

When the user asks for something ocre-jelly doesn't do, say so, name the closest feature, and offer a feature request: read [references/feedback.md](references/feedback.md). When the session says an ocre-jelly update is available, read [references/personal.md](references/personal.md). Before you run `git commit`, check the message: read [references/commits.md](references/commits.md).

Input is inline text or a file path the user gives. Only read files the user named. Never go looking for writing samples elsewhere on disk.

## Pass 0: ubiquitous language

1. Find the project root: `git rev-parse --show-toplevel`, or the current directory outside git. Look, case-insensitively, for `docs/ubiquitous-language.md`, then `UBIQUITOUS-LANGUAGE.md` at the root.
2. If you find it, read it. It is a set of markdown tables, grouped by context, each with a **Term** column and an **Aliases to avoid** column (other columns, such as a UI label, are allowed). A Term is a protected technical name (STE100 allows these): never simplify, rename or synonym-cycle it. An alias to avoid is a finding: replace it with its Term. Where an alias maps to several Terms, the **Flagged ambiguities** section decides which one applies. Each `##` section is a bounded context. An alias from one context is a finding only in text about that context, so check the section before you replace anything. Words in a **UI label** column are valid.
3. If you find none, ask the user (AskUserQuestion when available) where to create it:
   - **Committed** (recommended for a shared repo): `docs/ubiquitous-language.md`. Write it, but don't commit it; the user commits it.
   - **Local only**: `UBIQUITOUS-LANGUAGE.md` at the root, plus a `UBIQUITOUS-LANGUAGE.md` line appended to `.git/info/exclude`. That file ignores it for this clone only; don't touch `.gitignore`.
   - **Skip**: run without a glossary this time.
   Build it from [references/UBIQUITOUS-LANGUAGE.template.md](references/UBIQUITOUS-LANGUAGE.template.md). Seed it with the domain terms the input uses, and fill in the aliases when the input uses two words for one concept. Tell the user to review it.

## Pass 1: diagnose

1. Read every sentence yourself first, headings and endings included. Note what each sentence contributes.
2. Then run the scanner for anything you missed. It reads stdin only; pipe the text in:
   ```bash
   python3 <this-skill-dir>/scripts/scan.py < input.txt
   ```
   Write inline text to a scratch file first. Never interpolate user text into a shell command line.
3. Load [references/patterns.md](references/patterns.md) for the full catalog and the protection rules. Check the text against its language's prose authority too, at full strength for technical text and vocabulary/clarity only for other registers. French has its own AI tells (« Il est important de noter que », « N'hésitez pas à », « Plongeons dans »); the scanner knows them.
4. Classify each candidate as **confirmed** (a real defect in this context) or **protected** (literal, quoted, domain-valid, attributed, or natural for the genre), with a one-line reason. A scanner hit is a candidate, not a verdict. Phrase lists are incomplete, so also catch paraphrased scaffolding by what it does.

## Pass 2: rewrite (rewrite mode only)

- Edit only sentences with confirmed findings. Copy every other sentence byte-for-byte, same order, same paragraphs.
- No confirmed findings: return the source unchanged and say so.
- Write every repaired sentence to STE100: simple words, active voice, one topic, length limits.
- Delete empty framing rather than swapping in new filler. Don't overcorrect into choppy staccato.
- Preserve exactly: numbers, dates, names, quotes, citations, code, URLs, units, version numbers, file paths.
- Never touch code, or tool markers in comments: `ponytail:`, `TODO:`, `FIXME:`, `NOTE:`, `HACK:`, `noqa`, `eslint-disable`, `@ts-`, `type: ignore`. Only the prose after a marker is in scope. The words after `ponytail:` stay as they are, because they name a ceiling and an upgrade path.
- Preserve meaning: negations, conditions, scope ("most", "73%"), uncertainty, attribution, causal strength, register.
- Keep force-bearing "never", "must", "all" in safety, security, legal and technical rules.
- Add nothing: no new claims, advice, anecdotes, personality, certainty or conclusions.
- Don't fact-check or treat missing evidence as an AI tell.

## Validate (rewrite mode only)

1. Re-scan the output with `scan.py`. Any **hard** hit you introduced blocks; fix it.
2. Run `python3 <this-skill-dir>/scripts/scan.py --preserve original.txt < rewritten.txt`. Any `MISSING` token blocks; restore it.
3. Re-read negations, conditions and scope side by side with the original.

## Output

Rewrite: return the cleaned text only. Add a short change list only if the user asks for one.

Audit: one line per finding, in the same shape as ponytail-review and caveman-review, so all three can go in one review:

```
L<line>: <category> "<smallest span>". <fix>.
```

Use `<file>:L<line>:` for several files. Tags are the scanner categories (`throat-clearing`, `ste-length`, `glossary-alias`, ...). After the findings, list protected spans as `L<line>: keep "<span>". <reason>.` End with one verdict line: `clean`, `light touch`, or `heavy rewrite`.

