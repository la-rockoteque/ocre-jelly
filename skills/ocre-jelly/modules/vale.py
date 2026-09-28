"""Render the ubiquitous-language aliases as a Vale substitution rule."""
import json
import re


def render(ctx: dict) -> str:
    lines = [
        f"# {ctx['mark']} from the ubiquitous-language glossary. Re-export after editing it.",
        "extends: substitution",
        "message: \"Use '%s' instead of '%s' (ubiquitous language).\"",
        "level: warning",
        "ignorecase: true",
        "swap:",
    ]
    for alias, terms in sorted(ctx["aliases"].items(), key=lambda kv: kv[0].lower()):
        # keys are regexes in Vale; json.dumps gives a valid YAML double-quoted scalar
        lines.append(f"  {json.dumps(re.escape(alias))}: {json.dumps(' or '.join(terms))}")
    return "\n".join(lines) + "\n"
