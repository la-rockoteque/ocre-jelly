---
kind: rules
when: doc comments in .ts/.tsx files
default: auto
detect_files: tsconfig.json, tsdoc.json, typedoc.json, */tsconfig.json
description: TSDoc and TypeDoc conventions for TypeScript
---
## TSDoc
- Never repeat types in braces. TypeScript already has them: `@param key - description`.
- The hyphen after the parameter name is required. Use `@returns`, `@remarks` for detail, and `{@link Name}` for references.
- Mark internal APIs `@internal` rather than explaining in prose that they are internal.
