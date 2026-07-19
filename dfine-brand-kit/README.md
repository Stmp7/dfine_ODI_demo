# dfine-brand-kit

A Claude Code plugin for building **on-brand Dfine presentations**. It ships the
`build-deck` skill, which enforces the Dfine palette, fonts, white backgrounds,
and role-correct colours, then auto-validates output against the brand rules.

## What you need

The brand kit builds `.pptx` files, so it rides on top of Anthropic's stock
**`pptx`** skill (from the `anthropic-skills` plugin). Make sure that's installed
too — the brand kit themes and validates; `pptx` does the actual slide I/O.

## Install

1. **Add this repo as a plugin marketplace:**

   ```
   /plugin marketplace add Stmp7/dfine_ODI_demo
   ```

2. **Install the plugin:**

   ```
   /plugin install dfine-brand-kit
   ```

3. Confirm the stock `pptx` skill is available (part of `anthropic-skills`).

## Use

Ask Claude to build a Dfine deck — the `build-deck` skill loads automatically.
The pipeline is `build → theme_and_embed → validate`:

- `skills/build-deck/tokens.json` — single source of truth for colours/fonts/spacing
- `skills/build-deck/scripts/theme_and_embed.py` — applies theme + embeds assets
- `skills/build-deck/scripts/validate_brand.py` — rejects / auto-fixes off-brand drift
- `skills/build-deck/assets/` — curated illustration/icon/logo/font/video bank

See `skills/build-deck/SKILL.md`, `VALIDATION-RULES.md`, and `ASSET-BANK.md` for
details, and `OPEN-THREADS.md` for in-flight work.
