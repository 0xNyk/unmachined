# Design tells: the catalog of AI slop patterns

Contents: Root cause · Critical tells · Major tells · Minor tells ·
Second-order monoculture · 10-second scan

Score generated or existing UI against this catalog. Severity tiers:

- CRITICAL: instantly reads as AI-generated. Any single hit is a defect. Fix before shipping.
- MAJOR: strong tell. Two or more together read as AI. Fix unless the brief explicitly asks for it.
- MINOR: weak signal alone. Flag in clusters, not individually.

Scoring rule: no single tell is proof. One centered section or one rounded card is not slop.
Score clusters of co-occurring tells, weighted by severity. This is the false-positive guard:
detectors that fire on single tells flag human work constantly.

## Root cause: distributional convergence

Models sample the statistical center of their training data unless steered. Given no direction,
the same brief lands on the same purple gradient, the same Inter headline, the same three cards,
every time. The output is not broken, it is average, and average is the tell.

Three counter-strategies:

1. Direct attention per design dimension. Decide typography, color, motion, and background
   explicitly instead of asking for "a nice design".
2. Reference, don't clone. Name inspirations (an IDE theme, a cultural aesthetic, a specific
   era or material world) without prescribing enough detail to copy them.
3. Name the defaults to avoid. Explicit bans on known defaults measurably raise output
   quality, and help smaller models most.

## Critical tells

### Color

- Purple or indigo gradient hero; any blue-to-purple, purple-to-cyan, cyan-to-magenta, or
  orange-to-pink gradient scheme. Known as "AI purple" (provenance: Tailwind's bg-indigo-500
  default). The single most-cited community tell.
- Gradient headline text (background-clip: text over a gradient fill).
- Pure #000 or #fff as page ground or ink. Always tint with a trace of chroma.
- Aurora blobs, floating orbs, mesh-gradient backgrounds, decorative wavy SVG dividers.

### Typography

- Inter, Roboto, Open Sans, Poppins, Lato, Arial, Montserrat, or system-ui as the display
  font. system-ui as primary is the "I gave up on typography" signal. Space Grotesk is the
  convergence trap: every AI tool reaches for it as the safe alternative to Inter.
- Italic headers. Any italic h1-h6, and especially one italicized emphasis word inside an
  otherwise upright headline. One of the most reliable single tells. Headings are roman.

### Layout

- The 3-column icon-card feature grid: icon in a colored circle, bold title, two-line
  description, repeated three times symmetrically. The most recognizable AI layout.
- The AI nav: wordmark left, inline links, CTA button right, hairline bottom border.
- The AI footer: four link columns, social icon row, copyright line.
- Full-viewport centered hero: min-height 100vh with everything center-aligned.
- Card-in-card nesting. Nested cards are always wrong.
- Cookie-cutter section rhythm: hero, three features, testimonials, pricing, CTA, each
  section the same height and pattern. Two pages for two different briefs must not share
  this rhythm.

### Decoration and chrome

- Re-drawn UI chrome: hand-built fake browser bars, phone frames, terminal windows,
  code-block windows, div-built dashboard screenshots. The user's environment already
  supplies real chrome; fake chrome is the top code-level tell.
- Emoji glyphs (sparkles, rocket, lightning bolt and friends) as feature icons, step
  markers, list bullets, or pricing icons.

### Copy and content

- Invented metrics: "10x faster", "trusted by 50,000+ teams", "99.9% uptime",
  "+47% conversion". If the user did not supply a metric, do not invent one.

## Major tells

### Structure and layout

- Eyebrow on every section, and section-number eyebrows ("01 / FEATURES",
  "001 · Capabilities"). Appears in 55-95% of generations. A kicker used once, on purpose,
  reads as a brand decision. A kicker used everywhere reads as a template. Cap: 1 per 3
  sections.
- Tag-left/heading-right split section headers (small label one side, big headline the
  other, in every section).
- Centered-everything: text-align center on every heading, card, and section.
- Icon tiles in colored circles or rounded squares as section decoration.
- Glassmorphism without purpose: backdrop-blur as the default surface treatment.
- Zigzag image/text alternation three or more times in a row.
- Colored accent stripe on the left edge of cards (border-left: 3px solid accent) as
  decoration. Reserve the left rule for exactly one semantic role, or drop it.
- The hero-metric template: big number, small label, supporting stats, gradient accent.
- Bento grid as reflex; bento with empty filler cells (N items means exactly N cells).
- Ghost-card: 1px border plus a large soft box-shadow (blur 16px or more) on one element.
- Uniform bubbly border-radius on everything; radius of 32px or more on cards.

### Color and surface

- The premium-consumer palette cluster: warm beige/cream grounds (#f5f1ea, #fbf8f1,
  #efeae0 family) with brass, clay, or oxblood accents (#b08947, #b6553a, #9a2436 family)
  and espresso ink (#1a1714 family). The reflexive "premium" look; the brand disappears.
- The three named AI-default looks. Banned as defaults, allowed only when the brief asks:
  1. Warm cream ground (near #F4F1EA), high-contrast serif display, terracotta accent.
  2. Near-black ground, one saturated accent (acid-green or vermilion), nothing else.
  3. Broadsheet: hairline rules, zero border-radius, dense newspaper columns.
- Serif conflict resolution: serif display is allowed as a deliberate, justified choice;
  it is banned as the unconsidered "creative brief means serif" reflex. Fraunces and
  Instrument Serif are specifically flagged as trending-to-cliche.

### Copy and content

- Generic hero copy: "Welcome to X", "Your all-in-one solution", "Build the future",
  "Unlock the power of".
- Version labels in the hero: V0.6, BETA, INVITE-ONLY.
- Scroll cues: "Scroll to explore", bouncing chevrons, down arrows.
- Startup-cliche product names: Acme, Nexus, Pulse, SmartFlow.
- "Quietly in use at" social-proof tropes and logo walls inside the hero.
- Filler verbs as copy: Elevate, Unleash, Revolutionize, Seamless, Next-Gen. These are
  banned vocabulary, not synonyms.
- Duplicate-intent CTAs: "Get in touch" plus "Let's talk" plus "Contact us". One intent,
  one label, used everywhere.
- "Built for X" / "Designed for Y" marketing filler; "Get Started" and "Learn More" as
  the only CTA vocabulary.
- Decorative status dots; a blinking "live" or "AI" dot in the nav.
- Locale/time/weather strips ("LIS 14:23 · 18°C") and decoration text strips
  ("BRAND. MOTION. SPATIAL.") on marketing pages.
- Stat banners of fake-round numbers; badge or pill floating above the H1.
- Numbered 1-2-3 step sections when the content is not actually a sequence.
- All-caps micro-labels on every section (the uppercase-tracking eyebrow in another coat).
- Dark mode as an unconsidered default, usually paired with low-contrast grey body text
  that fails WCAG AA.

### Motion

- Infinite-loop fade-ins and perpetual ambient micro-animations everywhere.
- Uniform hover:scale-105 on every card and button; several simultaneous hover effects
  on one element.
- Bouncy or elastic easing on UI state changes; the default `ease` keyword everywhere.
- Animating layout properties (top, left, width, height, margin, padding).
- Focus rings that fade in; celebratory confetti or toast for routine visible actions.
- More than one marquee per page.
- Scroll-listener jank: window.addEventListener("scroll") or useState tracking scroll
  and mouse position (visible as stutter on mobile).

## Minor tells

- Placeholder names: Jane Doe, John Smith, Sarah Chan; generic avatars.
- z-index: 999 or 9999. Use a semantic z-index scale.
- 100vw widths (horizontal overflow once scrollbars exist).
- Straight (dumb) quotes and apostrophes in display copy.
- transition: all.
- h-screen heroes (iOS address bar jump); use min-height 100dvh.
- Middle-dot separator overuse (more than one per metadata line).
- Photo-credit captions as decoration; version footers (v1.4.2, Build 0048) on
  marketing pages.
- Lorem ipsum or "your text here" placeholder content.
- Two icon libraries mixed in one page; lucide-react as an unconsidered default.
- Display letter-spacing crushed tighter than -0.04em.
- Uniform 16px radius, identical 24px padding, and shadows at exactly 0.1 opacity across
  every component (the unedited-defaults fingerprint; each is fine alone, the triple is
  the signal).
- Pills or labels overlaid directly on images.
- Hand-rolled decorative SVG illustrations and sketchy doodle graphics where a real asset
  or plain type would do.
- Teal (#16d5e6-adjacent) as the accent on CTA, headline, focus ring, and chart fill at
  once: an accent chosen by tool default rather than by brand.
- Broken or hotlinked placeholder images (dead Unsplash URLs, picsum leftovers).

## Second-order monoculture

The fixes become tells. The first wave of anti-slop guidance pushed outputs off
purple-gradient-Inter, and unguided "fixed" outputs then converged, roughly 8 in 10, on
warm cream paper, a Fraunces-style serif, a terracotta accent, mono micro-labels, a corner
page counter, and a colored last word in the headline. That combination is now itself a tell.
Any two of those together is a smell; the full set is the tell.

The rule that follows: require variety across outputs, not just quality within one output.

- First-order check: could someone guess the palette and theme from the product category
  alone? Then it is the first training-data reflex. Rework it.
- Second-order check: could someone guess the aesthetic family from the category plus the
  known anti-references? Then it is the trap one tier deeper. Rework it again.
- Rotate deliberately across consecutive outputs: macrostructure, ground (light/dark/tinted),
  display style, and accent hue. Do not reuse the same serif or the same palette family in
  back-to-back projects.
- No fixed alternative is safe forever. This catalog is time-bound; refresh it by
  periodically generating an unguided sample set and cataloging what the model currently
  converges on.

## 10-second scan

Fastest checks first. Grep before you look, look before you judge.

1. Grep for purple/indigo/violet gradients: `gradient` near `indigo|violet|purple|#7c3aed|#8b5cf6|#6366f1`.
2. Grep font stacks: `Inter|Roboto|Open Sans|Poppins|Lato|Montserrat|system-ui|Space Grotesk`.
3. Grep `background-clip: text` (gradient headlines).
4. Grep `#000|#fff|black|white` as ground/ink tokens.
5. Grep `transition: all`, `z-index: 999`, `100vw`, `h-screen`.
6. Grep emoji codepoints in markup and invented-metric strings (`10x|99.9%|50,000+`).
7. Count feature cards: three identical icon-cards is a fail.
8. Look at nav and footer: wordmark-links-CTA-hairline nav, four-column footer.
9. Count eyebrows against sections; check for "01 /" numbering without a real sequence.
10. Check headings for italics, the hero for min-height 100vh centering, and cards for
    nesting.

If two or more CRITICAL groups hit, stop scanning and start fixing.
