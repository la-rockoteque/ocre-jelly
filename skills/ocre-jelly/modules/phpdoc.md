---
kind: rules
when: PHPDoc comments
default: auto
detect_files: composer.json, */composer.json
description: PHPDoc conventions
---
## PHPDoc
- Omit `@param` and `@return` tags that only repeat native type declarations. Keep them when they add generics (`array<int, User>`) or a description.
- Write `@throws` for each exception a caller should handle.
