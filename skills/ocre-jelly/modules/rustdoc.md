---
kind: rules
when: rustdoc comments
default: auto
detect_files: Cargo.toml, */Cargo.toml
description: rustdoc conventions
---
## rustdoc
- Write a one-line summary in the third person, then a blank line.
- A public fn returning `Result` gets a `# Errors` section. One that can panic gets `# Panics`. An `unsafe fn` gets `# Safety`.
- Put examples under `# Examples` as doctests. They are code, and are never rewritten.
- Link with intra-doc links: [`Name`].
