---
kind: rules
when: Ruby YARD comments
default: auto
detect_files: .yardopts, Gemfile
description: YARD conventions for Ruby
---
## YARD
- Use `@param name [Type] description` and `@return [Type] description`.
- Add `@raise [ErrorClass]` for each error a caller should rescue.
