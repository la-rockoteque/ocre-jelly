---
kind: rules
when: "deslop" requests, or docs from the OMC writer agent
default: auto
detect: oh-my-claudecode
description: oh-my-claudecode - ai-slop-cleaner, writer agent
---
## With oh-my-claudecode
- "deslop" and "anti-slop" route to ai-slop-cleaner, which cleans code. Ocre-jelly cleans prose. When the target is docs or comments, use ocre-jelly.
- The `writer` agent's README and API docs are prose artifacts, so these rules apply to them.
