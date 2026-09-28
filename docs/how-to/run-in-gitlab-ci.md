# Run in GitLab CI

This job checks the prose a merge request adds, and shows the findings in the merge request's **Code quality** widget. It reports only added lines, so legacy text doesn't flood the report.

## The job

Add this to `.gitlab-ci.yml`:

```yaml
ocre-jelly:
  stage: test
  image: python:3.12-slim
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  variables:
    GIT_DEPTH: 0                      # the diff needs the target branch's history
  before_script:
    - apt-get update -qq && apt-get install -y -qq git >/dev/null
    - git clone --depth 1 "https://gitlab-ci-token:${CI_JOB_TOKEN}@git.nexapptech.com/vbernier/ocre-jelly.git" /tmp/ocre-jelly
  script:
    - git fetch -q origin "$CI_MERGE_REQUEST_TARGET_BRANCH_NAME"
    - git diff "origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME...HEAD"
      | python3 /tmp/ocre-jelly/skills/ocre-jelly/scripts/codedoc.py --diff --format gitlab
      > gl-code-quality-report.json
  artifacts:
    when: always
    reports:
      codequality: gl-code-quality-report.json
```

- The job reads the repo's `.claude/ocre-jelly.json`, so locales, the glossary, `severity` and `ignore_paths` apply in CI as they do locally.
- Hard findings show as **major**, and soft ones as **minor**.
- Inline markers (`ocre-jelly: ignore …`) silence a spot, in CI too.

## Fail the pipeline (optional)

Out of the box, the job reports and never fails. To fail on hard findings, add `--fail-on hard` to the `codedoc.py` command. Use `--fail-on soft` to fail on any finding.

## Access to the ocre-jelly repo

The clone uses the job's token. In the ocre-jelly project, allow the repos that run this job: **Settings → CI/CD → Job token permissions**, then add each project. You can also mirror ocre-jelly into your group, or vendor a pinned copy.

Pin a version with `--branch v0.1.0` on the clone, so a change on `main` never changes CI results unannounced.

## Check it locally

```bash
git diff main... | python3 $OJ/codedoc.py --diff --format gitlab | head
```
