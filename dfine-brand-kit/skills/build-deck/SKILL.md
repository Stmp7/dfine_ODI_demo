---
name: build-deck
description: >-
  Build and edit on-brand Dfine presentations. Use this WHENEVER the user wants to create,
  build, make, draft, assemble, add a slide to, edit, update, restyle, or rebrand a
  presentation, slide, deck, pitch, product overview, company/mission deck, or sprint/status
  update — even if they never say "brand", "template", or name this skill. If the artifact is
  a presentation (.pptx), this skill is in play. It enforces the Dfine palette
  (teal/navy/iris/scarlet/neutral), Bricolage Grotesque + Avenir fonts, pure-white backgrounds,
  role-correct colours (borders, warning/danger/success), and uses ONLY illustrations and icons
  from the bundled asset bank. It runs a validator that auto-fixes off-brand drift and rejects
  violations, so nothing off-brand ships.
allowed-tools: Bash Read Write Edit
---

# Apply the Dfine brand to presentations

This skill is the **brand layer** — it does **not** decide content, length, structure, or how the
user drafts their idea. That stays in the user's workflow. Its one job: whatever presentation the
user is building or editing, make it correct in the Dfine brand — right fonts, colours, role usage,
white backgrounds, on-brand layouts, bank assets — and verify it with the validator. Enforced, not
suggested: you build/edit, run the checker, fix until it passes.

## The one source of truth

`tokens.json` defines every colour, role, and font. **Read it first, every time.** Do not
hardcode brand values from memory — read them from the file so you stay in sync when they change.
Detailed rules and rationale live in [VALIDATION-RULES.md](VALIDATION-RULES.md).

Non-negotiables (all defined in `tokens.json`):
- **Backgrounds are pure white `#FFFFFF`.** Illustrations are composited on white; any off-white
  leaves a visible seam behind them.
- **Fonts:** headings `Bricolage Grotesque` (the clean name — never a "…14pt Medium" variant),
  body `Avenir`.
- **Colours only from the token set**, used by role: neutral grey for borders/chrome; teal/iris
  as brand accents; scarlet as the single sparing signal; status colours (success/warning/
  caution/danger) only for status.
- **Sentence case everywhere** — kickers, labels, and titles. No ALL-CAPS / uppercase transform
  (matches the product-UI rule). Acronyms (IT, OT, CVE) keep their natural caps.
- **Illustrations sparingly** — use them on hero / section / statement moments; keep most content
  slides clean and typographic. Not every slide needs art.
- **Logo variant follows the background.** Place `on-light`/`black` on light grounds,
  `on-dark`/`white` on dark. If a transform flips a slide's background lightness, swap the logo
  variant in the **same** pass — the flip and the logo are coupled. The validator now enforces this
  (hard fail for a bank logo on the wrong background; advisory for a low-contrast non-bank mark).
- **Titles in Bricolage Medium** throughout (Bold exists but isn't the default).
- **Accent hierarchy:** teal primary → iris secondary → scarlet only for the key emphasis point
  (sparing). Never let scarlet become a wash.
- **16:9 widescreen only** (13.333 × 7.5 in). No 4:3 or portrait.
- **Static by default** — no transitions/builds unless the user asks.
- **Photos from the photography bank only** (`assets/photo`, curated) — never stock/arbitrary.
- **Type scale is guidance, not enforced** — follow the recommended sizes in `tokens.json`
  (`type_scale`) but don't fail on sensible deviations.
- **Sparse & premium** — generous whitespace, ideally one idea per slide; flex denser only for
  data/sprint decks. Bullets OK but styled minimally; tables are hairline + faint header, no zebra
  (see `tokens.json → layout_style`).

### If you spot off-brand content
If part or all of a deck the user is working on is off-brand, **flag it and ask** whether to bring
it on-brand — show what's off (wrong fonts/colours/bg/non-bank images) and offer to fix. Never
silently rewrite their deck; transform only on their go-ahead. (The transform pipeline is the same
recolour/refont/re-bg/re-embed flow the validator drives.)
- **Illustrations, icons, and the logo come only from `assets/`** — never generated, invented, or
  recreated. The **logo especially**: never redraw it as shapes/text or regenerate it — place the
  approved file from `assets/logos` unmodified.

## Workflow

1. **Read `tokens.json`.** Load the palette, roles, and fonts.
2. **Take the user's content/structure as given.** They may be creating new slides, editing
   existing ones, or restyling. Don't impose a content approach, deck length, or drafting method —
   work with whatever they bring and make it on-brand.
3. **Start from the template (hybrid).** Duplicate `assets/templates/dfine-brand-template.pptx`
   as the base — it carries the Hero, embedded fonts, theme picker, and white master. Add or
   fill layouts from the layout library in `scripts/`. Generate new layouts on demand when the
   library doesn't have what's needed, following the token rules.
4. **Pick assets from the bank.** For any illustration or icon, choose from `assets/illustrations`
   / `assets/icons` using [ASSET-BANK.md](ASSET-BANK.md). Product screenshots the user provides
   may be placed anywhere. Never generate art or icons. **If the bank has no match, use a clean
   typographic layout — don't invent.** Place the **logo** (from `assets/logos`, never generated)
   where it best fits the slide's content; the user can move or remove it.
5. **Apply theme + embed fonts** (reads `tokens.json`, embeds clean Bricolage, sweeps stray fonts):
   ```bash
   python3 scripts/theme_and_embed.py <deck>.pptx
   ```
6. **Validate:**
   ```bash
   python3 scripts/validate_brand.py <deck>.pptx --json
   ```
   (See `scripts/example-build.js` for a worked build that pulls logo + illustration + icons from
   the banks and places text in each illustration's `safe_zone`.)
6. **Resolve violations (see policy below), then re-validate until it passes (exit 0).**

## On a violation

Follow `policy` in `tokens.json`:

- **Drift → auto-fix silently, then note it.** Snap an off-palette colour to the nearest token,
  a wrong font to Bricolage/Avenir, a non-white background to white. Report what you changed in
  a short summary.
- **The user explicitly asked for the off-brand value → do NOT override.** Warn that it's
  off-brand, suggest the on-brand equivalent, and let them decide. Respect intent over the rule.

Example: if a generated card comes out with a `#000000` border (drift), silently fix it to
`#E5E7EB` and mention it. If the user said "make that callout red `#FF0000`", keep it but reply:
"that's off-palette — the brand danger red is `#EF4444`; want me to use that instead?"

## Verify

**Always run the validator** after building or editing (it's the gate). The validator checks
structure, not layout — so **render a preview only when the user asks**:
```bash
soffice --headless --convert-to pdf <deck>.pptx && pdftoppm -jpeg -r 110 <deck>.pdf out
```
When you do render, check for overflow, overlap, and that illustrations sit cleanly on white.

## Charts — open thread

The chart / data-series palette (bar, line, pie) isn't defined yet. Don't improvise one: keep any
charts minimal and token-coloured, and tell the user the chart palette still needs to be decided.

## Layout library

`scripts/` holds generators for the baseline layouts (cover/Hero, agenda, statement, KPI row,
screenshot showcase, timeline/roadmap, table, and more as they're added). Reuse them; when you
must author a new layout, keep it token-driven and re-usable, and add it to the library.
**There are no fixed per-use-case deck skeletons** — assemble layouts to the user's own structure;
never impose a canned outline. Export a shareable **PDF only when asked**.

## Scope

Presentations (`.pptx`) for now. Word documents are a later phase — do not attempt `.docx`
branding with this skill yet.
