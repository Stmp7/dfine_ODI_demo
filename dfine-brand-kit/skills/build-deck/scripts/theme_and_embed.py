#!/usr/bin/env python3
"""
Apply the Dfine brand theme + embed clean Bricolage into a .pptx.

Reads tokens.json (single source of truth) to build the theme colour scheme + font scheme,
embeds assets/fonts/BricolageGrotesque-Regular/Bold as the clean 'Bricolage Grotesque' family,
and sweeps any stray fonts (Arial/Aptos/Calibri leaked by generators) to the brand fonts.

Run AFTER generating a deck, BEFORE validate_brand.py:
    python3 theme_and_embed.py deck.pptx
"""
import re, os, sys, shutil, zipfile, json

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)


def clrscheme(t):
    c = t["colors"]
    def v(x): return x.replace("#", "")
    teal = c["teal"]
    return ("<a:clrScheme name=\"Dfine\">"
        f"<a:dk1><a:srgbClr val=\"{v(c['navy']['value'])}\"/></a:dk1><a:lt1><a:srgbClr val=\"FFFFFF\"/></a:lt1>"
        f"<a:dk2><a:srgbClr val=\"{v(c['ink']['value'])}\"/></a:dk2><a:lt2><a:srgbClr val=\"FFFFFF\"/></a:lt2>"
        f"<a:accent1><a:srgbClr val=\"{v(teal['value'])}\"/></a:accent1>"
        f"<a:accent2><a:srgbClr val=\"{v(c['iris']['value'])}\"/></a:accent2>"
        f"<a:accent3><a:srgbClr val=\"{v(c['scarlet']['value'])}\"/></a:accent3>"
        f"<a:accent4><a:srgbClr val=\"{v(c['muted']['value'])}\"/></a:accent4>"
        f"<a:accent5><a:srgbClr val=\"{v(teal['tints'][2])}\"/></a:accent5>"
        f"<a:accent6><a:srgbClr val=\"{v(teal['tints'][0])}\"/></a:accent6>"
        f"<a:hlink><a:srgbClr val=\"{v(teal['value'])}\"/></a:hlink>"
        f"<a:folHlink><a:srgbClr val=\"{v(c['iris']['value'])}\"/></a:folHlink></a:clrScheme>")


def main(pptx):
    t = json.load(open(os.path.join(SKILL, "tokens.json"), encoding="utf-8"))
    head = t["fonts"]["heading"]["family"]; body = t["fonts"]["body"]["family"]
    root = pptx + "._x"
    if os.path.exists(root): shutil.rmtree(root)
    zipfile.ZipFile(pptx).extractall(root)

    # theme
    thp = f"{root}/ppt/theme/theme1.xml"; th = open(thp, encoding="utf-8").read()
    th = re.subn(r'<a:clrScheme.*?</a:clrScheme>', clrscheme(t), th, flags=re.S)[0]
    th = re.subn(r'<a:majorFont>.*?</a:majorFont>', lambda m: re.sub(r'<a:latin typeface="[^"]*"', f'<a:latin typeface="{head}"', m.group(), 1), th, flags=re.S)[0]
    th = re.subn(r'<a:minorFont>.*?</a:minorFont>', lambda m: re.sub(r'<a:latin typeface="[^"]*"', f'<a:latin typeface="{body}"', m.group(), 1), th, flags=re.S)[0]
    open(thp, "w", encoding="utf-8").write(th)

    # font sweep: any stray face -> brand (headings default to Bricolage; keep Avenir)
    for f in [p for p in _walk(root, ".xml")]:
        s = open(f, encoding="utf-8").read()
        s2 = s.replace('typeface="Aptos Display"', f'typeface="{head}"').replace('typeface="Aptos"', f'typeface="{body}"')
        s2 = s2.replace('typeface="Arial"', f'typeface="{body}"').replace('typeface="Calibri"', f'typeface="{body}"')
        s2 = re.sub(r'typeface="Bricolage Grotesque[^"]*"', f'typeface="{head}"', s2)  # normalise long names
        if s2 != s: open(f, "w", encoding="utf-8").write(s2)

    # embed clean Bricolage (regular + bold)
    fd = f"{root}/ppt/fonts"; os.makedirs(fd, exist_ok=True)
    shutil.copy(os.path.join(SKILL, "assets/fonts/BricolageGrotesque-Regular.ttf"), fd + "/dfine-bric-reg.fntdata")
    shutil.copy(os.path.join(SKILL, "assets/fonts/BricolageGrotesque-Bold.ttf"), fd + "/dfine-bric-bold.fntdata")
    ct = f"{root}/[Content_Types].xml"; c = open(ct).read()
    if "fntdata" not in c:
        c = c.replace('<Default Extension="xml"', '<Default Extension="fntdata" ContentType="application/x-fontdata"/><Default Extension="xml"', 1)
        open(ct, "w").write(c)
    rp = f"{root}/ppt/_rels/presentation.xml.rels"; rl = open(rp).read()
    mx = max(int(x) for x in re.findall(r'Id="rId(\d+)"', rl))
    a, b = f"rId{mx+1}", f"rId{mx+2}"
    rl = rl.replace('</Relationships>',
        f'<Relationship Id="{a}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/font" Target="fonts/dfine-bric-reg.fntdata"/>'
        f'<Relationship Id="{b}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/font" Target="fonts/dfine-bric-bold.fntdata"/></Relationships>')
    open(rp, "w").write(rl)
    pp = f"{root}/ppt/presentation.xml"; pr = open(pp).read()
    if "embedTrueTypeFonts" not in pr: pr = pr.replace("<p:presentation ", '<p:presentation embedTrueTypeFonts="1" ', 1)
    pr = re.sub(r'<p:embeddedFontLst>.*?</p:embeddedFontLst>', '', pr, flags=re.S)
    efl = f'<p:embeddedFontLst><p:embeddedFont><p:font typeface="{head}"/><p:regular r:id="{a}"/><p:bold r:id="{b}"/></p:embeddedFont></p:embeddedFontLst>'
    pr = re.subn(r'(<p:defaultTextStyle)', efl + r'\1', pr, count=1)[0] if "<p:defaultTextStyle" in pr else pr.replace("</p:presentation>", efl + "</p:presentation>")
    open(pp, "w").write(pr)

    os.remove(pptx)
    with zipfile.ZipFile(pptx, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(ct, "[Content_Types].xml")
        for base, _, files in os.walk(root):
            for f in files:
                arc = os.path.relpath(os.path.join(base, f), root)
                if arc != "[Content_Types].xml": z.write(os.path.join(base, f), arc)
    shutil.rmtree(root)
    print(f"themed + embedded: {os.path.basename(pptx)}")


def _walk(root, ext):
    for base, _, files in os.walk(root):
        for f in files:
            if f.endswith(ext): yield os.path.join(base, f)


if __name__ == "__main__":
    main(sys.argv[1])
