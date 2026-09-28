"""Québec French: OQLF usage (Banque de dépannage linguistique, Grand dictionnaire terminologique)."""
A = "['’]"
PARENT = "fr"
SUMMARY = "fr-CA: OQLF usage. courriel, clavarder, fin de semaine, infonuagique, balado; avoid anglicisms (céduler, faire du sens, à l'effet que)."
# Anglicisms the OQLF advises against in formal writing. Soft: register decides.
SOFT = {
    "anglicism": (
        rf"\b(?:cédul(?:e|er|é|ée|és|ées)|cancell(?:e|er|é|ée)|(?:faire|fait|fais|font|faisait|ferait) du sens|à l{A}effet que|"
        r"adresser (?:un|le|ce|les|des) (?:problème|enjeu)s?|en termes de|"
        r"supporter (?:le|la|les|un|une) (?:projet|équipe|client|décision)s?|"
        r"(?:au|en) meilleur de (?:ma|notre|leur) connaissance|"
        r"canceller|booker|checker|forwarder|flusher)\b"
    ),
}
PREFER = {
    r"\be-?mails?\b": "courriel",
    r"\bspams?\b": "pourriel",
    r"\bchats?(?= (?:en ligne|en direct|web))|\bchatter\b": "clavardage / clavarder",
    r"\bweek-?ends?\b": "fin de semaine",
    r"\bparkings?\b": "stationnement",
    r"\bpodcasts?\b": "balado",
    r"\bhashtags?\b": "mot-clic",
    r"\bselfies?\b": "égoportrait",
    r"\bphishing\b": "hameçonnage",
    r"\bcookies?\b(?= (?:de|du|tiers|techniques?|web))": "témoin (de connexion)",
    r"\bcloud\b": "infonuagique / nuage",
    r"\bupload(?:er)?\b": "téléverser",
    r"\bfaire du shopping\b": "magasiner",
}
