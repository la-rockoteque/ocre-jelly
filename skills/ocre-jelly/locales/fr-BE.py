"""Belgian French: septante and nonante; espace insécable before ; : ! ?"""
PARENT = "fr"
SUMMARY = "fr-BE: septante, nonante; espace insécable avant ; : ! ?"
PREFER = {r"\bsoixante-dix\b": "septante", r"\bquatre-vingt-dix\b": "nonante"}
SOFT = {"typography": r"(?<=[\w»)])[;:!?](?=\s|$)"}
