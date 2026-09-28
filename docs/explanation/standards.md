# The ocre-jelly writing standards

This page explains the standards that ocre-jelly applies, and why. The binding text for the agent is in `skills/ocre-jelly/SKILL.md` and `skills/ocre-jelly/references/`. This page is the human summary.

## The core idea: repair defects, not style

ocre-jelly doesn't have a house style to impose. It looks for concrete defects: text that carries no information, pretends to more certainty or importance than it has, or reads as generated. It repairs only those. Everything else stays as the author wrote it.

Three consequences:

1. **A no-op beats an uncertain edit.** When nothing is clearly wrong, the rewrite returns the text unchanged.
2. **A scanner hit is a candidate, not a verdict.** The agent reads every sentence first, then confirms each hit in context, or protects it.
3. **The smallest repair wins.** Only sentences with a confirmed defect change. Every other sentence is copied byte for byte.

## What counts as a defect

| Family | Examples | Why it is a defect |
|---|---|---|
| Empty framing | "Here's the thing:", "It's worth noting that", « Il convient de noter que » | Delays the point and adds nothing. |
| Manufactured importance | "Let that sink in", "a pivotal moment", « change la donne » | Claims significance instead of showing it. |
| Chat leftovers | "I hope this helps", "Great question", « N'hésitez pas à » | Conversation residue in a document. |
| False drama | "It's not a tool. It's a revolution." | Contrasts with a claim nobody made. |
| Hollow tails | ", highlighting its commitment to quality" | A participle that states no fact. |
| Unsupported attribution | "Experts agree", « De nombreuses études » | A claim with no source. |
| Wordiness | "in order to", "utilize", « afin de », « procéder à » | A long form where a short one says the same thing. |
| Echo docs | "Gets the user name." on `GetUserName` | Repeats the signature, and costs the reader time. |
| Vocabulary drift | "basket" when the glossary says **Order** | Two words for one concept confuse readers and code. |

The full list is on the [Checks](../reference/checks.md) page.

## What is always protected

- **Facts:** numbers, dates, names, quotes, citations, URLs, units, versions and file paths. The `--preserve` check proves they survived.
- **Meaning:** negations, conditions, scope ("most", "73%"), uncertainty, attribution, causal strength.
- **Force words** in safety, security, legal and technical rules: "never", "must", "all", and the RFC 2119 keywords.
- **Code and markers:** code, identifiers, `ponytail:`, `TODO:`, lint directives. GhostDoc and autoDocstring placeholders are the one exception.
- **Quoted and attributed text,** and literal or domain-valid uses: "robust" in statistics, "the struggle is real" when the text analyzes the meme.
- **Register:** a warm email stays warm. STE applies in full only to technical text.
- **Glossary Terms and protected terms:** never reworded, never respelled.

## English: ASD-STE100

ASD-STE100 Simplified Technical English is the aerospace standard for maintenance documentation. ocre-jelly restates its writing rules in its own words (the official dictionary is copyrighted) in `references/ste100.md`:

- Use one word for one meaning, and the simple word ("use", not "utilize").
- Keep technical names (parts, tools, software, units) and technical verbs as the domain needs them.
- Use simple verb forms and the active voice. In instructions, always use the imperative.
- Write 20 words or fewer per instruction, and 25 or fewer per descriptive sentence. Write one topic per sentence.
- Don't drop articles to save words ("Close the valve", not "Close valve").
- Put the condition before the action. Start a warning with the command, then give the risk.

## French: plain and rationalized French

No French edition of STE100 exists. `references/ste-fr.md` (written in French) combines three sources:

- **ISO 24495-1:2023** *Langage clair et simple*: the international plain-language principles, published in French.
- **Français Rationalisé**: the aerospace industry's controlled French from the 1990s (GIFAS), the French counterpart of STE.
- **OQLF**: Québec usage from the *Banque de dépannage linguistique* and the *Grand dictionnaire terminologique*.

The rules follow STE's shape: one idea per sentence, the active voice, the verb instead of the noun made from it ("valider", not « effectuer la validation »), no noun chains, and the same length limits. French runs slightly longer, so a sentence a few words over the limit can stay. Regional files set the vocabulary and typography, and they respect what the OQLF now accepts (« réaliser », « opportunité », « présentement »).

## Hard and soft

- **Hard** findings are almost never correct prose outside quotes: throat-clearing, chat leftovers, echo docs, generator placeholders. In rewrite mode, a hard finding the rewrite introduced blocks the result.
- **Soft** findings need a reader: a long sentence, a regional spelling, a glossary alias outside its context, three em-dashes in one paragraph. The agent confirms or protects each one, with a reason.

Teams can change any category's severity, or turn it off. See [Tune the checks](../how-to/tune-checks.md).

## Conventions on top

Named conventions add rules for specific artifacts, through modules: Conventional Commits for commit messages, Conventional Comments for review feedback, Keep a Changelog, ADRs, PR templates, Gherkin, the doc-comment format of each language, and more. A convention owns the shape of its artifact (for example, a commit subject line). The standards above govern the prose inside it.
