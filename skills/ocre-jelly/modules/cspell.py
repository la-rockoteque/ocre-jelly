"""Render the glossary Terms as a cspell dictionary, one word per line."""
import re


def render(ctx: dict) -> str:
    words = {w for terms, *_ in ctx["rows"] for t in terms for w in re.findall(r"[^\W\d_][\w'-]*", t)}
    return f"# {ctx['mark']} from the ubiquitous-language glossary.\n" + "\n".join(sorted(words, key=str.lower)) + "\n"
