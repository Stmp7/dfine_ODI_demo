# Open threads — dfine-brand-kit

Refinement items still to resolve. Nothing here is finalised.

## Design / rules
- [ ] **Section dividers** — will use approved background **images** (into the asset bank) + a
      to-be-defined set of allowed background **colours**. Until defined, the validator treats any
      non-white background as a violation. Then: list approved divider bg images, define allowed
      colours, exempt dividers in `validate_brand.py`. (`tokens.json → section_divider`)
- [ ] **Charts / data palette** — how bar/line/pie series are coloured. **Needs testing** before
      defining. Until then: charts stay minimal + token-coloured, and the skill flags it.
- [x] **Content-slide chrome** — RESOLVED: no fixed footer. Place the real logo (from the bank)
      contextually where it fits; user can move/remove. Never generate the logo.
- [~] **Hero motion assets** — DONE: `hero-tree` + `hero-globe` videos imported (`assets/video/`)
      with posters + `safe_zone`/`image_zone` metadata. Layouts + overlap-check still below.
- [ ] **Hero cover geometry** — build hero LAYOUTS with a baked image/video zone (right ~45%) +
      left text safe-zone placeholder; add `safe_zone` / `image_zone` metadata per hero asset; add a
      validator check that fails text overlapping `image_zone`. Solves cover text colliding with the
      side image/video. (`tokens.json → hero`)
- [ ] **Confidentiality marker** — off by default; build the deck-wide toggle + a small muted marker.
- [ ] **Non-Latin fallback font** — pick a fallback for languages Bricolage/Avenir don't cover,
      for non-English decks on request.

## Assets (need input from Ran)
- [x] **Icons** — DONE: 98 imported to `assets/icons/` with descriptive names + concept tags in
      manifest. TODO: confirm 2 ambiguous names — `target` (62) and `cursor-arrow` (74).
- [x] **Illustrations** — DONE (first set): 5 approved imported (single-flower, two-flowers,
      branch-buds, branch-spray, network-branch) with `sha256` + computed hero zones. More coming.
- [x] **Logos** — DONE: 4 variants (on-light default / on-dark / black / white), each SVG·PNG·@2x·@3x·PDF,
      imported to `assets/logos/` + manifest with per-PNG sha256. (Source re-exported clean; earlier
      set had a purple clearspace guide baked in — fixed.)
- [ ] **Photography bank** — create a curated `assets/photo/` bank (seed from repo
      `assets/photo`), then define treatment (full-bleed / framed / brand-tinted) and when photos
      are used vs. illustrations.

## Build / tooling
- [x] **Font normalisation** — DONE: clean Bricolage statics in `assets/fonts/`;
      `scripts/theme_and_embed.py` embeds them, sets the theme from tokens, and normalises any
      `Bricolage Grotesque 14pt Medium` → `Bricolage Grotesque`. Proven end-to-end (test build passes).
- [~] **Layout library** — SEEDED: `scripts/example-build.js` is a working 6-layout build that
      pulls from the banks + uses illustration safe-zones. TODO: refactor into clean reusable
      layout functions + add remaining layouts (agenda / timeline / table into the reusable set).
- [ ] **Validator `--fix` mode** — auto-apply the drift fixes; + optional `PostToolUse` hook.
- [ ] **Evals** — via skill-creator, once the draft stabilises: prove triggering + that the
      validator catches each violation type.

## Transform v2 plan (from the real-deck test — "Scarlet Sprint2-3 Kickoff")

**Core lesson:** raw per-hex remapping is both too blunt *and* too eager. The token-only validator
PASSED at 0 while text was invisible — **token-compliance ≠ legibility**. The transform must be
minimal-diff, component-aware, and background-aware, with a contrast backstop.

**Confirmed bug:** the "dark slide?" test was `<p:bg>.*?172124`, which matches any slide that merely
*contains* the old ink `#172124` (it's the heading colour, 10× on slide 10) — not slides whose
*background* is dark. So light slides (10/11/12/13, bg `#FFFFFF`/`#F9FAFA`) were mis-labelled dark →
the correct dark→light move (flip every white→navy) ran on the wrong slides → white circle-numbers
went navy on the kept dark-teal circles → invisible. This is behind most of the reported issues.

Plan:
- [ ] **1. Minimal-diff + background-aware decisions** (was "contrast pass"). Only change a colour when
      it's off-token AND wrong for its *local* context; leave working combos (white-on-teal) alone.
      Anchor every light/dark decision to the element's ACTUAL background (text → its shape fill →
      slide bg), never a slide-wide blanket. Fix the dark-slide detector to read the real bg fill.
      A contrast pass is a cheap **safety-net backstop** (rarely fires), plus add a **contrast/legibility
      dimension to the validator** (token-only gives false confidence).
- [ ] **2. Component-aware re-theming, not raw-hex.** Parse each shape as a unit (fill + stroke + text)
      → classify (card / stat-circle / chip / panel) → apply that component's canonical tokens as a
      SET. Fixes dark boxes (4,5), flipped boxes (6), dark-on-dark circles (10), stray strokes (9).
- [ ] **3. Preserve role, not colour.** Content card → white; deliberate accent/dark panel → keep an
      accent fill AND force white text. Never leave a box dark just because its old fill was a kept
      token (deep-teal). Fixes 4, 5, 11, 12.
- [ ] **4. Map emphasis → accent, not neutral.** Highlighted boxes / hero numbers / "current sprint"
      markers → teal/iris, not navy/grey. Keeps decks alive (8) and preserves highlights (9).
- [ ] **5. Only recolour visible borders** (check stroke width/alpha first) — don't add a stroke where
      there wasn't a meaningful one (9).
- [ ] **6. Transforms always get a visual pass** — auto-render + eyeball; the validator can't see
      dark-on-dark.
- [ ] **7. Validator: geometry / distortion dimension.** For each `<p:pic>`, compare placed box
      aspect (`<a:ext>` cx/cy, minus any `<a:srcRect>` crop) to the image's real pixel aspect; flag
      if off > ~2-3% (stretched/squashed). Extra-precise for bank logos (native dims known → auto-fix
      by snapping to native aspect). Catches any distorted image. (Proven: slide 10 footer logo placed
      3.80:1 vs native 2.42:1 = 57% stretched — the token-only validator missed it, same blind spot
      as contrast.) Alongside the contrast dimension, this makes the validator check *legibility +
      geometry*, not just tokens.
- [ ] **Icon/mark filler** — detect a brand-mark image repeated across many slides (used because there
      were no illustrations) → flag & offer bank illustrations, or drop; don't propagate filler.
- [ ] **Logo variant on bg flip** — swap to the matching bank variant (on-light/on-dark) or recolour a
      monochrome logo when a slide flips light↔dark (white cover logo went invisible on new white bg;
      fixed manually by recolouring → navy).
- [ ] **Casing on transform** — flag uppercase kickers ("SCARLET PROJECT") per the sentence-case rule.
- [ ] **Watermark opacity on flip** — a faint dark-on-dark mark becomes a prominent mid-tone on white;
      tone opacity on flip.

## Scope
- [ ] **Word documents** — phase 2 (own style-set + docx validator). Decks only for now.
