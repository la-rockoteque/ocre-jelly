# Tune the checks

Every setting below goes in a config layer: `--project` for the team, `--local` for you in this clone, or no flag for you in every repo. See [Configuration](../reference/configuration.md).

## Silence one spot

Put a marker in a comment, in the file's own comment syntax:

```markdown
<!-- ocre-jelly: ignore throat-clearing -->
Here's the thing: this sentence quotes the pattern on purpose.
```

```ts
// ocre-jelly: ignore echo-doc
/** Gets the user. */
```

- `ocre-jelly: ignore cat1, cat2` on a line of its own covers the next non-blank line. As a trailing comment, it covers its own line.
- `ocre-jelly: ignore` with no category covers every category.
- `ocre-jelly: off` … `ocre-jelly: on` covers the lines in between.

There is no other syntax. For a whole category, change its severity instead (next section).

## Turn a check off, or change its severity

```bash
python3 $OJ/modules.py config set severity '{"em-dash":"off","anglicism":"hard"}' --project
```

- `off` drops the category.
- `soft` makes it a candidate that Claude confirms in context.
- `hard` makes it a blocking defect in rewrite mode.

[Checks](../reference/checks.md) lists every category.

## Change the limits

```bash
python3 $OJ/modules.py config set thresholds.sentence_words 30 --project
```

| Threshold | Default | Effect |
|---|---|---|
| `sentence_words` | 25 | `ste-length` flags sentences longer than this. |
| `instruction_words` | 20 | Claude's limit for procedural sentences (judged in context). |
| `em_dash_per_paragraph` | 3 | `em-dash` flags a paragraph with this many or more. |
| `length_hits_per_file` | 3 | `codedoc.py` lists this many long sentences per file, then one summary line. |

## Skip files

```bash
python3 $OJ/modules.py config set ignore_paths '["**/*.generated.cs","vendor/*","migrations/*"]' --project
```

Patterns are matched against the path from the repo root, and `*` also crosses `/`. `codedoc.py` prints how many files it skipped.

## Protect words

```bash
python3 $OJ/modules.py config set protected_terms '["MoFlex","CMiC","Centerline"]' --project
```

A protected term is never flagged as an alias, and never respelled for the locale. Glossary Terms are protected already.

## Reduce what the session receives

The hooks inject a short core, a locale line, and one index line per active module (about 160 to 200 words). To cut more:

- Disable modules you don't need: `modules.py disable atlassian`.
- Give the rules only to doc-writing subagents:

  ```bash
  python3 $OJ/modules.py config set subagents '{"inject":true,"matcher":"writer|doc"}'
  ```

- Or stop injecting into subagents: `config set subagents '{"inject":false}'`.

To get everything inlined instead, use `config set inject full`.

## Turn ocre-jelly off

- For one session: start Claude Code with `OCRE_JELLY=off`.
- In chat: say "stop ocre-jelly".
- For a repo: `config set enabled false --project`.
