# Getting started

In this tutorial, you install ocre-jelly, audit a paragraph, rewrite it, and set up one repo with a locale. It takes about ten minutes.

You need Claude Code, Python 3.10 or later, and read access to `https://git.nexapptech.com/vbernier/ocre-jelly`.

## 1. Install the plugin

Run these two commands in a terminal:

```bash
claude plugin marketplace add https://git.nexapptech.com/vbernier/ocre-jelly.git
claude plugin install ocre-jelly@ocre-jelly
```

Restart Claude Code. At the start of each session, a status message says "Loading ocre-jelly prose mode...".

## 2. Audit a paragraph

In Claude Code, type:

```
/ocre-jelly audit Here's the thing: our platform isn't just a tool. It's a revolution, showcasing world-class design. In order to scale, we utilize caching.
```

The audit changes nothing. It returns one line per finding, with the category and a fix. The wording varies; the output looks like this:

```
L1: throat-clearing "Here's the thing:". Delete it.
L1: binary-contrast "isn't just a tool. It's a revolution". State what the platform does.
L1: ing-tail ", showcasing world-class design". Delete it, or name the design fact.
L1: promotional "world-class". Say what makes the design good, or delete it.
L1: ste-wordy "In order to". Write "To".
L1: ste-wordy "utilize". Write "use".
light touch
```

Each finding is **hard** (almost always a defect) or **soft** (a candidate that Claude confirms in context). See [Checks](../reference/checks.md) for the full list.

## 3. Rewrite it

```
/ocre-jelly rewrite Here's the thing: our platform isn't just a tool. It's a revolution, showcasing world-class design. In order to scale, we utilize caching.
```

The rewrite edits only the sentences with confirmed findings, and it keeps every fact. You get the cleaned text back. One possible result:

```
Our platform caches results so it can scale.
```

Claude checks the rewrite again with the scanner, and confirms that no number, name, URL or code span was lost.

## 4. Set up a repo

Open a repo in Claude Code and ask:

```
Set ocre-jelly's locales to en-CA and fr-CA for this repo, shared with the team.
```

Claude runs:

```bash
modules.py config set locales '["en-CA","fr-CA"]' --project
```

This writes `.claude/ocre-jelly.json` in the repo. Commit it. Everyone on the team now gets Canadian spelling checks in English (colour, centre, organize) and OQLF terms in French (courriel, clavardage).

## 5. See what is active

```
/ocre-jelly modules list
```

Modules that match the repo turn on by themselves. For example, a `tsconfig.json` turns on the TSDoc conventions, and a `docs/adr` folder turns on the ADR conventions. Each module adds only one line to the session until the work needs it.

## Next steps

- Give the project one vocabulary: [Write a ubiquitous-language glossary](../how-to/write-a-glossary.md).
- Fix doc comments and i18n files: [Audit code docs and UI strings](../how-to/audit-code-docs-and-ui-strings.md).
- Read the rules ocre-jelly applies: [The ocre-jelly writing standards](../explanation/standards.md).
