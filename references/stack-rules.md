# Stack rules: Tailwind v4, Next.js 16, shadcn/ui, React

Framework-correctness layer. LLMs are trained on Tailwind v3 and pre-Cache-Components Next.js; they default to obsolete syntax and stock shadcn themes. Apply these rules whenever generating or reviewing code on this stack.

Contents: Version detection · Tailwind v4 · Next.js 16 App Router ·
shadcn/ui de-genericization · React performance quick-flags · 10-second scan

## Version detection (do this first)

Before applying any rule below, confirm what the project actually runs:

1. Read `package.json`: check `tailwindcss` (v4.x vs 3.x), `next` (16 vs 15/14), `react` (19 vs 18).
2. Tailwind signal: `tailwind.config.js/ts` present and referenced = likely v3. `@import "tailwindcss"` in CSS + `@theme` block = v4.
3. Next.js signal: `cacheComponents: true` in `next.config.ts` = Cache Components model active. Without it, `use cache` rules do not apply.
4. shadcn signal: `components.json` present. Run `npx shadcn@latest info --json` to read live config (tailwindVersion, base: radix vs base-ui, isRSC, iconLibrary, aliases) before generating components.

If the project pins older versions, follow the project and flag the pin. Never mix v3 and v4 syntax in one codebase.
`scan_ui.py` reads the nearest `package.json` before applying v4-only checks. Pass
`--tailwind-version 3` or `4` when scanning a partial tree without package metadata.

## 1. Tailwind v4 (not v3)

### Banned v3 patterns and their v4 replacements

| v3 (banned) | v4 (correct) |
|---|---|
| `@tailwind base; @tailwind components; @tailwind utilities;` | `@import "tailwindcss";` |
| `tailwind.config.js` JS object config | CSS-first `@theme { }` block |
| `postcss-import` + `autoprefixer` plugins | single `@tailwindcss/postcss` (both built in) |
| `@layer utilities` for custom utilities | `@utility` |
| `bg-opacity-50`, `text-opacity-*`, `border-opacity-*`, `ring-opacity-*`, `divide-opacity-*`, `placeholder-opacity-*` | slash modifier: `bg-red-500/50`, `text-white/80` |
| `bg-gradient-to-r` | `bg-linear-to-r` (also `bg-linear-45`, `bg-conic-*`, `bg-radial-*`) |
| prefix important: `!flex` | suffix important: `flex!` |
| CSS var in brackets: `bg-[--brand]` | parens: `bg-(--brand)` |
| comma in arbitrary grid values: `grid-cols-[max-content,auto]` | underscore: `grid-cols-[max-content_auto]` |
| `shadow-sm` / `shadow` | `shadow-xs` / `shadow-sm` |
| `drop-shadow-sm` | `drop-shadow-xs` |
| `blur-sm` / `blur` | `blur-xs` / `blur-sm` |
| `backdrop-blur-sm` | `backdrop-blur-xs` |
| `rounded-sm` / `rounded` | `rounded-xs` / `rounded-sm` |
| `outline-none` | `outline-hidden` |
| `ring` (bare) | `ring-3` (if you want the old 3px) |
| `flex-shrink-*` / `flex-grow-*` | `shrink-*` / `grow-*` |
| `overflow-ellipsis` | `text-ellipsis` |
| `decoration-slice` | `box-decoration-slice` |
| `focus:transform-none` | `focus:scale-none` (transforms are individual CSS props now) |
| `transition-[opacity,transform]` | `transition-[opacity,scale]` |
| v3 bare class prefix (`tw-flex`) | variant-style prefix at start: `tw:flex tw:hover:bg-red-600` |

Removed v3 utilities fail silently: the compiler drops unknown classes with no error, so stale syntax ships as unstyled UI. Grep for the left column after generating.

### Numeric and default-behavior gotchas

| Changed default | v3 | v4 |
|---|---|---|
| `ring` width | 3px, blue-500 | 1px, currentColor |
| `border-*` / `divide-*` color | gray-200 | currentColor |
| placeholder color | gray-400 | current text color at 50% opacity |
| button cursor | pointer | default |
| `hover:` variant | always | only under `@media (hover: hover)`; no sticky hover on touch |
| `space-y/x` selector | margin-top on `~ :not([hidden])` | margin-bottom on `> :not(:last-child)` |
| outline-`<number>` | width only | also sets `outline-style: solid` |

Browser floor: Safari 16.4+, Chrome 111+, Firefox 128+ (native cascade layers, `@property`, `color-mix()`). Flag v4 for projects that must support older targets.

### @theme design tokens

Theme variables are not just CSS variables; they instruct Tailwind to generate utility classes. Namespaces map 1:1 to utility families:

| Namespace | Generates |
|---|---|
| `--color-*` | `bg-*`, `text-*`, `border-*`, etc. |
| `--font-*` | `font-*` |
| `--text-*` | `text-*` sizes |
| `--font-weight-*` | `font-*` weights |
| `--spacing-*` | padding, margin, gap, width scales |
| `--radius-*` | `rounded-*` |
| `--shadow-*` | `shadow-*` |
| `--breakpoint-*` | `sm:`, `md:`, ... |
| `--animate-*` | `animate-*` |

Rules:
- Define brand tokens in `@theme { }`, not `:root` (use `:root` only for vars that should not generate utilities).
- Reset a namespace with `--color-*: initial;` then define only your values.
- Alias existing vars with `@theme inline` (e.g. `--font-sans: var(--font-inter)`).
- Prefer `@theme` tokens over repeated inline arbitrary values.
- Container queries are built in: `@container` on the parent, `@sm:`/`@md:` variants on children.
- CSS-only entry animations: `starting:` variant (`@starting-style`), no JS needed.
- Migrating a v3 project: run `npx @tailwindcss/upgrade`, do not hand-migrate.

## 2. Next.js 16 App Router

Cache Components (`cacheComponents: true`) makes Partial Prerendering the default: static shell + cached content + Suspense-streamed dynamic holes. Uncached data accessed outside `<Suspense>` or `use cache` is a build error, not a style preference.

### The `use cache` contract

Banned inside a `use cache` scope (build error or 50s cache-fill hang):

- `cookies()`, `headers()`, `searchParams`, `params`. Read them outside and pass values as arguments.
- Passing runtime Promises (e.g. the cookies store) via props, closure, or a shared Map into a cached function.
- Non-determinism: `Math.random()`, `Date.now()`, `crypto.randomUUID()`. Defer with `connection()` + Suspense instead.
- Non-serializable arguments: class instances, functions (except pass-through), Symbols, WeakMap/WeakSet, URL instances.
- Invoking a Server Action or introspecting `children`/JSX slots. Pass through only, never call or read.
- `React.cache` to smuggle data in: `use cache` has an isolated React.cache scope; it reads back null.
- Toggling Draft Mode (`enable()`/`disable()`).
- Relying on in-memory persistence across requests on serverless: it will not persist. Use `use cache: remote`.

Arguments and closed-over values become the cache key: different inputs produce separate entries.

### cacheLife TTL table

| Profile | stale (client) | revalidate (server) | expire |
|---|---|---|---|
| default | 5 min | 15 min | never |
| seconds | 30 s | 1 s | 1 min |
| minutes | 5 min | 1 min | 1 hr |
| hours | 5 min | 1 hr | 1 day |
| days | 5 min | 1 day | 1 week |
| weeks | 5 min | 1 week | 30 days |
| max | 5 min | 30 days | 1 year |

Hard rules: always set an explicit `cacheLife`; `expire` must exceed `revalidate`; client router enforces a 30-second minimum stale time regardless of config; caches with zero revalidate or expire under 5 minutes are excluded from prerenders and become dynamic holes (the `seconds` profile is always dynamic). Invalidate via `cacheTag` on read + `updateTag`/`revalidateTag` in a Server Action. Debug with `NEXT_PRIVATE_DEBUG_CACHE=1`.

### Four-layer cache model (brief)

Request memoization (per render pass) -> Data Cache (`use cache` + cacheLife, survives requests) -> Full Route Cache (the prerendered static shell) -> Client Router Cache (30s minimum stale). Know which layer a bug lives in before touching config.

### RSC data fetching

- `fetch` is memoized per request tree but NOT cached by default; it blocks rendering until done. Cache with `use cache` or stream with `<Suspense>`.
- Never sequential-await independent requests. Initiate all fetches first, then `await Promise.all([...])`. Requests start when `fetch` is called, not when awaited.
- `React.cache()` is per-request deduplication only; no sharing between requests.
- Fetch data in the component that needs it; memoization makes prop drilling for data unnecessary.

### Project structure

- Colocation is safe: a route is not public until `page.js`/`route.js` exists in the segment.
- `_folder` opts a folder and its subtree out of routing (private folders).
- `(group)` folders organize routes without affecting the URL; use route groups for multiple root layouts.
- Do not put an empty-fallback `<Suspense>` above `<body>` unless you intend to opt the whole app out of the static shell.

## 3. shadcn/ui de-genericization

### The three dials

Stock `--primary` (muted indigo/zinc), stock `--radius` (0.5rem), and stock Inter are the instantly recognizable "default shadcn" fingerprint. People think they are choosing a color theme; they are choosing a product feel. Change all three before building anything:

| Dial | Stock (banned as-is) | Move to |
|---|---|---|
| `--primary` | muted indigo or zinc | one saturated brand accent, used sparingly. One accent is the look; never add a second competing accent |
| `--radius` | 0.5rem uniform | 0px (sharp), 1rem (soft), or 999px (pill). Avoid 0.5rem; the same components at a different radius read as a different product |
| `--font-sans` / `--font-display` | Inter at defaults | a real pairing (serif display + clean sans body, or geometric display + humanist body) |

Then add exactly ONE signature token shadcn does not ship (grain texture, signature shadow stack, custom easing curve, or non-default border treatment) and apply it consistently.

### Token layer

- Theme with OKLCH cssVars in `@theme`, not hex. Example editorial neutrals: surface `oklch(0.97 0.01 80)`, foreground `oklch(0.16 0.012 250)`. Replace untouched slate/zinc scales.
- Semantic tokens only: `bg-primary`, `text-muted-foreground`, `bg-destructive`. Never raw values like `bg-blue-500`. Base token = surface, `-foreground` = text/icons on that surface.
- Single `--radius` derives the whole radius scale (radius-sm through radius-4xl); set it once at the token layer.
- `className` is for layout, not styling. Never override component colors or typography via className; restyle at the token layer.

### Update-safe composition

- Never edit generated files in `components/ui/`. Wrap them; keep originals unchanged so CLI updates apply cleanly. Preview updates with `--dry-run` / `--diff`.
- Import from `@/components/ui/*`, never from a package like `@shadcn/ui` (copy-paste ownership model).
- Custom triggers: `asChild` (radix) or `render` (base-ui); check the `base` field from project config.
- Variants via `cva`, class merging via `cn()`. No template-literal conditional class strings.
- Forms: `FieldGroup` + `Field`, never raw `div` with `space-y-*`. Validation: `data-invalid` on Field, `aria-invalid` on the control (React Hook Form + Zod, not manual validation).
- Option sets of 2-7 choices: `ToggleGroup`, not a loop of Buttons.
- Items always inside their Group (SelectItem in SelectGroup, CommandItem in CommandGroup, etc.). Full Card composition (CardHeader/CardTitle/CardDescription/CardContent/CardFooter).
- Layout: flex + `gap-*`, never `space-x-*`/`space-y-*`. Use `size-10` when width equals height. No manual z-index on Dialog/Sheet/Popover. No sizing classes on icons inside components.
- A11y structure: Dialog/Sheet/Drawer always need a Title (`sr-only` if hidden); Avatar always needs AvatarFallback; icon-only buttons need `aria-label`.
- Run `npx shadcn@latest info --json` before generating; never import a component that was not added; ask which registry when unspecified.

## 4. React performance quick-flags

Highest-impact rules from Vercel's react-best-practices, condensed:

1. Parallelize independent async work with `Promise.all()`; sequential awaits are the top server-side sin (2-10x).
2. Import directly; avoid barrel files (major dev-boot, build, and cold-start cost).
3. Virtualize lists over 50 items (virtua, or `content-visibility: auto`).
4. `<img>` always gets explicit width and height (prevents CLS). Below-fold: `loading="lazy"`; above-fold: `fetchpriority="high"`.
5. Never define components inside components (inputs lose focus on every keystroke).
6. Derive state during render, not in `useEffect`.
7. Pass a function to `useState` for expensive initial values.
8. Use Set/Map for hot lookups, not `array.includes` (O(1) vs O(n)).
9. Use `toSorted()`, not mutating `sort()`.
10. Ternary, not `&&`, for conditional render.
11. No layout reads in render (`getBoundingClientRect`, `offsetHeight`, `scrollTop`).
12. Animate transform/opacity only; never `transition: all`; honor `prefers-reduced-motion`; animations must be interruptible.
13. Authenticate Server Actions like public API endpoints.
14. `after()` for non-blocking post-response work; `React.cache()` for per-request dedup.
15. `<button>` for actions, `<a>`/`<Link>` for navigation; never `<div onClick>`. Never `outline-none` without a `focus-visible` replacement. Never block paste.

Also flag on sight: `user-scalable=no` or `maximum-scale=1`, form inputs without labels, hardcoded date/number formats (use `Intl.*`), unjustified `autoFocus`, `"use client"` sprawl on components that never touch state or browser APIs.

## 10-second scan

Grep these before shipping; any hit is stack slop:

```
@tailwind                  # v3 directives
tailwind.config.(js|ts)    # JS config in a v4 project
bg-opacity-|text-opacity-  # v3 opacity utilities
bg-gradient-to             # v3 gradient syntax
bg-\[--                    # v3 var-in-brackets
"!flex|!bg-|!text-         # prefix important
bg-blue-500|bg-indigo-     # raw colors in a shadcn project
space-x-|space-y-          # use flex + gap
@shadcn/ui                 # wrong import path
w-10 h-10                  # should be size-10
transition: all|transition-all
outline-none               # v4: outline-hidden; and needs focus-visible
"use client"               # count them; sprawl = server-first violated
Math.random()|Date.now()   # inside any "use cache" file
cookies()|headers()        # inside any "use cache" file
```

Also check: every `use cache` has an explicit `cacheLife`; `--primary`, `--radius`, `--font-sans` differ from stock; no edits inside `components/ui/` generated files.
