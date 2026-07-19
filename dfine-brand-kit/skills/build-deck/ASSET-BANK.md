# Asset bank — catalogue

Closed banks. The skill selects from these; it never generates or invents. Machine-readable
index is `assets/manifest.json` (with a `sha256` per file so the validator can confirm
provenance). This file is the human-readable browse view.

## Illustrations — `assets/illustrations/`
Bloom / flower / network motif, all composited on **white**, all right-placed. Each carries a
`hero` block (`image_zone` / `safe_zone`, computed from the real content bbox) so cover/section
text sits clear. `sha256` per file → provenance-checkable. Use **sparingly** (hero/section/statement).
More coming.

| id | shows | best use |
|----|-------|----------|
| **single-flower** | one periwinkle bloom + leaves, right | hero / statement |
| **two-flowers** | two blooms + faint network (spans width) | cover / statement backdrop |
| **branch-buds** | branch w/ buds + leaves, orange signal node, right | section side |
| **branch-spray** | delicate branch spray, subtle, right | section / quiet background |
| **network-branch** | dense node-tree (bare network), right | section / background |
| **thank-you** | faint corner sprigs framing an empty centre (full-bleed) | closing / thank-you / statement backdrop (text centre) |

## Side elements — `assets/side-elements/`
Bloom **sprigs anchored to one edge**, composited on white, leaving open content space. Unlike hero
illustrations (a slide's focal visual), these **frame or accent a content slide**. Each carries
`place` (which side the art sits on) + `image_zone` / `safe_zone` (where text goes), so cover text
sits clear. `sha256` per file → provenance-checkable. Pick by the edge you need kept clear.

| id | shows | best use |
|----|-------|----------|
| **side-left-01** | sprig from the left, mid-height (landscape) | content slide, text on the right |
| **side-left-02** | taller sprig up the left edge (landscape) | content slide, text on the right |
| **side-left-03** | tall portrait sprig, left (portrait) | full-height left edge panel |
| **side-right-01** | sprig from the right, mid-height (landscape) | content slide, text on the left |
| **side-right-02** | taller sprig down the right edge (landscape) | content slide, text on the left |
| **side-right-03** | tall portrait sprig, right (portrait) | full-height right edge panel |

## Line elements — `assets/line-elements/`
The **line-grammar motif** — abstract topographic current lines with a few signal nodes and one peach
ripple, on white. **Subtle full-bleed / side backgrounds**: text may overlay the faint lines, but
`safe_zone` marks the clearest band. SVG (vector), recoloured at build time like icons — no per-file
hash; bank-only. Use **sparingly**, one per section at most.

| id | shows | best use |
|----|-------|----------|
| **vertical-current** | vertical currents up a centre-right column | section bg, text left |
| **side-ribbon** | narrow ribbon of lines hugging the right edge | section bg, text left |
| **diagonal-flow** | lines sweeping diagonally across the top | section bg, text bottom |
| **corner-sweep** | lines sweeping up from the lower-right corner | section bg, text left |
| **soft-s-column** | soft S-curve column through the centre | statement bg, open edges |
| **signal-river** | wide river of lines with signal nodes, centre-right | section bg, text left |

## Icons — `assets/icons/`
**98 icons** from the Scarlet DS (Figma), SVG, ink stroke. Recoloured/resized to brand at build
time. Bank-only — match by **name + tags**; full index (name → tags) is in `assets/manifest.json`.
No per-file hash check (icons are transformed on use); bank-only is enforced at build.

Grouped for browsing:
- **Navigation** — chevron-{up,down,left,right}, arrow-* (up/down/left/right + diagonals + to-start/end/top/bottom), menu, more-horizontal, more-vertical, close
- **Actions** — plus, minus, edit, edit-line, copy, trash, trash-alt, search, zoom-in, zoom-out, filter (+add/-remove), sliders, upload, download, download-tray, send, swap, scan, log-in, expand, collapse, fullscreen, external-link, settings, cursor, click
- **Content** — file, folder, folder-open, clipboard, clipboard-list, calendar, message, mail, tag, list, rows
- **People / status** — user, users, profile, crown, alert, help, ban, lock, unlock, view, hide, flag, asterisk
- **Brand / AI** — sparkle, sparkles-add, sparkle-star, lightbulb, lightbulb-add
- **Domain / entities** — server, router, database, monitor, mobile, globe, linux, home, window, window-tiles, package, shield, bug, location, clock, dashboard, grid-modules, layout-grid, ghost, target

**Confirm names:** `target` (62) and `cursor-arrow` (74) were ambiguous at icon size — rename in the manifest if they're something else.

## Logos — `assets/logos/`
Bank-only, never recreated — place the file unmodified, positioned to fit the slide. Each variant
ships as SVG · PNG (+@2x/@3x) · PDF. Pick by background (`tokens.json → policy.logo_variant`).

| variant | art | use on | files |
|---|---|---|---|
| **on-light** (default) | teal mark + navy wordmark | white / light backgrounds | `dfine-logo-on-light.*` |
| **on-dark** | mint mark + white wordmark | dark backgrounds (dark divider / photo) | `dfine-logo-on-dark.*` |
| **black** | all black | single-colour / print on light | `dfine-logo-black.*` |
| **white** | all white | single-colour on dark / photo | `dfine-logo-white.*` |

## Photography — `assets/photo/`
Curated photo bank (satellite / fiber / datacenter seed in the main repo `assets/photo`), so we
control the kind of imagery shown. **OPEN THREAD:** define treatment (full-bleed / framed /
brand-tinted) and when photos are used vs. illustrations. Bank-only — never stock/arbitrary.

| id | file | shows | use for |
|----|------|-------|---------|
| _pending bank_ | | | |

## Video / motion — `assets/video/`
Hero motion, square, on white. Each has an `.mp4` + a `-poster.png` + `hero` metadata
(`image_zone` / `safe_zone`) so cover text sits clear of the visual. Embedded as-is → hash-checkable.

| id | shows | use for |
|----|-------|---------|
| **hero-tree** | branch growing into a network (bloom motif; one orange signal node) | cover / section hero |
| **hero-globe** | messy network resolving into a globe — the Dfine mark | cover / intro / closing |

## Templates — `assets/templates/`
`dfine-brand-template.pptx` — the hybrid base (Hero/video, embedded fonts, theme picker, white
master). Duplicated as the starting point for new decks.

## Adding assets
1. Drop the file in the right folder.
2. Add an entry to `assets/manifest.json` with `path`, `sha256`, and metadata (what it shows /
   concept tags / when to use).
3. Add a human row to the table above.
Keep the manifest and this catalogue in sync — the validator trusts the manifest.
