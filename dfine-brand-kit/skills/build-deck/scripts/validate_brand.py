#!/usr/bin/env python3
"""
Dfine brand validator — the enforcement teeth.

Scans a .pptx and reports brand violations against tokens.json:
  - fonts     : only the token font families (+ theme scheme refs) allowed
  - colors    : only token hexes allowed for vector fills/lines/text
  - background: every slide background must be pure white
  - images    : lists embedded images; approved-bank hashes vs. user screenshots (advisory)

Raster screenshots/photos are exempt from the colour check by design — their pixels
aren't XML colours, so scanning slide XML naturally ignores them.

Usage:
    python3 validate_brand.py deck.pptx [--tokens tokens.json] [--manifest assets/manifest.json] [--json]

Exit code 0 = clean, 1 = hard violations found. Fonts/colours/background are hard;
image provenance is advisory (see policy.screenshots in tokens.json).
"""
import sys, os, re, json, zipfile, hashlib, argparse, io

try:
    from PIL import Image  # raster logo/mark contrast heuristic; degrades gracefully if absent
except Exception:
    Image = None

HEX = re.compile(r'srgbClr val="([0-9A-Fa-f]{6})"')
FACE = re.compile(r'typeface="([^"]*)"')
EMBED = re.compile(r'r:embed="([^"]+)"')
HERE = os.path.dirname(os.path.abspath(__file__))


HEXVAL = re.compile(r'^#[0-9A-Fa-f]{6}$')

def _collect_hex(node, out):
    """Recursively gather every #RRGGBB token value, skipping the 'deprecated' subtree
    (e.g. the old paper background must NOT be an allowed colour)."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "deprecated":
                continue
            _collect_hex(v, out)
    elif isinstance(node, list):
        for v in node:
            _collect_hex(v, out)
    elif isinstance(node, str) and HEXVAL.match(node):
        out.add(node[1:].upper())

def load_tokens(path):
    t = json.load(open(path, encoding="utf-8"))
    colors = set()
    _collect_hex(t, colors)
    fonts = {t["fonts"]["heading"]["family"], t["fonts"]["body"]["family"]}
    return colors, fonts, t


SHA = re.compile(r'^[0-9a-fA-F]{64}$')

def _collect_sha(node, out):
    """Gather every sha256-looking string anywhere in the manifest, so assets can carry
    per-file hashes (a logo has 1x/2x/3x PNGs) without a rigid schema."""
    if isinstance(node, dict):
        for v in node.values():
            _collect_sha(v, out)
    elif isinstance(node, list):
        for v in node:
            _collect_sha(v, out)
    elif isinstance(node, str) and SHA.match(node):
        out.add(node.lower())

def load_manifest(path):
    hashes = set()
    if path and os.path.exists(path):
        _collect_sha(json.load(open(path, encoding="utf-8")), hashes)
    return hashes


# ── logo/background contrast ────────────────────────────────────────────────
# A logo is a raster PNG, so it's exempt from the palette check by design — which
# also means nothing caught a light logo sitting on a whitened slide (invisible).
# This closes that gap: the manifest tags each logo variant with the background it
# BELONGS on, so a bank logo on the wrong background is an exact, hard violation;
# a non-bank transparent mark that vanishes into its background is an advisory.
LIGHT_BG_VARIANTS = {"on-light", "black"}   # meant to sit on light backgrounds
DARK_BG_VARIANTS = {"on-dark", "white"}     # meant to sit on dark backgrounds

def load_logo_variants(path):
    """sha256 -> 'light'|'dark' : which background this logo file is meant to sit on."""
    out = {}
    if not (path and os.path.exists(path)):
        return out
    logos = (json.load(open(path, encoding="utf-8")).get("logos") or {})
    for name, v in logos.items():
        belongs = "light" if name in LIGHT_BG_VARIANTS else "dark" if name in DARK_BG_VARIANTS else None
        if belongs:
            for h in (v.get("sha256") or {}).values():
                out[h.lower()] = belongs
    return out

def _luminance(hex6):
    """WCAG relative luminance (0=black..1=white) of an #RRGGBB string."""
    r, g, b = (int(hex6[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def _slide_bg_lum(xml):
    """Effective slide background luminance. No <p:bg> => inherits the white master."""
    m = re.search(r'<p:bg>.*?</p:bg>', xml, re.S)
    hexes = HEX.findall(m.group()) if m else []
    return _luminance(hexes[0]) if hexes else 1.0  # 1.0 = white

def _raster_stats(data):
    """(opaque_fraction, mean_luminance_of_opaque_pixels) for a raster image, or None."""
    if Image is None:
        return None
    try:
        im = Image.open(io.BytesIO(data)).convert("RGBA")
    except Exception:
        return None
    im.thumbnail((64, 64))
    px = list(im.getdata())
    if not px:
        return None
    opaque = [(r, g, b) for r, g, b, a in px if a > 40]
    if not opaque:
        return (0.0, None)
    lum = sum(_luminance("%02x%02x%02x" % rgb) for rgb in opaque) / len(opaque)
    return (len(opaque) / len(px), lum)


def scan(pptx, allowed_colors, allowed_fonts, bank_hashes, logo_variants=None):
    z = zipfile.ZipFile(pptx)
    names = z.namelist()
    logo_variants = logo_variants or {}
    v = {"fonts": [], "colors": [], "background": [], "images": [], "logos": [], "logo_warnings": []}

    def parts(prefix):
        return sorted([n for n in names if re.match(prefix, n)])

    # fonts + colours across slides/layouts/masters
    for n in parts(r'ppt/(slides|slideLayouts|slideMasters)/[^/]+\.xml$'):
        d = z.read(n).decode("utf-8", "ignore")
        who = n.split("/")[-1]
        for f in set(FACE.findall(d)):
            if f and not f.startswith("+") and f not in allowed_fonts:
                v["fonts"].append({"part": who, "font": f})
        for c in set(x.upper() for x in HEX.findall(d)):
            if c not in allowed_colors:
                v["colors"].append({"part": who, "hex": "#" + c})

    # background must be white per slide
    WHITE = {"FFFFFF"}
    for n in parts(r'ppt/slides/slide\d+\.xml$'):
        d = z.read(n).decode("utf-8", "ignore")
        m = re.search(r'<p:bg>.*?</p:bg>', d, re.S)
        if m:
            hexes = HEX.findall(m.group())
            if hexes and hexes[0].upper() not in WHITE:
                v["background"].append({"part": n.split("/")[-1], "bg": "#" + hexes[0].upper()})

    # images: approved-bank vs. user screenshot (advisory)
    for n in [x for x in names if re.match(r'ppt/media/', x)]:
        ext = n.rsplit(".", 1)[-1].lower()
        if ext in ("png", "jpg", "jpeg", "gif", "bmp", "tiff", "svg", "emf"):
            h = hashlib.sha256(z.read(n)).hexdigest()
            v["images"].append({
                "file": n.split("/")[-1],
                "in_bank": h in bank_hashes if bank_hashes else None,
            })

    # logo vs. background contrast — per slide, for each image actually placed on it
    RASTER = ("png", "jpg", "jpeg", "gif", "bmp", "tiff")
    for n in parts(r'ppt/slides/slide\d+\.xml$'):
        who = n.split("/")[-1]
        d = z.read(n).decode("utf-8", "ignore")
        bg_lum = _slide_bg_lum(d)
        bg_word = "light" if bg_lum >= 0.5 else "dark"
        # resolve this slide's r:embed ids -> media files via its rels
        rid_ids = set(EMBED.findall(d))
        if not rid_ids:
            continue
        rels_name = f"ppt/slides/_rels/{who}.rels"
        if rels_name not in names:
            continue
        rels = z.read(rels_name).decode("utf-8", "ignore")
        rid_to_media = dict(re.findall(r'Id="([^"]+)"[^>]*Target="[^"]*media/([^"]+)"', rels))
        for rid in rid_ids:
            media = rid_to_media.get(rid)
            if not media or media.rsplit(".", 1)[-1].lower() not in RASTER:
                continue
            mpath = "ppt/media/" + media
            if mpath not in names:
                continue
            data = z.read(mpath)
            h = hashlib.sha256(data).hexdigest().lower()
            # (a) recognised bank logo on the wrong background -> hard violation (exact)
            if h in logo_variants:
                belongs = logo_variants[h]
                if belongs != bg_word:
                    v["logos"].append({"part": who, "file": media,
                                       "logo_for": belongs + " backgrounds", "bg": bg_word,
                                       "fix": f"use the '{'on-light' if bg_word=='light' else 'on-dark'}' logo variant"})
                continue
            # (b) non-bank transparent mark that melts into the background -> advisory.
            # Gated on transparency so opaque screenshots/photos never trip it.
            stats = _raster_stats(data)
            if not stats:
                continue
            opaque_frac, mean_lum = stats
            if mean_lum is None or opaque_frac >= 0.6:
                continue  # opaque => screenshot/photo, not a logo/mark
            if abs(mean_lum - bg_lum) < 0.22:
                v["logo_warnings"].append({"part": who, "file": media,
                                           "contrast": round(abs(mean_lum - bg_lum), 3), "bg": bg_word,
                                           "note": "low-contrast mark, and not a bank logo — place the "
                                                   f"'{'on-light' if bg_word=='light' else 'on-dark'}' logo from assets/logos"})
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("--tokens", default=os.path.join(HERE, "..", "tokens.json"))
    ap.add_argument("--manifest", default=os.path.join(HERE, "..", "assets", "manifest.json"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    colors, fonts, _ = load_tokens(a.tokens)
    bank = load_manifest(a.manifest)
    logo_variants = load_logo_variants(a.manifest)
    v = scan(a.pptx, colors, fonts, bank, logo_variants)

    hard = len(v["fonts"]) + len(v["colors"]) + len(v["background"]) + len(v["logos"])
    report = {
        "file": os.path.basename(a.pptx),
        "clean": hard == 0,
        "hard_violations": hard,
        "fonts": v["fonts"],
        "colors": v["colors"],
        "background": v["background"],
        "logos": v["logos"],
        "logo_warnings": v["logo_warnings"],
        "images": v["images"],
    }
    if a.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"== brand check: {report['file']} ==")
        if v["fonts"]:
            print(f"\nFONTS off-brand ({len(v['fonts'])}): only {sorted(fonts)} allowed")
            for x in v["fonts"]: print(f"   {x['part']:16} {x['font']}")
        if v["colors"]:
            uniq = sorted({x['hex'] for x in v['colors']})
            print(f"\nCOLOURS off-palette ({len(uniq)} unique): {', '.join(uniq)}")
        if v["background"]:
            print(f"\nBACKGROUND not white ({len(v['background'])}):")
            for x in v["background"]: print(f"   {x['part']:16} {x['bg']}")
        if v["logos"]:
            print(f"\nLOGO on wrong background ({len(v['logos'])}):")
            for x in v["logos"]:
                print(f"   {x['part']:16} {x['file']} — {x['logo_for']} logo on a {x['bg']} slide → {x['fix']}")
        if v["logo_warnings"]:
            print(f"\nLOGO low-contrast (advisory, {len(v['logo_warnings'])}):")
            for x in v["logo_warnings"]:
                print(f"   {x['part']:16} {x['file']} — contrast {x['contrast']} on a {x['bg']} slide · {x['note']}")
        imgs = v["images"]
        if imgs:
            unk = [i for i in imgs if i["in_bank"] is False]
            print(f"\nIMAGES: {len(imgs)} embedded" +
                  (f" — {len(unk)} not in the asset bank (treated as user screenshots/photos, allowed)" if bank else " (no manifest — provenance not checked)"))
        print("\n" + ("PASS — on brand" if hard == 0 else f"FAIL — {hard} hard violation(s) to fix"))
    sys.exit(0 if hard == 0 else 1)


if __name__ == "__main__":
    main()
