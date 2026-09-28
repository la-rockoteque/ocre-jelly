---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

The repo uses Conventional Commits. Check this commit message before I commit it, and propose a fixed version:

```
Added retry logic to the billing client.
The client now retries failed calls to CMiC three times because the API drops about 1 call in 50.
```
