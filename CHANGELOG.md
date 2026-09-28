# Changelog

All notable changes to ocre-jelly are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Brand icon in `assets/`, shown in the README and referenced by the plugin manifest.
- User documentation in `docs/`: a getting-started tutorial, nine how-to guides, the configuration, command-line and glossary-format reference, and explanations of the writing standards and the design.
- `gen_docs.py` generates the modules, locales and checks reference pages from the code. `setup.sh --check` fails when they are stale.
- `commitmsg.py` checks commit messages: subject length and period, the blank line, body wrap, the imperative, Conventional Commits or gitmoji, and the prose of the body.
- `commits` config section: `enforce` (off, warn, block), `convention`, `subject_max`, `subject_target`, `body_wrap`, `types`.
- `git-hook` export module (`.git/hooks/commit-msg`) and `.pre-commit-hooks.yaml` for the pre-commit framework.
- The `commit` skill mode, and a guide for commit messages and PR descriptions.

## [0.1.0] - 2026-09-28

### Added

- `ocre-jelly` skill with audit, rewrite, docs, modules and config modes.
- Prose scanner with hard and soft AI-writing patterns, STE sentence-length and wordiness checks, a glossary alias check and a fact-preservation check.
- English (ASD-STE100) and French (ISO 24495-1, Français Rationalisé, OQLF) prose authorities.
- Locales: en, en-US, en-GB, en-CA, en-AU, fr, fr-CA, fr-FR, fr-BE, fr-CH, picked per paragraph and per resource-file path.
- Code-doc scanner for comments, doc comments and string resources, with echo, placeholder and generated-stub checks, and a gate that proves only comments changed.
- 38 modules: tool integrations, doc-comment conventions, writing conventions, and exports for other agents, Vale and cspell.
- Layered JSON config (user, project, local) with a JSON Schema.
- SessionStart and SubagentStart hooks with progressive disclosure.
