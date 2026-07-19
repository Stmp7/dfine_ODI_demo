# Drop zone — assets to import into the brand kit

Drop files into the matching subfolder (logos / icons / illustrations / photo), then tell Claude.
Claude will: move them into skills/build-deck/assets/<bank>/, compute sha256, and add manifest
entries + catalogue rows. After import, this folder can be emptied.

- logos/         SVG (+ PNG), transparent bg
- icons/         SVG (from the Figma DS icon set)
- illustrations/ PNG on WHITE (SVG welcome)
- photo/         JPG / PNG
