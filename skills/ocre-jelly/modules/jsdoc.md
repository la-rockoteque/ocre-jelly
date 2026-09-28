---
kind: rules
when: JSDoc in .js files
default: auto
detect_files: jsdoc.json, .jsdoc.json, jsconfig.json, */jsconfig.json
description: JSDoc conventions for JavaScript
---
## JSDoc
- Use `@param {Type} name - description` with the hyphen, and `@returns`, not `@return`.
- Every type in braces is real: never `{*}` or `{Object}` when the shape is known. Use `@typedef` for a reused shape.
- Put runnable code under `@example`. Its code is never rewritten.
