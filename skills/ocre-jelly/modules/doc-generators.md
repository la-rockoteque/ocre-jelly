---
kind: rules
when: docs from autoDocstring, Document This, IDE stubs or AI doc writers
default: off
description: Opinions for doc stubs from autoDocstring, Document This, IDE generators and AI doc writers
---
## Doc generators (opinionated)
- autoDocstring placeholders (`_summary_`, `_description_`, `_type_`) never ship. Write the text, or delete the docstring when docs aren't required.
- Document This `@param {*} name` stubs: in TypeScript, drop the `{*}`; in JavaScript, write the real type.
- IDE stub tags with no text (`@param id`, `@return`): fill them in or delete them. An empty tag is noise.
- AI doc writers (Copilot /doc, Mintlify, Cursor) produce echo docs and "This function is used to..." openers. Audit their output with `docs` mode before you commit it.
