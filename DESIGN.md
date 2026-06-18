---
name: AI Act Navigator
description: Source-cited EU AI Act compliance — dark regulatory canvas with emerald accent
colors:
  canvas-dark: "#020617"
  surface-dark: "#0f172a"
  surface-elevated: "#1e293b"
  border-subtle: "#334155"
  border-muted: "#475569"
  text-primary: "#f1f5f9"
  text-secondary: "#94a3b8"
  text-muted: "#cbd5e1"
  accent: "#10b981"
  accent-hover: "#34d399"
  accent-deep: "#059669"
  accent-on-dark: "#020617"
  canvas-light: "#ffffff"
  text-on-light: "#0f172a"
typography:
  display:
    fontFamily: "var(--font-geist-sans), ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(2.25rem, 5vw, 3rem)"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "var(--font-geist-sans), ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.875rem"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  title:
    fontFamily: "var(--font-geist-sans), ui-sans-serif, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.45
  body:
    fontFamily: "var(--font-geist-sans), ui-sans-serif, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "var(--font-geist-sans), ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "0.05em"
  mono:
    fontFamily: "var(--font-geist-mono), ui-monospace, monospace"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  md: "8px"
  lg: "12px"
spacing:
  card-padding: "24px"
  section-gap: "96px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.accent-on-dark}"
    rounded: "{rounded.md}"
    padding: "12px 24px"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
    textColor: "{colors.accent-on-dark}"
    rounded: "{rounded.md}"
    padding: "12px 24px"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: "12px 24px"
  card-default:
    backgroundColor: "rgba(15, 23, 42, 0.5)"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.lg}"
    padding: "{spacing.card-padding}"
  input-default:
    backgroundColor: "{colors.surface-dark}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
---

# Design System: AI Act Navigator

## 1. Overview

**Creative North Star: "The Regulatory Console"**

A dark, focused compliance workstation — not a marketing gimmick. Surfaces read as panels on a regulatory canvas: deep slate backgrounds, crisp borders, emerald used sparingly for action and status. Typography is Geist throughout; hierarchy comes from weight and size, not decorative display faces.

The system rejects AI-slop aesthetics (neon, glass, gradient heroes) and template SaaS patterns. Depth is tonal layering (canvas → surface → elevated), not drop shadows. Motion is functional (150–250ms state transitions), never decorative page-load choreography.

**Key Characteristics:**

- Dark canvas (`slate-950` / `#020617`) as default; light canvas only for long-form pSEO reading
- Emerald accent ≤10% of any screen — primary CTAs, eyebrows, risk-tier highlights, focus rings
- Geist Sans + Geist Mono; fixed rem type scale with `text-wrap: balance` on headings
- 1px `slate-800` borders on cards; 12px card radius; 8px on buttons and inputs
- Full interactive states: hover, focus-visible, disabled, error on every control

## 2. Colors

Restrained palette: cool slate neutrals with a single emerald accent for trust and "go" actions.

### Primary

- **Compliance Emerald** (`#10b981` / emerald-500): Primary buttons, selected option borders, eyebrows, risk-tier labels, focus rings. Hover: `#34d399` (emerald-400). Deep links on light prose: `#059669` (emerald-600).

### Neutral

- **Regulatory Canvas** (`#020617` / slate-950): App shell and marketing hero background.
- **Panel Surface** (`#0f172a` / slate-900): Cards, inputs, elevated panels at 50% opacity on canvas.
- **Border Line** (`#1e293b` / slate-800): Card and section borders.
- **Muted Border** (`#334155` / slate-700): Secondary buttons, input strokes.
- **Primary Text** (`#f1f5f9` / slate-100): Headlines and body on dark.
- **Secondary Text** (`#94a3b8` / slate-400): Supporting copy, metadata.
- **Light Canvas** (`#ffffff`): pSEO long-form articles only.
- **Ink on Light** (`#0f172a` / slate-900): Headings in prose-seo.

### Named Rules

**The Emerald Rarity Rule.** Accent green appears on ≤10% of any screen. If everything is emerald, nothing is actionable.

**The Canvas Hierarchy Rule.** Background flows Regulatory Canvas → Panel Surface → Border Line. Never skip a layer without reason.

## 3. Typography

**Display / Body / Label Font:** Geist Sans (`var(--font-geist-sans)`) with system-ui fallback  
**Mono Font:** Geist Mono (`var(--font-geist-mono)`) for codes, IDs, legal refs

**Character:** Technical and legible — tight tracking on headlines, no Arial or system-only overrides on `body`.

### Hierarchy

- **Display** (700, `clamp(2.25rem, 5vw, 3rem)`, lh 1.15): Marketing hero only. Class: `.text-display`
- **Headline** (700, 1.875rem, lh 1.25): Page titles (wizard, pricing, reports). Class: `.text-headline`
- **Title** (600, 1rem, lh 1.45): Card headings, section titles. Class: `.text-title`
- **Body** (400, 1rem–1.125rem, lh 1.65, max 65ch): Paragraphs. Class: `.text-body-lg` for lead copy
- **Label** (500, 0.875rem, uppercase, tracking 0.05em): Eyebrows, field labels. Class: `.text-label`
- **Mono UI** (400, 0.875rem): Rule IDs, version strings. Class: `.text-mono-ui`

### Named Rules

**The Geist-Only Rule.** Do not set `font-family: Arial` on `body`. Geist variables from `layout.tsx` are canonical.

**The Eyebrow Rule.** Section labels use uppercase tracked emerald (`text-label` + `text-emerald-400`).

## 4. Elevation

Flat-by-default. No ambient drop shadows on cards or buttons. Depth is conveyed by:

- Tonal steps: canvas → `bg-slate-900/50` card → `border-slate-800`
- Highlight cards: `border-emerald-500` + `bg-emerald-950/20` for pricing emphasis or selected tier
- Focus rings: 2px emerald offset ring (`focus-visible:ring-emerald-500 ring-offset-slate-950`)

### Named Rules

**The Flat-By-Default Rule.** Shadows do not appear at rest. Elevation is border + background tint only.

## 5. Components

### Buttons

- **Shape:** `rounded-lg` (8px)
- **Primary:** `bg-emerald-500 text-slate-950`, hover `bg-emerald-400`, sizes `md` (px-4 py-2) and `lg` (px-6 py-3)
- **Secondary:** `border border-slate-700`, transparent bg, hover `border-slate-500`
- **Focus:** 2px emerald ring with offset via `focusRing` / `focusRingLight` for light surfaces
- **Disabled:** `opacity-50`, no hover change on primary

### Cards / Containers

- **Corner Style:** `rounded-xl` (12px)
- **Background:** `bg-slate-900/50` on dark; highlight variant `border-emerald-500 bg-emerald-950/20`
- **Border:** 1px `border-slate-800` (default) or `border-emerald-500` (highlight)
- **Internal Padding:** `p-6` (24px)

### Inputs / Fields

- **Style:** `border-slate-700 bg-slate-900`, `rounded-lg`, `text-slate-100`, placeholder `text-slate-500`
- **Focus:** `border-emerald-500` + emerald focus ring
- **Error:** `text-red-400` with `role="alert"`

### Navigation

- **Marketing header:** `max-w-5xl` centered, product name semibold, nav links `text-slate-300 hover:text-white`
- **Back links:** `text-sm text-slate-400 hover:text-white`

### Assessment Options

- Full-width option buttons: selected `border-emerald-500 bg-emerald-500/10`, default `border-slate-700`

### pSEO Prose

- Light canvas article body via `.prose-seo` — slate body text, emerald-deep links, structured h2/h3

## 6. Do's and Don'ts

### Do:

- **Do** use CSS variables from `globals.css` (`--canvas-dark`, `--accent`, etc.) for new surfaces.
- **Do** wrap app and marketing flows in `AppShell` + `PageContainer` for consistent width (`max-w-5xl` / `max-w-xl` form).
- **Do** ship hover, focus-visible, disabled, and error states on every interactive control.
- **Do** use emerald only for primary actions, selection, eyebrows, and risk/status emphasis.
- **Do** respect `prefers-reduced-motion` (already in `globals.css`).

### Don't:

- **Don't** use neon accents, purple gradients, glassmorphism, or "Powered by AI" marketing tropes.
- **Don't** imply LLM-decided legal outcomes in visual hierarchy — show citations and rule versions instead.
- **Don't** override Geist with Arial or unstyled system fonts on `body`.
- **Don't** use side-stripe borders, gradient text, or nested cards.
- **Don't** put display-sized type on UI labels, buttons, or data tables.
- **Don't** use spinners alone where skeleton or inline loading state would teach the interface.
