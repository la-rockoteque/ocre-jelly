"""French base patterns. Regional files (fr-CA, fr-FR, fr-BE, fr-CH) extend this one.

HARD: almost always slop outside quotes. SOFT: confirm in context.
Apostrophes match both ' and ’.
"""
A = "['’]"  # apostrophe
P = r"[^.!?\n]{1,80}"

SUMMARY = "French. Prose authority: references/ste-fr.md (ISO 24495-1 langage clair, Français Rationalisé principles)."
AUTHORITY = "references/ste-fr.md"
STOPWORDS = set("le la les des une un est sont et du de pour que qui dans avec pas sur au aux ce cette ou par ne se".split())

HARD = {
    "throat-clearing": rf"\b(?:il est (?:important|essentiel|crucial|intéressant) de (?:noter|souligner|rappeler|mentionner)|il convient de (?:noter|souligner)|force est de constater|plongeons(?: ensemble)?(?: dans| au cœur)|décortiquons|explorons ensemble|voyons (?:ensemble|de plus près)|entrons dans le vif du sujet)\b",
    "emphasis-crutch": rf"\b(?:et c{A}est là (?:tout l{A}enjeu|que tout se joue)|point final\.|on ne le dira jamais assez|relisez bien)",
    "chatbot-artifact": rf"\b(?:j{A}espère que cela (?:vous )?(?:aide|aidera)|excellente question|bonne question|n{A}hésitez pas à|je (?:suis|serais) ravi de vous aider|avec plaisir !)",
    "cutoff-disclaimer": rf"\b(?:selon mes (?:dernières )?(?:données|connaissances)|en tant qu{A}(?:IA|intelligence artificielle|modèle de langage))\b",
    "significance-inflation": rf"\b(?:témoigne de|véritable révolution|change la donne|marque un tournant|pierre angulaire|riche tapisserie|dans un monde en (?:constante|perpétuelle) évolution|à l{A}ère du numérique|dans le paysage (?:actuel|numérique|en constante évolution))\b",
    "generic-conclusion": r"\b(?:l'avenir s'annonce (?:prometteur|radieux)|seul l'avenir nous le dira|une chose est sûre|les possibilités sont infinies)\b",
    "ai-vocabulary": r"\b(?:tapisserie|multifacette|foisonnant)\b",
}

SOFT = {
    "binary-contrast": rf"\b(?:ce n{A}est pas{P}[.,]\s+c{A}est|il ne s{A}agit pas (?:seulement|simplement) de|non seulement{P}mais (?:aussi|également))\b",
    "ing-tail": r",\s+(?:soulignant|mettant en (?:lumière|valeur|évidence)|illustrant|témoignant|reflétant|favorisant|ouvrant la voie)\b",
    "vague-attribution": r"\b(?:les experts (?:s'accordent|affirment|estiment)|de nombreuses études|selon certains|il est largement reconnu|beaucoup pensent)\b",
    "copula-avoidance": r"\b(?:sert de|se positionne comme|fait office de|joue un rôle (?:clé|crucial|essentiel|central|majeur))\b",
    "promotional": r"\b(?:de pointe|haut de gamme|révolutionnaire|inégalé|sans précédent|à couper le souffle|au cœur de|de premier plan|fluide et intuitive?|incontournable|inédit|synergie)\b",
    "filler-adverb": r"(?:^|[.!?]\s+|\n)(?:notamment|fondamentalement|essentiellement|concrètement|en fin de compte|en définitive|au final),",
    "reader-steering": r"\b(?:voici pourquoi|voici ce qu'il faut retenir|à retenir|pourquoi c'est important)\b",
    "recap-coda": r"(?:^|\n)\s*(?:en (?:résumé|conclusion|somme|bref)|pour conclure|pour résumer),",
    "colon-reveal": r"\b(?:la (?:clé|réponse|réalité|leçon)|le (?:secret|vrai problème)) (?:est|réside) :",
    "list-inflation": r"\b(?:voici \d+ (?:raisons|astuces|choses|façons)|(?:trois|cinq|\d+) points clés)\b",
    # Wordy phrasing (langage clair): prefer the short form
    "ste-wordy": rf"\b(?:afin de|dans le cadre de|au niveau de|procéder à|effectuer une?|être en mesure de|en vue de|par le biais de|au moyen de|il y a lieu de|de (?:manière|façon) \w+|faire en sorte que|permettre de)\b",
}

# Register: "neutral" is the base. "casual" drops checks that only formality needs;
# "formal" adds soft checks for informal markers. AI-tell checks stay on in every register.
REGISTER = {
    "casual": {"off": ["anglicism"]},
    "formal": {"SOFT": {"register-informal": rf"\b(?:tu|toi|ton|ta|tes|t{A}(?=[aeiouhé]))\b|\b(?:pis|chu|faque|genre)\b"}},
}
