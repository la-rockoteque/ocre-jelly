---
kind: rules
when: Go doc comments
default: auto
detect_files: go.mod, */go.mod
description: Go doc comment conventions
---
## Go doc comments
- Start with the name of the thing, then say what it does in a full sentence: "Parse reads a URL …". A comment that only says "Parse parses." is an echo.
- Mark deprecations with a paragraph that starts with `Deprecated:`.
- Link with `[Name]`. A package comment starts with "Package name".
