# AI writing patterns

`scan.py` flags **hard** patterns (almost always slop outside quotes) and **soft** ones (need context). The scanner's categories match the headings below.

## Hard

| Category | Examples | Fix |
|---|---|---|
| throat-clearing | "Here's the thing:", "The truth is", "Let's dive in", "Let's unpack", "It's no secret that" | Delete; start at the point |
| emphasis-crutch | "Let that sink in", "Full stop.", "Make no mistake", "Read that again", "This cannot be overstated" | Delete |
| chatbot-artifact | "I hope this helps", "Great question", "Certainly!", "Happy to help", "Let me know if you need" | Delete |
| cutoff-disclaimer | "As of my last update", "based on my training data" | Delete, or state the actual date/source |
| reasoning-artifact | "Let me think step by step", "Here's my thought process" | Delete |
| significance-inflation | "stands as a testament", "pivotal moment", "rich tapestry", "indelible mark", "cornerstone of" | Say what actually happened |
| generic-conclusion | "The future looks bright", "Only time will tell", "Exciting times lie ahead", "One thing is certain" | Delete, or end on the last real fact |
| ai-vocabulary | "delve", "tapestry", "multifaceted", "intricate", "interplay", "paramount", "burgeoning", "garner", "underscore(s)" | Plain word: "look at", "complex", "important", "growing", "get", "show" |

## Soft (confirm in context)

| Category | Examples | Protect when |
|---|---|---|
| binary-contrast | "It's not X. It's Y.", "not just about X", "not only X but also Y" | The contrast corrects a real misconception stated nearby |
| ing-tail | ", highlighting…", ", showcasing…", ", underscoring…", ", paving the way…" | The participle adds a concrete fact |
| vague-attribution | "Experts argue", "Many believe", "Studies show" (no source) | A source is named nearby |
| copula-avoidance | "serves as a", "stands as a", "functions as a" | Literal ("serves as a proxy server") |
| promotional | "nestled", "boasts", "world-class", "state-of-the-art", "breathtaking" | Quoted marketing copy under review |
| filler-adverb | Sentence-initial "Importantly,", "Crucially,", "Fundamentally,", "Interestingly," | Rarely |
| reader-steering | "Here's why", "Here's what stood out", "worth exploring", "Why this matters" | Rarely |
| colon-reveal | "The key is:", "The answer is:", "The reality is:" | Genuine definition or list follows |
| false-range | "from X to Y, from A to B", "spanning everything from" | The range is real and bounded |
| list-inflation | "Here are 5 reasons", "three key takeaways" | The genre is literally a listicle the user wants |
| em-dash | Any "—"; 3+ per paragraph is a strong signal | The author's established style |
| fragmentation | ". That's it.", ". And that's the point." | Dialogue or deliberate voice |

## Not detectable by regex (read for these)

- **Synonym cycling**: "the company… the firm… the organization" for one referent. Pick one name.
- **Tricolon habit**: every list has exactly three items, adjective triples ("fast, reliable, and scalable").
- **Uniform rhythm**: every sentence the same length and shape.
- **Recap coda**: closing paragraph that restates the piece or moralizes. Delete it when it adds no fact.
- **Slogan headings**: "Speed, Reimagined." Replace with what the section actually says.
- **Tool personification**: "the pipeline decides", "the system knows". Name the actual mechanism.
- **Hedge stacking**: "may potentially", "could possibly help to".
- **Bold/emoji sprinkling** in body prose.

## Protection rules

A match never authorizes an edit by itself. Protect:

- Text inside quotes, blockquotes and code (the scanner masks these by default).
- Literal uses: "the struggle is real" in a meme analysis, "delve" in a mining report.
- Domain terms: "robust" in statistics, "leverage" in finance.
- Stock business words backed by a mechanism, definition, action or measure in context. "Game-changer" stays flagged unless the text says what changes.
- Punctuation, vocabulary or cadence alone prove neither defect nor authorship. Don't flag a single em-dash in otherwise clean prose.
