#!/usr/bin/env python3
"""Flag AI-writing candidates in text read from stdin.

Security posture, on purpose: stdlib only, no network, no subprocess, no
directory walking. Reads stdin, plus only the files named by --preserve
and --glossary.
All regexes are bounded (no nested unbounded quantifiers) to avoid ReDoS.

Usage:
  scan.py [--json] [--include-quoted] < text
  scan.py --glossary UBIQUITOUS-LANGUAGE.md < text
  scan.py --preserve original.txt < rewritten.txt
  scan.py --locale en-CA,fr-CA < text        paragraph language picks the locale
  scan.py --list-locales
  scan.py --selftest
"""
from __future__ import annotations

import argparse
import functools
import json
import re
import runpy
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True  # keep the installed plugin folder clean

MAX_BYTES = 1_000_000  # ponytail: hard cap, stream in chunks if long docs matter

STE_MAX_WORDS = 25  # ASD-STE100 descriptive limit; procedures are 20 (judge in context)

# Masked spans keep offsets stable so line numbers stay right.
MASKS = [
    re.compile(r"```.*?```", re.S),
    re.compile(r"`[^`\n]+`"),
    re.compile(r"(?m)^\s*>.*$"),
    re.compile(r"\"[^\"\n]{0,300}\"|“[^”\n]{0,300}”|«[^»\n]{0,300}»"),
]

PRESERVE = re.compile(
    r"https?://[^\s)>\]\"']+"
    r"|`[^`\n]+`"
    r"|\$?\d[\d,]*(?:\.\d+)?(?:%|[kKmMbB]\b|x\b)?"
    r"|\bv?\d+\.\d+(?:\.\d+)*\b"
    r"|\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+\b"  # multi-word proper nouns
)


def mask(text: str) -> str:
    for rx in MASKS:
        text = rx.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), text)
    return text


# ---- locales -----------------------------------------------------------------
# locales/<lang>.py holds a language's patterns; locales/<lang>-<REGION>.py extends
# it with spelling (SPELLING_STYLE), preferred terms (PREFER) and extra SOFT/HARD.

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
TAG_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")
DEFAULT_LOCALES = ("en", "fr")  # languages only, no regional checks, when none is configured
PARAGRAPH = re.compile(r"(?:[^\n]|\n(?!\s*\n))+")


@functools.lru_cache(maxsize=None)
def load_locale(tag: str) -> dict:
    if not TAG_RE.match(tag):
        raise ValueError(f"bad locale tag {tag!r}: use a form like en, en-CA, fr-FR")
    path = LOCALES_DIR / f"{tag}.py"
    if not path.exists():
        if "-" in tag:
            return {}  # unknown region: fall back to the language patterns only
        raise ValueError(f"no locale file for {tag!r} in {LOCALES_DIR}")
    return runpy.run_path(str(path))


def available_locales() -> list[str]:
    return sorted(p.stem for p in LOCALES_DIR.glob("*.py") if TAG_RE.match(p.stem))


REGISTERS = ("formal", "neutral", "casual")


@functools.lru_cache(maxsize=None)
def locale_patterns(tag: str, register: str = "neutral") -> tuple:
    """(severity, category, regex, suggestion or None) for one locale tag in one register."""
    lang = load_locale(tag.split("-")[0])
    region = load_locale(tag) if "-" in tag else {}
    reg = lang.get("REGISTER", {}).get(register, {})
    out = []
    for ns in (lang, region, reg):
        for sev in ("hard", "soft"):
            for cat, rx in ns.get(sev.upper(), {}).items():
                out.append((sev, cat, re.compile(rx, re.I), None))
    style = region.get("SPELLING_STYLE", {})
    endings = lang.get("SPELLING_ENDINGS", "")
    for cls, us, gb in lang.get("SPELLING", []):
        if cls in style:
            wrong, right = (gb, us) if style[cls] == "us" else (us, gb)
            out.append(("soft", "locale-spelling", re.compile(rf"\b{wrong}{endings}\b", re.I), (wrong, right)))
    for rx, prefer in region.get("PREFER", {}).items():
        out.append(("soft", "locale-term", re.compile(rx, re.I), prefer))
    off = set(reg.get("off", []))
    return tuple(p for p in out if p[1] not in off)


def detect_language(segment: str, tags: list[str]) -> str:
    """Pick the configured tag whose language's stopwords are most frequent; ties go to the first."""
    words = re.findall(r"[^\W\d_]+", segment.lower())
    best, best_score = tags[0], -1
    for tag in tags:
        stop = load_locale(tag.split("-")[0]).get("STOPWORDS", set())
        score = sum(w in stop for w in words)
        if score > best_score:
            best, best_score = tag, score
    return best


def suggestion(match: str, suggest) -> str:
    if isinstance(suggest, tuple):  # spelling: swap the stem, keep the ending and case
        wrong, right = suggest
        ending = match[len(wrong):]
        stem = right[:-1] if right.endswith("e") and ending[:1] in ("a", "e", "i") else right  # centre+ed -> centred
        fixed = stem + ending
        return f"{match} -> {fixed[0].upper() + fixed[1:] if match[0].isupper() else fixed}"
    return f"{match} -> {suggest}"


def register_for(tag: str, register: str | dict | None) -> str:
    if isinstance(register, dict):
        return register.get(tag, register.get(tag.split("-")[0], "neutral"))
    return register or "neutral"


def locale_hits(text: str, target: str, tags: list[str], protected: set[str], register=None) -> list[dict]:
    hits = []
    for para in PARAGRAPH.finditer(target):
        seg, base = para.group(), para.start()
        tag = detect_language(seg, tags)
        for sev, cat, rx, suggest in locale_patterns(tag, register_for(tag, register)):
            for m in rx.finditer(seg):
                span = text[base + m.start():base + m.end()].strip()
                if suggest is not None and span.lower() in protected:
                    continue  # a glossary Term keeps its spelling
                hits.append({"line": text.count("\n", 0, base + m.start()) + 1, "severity": sev,
                             "category": cat, "match": suggestion(span, suggest) if suggest else span})
    return hits


def scan(text: str, include_quoted: bool = False, aliases: dict[str, list[str]] | None = None,
         locales: list[str] | None = None, protected_terms: list[str] | None = None,
         register: str | dict | None = None) -> list[dict]:
    target = text if include_quoted else mask(text)
    tags = list(locales or DEFAULT_LOCALES)
    extra = [t for t in (protected_terms or []) if t.strip()]
    protected = {w.lower() for terms in (aliases or {}).values() for t in terms for w in re.findall(r"\w+", t)}
    protected |= {w.lower() for t in extra for w in re.findall(r"\w+", t)}
    if extra:  # a protected term is never an alias to avoid either
        aliases = {a: t for a, t in (aliases or {}).items() if a.lower() not in {x.lower() for x in extra}}
    hits = locale_hits(text, target, tags, protected, register)
    hits += long_sentences(text, target)
    hits += dash_paragraphs(text, target)
    hits += glossary_hits(text, target, aliases or {})
    return sorted(suppress(hits, text), key=lambda h: (h["line"], h["severity"]))


# ---- inline suppression -----------------------------------------------------
# `ocre-jelly: ignore [cat, cat]` covers the next non-blank line (or its own line as a
# trailing comment); `ocre-jelly: off` ... `ocre-jelly: on` covers a block. Any comment syntax.

MARKER = re.compile(r"ocre-jelly:\s*(ignore|off|on)\b([^\n]*)", re.I)
COMMENT_OPENER = re.compile(r"^\s*(?:<!--|/\*+|\*|//+|#+|--|;+|%+|'|\")?\s*$")


def suppressions(text: str) -> dict[int, set[str] | None]:
    """Line number -> suppressed categories (None = all)."""
    lines = text.split("\n")
    out: dict[int, set[str] | None] = {}
    off = False

    def add(n: int, cats: set[str] | None) -> None:
        if n in out and (out[n] is None or cats is None):
            out[n] = None
        else:
            out[n] = (out.get(n) or set()) | (cats or set()) if cats is not None else None

    for i, line in enumerate(lines, start=1):
        m = MARKER.search(line)
        if off:
            add(i, None)
        if not m:
            continue
        kind = m.group(1).lower()
        if kind == "off":
            off = True
            add(i, None)
        elif kind == "on":
            off = False
            add(i, None)
        else:
            rest = re.sub(r"(?:-->|\*/)\s*$", "", m.group(2)).strip()
            cats = {c.strip() for c in re.split(r"[,\s]+", rest) if re.fullmatch(r"[a-z][a-z0-9-]*", c.strip())} or None
            add(i, None)  # the marker line itself
            if COMMENT_OPENER.match(line[:m.start()]):  # a marker on its own line: the next non-blank line
                nxt = next((j for j in range(i, len(lines)) if lines[j].strip()), None)
                if nxt is not None:
                    add(nxt + 1, cats)
            else:
                add(i, cats)
    return out


def suppress(hits: list[dict], text: str) -> list[dict]:
    rules = suppressions(text) if "ocre-jelly:" in text.lower() else {}
    return [h for h in hits if not (h["line"] in rules and (rules[h["line"]] is None or h["category"] in rules[h["line"]]))]


EM_DASH_MIN = 3  # one em-dash proves nothing; a habit shows as several per paragraph


def dash_paragraphs(text: str, target: str) -> list[dict]:
    hits = []
    for m in re.finditer(r"(?:[^\n]|\n(?!\s*\n))+", target):
        n = m.group().count("\u2014")
        if n >= EM_DASH_MIN:
            hits.append({"line": text.count("\n", 0, m.start()) + 1, "severity": "soft",
                         "category": "em-dash", "match": f"{n} em-dashes in one paragraph"})
    return hits


def long_sentences(text: str, target: str) -> list[dict]:
    # ponytail: naive split on .!? ; and ": " plus blank lines; misreads "e.g." and decimals
    hits = []
    target = re.sub(r"[;:](?=\s)", ".", target)  # a clause break counts as a sentence break; same length
    target = re.sub(r"(?m)^[ \t]*\|.*$", lambda m: " " * len(m.group()), target)  # table rows aren't sentences
    for m in re.finditer(r"[^.!?\n]+(?:\n(?!\s*\n)[^.!?\n]+)*", target):
        n = len(m.group().split())
        if n > STE_MAX_WORDS:
            hits.append({"line": text.count("\n", 0, m.start()) + 1, "severity": "soft",
                         "category": "ste-length", "match": f"{n} words: {' '.join(m.group().split())[:60]}..."})
    return hits


def missing_tokens(original: str, rewritten: str) -> list[str]:
    seen = dict.fromkeys(m.group() for m in PRESERVE.finditer(original))
    return [tok for tok in seen if tok not in rewritten]


def _terms(cell: str) -> list[str]:
    # "**Backorder** / **Backordered**" -> both; "**Assumption** (Hypothèse)" -> Assumption
    bold = [t.strip("` ") for t in re.findall(r"\*\*([^*]+)\*\*", cell)]
    return bold or [re.sub(r"\([^)]*\)", "", cell).strip("*`_ ")]


def _aliases(cell: str) -> list[str]:
    # drop notes: "Line item (too generic)", "`#1042` _(the former form)_"
    cell = re.sub(r"_?\([^)]*\)_?", "", cell)
    out = []
    for part in re.split(r",|;|\s/\s|\bor\b", cell):
        if re.search(r"\b(?:is fine|is ok|allowed)\b", part, re.I):
            continue  # a note that the word is acceptable, not an alias
        quoted = re.findall(r'"([^"]+)"|\u201c([^\u201d]+)\u201d|\u00ab\s*([^\u00bb]+?)\s*\u00bb', part)
        out += [next(g for g in q if g) for q in quoted] or [part]
    parts = (p.strip("*`_ .") for p in out)
    return [p for p in parts if p and p not in {"—", "–", "-"}]


def glossary_rows(md: str) -> list[tuple[list[str], list[str], list[str]]]:
    """(terms, aliases, labels) per row of every table with a "term" and an "avoid" column.

    labels come from any "label" column, e.g. "UI label (fr-CA)": « Brouillon ».
    """
    rows = []
    header = None  # (term_col, avoid_col) of the current table; None between tables
    for line in md.splitlines():
        if not line.lstrip().startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue  # separator row
        if header is None:
            heads = [c.lower() for c in cells]
            header = (next((i for i, h in enumerate(heads) if "term" in h), -1),
                      next((i for i, h in enumerate(heads) if "avoid" in h), -1))
            label_cols = [i for i, h in enumerate(heads) if "label" in h]
            width = len(heads)
            continue
        term_col, avoid_col = header
        if min(term_col, avoid_col) >= 0 and len(cells) > max(header):
            # a "|" inside a cell adds columns, so read the avoid column from the end
            labels = [x.strip(" \u00ab\u00bb\"*`_") for i in label_cols if i < avoid_col
                      for x in re.split(r"\s/\s|,", cells[i]) if x.strip(" \u00ab\u00bb\"*`_\u2014-")]
            rows.append((_terms(cells[term_col]), _aliases(cells[avoid_col - width]), labels))
    return rows


def load_glossary(md: str) -> dict[str, list[str]]:
    """Map each avoided alias to its canonical term(s).

    An alias that is itself a Term or a UI label is skipped: it is valid in its own context,
    so only a reader can judge it.
    """
    rows = glossary_rows(md)
    known = {t.lower() for terms, _, labels in rows for t in terms + labels}  # Terms and UI labels are valid words
    aliases: dict[str, list[str]] = {}
    for terms, avoided, _ in rows:
        for alias in avoided:
            if alias.lower() in known:
                continue
            targets = aliases.setdefault(alias, [])
            targets += [t for t in terms if t not in targets]
    return aliases


def glossary_hits(text: str, target: str, aliases: dict[str, list[str]]) -> list[dict]:
    hits = []
    for alias, terms in aliases.items():
        for m in re.finditer(rf"(?<!\w){re.escape(alias)}(?!\w)", target, re.I):
            hits.append({"line": text.count("\n", 0, m.start()) + 1, "severity": "soft",
                         "category": "glossary-alias", "match": f"{m.group()} -> {' | '.join(terms)}"})
    return hits


def load_settings(no_config: bool) -> dict:
    """The layered project config (config.py), applied to this module's thresholds."""
    global STE_MAX_WORDS, EM_DASH_MIN
    if no_config:
        return {"locales": [], "severity": {}, "protected_terms": [], "glossary": None, "_root": None, "register": None}
    import config
    cfg = config.load()
    STE_MAX_WORDS = cfg["thresholds"]["sentence_words"]  # ponytail: process-wide knobs, set once at startup
    EM_DASH_MIN = cfg["thresholds"]["em_dash_per_paragraph"]
    return cfg


def default_glossary(cfg: dict) -> str | None:
    if not cfg.get("_root"):
        return None
    import config
    path = config.find_glossary(Path(cfg["_root"]), cfg)
    return str(path) if path else None


def parse_locales(value: str | None) -> list[str] | None:
    return [t.strip() for t in value.split(",") if t.strip()] if value else None


def read_capped(stream) -> str:
    data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        sys.exit(f"input exceeds {MAX_BYTES} bytes")
    return data


def selftest() -> None:
    slop = "Here's the thing: we delve into the rich tapestry.\nThe future looks bright\u2014truly\u2014and\u2014boldly."
    cats = {h["category"] for h in scan(slop)}
    assert {"throat-clearing", "ai-vocabulary", "significance-inflation",
            "generic-conclusion", "em-dash"} <= cats, cats
    assert scan("We shipped v2.1 on 2024-03-15 and cut p95 latency by 40ms.") == []
    assert scan('She wrote "let that sink in" as a joke.') == []
    assert scan('She wrote "let that sink in" as a joke.', include_quoted=True)
    assert scan("```\nlet's dive in\n```") == []
    assert missing_tokens("Revenue hit $47.3M at Acme Corp, see https://x.io/a", "Revenue hit $47M") \
        == ["$47.3M", "Acme Corp", "https://x.io/a"]
    assert missing_tokens("Up 23% in v2.1.0", "v2.1.0 is up 23%") == []
    assert {"ste-wordy"} <= {h["category"] for h in scan("We utilize caching in order to scale.")}
    assert [h["category"] for h in scan(" ".join(["word"] * 30) + ".")] == ["ste-length"]
    assert not any(h["category"] == "ste-length" for h in scan(" ".join(["word"] * 25) + "."))
    assert not any(h["category"] == "ste-length" for h in scan("; ".join([" ".join(["w"] * 12)] * 3) + "."))
    gl = load_glossary(
        "## Orders\n\n| Term | Definition | Aliases to avoid |\n|---|---|---|\n"
        "| **Order** (Commande) | A placed purchase | Purchase, Basket (too generic), `#12` _(old form)_ |\n"
        "| **Draft** / **Drafted** | Not yet placed | Pending, Order |\n"
        "| **Pending** | Awaiting payment | — |\n\n"
        "| Term (code) | UI label | Definition | Aliases to avoid |\n| --- | --- | --- | --- |\n"
        "| **Status** | « Statut » | Badge | State, Phase |\n\n"
        "| Term | Definition |\n|---|---|\n| **Summary** | « Sommaire » |\n")
    assert gl == {"Purchase": ["Order"], "Basket": ["Order"], "#12": ["Order"],
                  "State": ["Status"], "Phase": ["Status"]}, gl
    assert [h["match"] for h in scan("Each purchase is stored.", aliases=gl)] == ["purchase -> Order"]
    gl = load_glossary("| Term | Definition | Aliases to avoid |\n|---|---|---|\n"
                       "| **Login screen** | Uses `a|b` pipes | \"login page\" is fine, not \"portal\" |\n"
                       "| **Recall** | Take back | \"Cancel\", \u00ab Retirer \u00bb |\n")
    assert gl == {"portal": ["Login screen"], "Cancel": ["Recall"], "Retirer": ["Recall"]}, gl
    # locales: per-paragraph language, regional spelling and terms, glossary Terms protected
    mixed = "We organise the colour palette.\n\nIl est important de noter que le courriel part afin de valider."
    cats = [(h["line"], h["category"]) for h in scan(mixed, locales=["en-US", "fr-CA"])]
    assert (1, "locale-spelling") in cats and (3, "throat-clearing") in cats and (3, "ste-wordy") in cats, cats
    assert [h["match"] for h in scan("Colours ship.", locales=["en-US"]) if h["category"] == "locale-spelling"] == ["Colours -> Colors"]
    assert not [h for h in scan("We organize the color palette.", locales=["en-US"]) if h["category"] == "locale-spelling"]
    centred = [h["match"] for h in scan("It is centered and centering.", locales=["en-GB"]) if h["category"] == "locale-spelling"]
    assert centred == ["centered -> centred", "centering -> centring"], centred
    assert not [h for h in scan("Fulfilled items travel.", aliases={"x": ["Fulfilled"]}, locales=["en-GB"])]
    assert [h["match"] for h in scan("Envoyez un e-mail.", locales=["fr-CA"]) if h["category"] == "locale-term"] == ["e-mail -> courriel"]
    assert [h["category"] for h in scan("Attention: le serveur!", locales=["fr-FR"])].count("typography") == 2
    assert not [h for h in scan("Attention: le serveur!", locales=["fr-CA"]) if h["category"] == "typography"]
    assert not scan("Le libellé « Il est important de noter que » reste.", locales=["fr-CA"]), "guillemets not masked"
    assert scan("Here's the thing: it works.")  # default en,fr still catches English
    casual = "Salut! Check tes scores, pis dis-moi si ça fait du sens."
    assert "anglicism" in {h["category"] for h in scan(casual, locales=["fr-CA"])}
    assert "anglicism" not in {h["category"] for h in scan(casual, locales=["fr-CA"], register={"fr": "casual"})}
    assert "register-informal" in {h["category"] for h in scan(casual, locales=["fr-CA"], register={"fr": "formal"})}
    assert "register-informal" in {h["category"] for h in scan("We don't ship it.", register="formal")}
    assert "throat-clearing" in {h["category"] for h in scan("Salut! Il est important de noter que ça marche.", register={"fr": "casual"})}
    for tag in available_locales():
        for r in REGISTERS:
            locale_patterns(tag, r)  # every shipped locale compiles in every register
    assert not [h for h in scan("Colours ship.", locales=["en-US"], protected_terms=["Colours"])]
    assert not scan("Each purchase is stored.", aliases={"purchase": ["Order"]}, protected_terms=["purchase"])
    assert not scan("Don't treat missing evidence as an AI tell.") and scan("As an AI language model, I cannot.")
    assert not [h for h in scan("| " + " | ".join(["cell words here"] * 12) + " |") if h["category"] == "ste-length"]
    doc = ("<!-- ocre-jelly: ignore throat-clearing -->\nHere's the thing: kept on purpose.\nHere's the thing: flagged.\n"
           "Let's dive in. <!-- ocre-jelly: ignore -->\n<!-- ocre-jelly: off -->\nGreat question!\n<!-- ocre-jelly: on -->\nI hope this helps.\n")
    assert [(h["line"], h["category"]) for h in scan(doc)] == [(3, "throat-clearing"), (8, "chatbot-artifact")], scan(doc)
    assert [h["line"] for h in scan("# ocre-jelly: ignore em-dash\n\nHere's the thing.\n")] == [3], "wrong category suppressed"
    # ReDoS guard: pathological input must return fast
    scan("isn't " + "a" * 200_000)
    print("selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--include-quoted", action="store_true", help="also scan quotes, blockquotes, code")
    ap.add_argument("--glossary", metavar="MD", help="flag avoided aliases from a UBIQUITOUS-LANGUAGE.md table")
    ap.add_argument("--preserve", metavar="ORIGINAL", help="report tokens from ORIGINAL missing in stdin")
    ap.add_argument("--locale", help="comma list of locale tags, e.g. en-CA,fr-CA (default: config, else en,fr)")
    ap.add_argument("--no-config", action="store_true", help="ignore .claude/ocre-jelly*.json and ~/.claude/ocre-jelly.json")
    ap.add_argument("--list-locales", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.list_locales:
        for tag in available_locales():
            print(f"{tag:<6} {load_locale(tag).get('SUMMARY', '')}")
        return

    started = time.perf_counter()
    text = read_capped(sys.stdin)

    if args.preserve:
        with open(args.preserve, encoding="utf-8") as f:
            missing = missing_tokens(read_capped(f), text)
        if not args.no_config:
            import telemetry
            telemetry.record("gate", gate="preserve", ok=not missing, missing=len(missing))
        if args.json:
            print(json.dumps({"missing": missing}))
        else:
            print("\n".join(f"MISSING {t}" for t in missing) or "preserve ok")
        sys.exit(1 if missing else 0)

    cfg = load_settings(args.no_config)
    aliases = {}
    glossary = args.glossary or default_glossary(cfg)
    if glossary:
        with open(glossary, encoding="utf-8") as f:
            aliases = load_glossary(read_capped(f))
    locales = parse_locales(args.locale) or cfg["locales"] or None
    hits = scan(text, args.include_quoted, aliases, locales, cfg["protected_terms"], cfg.get("register"))
    if cfg["severity"]:
        import config
        hits = config.apply_severity(hits, cfg["severity"])
    if not args.no_config:
        import telemetry
        telemetry.record("scan", started, hits, locales=locales, chars=len(text), glossary=bool(aliases))
    if args.json:
        print(json.dumps(hits, indent=2))
    else:
        for h in hits:
            print(f"L{h['line']:<4} {h['severity']:<4} {h['category']:<22} {h['match']!r}")
        hard = sum(h["severity"] == "hard" for h in hits)
        print(f"-- {len(hits)} candidates ({hard} hard). Candidates only; confirm in context.")


def _record_error(e: BaseException) -> None:
    if "--no-config" not in sys.argv:
        import telemetry
        telemetry.error(Path(sys.argv[0]).stem, e)


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:  # bad locale tag or glossary: a clear message, not a traceback
        _record_error(e)
        sys.exit(f"{Path(__file__).name}: {e}")
    except Exception as e:
        _record_error(e)
        raise
