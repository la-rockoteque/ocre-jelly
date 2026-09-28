"""Swiss French: septante, huitante (Vaud, Valais, Fribourg), nonante; guillemets « » without inner spaces are common."""
PARENT = "fr"
SUMMARY = "fr-CH: septante, huitante, nonante."
PREFER = {r"\bsoixante-dix\b": "septante", r"\bquatre-vingts?\b(?!-)": "huitante", r"\bquatre-vingt-dix\b": "nonante"}
