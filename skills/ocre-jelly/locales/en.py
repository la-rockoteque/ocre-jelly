"""English base patterns. Regional files (en-US, en-GB, ...) extend this one.

HARD: almost always slop outside quotes. SOFT: confirm in context.
Keys are categories; the same category can exist in several languages.
"""
P = r"[^.!?\n]{1,80}"  # bounded clause, never crosses a sentence

SUMMARY = "English. Prose authority: ASD-STE100 (references/ste100.md)."
AUTHORITY = "references/ste100.md"
STOPWORDS = set("the a an and of to is are was were be for with that this it on in as by not or from at which".split())

HARD = {
    "throat-clearing": r"\b(?:here'?s the (?:thing|deal|problem)|the (?:uncomfortable )?truth is|let me be clear|let'?s be real|it'?s no secret(?: that)?|let'?s (?:dive in|unpack|break (?:this|it) down)|this is where it gets interesting|here'?s what nobody tells you)\b",
    "emphasis-crutch": r"\b(?:let that sink in|full stop\.|make no mistake|read that again|this cannot be overstated)",
    "chatbot-artifact": r"\b(?:i hope this helps|great question|happy to help|let me know if you (?:need|have|want))\b|(?:^|\n)\s*certainly!",
    "cutoff-disclaimer": r"\b(?:as of my (?:last|knowledge)|based on my training data|as an ai(?: language model)?,?\s+i)\b",
    "reasoning-artifact": r"\b(?:let me think step by step|here'?s my thought process|to approach this systematically)\b",
    "significance-inflation": r"\b(?:stands as a testament|a testament to|pivotal moment|indelible mark|rich tapestry|cornerstone of|ever-evolving landscape|in today'?s fast-paced)\b",
    "generic-conclusion": r"\b(?:the future looks bright|only time will tell|exciting times (?:lie )?ahead|one thing is certain)\b",
    "ai-vocabulary": r"\b(?:delve[sd]?|delving|tapestry|multifaceted|intricate|interplay|paramount|burgeoning|garner(?:s|ed)?|underscores?|underscoring)\b",
}

SOFT = {
    "binary-contrast": rf"\b(?:isn'?t|aren'?t|is not|are not){P}[.,]\s+(?:it'?s|they'?re)\b|\bit'?s not just about\b|\bnot only{P}but also\b|\bnot merely{P}but\b",
    "ing-tail": r",\s+(?:highlighting|showcasing|underscoring|fostering|demonstrating|reflecting|signaling|paving the way)\b",
    "vague-attribution": r"\b(?:experts (?:argue|say|agree)|many believe|some critics|studies show|it is widely regarded|industry reports)\b",
    "copula-avoidance": r"\b(?:serves as an?|stands as an?|functions as an?)\b",
    "promotional": r"\b(?:nestled|boasts an?|world-class|state-of-the-art|breathtaking|must-visit|a hidden gem|game-?changer|cutting-edge|seamless(?:ly)?)\b",
    "filler-adverb": r"(?:^|[.!?]\s+|\n)(?:interestingly|importantly|crucially|fundamentally|notably|ultimately),",
    "reader-steering": r"\b(?:here'?s why|here'?s what (?:stood out|caught my eye|'?s interesting)|worth (?:exploring|a look|your time)|why this matters)\b",
    "colon-reveal": r"\bthe (?:answer|secret|key|trick|truth|reality|takeaway|lesson) (?:is|was):",
    "false-range": rf"\bfrom{P}to{P},\s+from\b|\bspanning everything from\b",
    "list-inflation": r"\b(?:here are \d+ (?:reasons|things|ways|lessons)|(?:three|five|\d+) key takeaways)\b",
    "fragmentation": r"\.\s+(?:that'?s it\.|and that'?s the (?:point|thing)\.)",
    # ASD-STE100 vocabulary: prefer the simple verb
    "ste-wordy": r"\b(?:utili[sz](?:e|es|ed|ing)|commenc(?:e|es|ed|ing)|facilitat(?:e|es|ed|ing)|in order to|prior to|carry out an?|perform an?|make use of|is able to|a number of)\b",
}

# Spelling pairs by class: (class, US stem, British stem). A regional file sets
# SPELLING_STYLE = {class: "us" | "gb"}; the other side's stems become soft
# `locale-spelling` hits. Stems take the endings in SPELLING_ENDINGS.
SPELLING_ENDINGS = r"(?:e|es|ed|ing|s|er|ers|ation|ations|able|ful|ite|ites|ist|ists)?"
SPELLING = [
    ("our", "color", "colour"), ("our", "favor", "favour"), ("our", "honor", "honour"),
    ("our", "labor", "labour"), ("our", "neighbor", "neighbour"), ("our", "behavior", "behaviour"),
    ("our", "flavor", "flavour"), ("our", "humor", "humour"), ("our", "rumor", "rumour"),
    ("our", "harbor", "harbour"), ("our", "vapor", "vapour"), ("our", "rigor", "rigour"),
    ("our", "armor", "armour"), ("our", "endeavor", "endeavour"), ("our", "savor", "savour"),
    ("re", "center", "centre"), ("re", "liter", "litre"), ("re", "fiber", "fibre"),
    ("re", "theater", "theatre"), ("re", "caliber", "calibre"), ("re", "somber", "sombre"),
    ("ise", "organiz", "organis"), ("ise", "realiz", "realis"), ("ise", "recogniz", "recognis"),
    ("ise", "prioritiz", "prioritis"), ("ise", "optimiz", "optimis"), ("ise", "customiz", "customis"),
    ("ise", "authoriz", "authoris"), ("ise", "initializ", "initialis"), ("ise", "serializ", "serialis"),
    ("ise", "normaliz", "normalis"), ("ise", "finaliz", "finalis"), ("ise", "summariz", "summaris"),
    ("ise", "categoriz", "categoris"), ("ise", "minimiz", "minimis"), ("ise", "maximiz", "maximis"),
    ("ise", "utiliz", "utilis"), ("ise", "apologiz", "apologis"), ("ise", "synchroniz", "synchronis"), ("ise", "standardiz", "standardis"), ("ise", "visualiz", "visualis"),
    ("ise", "analyz", "analys"), ("ise", "paralyz", "paralys"),
    ("ll", "traveled", "travelled"), ("ll", "traveling", "travelling"), ("ll", "canceled", "cancelled"),
    ("ll", "canceling", "cancelling"), ("ll", "modeled", "modelled"), ("ll", "modeling", "modelling"),
    ("ll", "labeled", "labelled"), ("ll", "labeling", "labelling"), ("ll", "signaled", "signalled"),
    ("ll", "leveled", "levelled"), ("ll", "fueled", "fuelled"), ("misc", "gray", "grey"), ("misc", "aluminum", "aluminium"), ("misc", "defense", "defence"), ("misc", "offense", "offence"),
    ("misc", "catalog", "catalogue"), ("misc", "judgment", "judgement"), ("misc", "mold", "mould"),
    ("misc", "plow", "plough"), ("misc", "skeptic", "sceptic"), ]
# ponytail: word lists, not suffix rules. Pairs whose other spelling is also a valid
# word (emphasis, check, tire, program, enrolled) are left out; every spelling hit is soft.
