---
kind: rules
when: Swift doc comments
default: auto
detect_files: Package.swift, *.xcodeproj, *.xcworkspace, */Package.swift
description: Swift markup and DocC conventions
---
## Swift markup
- Write a one-line summary, then use `- Parameters:`, `- Returns:` and `- Throws:`.
- Link with double backticks (``` ``Name`` ```) for DocC symbol links.
