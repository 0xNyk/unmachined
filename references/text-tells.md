# Text tells: the merged catalog of AI writing patterns

Merged from blader/humanizer (28k stars, ported from Wikipedia's "Signs of AI writing",
WikiProject AI Cleanup), theclaymethod/unslop (313-phrase lexicon, deterministic scanners,
benchmarked +4.2pts on objective holdout), jalaalrd/anti-ai-slop-writing, a production
content gate, a Vale style pack, GOV.UK, and community tells discourse.
Empirical grounding: CMU arXiv:2502.12150 (ICML 2025) shows LLM idiosyncrasies live in
word-level distributions and survive rewriting, translation, and summarization. Lexical
blacklists alone are not enough. Fix structure and cadence, not just words.

Contents: How to apply this file · Vocabulary kill list · Banned phrases and
sentence patterns · Structural and cadence tells · Punctuation and formatting
tells · Honesty rules · Numeric thresholds · The rewrite loop · Detection heuristic

## How to apply this file

- Severity tiers: CRITICAL = any occurrence fails review. MAJOR = flag every occurrence;
  two or more distinct hits fail. MINOR = advisory; clean up in the editing pass.
- Score clusters, not single hits. Detectors false-positive on real human writing at 11-12%
  rates. One tell is suspicion; three co-occurring tells is a verdict.
- Mask before matching: skip fenced code and inline code, and reduce Markdown links to
  their labels. Scan blockquotes and quoted prose because they may be copy under review.
- Rule files are exempt: this catalog names banned terms by necessity. Never lint ban-list
  definitions as prose.
- Register guard: in legal, medical, security, and technical text, hedges and absolutes are
  content, not filler. "May cause drowsiness" and "never store secrets" must survive editing.
- Do no harm: if the text is already clean, change nothing. Do not invent problems.

## Vocabulary kill list

### CRITICAL: any occurrence = fail

These words almost never appear in natural writing and consistently mark AI output.

- delve, delves, delving, "delve into", "dive into"
- tapestry ("a rich tapestry of"), rich mosaic
- testament ("stands as a testament to")
- game changer, game-changing, "this changes everything"
- "the real unlock", "the unlock is", "the real question is", "the real move",
  "what really matters", "one thing is clear", "without a doubt"
- motivational filler: "unlock your potential", "become the best version",
  "dream big"
- ever-evolving, "evolving landscape" (any figurative landscape)
- treasure trove
- watershed moment, pivotal moment, "enduring legacy", "indelible mark"
- multifaceted
- myriad
- unwavering
- beacon, symphony, realm ("in the realm of") when figurative
- demystify
- embark ("embark on a journey")
- "at its core"
- "in today's fast-paced world", "in today's digital landscape", and every
  "In today's [adjective] [noun]" variant
- "as technology continues to evolve"

### MAJOR: hype and marketing fluff

Replace each with a concrete claim or a number (Vale pack).

- groundbreaking, revolutionary, revolutionize, redefine, disruptive
- cutting-edge, state-of-the-art, next-generation, next-level
- world-class, best-in-class, industry-leading, mission-critical
- transformative, unprecedented, remarkable, stunning, breathtaking, mind-blowing
- seamless, seamlessly, seamless experience (the single most diluted word in SaaS copy)
- innovative solution, robust platform, robust solution, comprehensive solution,
  scalable solution, powerful capabilities
- blazing fast, blazingly fast
- supercharge, supercharged
- epic (non-literal), "a hidden gem", must-visit
- "unlock the power of", unleash, ignite
- "take it to the next level", "elevate your", "streamline your"

### MAJOR: corporate buzzwords

- leverage, leveraging (as verbs), utilize, utilizing (write "use"), facilitate,
  commence (write "start")
- synergy, synergize, paradigm, holistic, ecosystem (figurative)
- empower, empowering, harness, harnessing, foster, fostering
- bolster, garner, spearheading, navigating (figurative)
- "move the needle", "circle back", "touch base", "deep dive", "low-hanging fruit"
- "bridge the gap", "pain points", "value add", "value proposition" (casual use)
- thought leader, thought leadership
- "moving forward", "rest assured", "it goes without saying"
- paramount, aforementioned, endeavour, encompass

### MAJOR: significance inflation and puffery

- crucial, pivotal, intricate, intricacies, interplay, meticulous, meticulously
- nuanced (as filler), profound, vibrant, dynamic
- comprehensive (about one's own output), robust (outside engineering)
- nestled, "in the heart of", renowned, boasts
- showcase, showcases, showcasing, underscore, underscores, highlighting, emphasizing, enhancing
  (especially as sentence-tail "-ing" analysis: see structural tells)

### MINOR: hedges and filler

Cut or commit to the claim.

- just, really, very, actually, basically, literally, simply
- obviously, clearly, somewhat, relatively, arguably
- "in order to" -> to, "due to the fact that" -> because, "at this point in time" -> now
- "has the ability to" -> can, "is able to" -> can, "in the event that" -> if
- "a large number of" -> many, "the vast majority of" -> most, "in close proximity to" -> near
- "for all intents and purposes" -> effectively, "in terms of", "with regard to",
  "on a daily basis", "needless to say"
- Nominalizations (spot by -tion, -sion, -ment, -ance, -ence): "make a decision" -> decide,
  "perform an analysis" -> analyze, "reach an agreement" -> agree,
  "take into consideration" -> consider
- Redundant pairs: past history, future plans, end result, final outcome, advance planning,
  unexpected surprise, completely eliminate, basic fundamentals, first began, true fact,
  free gift, added bonus
- Expletive openers: "There are three reasons that...", "It is important to note that...",
  "It should be noted that..."

## Banned phrases and sentence patterns

### Empty transitions and throat-clearing

- "It's worth noting that", "It's important to note that", "It's important to remember"
- "Let's dive in", "Let's unpack", "Let's explore", "Let's break this down",
  "Let's break it down", "Let's take a closer look", "Without further ado", "Buckle up"
- "Here's what you need to know"
- "When it comes to", "In the ever-evolving landscape of"
- "Here's the thing", "Here's the deal", "The uncomfortable truth is", "Let me be clear"
- "Picture this", "Imagine a world where"
- "Whether you're a seasoned developer or just starting out", "from beginners
  to experts", "no matter your experience" (reader-flattery brackets)
- "This is where X comes in", "now more than ever"

### AI conclusions

- "In conclusion", "Overall," (as a starter), "Ultimately,", "In essence", "In a nutshell"
- "At the end of the day", "The bottom line is", "the key takeaway"
- Generic upbeat closers: "the future looks bright", "exciting times ahead"
- Moralizing codas: "Ultimately, this reminds us that..."
- Grandiose closings that shift from the specific to the abstract

### Negation-redefinition (the "ChatGPT sentence")

- "It's not just X, it's Y" / "This isn't just X, it's Y" (Rolling Stone's name for it)
- "Not only... but also", "not about X, it's about Y"
- Contrastive definitions: "X isn't a Y. It's a Z."
- Tailing negations: "..., no guessing", "..., no fluff"
- Negative parallelism runs: "No X. No Y. Just Z."
- Carve-out: imperative corrections survive ("Use pnpm, not npm." is fine).

### False ranges and fake sweep

- "From X to Y" when the range is rhetorical, not real ("from the Big Bang to dark matter")
- Sweeping categorical claims: "every team", "most people", "most teams", "no team can",
  "100% of", "nobody talks about", "here's what people miss", "what most people miss"

### Rule of three as carousel

AI defaults to threes: triplet adjectives, three parallel clauses, three examples, three
benefits. Break the pattern. Use two, four, one, five (jalaalrd).

### Personification of abstractions

- "the data tells a story", "the numbers speak for themselves", "paints a clear picture"
- "the math doesn't care", "the market has spoken"
Give agency to people, not abstractions.

### Vague attribution and weasel words

- "Experts argue", "Studies show that", "Some critics argue", "Industry reports
  suggest", "Observers have noted", "analysts predict"
Name the source with a citation, or cut the claim.

### Emphasis crutches and manufactured drama

- "Full stop.", "Let that sink in.", "Read that again.", "Make no mistake",
  "This cannot be overstated."
- Rhetorical self-Q&A: "Why does this matter? Because...", "What changed? The math did."
- Cliffhanger fragments: "[Noun]. That's it. That's the [thing]."
- Two-beat imperative slogans as headers: "Emit 1,100 tokens. Ship 237KB."

### Banned sentence openers

Certainly, / Absolutely, / Sure, / Moreover, / Furthermore, / Additionally, / Interestingly, /
Notably, / Importantly, / Indeed, / Undoubtedly, / Ultimately, / In essence, / In summary, /
Overall, / Firstly, Secondly, Thirdly / "However, it's important to" /
"As a [role], I..." (real people just say the thing) / "Honestly? It depends..."

### Chatbot artifacts

Any of these in published text is a CRITICAL fail:

- "Great question!", "That's a great point!", "Excellent point!", "I'd be happy to"
- "I hope this helps", "Let me know if you have any questions"
- "As an AI", "as a language model", "as of my last training update" (cutoff disclaimers)
- Reasoning-chain leaks: "Let me think step by step", "Here's my thought process"
- Leftover markup: oaicite, oai_citation, contentReference, turn0search0, :::writing
- "I hope this email finds you well", "As per my last email",
  "Please don't hesitate to reach out"

### Sycophancy and echo openers

CRITICAL in replies and reviews:

- "You're absolutely right", "You're right", "Exactly right", "That's exactly",
  "This is exactly", "Spot on", "Great point", "Well said", "So true",
  "Couldn't agree more", "100%", "This!"
- Echo pattern: opening by restating what the other person just said, then rephrasing it

## Structural and cadence tells

This section sets ceilings, not technique — the positive craft that produces good rhythm in the first place (periodic/cumulative sentence theory, sound devices, polysyndeton/asyndeton, read-aloud cadence passes, line-level enjambment) and the persuasion maxims bounded by this file's limits belong in a companion positive-craft module (rhythm/persuasion technique) inside whatever authoring skill produced the draft.

- Uniform sentence length: no three consecutive sentences of the same length. The single
  most measurable AI detection signal (jalaalrd). Rhythm check: classify sentences
  S (<=8 words), M (<=20), L (>20); the same S/M/L trigram repeating 3+ times is monotony.
- Parataxis and staccato: short sentence. Then another. Then another. Reads like a poem,
  signals AI. Also banned as OVERCORRECTION: do not replace slop with "Not X. Y." punch
  fragments and runs of tiny sentences; that is anti-slop register, itself a tell (unslop).
- Punch-line paragraph endings: flag when more than ~35% of paragraphs end with a
  <=5-word sentence.
- Repetitive sentence openings: same first word starting 3+ sentences.
- Identical paragraph structure: topic -> explanation -> example -> transition, every time.
  Let paragraphs end abruptly. Not every paragraph needs a summary or transition.
- Fragmented headers: a heading followed by a one-line restatement of the heading.
  Every H2 should be a claim that advances the argument, never a category label.
- Preview-recap loops and the summary sandwich: announcing the sections, then delivering
  them, then recapping them. Outline-following is the strongest arrangement-level tell.
- Signposting: announcing what you are about to do instead of doing it ("Let's look at
  three reasons why...").
- Elegant variation: cycling synonyms to avoid repeating a word (the city / the metropolis /
  the urban center). Repeat the plain word.
- Copula avoidance: "serves as a", "stands as a", "boasts a", "boasts an",
  "features", "represents", "marks"
  where is/are/has would do. LLMs substitute elaborate constructions for simple copulas.
- Superficial -ing analysis tails: ", highlighting the importance of...", ", underscoring
  the need for...", ", reflecting a broader shift...". Cut the tail or make the claim directly.
- Formulaic sections: "Challenges and Future Prospects", "despite challenges... continues
  to thrive".
- Hedging stacks and the hedging seesaw: "could potentially possibly", equal-weight
  both-sidesism. Acknowledge a counterpoint in one sentence maximum, then commit.
- Connective paragraph scaffolds: paragraphs that open with "However," / "Moreover," /
  "Additionally," in sequence.
- Excessive bullets: never more than 5-7 in a row, and make them uneven in length.

## Punctuation and formatting tells

### Em-dash policy (RESOLVED)

Sources conflict: blader/humanizer cuts all em-dashes, jalaalrd allows 1 per 500 words,
unslop defaults to zero, production gates hard-block. Resolution, binding for this ecosystem:
em-dashes and en-dashes are BANNED in body text. Use a single hyphen with spaces, a comma,
a period, or parentheses instead. Before finishing, scan the text for the em-dash and
en-dash characters; any hit means the draft is not done.

Narrow exception, the only permitted use: '—' may appear as a labelled empty-value placeholder in a stat block or table cell (for example "views: —"), never in running prose.

### Budgets and casing

- Exclamation marks: max one per 1,000 words.
- Ellipses: max one per piece, only when genuinely trailing off. Never as a transition.
- Rhetorical questions: max two per piece.
- Semicolons: allowed and encouraged where natural; never as a dash substitute crutch.
- Bold: no mechanical boldface, no bolding random phrases for emphasis, no bolded
  "key takeaways".
- Inline-header vertical lists are banned: "**Performance:** one sentence." repeated.
- Headings: sentence case, never Title Case Every Word.
- Emoji: none in headings, none as bullets or section markers, none as icons. 1-2 inside
  a social post is acceptable where the register allows.
- Curly quotes: use straight quotes in code, config, and plain-text surfaces.
- Hyphenated-pair overuse: data-driven, cross-functional, end-to-end, real-time,
  high-quality applied with perfect consistency is a tell. Humans are inconsistent here.

### Surface leaks

- No markdown in plain-text surfaces: no # headers, ** bold, or backticks in emails, DMs,
  SMS, or social posts. Instant AI flag.
- No hashtag stacks (0-2, integrated into the sentence). No thread-emoji or "Thread:" openers.

### Template artifacts (CRITICAL: hard block)

Scaffolding the model left behind. Never publishable:

- {placeholder}, <template slot>, "____", [bracket scaffold lines]
- TODO, TBD, FIXME
- lorem ipsum
- Meta-instructions: "Write a ... using the hook", raw template field names left unrendered
  (suggested_body, generated_title)
- Dangling "…:" lines, bare ellipsis lines, empty ">" quote lines

## Honesty rules

All CRITICAL. These outrank style.

- Never invent statistics, studies, or data. Fake specificity kills trust faster than
  vagueness.
- Never fabricate quotes or put words in a real person's mouth.
- Never present a hypothetical as a real anecdote. Mark it: "imagine...", "suppose...".
- No superiority claims (fastest, lowest latency, guaranteed, #1, number one, best-in-class,
  market-leading, unbeatable) unless the text cites an actual measurement: number + unit,
  a percentile, or a named methodology (the benchmark-claim gate).
- Facts are sacred in any rewrite: numbers, names, dates, URLs, quotes, code identifiers,
  units, and scope words must survive. Magnitude-aware: $47.3M must not drift to $47.3B,
  150 km must not become 150 miles (unslop).
- Real numbers or labelled placeholders. Never fill a stat block with plausible inventions.

## Numeric thresholds

| Check | Limit |
|---|---|
| Opener sentence | <=18 words (mobile scan speed) |
| Body sentence | <=25 words; flag >30 |
| Paragraph (short-form) | <=3 sentences, <=4 lines on mobile |
| Opening paragraph | <=2 sentences |
| Flesch-Kincaid grade (long-form) | 6-8 |
| Flesch Reading Ease (long-form) | 60-80 |
| Consecutive same-length sentences | <3 |
| Rhetorical questions | <=2 per piece |
| Em/en dashes in body text | 0 |
| Exclamation marks | <=1 per 1,000 words |
| Ellipses | <=1 per piece |
| Bullets in a run | <=5-7, uneven |
| Hashtags (social) | 0-2, integrated |
| Punch-line paragraph endings | <=35% of paragraphs |
| Counterpoint hedging | 1 sentence max |

## The rewrite loop

The core process (blader/humanizer, benchmarked structure gates: unslop +4.2pts holdout):

1. Draft the rewrite. Preserve coverage and length: if the original has five paragraphs,
   the rewrite has five paragraphs. Every fact, number, name, and quote survives.
2. Ask yourself: "What makes the below so obviously AI generated?" Answer in brief bullets.
3. Revise once more, fixing each named tell. Then scan for the em-dash (U+2014) and
   en-dash (U+2013) characters; any hit means the draft is not done.
4. If a structural problem persists after a rewrite, do not re-prompt with "fix the
   structure". No model self-checks macro shape. Name the specific finding (e.g. "four
   paragraphs open with However") and regenerate against that directive (unslop).
5. Know when to stop: for encyclopedic, technical, legal, and reference text, neutral and
   plain IS the correct human voice. Do not inject opinions or first person there.

### Voice and soul

Avoiding AI patterns is only half the job. Sterile, voiceless writing is just as obvious
as slop (humanizer).

- Have opinions. Don't just report facts; react to them.
- Vary your rhythm. Short punchy sentences. Then longer ones that take their time getting
  where they're going.
- Allow some mess. Fragments. An occasional run-on because the thought isn't done.
  Paragraphs that just stop.
- Use "I" where the register permits. Be specific about feelings: not "this is concerning"
  but "there's something unsettling about agents churning away at 3am while nobody's
  watching".
- Be specific, not general: "you paste your treasury address and it tells you you'll run
  out of USDC in 47 days" beats "powerful analytics capabilities" (jalaalrd).
- Use contractions. Use the less obvious word; AI picks the highest-probability token.
- Write like a builder who noticed something useful, not a consultant naming a trend.
- Apply every rule silently. Never mention the guidelines in the output.

## Detection heuristic

Run these five checks first; they catch most slop in seconds:

1. Grep for the em-dash (U+2014) and en-dash (U+2013). Zero tolerance in body text.
2. Grep the CRITICAL vocab list plus "not just", "isn't just", "it's about" constructions.
3. Rhythm scan: three consecutive same-length sentences, or a repeating S/M/L pattern.
4. Opener scan: paragraphs starting with Moreover/Furthermore/Additionally/However, and
   headings followed by a one-line restatement.
5. Artifact scan: {placeholder}, TODO, lorem ipsum, "Great question", "I hope this helps",
   oaicite, and any markdown in a plain-text surface.
