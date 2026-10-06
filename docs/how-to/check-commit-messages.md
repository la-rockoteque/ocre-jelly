# Check commit messages and PR descriptions

ocre-jelly checks a commit message in two ways:

- **Shape:** the subject length, no trailing period, a blank line after the subject, body wrapping, the imperative mood, and the repo's convention (Conventional Commits or gitmoji).
- **Prose:** every check from `scan.py` runs on the body. Trailers (`Refs: #42`) and code are left out.

It can only report, or it can reject the commit. The `commits.enforce` setting decides.

## 1. Choose the enforcement

| `commits.enforce` | Effect |
|---|---|
| `off` | The hook prints nothing and never blocks. |
| `warn` (default) | The hook prints the findings. The commit goes through. |
| `block` | The hook prints the findings and rejects the commit when a **hard** finding remains. Soft findings never block. |

```bash
python3 $OJ/modules.py config set commits '{"enforce":"block"}' --project     # the team rule
python3 $OJ/modules.py config set commits '{"enforce":"warn"}' --local        # your override in this clone
```

In an emergency, `git commit --no-verify` skips every commit-msg hook.

## 2. Choose the convention

| `commits.convention` | Subject rule |
|---|---|
| `auto` (default) | `conventional` when the `conventional-commits` module is on; `gitmoji` when the `gitmoji` module is on; otherwise `none`. |
| `conventional` | `type(scope)!: summary`, with a type from `commits.types`. |
| `gitmoji` | A gitmoji (emoji or `:code:`) first. |
| `none` | No format rule. The length, period, blank-line, wrap and imperative checks still run. |

The `conventional-commits` module turns on by itself when the repo has a commitlint, commitizen, semantic-release or release-please config. To use the convention without those tools:

```bash
python3 $OJ/modules.py enable conventional-commits --project
```

Other limits, all in the `commits` object:

```json
{
  "commits": {
    "enforce": "block",
    "convention": "conventional",
    "subject_max": 72,
    "subject_target": 50,
    "body_wrap": 72,
    "types": ["feat", "fix", "docs", "refactor", "perf", "test", "build", "ci", "chore", "revert"]
  }
}
```

An empty `types` list means the standard list: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert.

## 3. Install the hook

Pick the route that matches how the repo runs git hooks.

### Plain git

```bash
python3 $OJ/modules.py export git-hook
```

This writes an executable `.git/hooks/commit-msg`. It calls this machine's `commitmsg.py`, so it stays out of git: each teammate runs the command once. The export refuses when:

- `.git/hooks/commit-msg` exists and ocre-jelly didn't write it. Merge it by hand, or use `--force`.
- `core.hooksPath` is set (husky and lefthook do this), because git then ignores `.git/hooks`. Use the routes below.
- the folder is a git worktree. Install the hook from the main clone.

### The pre-commit framework

In the target repo's `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/la-rockoteque/ocre-jelly.git
    rev: v0.1.0
    hooks:
      - id: ocre-jelly-commit-msg
```

Then run `pre-commit install --hook-type commit-msg`. The hook reads the target repo's `.claude/ocre-jelly.json`, so `commits.enforce` works the same way. The `rev` must be a tag or commit that exists on the server.

### husky

Add this line to `.husky/commit-msg`:

```sh
python3 "$HOME/.claude/plugins/marketplaces/ocre-jelly/skills/ocre-jelly/scripts/commitmsg.py" --hook "$1"
```

### lefthook

```yaml
commit-msg:
  commands:
    ocre-jelly:
      run: python3 "$HOME/.claude/plugins/marketplaces/ocre-jelly/skills/ocre-jelly/scripts/commitmsg.py" --hook {1}
```

For husky and lefthook, every teammate needs ocre-jelly installed at that path. Use the pre-commit route when some teammates don't use Claude Code.

## 4. Check a message by hand

```bash
python3 $OJ/commitmsg.py .git/COMMIT_EDITMSG
git log -1 --format=%B | python3 $OJ/commitmsg.py
python3 $OJ/commitmsg.py --enforce block --convention conventional message.txt
```

Without `--hook`, the script uses `warn` unless you pass `--enforce`. Example output:

```
ocre-jelly: commit message (conventional convention, enforce=block)
  L1   hard commit-format          'Added the thing.': expected type(scope)!: summary
  L1   soft commit-subject-period  Added the thing.
  L1   soft commit-imperative      'Added': use the imperative (add, fix, remove)
ocre-jelly: commit blocked. Fix the hard findings, or commit with --no-verify.
```

## What is skipped

- Lines that start with `#`, and everything below git's scissors line (`# --- >8 ---`), as git itself does.
- The shape checks for merge messages ("Merge …"), reverts (`Revert "…"`) and `fixup!`, `squash!` and `amend!` commits, since git or a tool wrote their subject.
- URLs, indented or fenced code, and trailers, for the wrap check.

## PR and MR descriptions

There is no hook for PR descriptions, because they live on the server. ocre-jelly covers them in three ways:

- When Claude writes a PR, the `pr-template` module has it fill every section of the repo's template, and the prose rules apply.
- To audit an existing PR, fetch the body with the repo's CLI and scan it. ocre-jelly itself never calls the network.

  ```bash
  gh pr view 123 --json body -q .body | python3 $OJ/scan.py
  ```

  On GitLab, print the MR description with `glab mr view 45` (see `glab mr view --help` for its JSON output option) and pipe the description the same way.

- In CI, the same pipe can fail a job. `scan.py` exits 0 whatever it finds, so the CI job fails on a count, for example `scan.py --json | python3 -c "import json,sys; sys.exit(any(h['severity']=='hard' for h in json.load(sys.stdin)))"`.

## Every finding

The categories and severities are on the [Checks](../reference/checks.md) page, under `commit-*`. `severity` in the config can change or drop each one, as for any other check.
