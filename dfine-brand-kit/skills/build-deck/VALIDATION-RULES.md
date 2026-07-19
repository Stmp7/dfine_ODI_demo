# Validation rules & rationale

The exact values live in `tokens.json` (single source of truth). This file explains the
*rules and the why*, so the model applies them with judgment rather than rote.

## Backgrounds — pure white only
Every slide background is `#FFFFFF`. The brand illustrations are drawn/exported on a white
ground, so any off-white background (the old `#F9FAFB` paper, tints, gradients) shows a visible
rectangular seam or halo behind a placed PNG. White is not a stylistic default here — it's a
compositing requirement. The validator fails any non-white slide background.

## Fonts
- Headings: **Bricolage Grotesque** — the *clean* family name, exactly. Never
  `Bricolage Grotesque 14pt Medium` or any optical-size named-instance string; those are
  variable-font instance names that fail to resolve on machines with the font installed
  normally, so titles silently fall back. Embed the clean OFL family so it travels.
- Body: **Avenir** (macOS-native). It's licensed and not embeddable; decks target Mac, and on
  Windows it substitutes acceptably.
- Any other typeface (Aptos, Calibri, Satoshi, Inter, …) is off-brand for decks and gets fixed.
  (Satoshi/Inter belong to the *product UI*, not brand presentations.)

## Colours — by role, from the token set
Only hexes in `tokens.json` are allowed for vector fills, lines, and text. Beyond "is it a token",
usage must be role-correct:
- **Neutral grey (`border.default`/`border.strong`) for chrome** — card/field/input borders,
  dividers, table lines. Never teal or any accent for borders.
- **Teal** = primary/identity accent. **Iris** = bloom accent. **Scarlet** = the *single* signal,
  used sparingly (one per surface), never a wash or a background.
- **Navy/ink** for text; **muted** for secondary text.
- **Status colours** (success/warning/caution/danger) *only* for status meaning — `-strong` for
  fills/dots/borders, `-text` for coloured text on white (readable contrast), `-bg` for tints.
  Never reuse a status colour as decoration.

## Images
- **Illustrations & icons: bank only.** Use files from `assets/illustrations` and `assets/icons`.
  Never generate or invent art/icons. The manifest carries a `sha256` per approved asset; the
  validator can confirm an embedded illustration matches the bank.
- **Logo: bank only, never recreated.** Use only the files in `assets/logos`. Never redraw the
  logo as shapes or text, and never regenerate it as an image — place the approved asset
  unmodified. A fabricated logo is the worst kind of off-brand; the manifest `sha256` lets the
  validator confirm a placed logo is the real one.
- **Screenshots / photos: allowed anywhere.** Product screenshots have arbitrary pixel colours;
  they're exempt from the palette check (the check only sees XML vector colours, not raster
  pixels). Chrome around them is still enforced.

## Logo vs. background — contrast
A logo is a raster PNG, so it's exempt from the palette check (its pixels aren't XML colours).
That exemption once let a *light* logo survive on a slide whose background got flipped to white —
technically "on brand", visually invisible. Two guards close that gap:

- **The transform rule (prevention).** Whenever a transform inverts a slide's background lightness
  (dark→light or light→dark), it **must** swap the logo to the matching variant in the same pass.
  The background flip and the logo choice are coupled — never change one without the other. The
  manifest tags each variant with the background it belongs on: `on-light` / `black` sit on light
  grounds; `on-dark` / `white` sit on dark grounds.
- **The validator check (backstop).** The validator resolves each image actually placed on a slide
  and compares it to that slide's background: a recognised **bank** logo on the wrong-lightness
  background is a **hard** violation (exact, via the manifest hashes). A **non-bank** transparent
  mark whose luminance melts into the background (contrast < ~0.22) is an **advisory** — gated on
  transparency so opaque screenshots/photos never trip it — and it nudges you to place the correct
  bank logo instead. Fix by placing the right variant from `assets/logos` (never a recreated logo).

## On a violation — auto-fix vs. respect intent
- **Drift** (the model produced something off-brand on its own) → **auto-fix silently** and note
  it: snap colour to nearest token, font to Bricolage/Avenir, background to white.
- **Explicit user request** for an off-brand value → **do not override.** Warn it's off-brand,
  suggest the on-brand equivalent, let the user decide. Intent beats the rule.

The distinction matters: enforcement should protect people from accidents, not fight their
deliberate choices.
