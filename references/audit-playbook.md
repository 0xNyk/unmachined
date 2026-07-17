# Audit playbook: scoring and fixing existing UI

How to audit a live or generated UI against design-tells.md and design-system.md, and how
to fix what you find without breaking the product.

## Audit flow

1. See it before judging it. Render the target and screenshot at 375px and 1440px (add
   320px and 768px for anything layout-heavy). Read the source alongside the screenshots.
2. Run the 10-second scan from design-tells.md first: greps for gradients, banned fonts,
   gradient text, pure black/white, transition: all, z-index 9999, 100vw, invented
   metrics. These are cheap and deterministic.
3. Then the visual pass: nav and footer fingerprints, section rhythm, eyebrow count,
   card grids, hero composition, italic headings, spacing consistency, contrast.
4. Then the content pass: happy-talk intros ("Welcome to..."), vague button labels
   ("Submit", "Learn More"), duplicate-intent CTAs, visible instructions longer than one
   sentence, placeholder names and metrics.
5. Record every finding as: severity (CRITICAL / MAJOR / MINOR), tell name, file:line
   where possible (screenshot region when the source is not available), and the concrete
   fix. Findings without a location are opinions; anchor them.
6. Rank by severity first, then by visibility (above the fold beats footer).

### Grading

Grade per category, then overall. Categories: typography, color and contrast, layout and
spacing, motion, copy and content, accessibility.

- Each category starts at A.
- Each CRITICAL finding drops the category one full letter.
- Each MAJOR finding drops it half a letter.
- MINOR findings do not move the grade; list them as polish.
- Floor is F. Overall grade is the average of category grades, reported next to a
  one-line verdict.

Report format: overall letter grade, per-category subscores, ranked findings table
(severity, tell, location, fix), and a recommended fix order. An audit-only run stops
here; do not edit unless asked to fix.

### Audit modes

- Quick: steps 1-3 only, overall grade plus the top 5 findings. For "does this look AI"
  triage.
- Full (default): all six steps, all categories.
- Regression: re-run a previous audit and diff the findings against the saved baseline;
  report new, fixed, and persisting items.

## Redesign constraints

A redesign changes the visual and interaction layer, nothing else.

Before touching anything, extract the design DNA of what exists: current macrostructure,
type pairing, color anchor, spacing scale, nav and footer pattern. The extract separates
what is brand (keep) from what is default (replace), and becomes the baseline the
regression audit diffs against.

Preserve:

- Routes, page slugs, anchor IDs, and primary nav labels (SEO depends on them).
- Component APIs and data flow; the information architecture unless the user asks.
- Copy intent: rewrite slop phrasing, keep the claims, numbers, and meaning.
- Genuine brand tokens. If purple is actually the brand, purple stays; the tell is the
  unbranded default, not the color.

Change:

- Typography pairing, scale, and weights. Color tokens. Spacing scale. Section-level
  layout composition. Motion. Microcopy voice.

When in doubt whether something is brand or default, ask before replacing it.

## Fix loop

1. Fix atomically: one finding per edit, commit-sized, referencing the finding ID.
2. Verify each fix at mobile widths (320/375) and desktop before moving on. A fix that
   breaks 320px is not a fix.
3. Cap risky auto-fixes. Track a running risk estimate: any revert, any edit touching
   files unrelated to a finding, or passing roughly 30 fixes in one session means stop,
   summarize, and hand the remainder back to the user as a punch list.
4. Fixes remove or restructure more often than they add. Never fix a tell by layering on
   decoration; that is how second-order monoculture starts.
5. Re-run the tell scan and re-grade after the batch. Report the true result ("B+, 3
   MAJOR findings remain"), never a rounded-up pass.

## Nielsen-style critique rubric (optional, /40)

For UX depth beyond the aesthetic scan, score the ten heuristics 0-4 each:

1. Visibility of system status
2. Match between system and the real world
3. User control and freedom
4. Consistency and standards
5. Error prevention
6. Recognition rather than recall
7. Flexibility and efficiency of use
8. Aesthetic and minimalist design
9. Help users recognize, diagnose, and recover from errors
10. Help and documentation

Scoring honesty: a 4 means genuinely excellent. Most real interfaces score 20-32. Tag
issues P0-P3 and keep the total across runs so trend is visible; re-run after fixes to
confirm the score moved.

Bias guard for high-stakes reviews: run two independent assessments that cannot see each
other, then synthesize. Disagreements between the two passes are usually the most honest
findings in the report.
