# Registers

The register can also depend on the context: `"register": {"default": "neutral", "contexts": {"comments": "formal", "pr": "casual"}}`. The contexts are `docs`, `comments`, `strings`, `commits`, `pr`, `tickets` and `chat`. For each piece of prose you write, use the register of its context and language; the session's Register line lists them. When you scan a PR description, a ticket or a chat post, pass `--context pr|tickets|chat` to `scan.py`.

A register is how formal the prose is. Set it per language in the config: `"register": {"fr": "casual", "en": "neutral"}`, or one value for every language. Write new prose in the configured register. A rewrite keeps the source's register, whatever the config says.

**Every register keeps the core rules.** No AI tells, facts preserved, one idea per sentence, one term per concept. A casual text still says something concrete, and a formal one is still plain. Only formality changes.

| | formal | neutral (default) | casual |
|---|---|---|---|
| For | Contracts, policies, customer letters, official notices | Docs, READMEs, commits, PRs, code comments, tickets | Team chat, Slack or Teams posts, beta invitations, internal emails |
| Scanner | Adds soft `register-informal` findings | As usual | Turns off fr-CA `anglicism` |

## English

- **formal:** no contractions ("do not", "it is"), no slang, third person or "you" used sparingly, full sentences.
- **neutral:** plain STE English. Contractions are fine in guides, but avoid them in reference text.
- **casual:** contractions, "you", short sentences, fragments where they read naturally. Emoji or shortcodes only where the channel uses them. No hype.

## Français

- **soutenu (formal)** : vouvoiement, négation complète (« ne … pas »), aucun anglicisme critiqué par l'OQLF, pas d'abréviations familières.
- **neutre (neutral)** : le français clair de `ste-fr.md`. Le vouvoiement ou l'infinitif, selon le document.
- **familier (casual)**, surtout en fr-CA :
  - le tutoiement ;
  - des phrases courtes et directes ;
  - la négation sans « ne » à l'oral écrit (« pour pas perdre », « il bloque jamais rien ») ;
  - les mots courants du milieu, en français d'ici (« pis », « check tes scores », « un nudge ») ;
  - des emojis ou des shortcodes (`:wave:`) seulement si le canal s'en sert.

  Ce qui reste interdit : les tics d'IA (« Il est important de noter que », « N'hésitez pas à »), le ton promotionnel, les phrases qui ne disent rien.

A casual example that passes: "Plum regarde comment tu utilises Claude Code. Par défaut, il bloque jamais rien." A casual example that fails: "Plongeons ensemble dans cette expérience révolutionnaire!" The scanner flags that one in every register.
