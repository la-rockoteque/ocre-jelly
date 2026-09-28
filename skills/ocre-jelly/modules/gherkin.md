---
kind: rules
when: writing or editing Gherkin .feature files
default: auto
detect_files: *.feature, */*.feature
description: Gherkin / BDD scenario wording
---
## Gherkin
- One behavior per scenario. The scenario title says the outcome: "Rejects an expired token".
- Given is state, When is one action, Then is an observable result. Use one When per scenario.
- Write in the domain's words (glossary Terms), not UI mechanics: "When the requester submits the requisition", not "When I click the blue button".
- Write steps in the present tense, third person. Don't put "should" in Then; state the result.
- Put examples in `Scenario Outline` tables, not in copy-pasted scenarios.
