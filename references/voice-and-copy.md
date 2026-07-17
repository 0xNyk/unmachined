# Voice and copy: microcopy, tone, and honest claims

Sources: Mailchimp Voice & Tone (open-sourced), Atlassian Design System, Slack, Intuit,
Shopify Polaris, Google Material and developer style, GOV.UK content design, VOICE.md spec,
MindStudio voice profiles. Text tells in text-tells.md apply to every surface here first;
this file adds the rules specific to product copy and voice.

## UX microcopy rules

- Name things from the user's side. Sentences start with the user's goal (Google), not the
  system's process: "To save your changes, press Save", not "The system requires saving".
- Active voice, present tense. The user does things; the interface responds.
- Errors don't apologize and are never vague. No "Oops!", no "Something went wrong" with
  no next step. Say what happened, why, and what to do next, in that order. Never blame
  the user.
- Action labels are verb + object: "Save changes", "Delete project", not bare "OK",
  "Submit", "Yes". Keep the same label for the same action through the entire flow; if the
  button says "Create workspace", the confirmation says "Workspace created", not
  "Environment ready".
- Empty states invite action. State what belongs here and give the first step:
  "No projects yet. Import a repo to get started." Never a bare "No data".
- Links describe their destination: "View billing history", not "click here" or a bare
  "Learn more".
- No generic CTAs everywhere. A page where every button reads "Get Started" or
  "Learn More" is a tell. Name the value: "Start free scan", "See the pricing math".
- Silent success over celebratory toasts. Confirm quietly and get out of the way. Reserve
  delight for genuine milestones; add the wink only when the user feels success, pride, or
  relief (Atlassian: "give flowers, not puppies").
- Copy should sound like something a person would actually say (Shopify Polaris). Read
  every label aloud.
- Clear beats clever, always (Mailchimp: "always more important to be clear than
  entertaining"). Omit unnecessary words, but don't be robotic (Slack).
- Dial personality DOWN in AI-generated copy. Intuit tested this: "breezy or funny comments
  didn't test well... AI models have no ability to read the room." Wit is for
  human-authored surfaces.

## Voice profile structure

- Constant voice, variable tone (Mailchimp): "You have the same voice all the time, but
  your tone changes." Voice is who the product is; tone adapts to the moment.
- Emotional-state -> tone matrix (Atlassian): before writing, name the reader's likely
  state. Frustrated at an error: practical, calm, zero jokes. Curious at onboarding:
  encouraging, brief. Proud at success: warmer, one light note allowed. Dial boldness,
  optimism, and practicality up or down per state; never change the underlying voice.
- The "X not Y" contrast device: define 3-5 named voice attributes, each with one contrast
  and a do/don't example pair. "Confident but not cocky. Witty but never silly. Helpful
  but not overbearing." The negation forces a rejection test on every draft.
- Per-project voice profile (a compact VOICE.md, 400-700 words so it fits a system prompt):

  ```
  voice: 3-5 attributes, each phrased "X not Y", each with a do/don't pair
  spectra: formality, energy, warmth, complexity (mark a point on each)
  case: sentence case for headings and UI text; caps policy (e.g. no ALL-CAPS lines,
        or exactly one caps hook line, per brand)
  banned claim terms: fastest, lowest latency, guaranteed, #1, best-in-class,
        market-leading, unbeatable (exempt only with a cited measurement)
  banned phrases: the brand's own list (e.g. game-changer, supercharge, seamless,
        unlock, revolutionary, blazing fast)
  brand spellings: canonical product names; internal names never said publicly
  lexicon: protected terms (never rewrite) and forbidden terms, each with a reason
  tones: per-surface adjustments (error, onboarding, success, marketing, support)
  formatting tokens: date format, number style (spell out one-nine, numerals for 10+)
  beliefs: 3-5 stated positions; every piece must trace to at least one
  ```

- Teach voice by exemplar: keep 8-12 annotated samples of real on-voice writing
  (MindStudio). Output gets checked against the samples, not the internet average.
- Store the profile in the repo and version it. Voice that lives in a PDF drifts; a
  lint-able file doesn't. Export the forbidden lexicon as Vale existence rules for
  deterministic review.

## Honest copy principles

- Replace buzzwords with plain words (GOV.UK, with its rationale: "we lose trust if we
  write government buzzwords and jargon"). The core table:

  | Banned | Write instead |
  |---|---|
  | deliver | make, create, provide (only pizzas get delivered) |
  | leverage, utilize, deploy | use |
  | facilitate | say specifically what you do |
  | key (adjective) | important, or cut it |
  | streamline | simplify |
  | tackle, combat | solve, fix, reduce |
  | liaise, collaborate | work with |
  | overarching | cut it |
  | one-stop shop | name the actual thing |
  | agenda | plan |
  | purchase | buy |
  | assist | help |
  | approximately | about |

- No false urgency. No countdown timers, "only 2 left", or "low stock" unless tied to real
  inventory. Fake scarcity is a dark pattern and a legal exposure (UK CMA enforcement).
- Real numbers or labelled placeholders. Never invent a metric, testimonial, or user count
  to fill a layout. Ship "users: [pending launch]" over a fabricated "10,000+ users".
- No superlatives or absolutes without a measurement. "Fastest" requires a number, a unit,
  and a method.
- Define jargon on first use. Prefer the short word: buy, help, about, start.
- Substance over slogan: "seamless" is a placeholder for a missing feature description.
  Replace it with the concrete claim or the number that proves it.

## Brand voice (keep this layer thin)

Brand voice sits on top of the honesty and microcopy rules; it never overrides them.

- Never let character overwhelm content (Slack). If the joke costs clarity, cut the joke.
- Resolve the wit conflict by authorship: Mailchimp and Slack encourage dry humor in
  human-authored copy; Intuit's tested finding says AI-generated copy should stay plain
  and warm. Default AI output to plain.
- One canonical banned-lexicon per brand, machine-checkable, not vibes. Per-brand
  profiles may override fields (case policy, allowed hype level) without forking the rules.

## Detection heuristic

Run these five checks first on any product copy:

1. Buttons and links: any bare "Get Started", "Learn More", "Submit", or "click here"
   without a named object or value?
2. Errors: any apology, blame, or "Something went wrong" without a stated next step?
3. Claims: any fastest/#1/guaranteed/best-in-class without a cited measurement, or any
   urgency not tied to real inventory?
4. Consistency: does the same action keep the same label across the whole flow, and does
   heading case follow the profile (sentence case unless the brand says otherwise)?
5. Evidence: any invented stats, fake testimonials, or unlabelled placeholder numbers in
   stat blocks?
