"""France French: FranceTerme recommendations, espaces insécables before ; : ! ?"""
PARENT = "fr"
SUMMARY = "fr-FR: FranceTerme terms (courriel, mot-dièse, informatique en nuage); espace insécable avant ; : ! ?"
PREFER = {
    r"\bhashtags?\b": "mot-dièse",
    r"\bcloud computing\b": "informatique en nuage",
    r"\bphishing\b": "hameçonnage",
    r"\bstreaming\b": "diffusion en continu",
    r"\bpodcasts?\b": "podcast / balado (FranceTerme : audio à la demande)",
    r"\bmalwares?\b": "logiciel malveillant",
    r"\bupload(?:er)?\b": "téléverser",
}
# Missing (narrow) no-break space before ; : ! ? in French text
SOFT = {"typography": r"(?<=[\w»)])[;:!?](?=\s|$)"}
