# Evals

Eight cases scored by an LLM judge, each run with and without ocre-jelly, so the report shows what the plugin adds (quality delta) and what it costs (tokens, time).

| Case | Measures |
|---|---|
| audit-en | Recall on English AI tells; audit mode doesn't rewrite |
| rewrite-preserve | Rewrites remove slop and keep every fact |
| clean-noop | Precision: clean text stays unchanged |
| protected-quote | Quoted patterns are protected, not flagged |
| audit-fr | French tells and a fr-CA term (courriel) |
| docs-echo | Echo doc comments flagged; good ones left alone |
| commit-msg | Commit-message shape and a Conventional Commits fix |
| unsupported-feedback | Honest "not supported", feedback offered, nothing sent without consent |

Run (each run is a full Claude session on your account, so cap the cost):

```bash
claude plugin eval . --allow-tools Bash Write --runs 1 --max-cost-usd 3 --no-publish
claude plugin eval . --case audit-fr --runs 1          # one case
```

Results go to `evals/results/` (git-ignored). Add a case: a folder with `prompt.md` (front matter: `max_turns`, `allowed_tools`) and `graders/criteria.md` (`type: llm`, a scoring rubric).
