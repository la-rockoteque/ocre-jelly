#!/usr/bin/env python3
"""Prepare feedback for the ocre-jelly author: a feature request, a bug or a comment.

It never sends anything. It builds the text, prints it, and builds a link to
the feedback form with the text pre-filled. With --open, it opens that link in
your browser, where you read it and click Submit yourself.

Usage:
  feedback.py --kind feature --message "Support Spanish (es-MX)" --why "Half our docs are Spanish"
  feedback.py --kind feedback < note.txt
  feedback.py ... --open          open the pre-filled form in the browser
  feedback.py ... --no-context    leave out the version and locale line
  feedback.py --selftest

The form comes from the `feedback` config (form_url, entry). A team can point it
at its own Google Form, or set "enabled": false.

Security posture: stdlib only. No network access: the browser, not this script,
talks to the form. The context line holds only the ocre-jelly version, the
configured locales and the Python version; never paths, code or repo names.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import urllib.parse
import webbrowser
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import config  # noqa: E402

KINDS = {"feature": "Feature request", "bug": "Bug", "feedback": "Feedback"}
MAX_URL = 7000  # ponytail: conservative; longer text opens the empty form and prints the text to paste
MAX_TEXT = 5000


def plugin_version() -> str:
    try:
        manifest = HERE.parent.parent.parent / ".claude-plugin" / "plugin.json"
        return json.loads(manifest.read_text(encoding="utf-8")).get("version", "unknown")
    except (OSError, ValueError):
        return "unknown"


def compose(kind: str, message: str, why: str = "", locales: list[str] | None = None,
            context: bool = True, contact: str = "") -> str:
    message = message.strip()
    if not message:
        raise ValueError("the message is empty")
    lines = [f"[{KINDS[kind]}] {message.splitlines()[0][:120]}"]
    rest = message.splitlines()[1:]
    if rest:
        lines += ["", *rest]
    if why.strip():
        lines += ["", f"Why: {why.strip()}"]
    if context:
        lines += ["", f"Context: ocre-jelly {plugin_version()}, locales {', '.join(locales or []) or 'none'}, "
                      f"Python {platform.python_version()}"]
    if contact.strip():
        lines += [f"Contact: {contact.strip()}"]
    text = "\n".join(lines)
    if len(text) > MAX_TEXT:
        raise ValueError(f"the feedback is {len(text)} characters; keep it under {MAX_TEXT}")
    return text


def form_link(form_url: str, entry: str, text: str) -> tuple[str, bool]:
    """(link, prefilled). Falls back to the plain form when the pre-filled link would be too long."""
    parsed = urllib.parse.urlsplit(form_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"feedback.form_url must be an https URL, got {form_url!r}")
    query = urllib.parse.urlencode({"usp": "pp_url", f"entry.{entry}": text})
    link = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, ""))
    if len(link) > MAX_URL:
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", "")), False
    return link, True


def selftest() -> None:
    text = compose("feature", "Support Spanish (es-MX)", "Half our docs are Spanish", ["en-CA"], True)
    assert text.startswith("[Feature request] Support Spanish (es-MX)") and "Why: Half our docs" in text
    assert "Context: ocre-jelly" in text and "locales en-CA" in text and "/Users" not in text
    assert "Context:" not in compose("feedback", "Nice tool", context=False)
    assert compose("bug", "Title\nmore detail").splitlines()[2] == "more detail"
    link, pre = form_link("https://docs.google.com/forms/d/e/X/viewform?usp=send_form", "123", "a b & c")
    assert pre and link == "https://docs.google.com/forms/d/e/X/viewform?usp=pp_url&entry.123=a+b+%26+c", link
    link, pre = form_link("https://docs.google.com/forms/d/e/X/viewform", "123", "é" * 2000)
    assert not pre and link.endswith("/viewform")
    for bad in ("http://example.com/form", "javascript:alert(1)", "file:///etc/passwd"):
        try:
            form_link(bad, "1", "x")
            raise AssertionError(f"accepted {bad}")
        except ValueError:
            pass
    try:
        compose("feature", "   ")
        raise AssertionError("empty accepted")
    except ValueError:
        pass
    print("selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kind", choices=tuple(KINDS), default="feedback")
    ap.add_argument("--message", help="the request or comment; default: stdin")
    ap.add_argument("--why", default="", help="the use case, for a feature request")
    ap.add_argument("--contact", default="", help="optional: how the author can reach you")
    ap.add_argument("--no-context", action="store_true", help="leave out the version, locales and Python line")
    ap.add_argument("--open", action="store_true", help="open the pre-filled form in the browser")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    cfg = config.load()
    fb = cfg["feedback"]
    if not fb.get("enabled", True):
        sys.exit("feedback is turned off in this repo's ocre-jelly config (feedback.enabled: false)")
    message = args.message if args.message is not None else sys.stdin.read()
    text = compose(args.kind, message, args.why, cfg.get("locales"), not args.no_context, args.contact)
    link, prefilled = form_link(fb["form_url"], fb["entry"], text)

    print("---- feedback text (nothing is sent until you click Submit in the form) ----")
    print(text)
    print("----")
    host = urllib.parse.urlsplit(link).netloc
    if prefilled:
        print(f"Pre-filled form on {host}:\n{link}")
    else:
        print(f"The text is too long to pre-fill. Open the form on {host}, then paste the text above:\n{link}")
    if args.open:
        webbrowser.open(link)


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        sys.exit(f"feedback.py: {e}")
