# Commits and PRs

- Before you run `git commit`, write the message to a scratch file and check it with `python3 <this-skill-dir>/scripts/commitmsg.py <file>`. Fix the hard findings, and weigh the soft ones. The convention (Conventional Commits, gitmoji or none), the limits and the enforcement come from the `commits` config.
- When the repo runs the hook with `commits.enforce: block`, a commit with a hard finding fails. Read the hook's output, fix the message, and commit again. Never bypass it with `--no-verify` unless the user asks.
- To install the hook: `modules.py export git-hook` writes `.git/hooks/commit-msg`. With husky, lefthook or the pre-commit framework, follow `docs/how-to/check-commit-messages.md` in the ocre-jelly repo instead.
- PR and MR descriptions: fill the repo's template (the `pr-template` module), then scan the body with `scan.py` like any prose. For the PR's changes, run `git diff <base>... | codedoc.py --diff`. To audit an existing PR, fetch the body with the repo's CLI (`gh pr view --json body -q .body`, `glab mr view`), then scan it.
