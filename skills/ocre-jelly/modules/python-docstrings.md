---
kind: rules
when: Python docstrings
default: auto
detect_files: pyproject.toml, setup.py, setup.cfg, */pyproject.toml
description: PEP 257 docstrings (Google style unless the repo uses another)
---
## Python docstrings
- The summary line is imperative and ends with a period: "Return the user." Put a blank line before any details.
- Keep the style the repo already uses (Google, NumPy or reST). In a repo with no style yet, use Google style.
- Don't repeat type hints in docstrings. `x (int):` adds nothing when the signature says `x: int`.
- Doctests (`>>>`) are code. They are never rewritten.
