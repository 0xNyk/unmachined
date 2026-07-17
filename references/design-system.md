# Design system: the constructive rules

What to do instead of the defaults. Pair with design-tells.md: that file bans, this file
builds. Every rule here is a decision to make on purpose; the tell is never the pattern
itself, it is the pattern chosen by reflex.

Contents: Typography · Color · Layout and spacing · Interface copy · Motion ·
The three dials · Mobile hard floor · The self-critique loop

## Typography

### Pairing

- Pick a deliberate display + body pairing before writing any code. The canonical shape is
  2 + 1: two main families (display and body) plus one optional mono or utility outlier
  used in at most two slots. Three families is the ceiling. Four is slop.
- Pair on a contrast axis: serif display with geometric sans body, characterful display
  with mono data face, or one variable family stretched across extreme weights.
- Serif is allowed as a deliberate, justified choice and banned as the unconsidered
  "creative brief means serif" reflex. Avoid Fraunces and Instrument Serif; both are
  trending-to-cliche. If serif, pick one you can defend for this brief.
- Never Inter, Roboto, Open Sans, Poppins, Lato, Arial, or system-ui as display. Do not
  swap in Space Grotesk as the safe alternative; that is the convergence trap.

### Weight and style

- Commit to weight extremes: 100-200 against 800-900. Weight 400 next to weight 600 reads
  as a default setting.
- Headings and display type are always roman (font-style: normal), h1 through h6. No
  italicized emphasis word inside an upright headline.
- Display letter-spacing floor: never tighter than -0.04em. -0.02 to -0.03em is plenty.
- All-caps text gets 5-12% extra letterspacing and stays under one line.

### Scale and measure

- Pick one type-scale ratio and hold it: 1.25 (major third) or 1.333 (perfect fourth) for
  standard hierarchy; up to 1.5 or 1.618 for dramatic editorial work.
- Body text 15-25px on the web. Line spacing 120-145% of the point size (body line-height
  1.5-1.65; display 1.05-1.2, with an absolute floor of 1.0 for all-caps display).
- Measure 45-90 characters including spaces; default max-width: 65ch.
- Size hero type by copy length, not by template:
  - Self-written headlines: 7 words or fewer, 50 characters or fewer.
  - 21-50 characters: full display size.
  - 51-90 characters: one step down from display.
  - Over 90 characters: rewrite the headline, or cap at a mid-size heading token.
- Headline never wraps past 2 lines. Use text-wrap: balance on h1-h3, text-wrap: pretty
  on prose.

## Color

### Tokens

- Define the palette as OKLCH tokens in CSS custom properties on :root. 4-6 named values
  covering paper, ink, neutrals, and accent.
- Lock the tokens. Every color and every font-family declaration in the artifact
  references a named token. Inline hex, rgb(), or oklch() values outside :root are
  mid-render improvisation and are not allowed.

### Neutrals and grounds

- Micro-tint every neutral. No zero-chroma grey as paper: minimum 0.005 chroma, typically
  0.005-0.015, tinted toward the palette's anchor hue.
- Paper lightness: L 96-98% in light mode, 12-16% in dark mode. Ink: L 16-22% light,
  92-96% dark. Never pure #000 or #fff.
- Dark versus light is never a default. Write one sentence about who uses this, where,
  under what ambient light; if the sentence does not force the answer, it is not concrete
  enough yet.

### Accent

- One chromatic accent per page, maximum two. Everything else is neutral.
- Accent footprint: 3% or less of any viewport, hard cap 5% (atmospheric background
  washes may go higher, by decision, not by default).
- Accent chroma 0.12-0.22; keep saturation under 80%. Dominant color with sharp accents
  beats a timid, evenly distributed palette.
- Never grey text on a colored background: keep the hue of the background and adjust
  lightness and saturation instead.

### Contrast: the deterministic gate

- WCAG 2.2 AA is the hard pass/fail gate, checkable by tool, not by eye:
  - Body text (including placeholder text): 4.5:1 minimum.
  - Large text (18px+, or 14px bold), UI components, icons, focus rings: 3:1 minimum.
- APCA is the design-stage signal, not the compliance bar: aim near Lc 75 for 14px body,
  Lc 60 for large or bold headings. When WCAG and APCA disagree, WCAG AA decides
  compliance and APCA tells you whether people will actually read it.
- Quick pre-check in OKLCH: if |L_text - L_bg| is under 50 percentage points, it will
  probably fail. Compute the real ratio before shipping.

## Layout and spacing

### Spacing scale

- Use a 4pt/8pt scale with semantic token names (--space-3xs through --space-5xl, or
  2xs/xs/sm/md/lg/xl/2xl/3xl). All margins, padding, and gaps come from the scale;
  off-scale values are defects.
- Whitespace first: start with too much, then remove until it is right.
- Spacing is grouping: space inside a group must be smaller than space between groups.
  Equal inside and outside spacing is ambiguous and reads as unconsidered.

### Structure is information

- Structural devices (numbering, eyebrows, dividers, labels) must encode something true
  about the content. Numbered markers (01 / 02 / 03) only when the content is actually a
  sequence. A divider only where the subject actually changes.
- Think macrostructure first: decide the page's structural concept (what kind of page is
  this, what shape does its argument have) before styling any component.
- Structural variety across outputs: two pages for two different briefs must not share
  the same hero, three-features, CTA, footer rhythm. Rotate macrostructure, nav, and
  footer patterns across consecutive outputs.
- Layout-family cap within a page: each layout family (card grid, split, full-bleed,
  list, bento, marquee) appears at most once; a page with 8 sections needs at least 4
  distinct families. Zigzag image/text splits: 2 in a row maximum.
- One job per section: one purpose, one headline, one short supporting sentence.

### Hero constraints

- Headline 2 lines maximum. Subtext 20 words or fewer, 3-4 lines maximum.
- At most 4 text elements in the hero; primary CTA visible without scrolling.
- Logo walls and social proof go under the hero, never inside it.
- Full-height heroes use min-height: 100dvh, never h-screen/100vh.

### Engineering floor

- overflow-x: clip on both html and body. Clip, not hidden.
- Image-bearing grid tracks use minmax(0, 1fr) so images cannot blow the track out.
- CSS Grid over flexbox percentage math (no width: calc(33% - 1rem) rows).
- Cards earn their existence: use a card only when the card is the interaction. Nested
  cards are always wrong. Card radius tops out at 12-16px; full-pill radius is for tags
  and buttons only.
- Build a semantic z-index scale (dropdown, sticky, modal-backdrop, modal, toast,
  tooltip). Never 999 or 9999.

### Interaction states

- Every interactive component ships all eight states: default, hover, focus-visible,
  active, disabled, loading, error, success. A button with only default and hover is
  half-built.
- Inputs share one minimum height (44px) and keep a fixed 1px border width across all
  states, so state changes never shift layout.
- An empty state points somewhere; it does not shrug. Say what belongs here and hand over
  the control that creates the first one.

## Interface copy

Words carry as much of the design as the spacing does. Every label is there to make the
thing easier to use, so treat copy as a material and not as trim.

- Label for the person, not the architecture. Users recognize what they operate; they do
  not recognize your plumbing. Someone turns off alerts. Nobody edits a webhook payload.
- A control names its own consequence. "Save changes" beats "Submit", which promises
  nothing. Cap primary CTA labels at 3 words.
- Hold one verb across the whole flow. Press "Publish" and the confirmation should say
  "Published" - not "Success", not "Your content is live".
- One intent, one label. "Get in touch", "Contact us", and "Let's talk" are the same
  intent wearing three costumes; pick one and reuse it.
- An error states the failure and the way out of it, phrased the way the rest of the
  product speaks. No apology, no vagueness. Loading states end with an ellipsis
  ("Saving…", the single ellipsis glyph, not three periods).
- Specific beats clever, every time. If deleting 30% of the copy improves it, keep
  deleting.
- Honest copy only: no invented metrics, no fabricated precision, no placeholder names.
  One register per page; typographic quotes and apostrophes in display copy.

## Motion

- Animate transform and opacity only. Never top, left, width, height, margin, or padding.
- Named easings only: ease-out expo/quart/quint, or cubic-bezier(0.16, 1, 0.3, 1). Never
  the default `ease` keyword, never bounce or elastic on UI state changes.
- Duration bands: micro 50-100ms, short 150-250ms, medium 250-400ms, long 400-700ms.
  Nothing over 700ms without a stated reason.
- prefers-reduced-motion is not optional: every animation collapses to a crossfade of
  150ms or less, or to nothing.
- No scroll-listener jank: window.addEventListener("scroll") is banned, and so is
  useState for continuous input values (mouse position, scroll progress). Use
  useMotionValue/useTransform/useScroll, GSAP ScrollTrigger, IntersectionObserver, or CSS
  scroll-driven animations. Do not mix GSAP or Three.js with Motion in one component tree.
- One orchestrated moment beats scattered effects: a single staggered page-load reveal
  creates more delight than micro-interactions everywhere. Fewer than 3 microinteraction
  primitives per page. Cut motion before adding it.
- Motion must be motivated: if you cannot state the reason for an animation in one
  sentence, drop it.
- Silent success over celebratory toasts; optimistic update with undo over confirmation
  dialogs.
- Focus rings meet 3:1 contrast, appear instantly, and are never animated in. Reveal
  animations enhance an already-visible default; never gate content visibility on a
  class-triggered transition.

## The three dials

A configuration surface set from the brief before generating. Each dial is 1-10.

| Dial | 1 means | 10 means | Baseline |
|---|---|---|---|
| VARIANCE | perfect symmetry | artful chaos | 8 |
| MOTION | fully static | cinematic, physics | 6 |
| DENSITY | airy gallery | packed cockpit | 4 |

Conditional rules keyed to the dials:

- Centered hero allowed only when VARIANCE is 4 or lower.
- Reduced-motion support mandatory whenever MOTION is above 3; any motion claimed in copy
  must actually be shown when MOTION is above 4; magnetic or perpetual micro-interactions
  only when MOTION is above 5.
- Generic card containers banned when DENSITY is above 7; render dense numbers in mono.

State the dial values out loud (in a comment or the design read) before building, so the
choice is inspectable.

## Mobile hard floor

- Verify at 320, 375, 414, and 768px before calling anything done. Desktop checks at
  1280 and 1440 are secondary.
- No horizontal scroll at any width. Touch targets 44px minimum. No two-line clickable
  text. Inputs share a consistent minimum height with fixed 1px borders across states.

## The self-critique loop

Run before emitting, not after shipping.

1. Plan first: a compact token system (4-6 named color tokens, 2+ type roles, a layout
   concept, one signature element). Then critique the plan against the brief: "would I
   produce this for any similar brief?" If yes, revise the generic part and say what
   changed and why. Only then write code.
2. Pre-emit scoring on six axes, each 1-5: Philosophy, Hierarchy, Execution, Specificity,
   Restraint, Variety. Any axis below 3 triggers a revision pass. Two passes is normal;
   needing a third means the brief itself is wrong.
3. Spend your boldness in one place. One signature element is the memorable thing;
   everything around it stays quiet and disciplined.
4. Take one real aesthetic risk you can justify. Not taking a risk is itself a risk.
5. The Chanel rule: before shipping, remove one accessory.
6. Render it and look. A screenshot is worth a thousand tokens; beautiful code that does
   not mount is worth zero.
