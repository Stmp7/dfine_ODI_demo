const pptxgen = require("pptxgenjs");
const fs = require("fs");
const KIT = "/Users/ran/Library/CloudStorage/OneDrive-DreamAdvancedTechnologies/Documents/Olympus/dfine-brand-kit/skills/build-deck";
const T = JSON.parse(fs.readFileSync(KIT + "/tokens.json", "utf8"));
const hx = s => s.replace("#", "");
const C = {
  white: "FFFFFF", paper: "FFFFFF",
  ink: hx(T.colors.ink.value), navy: hx(T.colors.navy.value), muted: hx(T.colors.muted.value),
  teal: hx(T.colors.teal.value), iris: hx(T.colors.iris.value), scarlet: hx(T.colors.scarlet.value),
  line: hx(T.border.default), faint: hx(T.surface.muted),
};
const HEAD = "Bricolage Grotesque", BODY = "Avenir";
const A = "tb_build/assets", I = "tb_build";
const p = new pptxgen(); p.layout = "LAYOUT_WIDE";
const W = 13.333, H = 7.5, M = 0.9;
const white = { color: "FFFFFF" };
const illo = (path, aspect) => { const w = W, h = W / aspect; return { path, x: 0, y: (H - h) / 2, w, h }; };

// 1 — COVER (hero illustration right, text in left safe zone, logo top-left)
let s = p.addSlide(); s.background = white;
s.addImage(illo(`${A}/single-flower.png`, 1800 / 941));
s.addImage({ path: `${A}/logo.png`, x: M, y: 0.6, w: 1.9, h: 1.9 * 755 / 1828 });
s.addText("Sovereign cyber\nresilience, engineered.", { x: M, y: 2.7, w: 5.4, h: 2, fontFace: HEAD, fontSize: 40, color: C.navy, bold: false, charSpacing: -0.3, lineSpacingMultiple: 1.02 });
s.addText("Dfine · Scarlet overview", { x: M, y: 4.8, w: 5, h: 0.5, fontFace: BODY, fontSize: 16, color: C.muted });

// 2 — STATEMENT
s = p.addSlide(); s.background = white;
s.addShape(p.ShapeType.rect, { x: M, y: 2.55, w: 0.16, h: 2.4, fill: { color: C.iris } });
s.addText("Built from nodes,\ngrown into meaning.", { x: M + 0.5, y: 2.4, w: 11, h: 2.8, fontFace: HEAD, fontSize: 52, color: C.navy, bold: false, lineSpacingMultiple: 1.02, charSpacing: -0.5 });

// 3 — KPI ROW
s = p.addSlide(); s.background = white;
s.addText("Metrics", { x: M, y: 0.62, w: 6, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: C.teal, charSpacing: 2 });
s.addText("Key metrics", { x: M, y: 0.95, w: 11, h: 0.9, fontFace: HEAD, fontSize: 34, color: C.navy, bold: false });
[["98%", "Network coverage", C.teal], ["3.2k", "Assets mapped", C.iris], ["12", "Integrations", C.navy], ["< 5 min", "Time to first map", C.scarlet]]
  .forEach(([n, l, col], i) => { const x = M + i * 2.9; s.addText(n, { x, y: 2.9, w: 2.75, h: 1.1, fontFace: HEAD, fontSize: 52, color: col, bold: false, charSpacing: -1 }); s.addText(l, { x, y: 4.05, w: 2.75, h: 0.5, fontFace: BODY, fontSize: 15, color: C.muted }); });

// 4 — THREE-UP with bank icons (teal)
s = p.addSlide(); s.background = white;
s.addText("What Scarlet does", { x: M, y: 0.75, w: 11, h: 0.9, fontFace: HEAD, fontSize: 34, color: C.navy, bold: false });
const cards = [["icon_globe", "Full picture", "One source of truth — every asset and relationship, mapped as it changes."],
["icon_shield", "Investigate", "Analyst-led, objective-driven insight across paths and critical assets."],
["icon_database", "Simulate", "A high-fidelity twin — validate and rehearse changes safely."]];
const cw = 3.7, cg = 0.4, cy = 2.1;
cards.forEach(([ic, h, b], i) => { const x = M + i * (cw + cg);
  s.addShape(p.ShapeType.roundRect, { x, y: cy, w: cw, h: 3.9, rectRadius: 0.12, fill: { color: C.white }, line: { color: C.line, width: 1 } });
  s.addImage({ path: `${I}/${ic}.png`, x: x + 0.4, y: cy + 0.45, w: 0.62, h: 0.62 });
  s.addText(h, { x: x + 0.4, y: cy + 1.3, w: cw - 0.8, h: 0.6, fontFace: HEAD, fontSize: 21, color: C.navy, bold: false });
  s.addText(b, { x: x + 0.4, y: cy + 1.95, w: cw - 0.8, h: 1.7, fontFace: BODY, fontSize: 14.5, color: C.muted, lineSpacingMultiple: 1.25, valign: "top" }); });

// 5 — SECTION with network-branch illustration
s = p.addSlide(); s.background = white;
s.addImage(illo(`${A}/network-branch.png`, 1672 / 941));
s.addText("Section", { x: M, y: 2.75, w: 5, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: C.teal, charSpacing: 2 });
s.addText("The living network", { x: M, y: 3.15, w: 5.6, h: 1.4, fontFace: HEAD, fontSize: 40, color: C.navy, bold: false, charSpacing: -0.3 });

// 6 — CLOSING
s = p.addSlide(); s.background = white;
s.addImage({ path: `${A}/logo.png`, x: M, y: 2.9, w: 2.6, h: 2.6 * 755 / 1828 });
s.addText("Sovereign cyber resilience, engineered.", { x: M, y: 4.1, w: 10, h: 0.9, fontFace: HEAD, fontSize: 28, color: C.navy, bold: false, charSpacing: -0.3 });
s.addText("dfinesecurity.com", { x: M, y: 5.0, w: 6, h: 0.5, fontFace: BODY, fontSize: 16, color: C.teal });

p.writeFile({ fileName: "sample.pptx" }).then(f => console.log("wrote", f));
