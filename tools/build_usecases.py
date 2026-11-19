#!/usr/bin/env python3
"""Scene 4, 'Use cases I've solved with agents': six outcome tiles (internals hidden).

Writes assets/usecases.svg (850 wide, 3x2 grid) and assets/usecases-narrow.svg (400 wide, one column)
from the shared svgkit. Python 3 stdlib only, deterministic. Never hand-edit the SVGs; change this file
and re-run.

Each tile reads top to bottom, getting brighter as it goes: where (muted eyebrow and domain label), the
problem (ash grey), what the agent does (violet band, the only violet text), the result (ivory, biggest
type). Azure appears only for the human gate and citations in the pattern tile.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgkit as K  # noqa: E402

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

TITLE = "Use cases I've solved with agents"
LIT = ("DATA", "SVC", "AGENT", "TRUST")
AG_TXT = K.tech_tint(K.AGENT)
TR_TXT = K.name_tint(K.TRUST)
UNDER = K.mix(K.RESULT, K.INK, .45)          # dim ivory underline under ivory results

# where, domain label, glyph, problem, agent move [(text, hue)], result [(text, kind, hue)], context lines
# Every word and number is from the resume; tiles 5 and 6 carry no invented metrics (tile 6 has none).
TILES = [
    ("ENEGMA", "Shipping new agents", "orch",
     "Every new agent was built from scratch",
     [("A reusable agent framework with memory, tools and multi-agent orchestration built in", AG_TXT)],
     [("weeks → ~1 day", 25, UNDER)], ["per new agent"]),
    ("ENEGMA", "Changing agent behaviour", "sop",
     "Every behaviour change meant a code change",
     [("Written procedures (SOPs) become agent execution flows on a canvas, so core code stays untouched",
       AG_TXT)],
     [("~60%", 30, UNDER)], ["faster workflow iteration"]),
    ("ENEGMA", "Real-time agents", "micro",
     "Slow first token",
     [("One big prompt split into small, focused prompts (micro-prompting)", AG_TXT)],
     [("~5×", 30, UNDER)], ["faster first token", "~90% fewer prompt tokens"]),
    ("PAYPAL", "Understanding a large codebase", "map",
     "Engineers mapped services and dependencies by hand",
     [("Agents read the code and draw service maps and call graphs", AG_TXT)],
     [("−60%", 30, UNDER)], ["architectural-analysis time", "−70% dependency discovery"]),
    ("PAYPAL · VENMO", "Breaking up a monolith", "split",
     "A 9-month manual service-decomposition process",
     [("An agentic workflow does the decomposition", AG_TXT)],
     [("~30%", 30, UNDER)], ["faster monolith-to-microservices migration"]),
    ("PATTERN I BUILD WITH", "Turning a long spec into working artifacts", "model",
     "Forms, specs and mappings hand-built from a long document",
     [("Agents draft each artifact from a computable model of the document", AG_TXT),
      ("Cited · amendments propagate", TR_TXT)],
     [("AI drafts", 19, UNDER), ("humans approve", 19, K.TRUST)], []),
]

ALT = ("Six use cases solved with agents, each tile read top to bottom as where, problem, what the agent does "
       "and result. 1. Shipping new agents at Enegma: every new agent was built from scratch; a reusable agent "
       "framework with memory, tools and multi-agent orchestration built in; weeks to ~1 day per new agent. "
       "2. Changing agent behaviour at Enegma: every behaviour change meant a code change; written procedures "
       "(SOPs) become agent execution flows on a canvas, so core code stays untouched; ~60% faster workflow "
       "iteration. 3. Real-time agents at Enegma: slow first token; one big prompt split into small, focused "
       "prompts (micro-prompting); ~5× faster first token and ~90% fewer prompt tokens. 4. Understanding a large "
       "codebase at PayPal: engineers mapped services and dependencies by hand; agents read the code and draw "
       "service maps and call graphs; architectural-analysis time down 60% and dependency discovery down 70%. "
       "5. Breaking up a monolith at PayPal (Venmo): a 9-month manual service-decomposition process; an agentic "
       "workflow does the decomposition; ~30% faster monolith-to-microservices migration. 6. Turning a long spec "
       "into working artifacts, a pattern I build with: forms, specs and mappings hand-built from a long "
       "document; the document becomes a structured, computable model, agents draft each artifact, amendments "
       "propagate to everything that depends on them, and every answer cites its section; "
       "AI drafts, humans approve.")
DESC = ("Six tiles in a three by two grid, each showing a problem, what the agent does in a violet band, and the "
        "outcome in large ivory type.")
DESC_NARROW = ("Six stacked tiles, each showing a problem, what the agent does in a violet band, and the outcome "
               "in large ivory type.")

LEGEND = [("PROBLEM", K.PROBLEM), ("WHAT THE AGENT DOES", K.AGENT), ("RESULT", K.RESULT),
          ("APPROVAL · CITATIONS", K.TRUST)]

CYCLE, LOOP0, STAGGER = 12, 2.2, .8      # violet band pulse: one tile at a time, reading order, ~56% still


# ---------------------------------------------------------------- glyphs (kit pieces, right-aligned at xr)
def glyph(kind, xr, gy):
    """The tile's one glyph, its right edge near xr and its ground near gy."""
    if kind == "orch":
        return K.orchestrator(xr - 22, gy + 2, s=.44, n=3)
    if kind == "sop":
        return K.sheet(xr - 20, gy, s=.58, lines=4)
    if kind == "micro":
        return "".join(K.sheet(xr - 40 + 15 * i, gy - 4 + 4 * i, s=.30, lines=2) for i in range(3))
    if kind == "map":
        return K.cubes(xr - 22, gy - 2, s=.62, n=4)
    if kind == "split":
        I = K.Iso(xr - 46, gy - 2, 36)
        return (I.box(.32, .32, .36, .36, 48, K.PROBLEM) +
                K.chevron(xr - 30, gy - 9, 0, K.MUTED, .9, 3.6, 1.3) +
                K.cubes(xr - 12, gy - 2, s=.5, n=2))
    if kind == "model":
        return K.doc_model(xr - 26, gy - 2, s=.5)
    raise KeyError(kind)


# ---------------------------------------------------------------- layout
LH, LH_C = 15, 14          # wide line heights (narrow: +2)


def plan(t, tw, narrow):
    """Measure one tile's text: returns dict of wrapped lines and zone sizes."""
    where, label, g, prob, moves, res, ctx = t
    box = tw - 36
    l_lines = K.wrap(label, "st", box - 50, narrow)          # clear of the top-right glyph
    p_lines = K.wrap(prob, "lb", box, narrow)
    m_lines = []
    for j, (text, fill) in enumerate(moves):
        m_lines += [(ln, fill, 4 * (j > 0 and i == 0)) for i, ln in enumerate(K.wrap(text, "lb", box - 8, narrow))]
    c_lines = [ln for s in ctx for ln in K.wrap(s, "ctx", box, narrow)]
    for text, size, _ in res:
        K.assert_within(K.tw(text, size, bold=True), box, f"result '{text}'")
    return {"l": l_lines, "p": p_lines, "m": m_lines, "c": c_lines}


def band_h(pl, lh):
    """Height of a tile's violet band (18 to the first baseline, 12 below the last; 4 px before a change of colour)."""
    return 18 + lh * (len(pl["m"]) - 1) + sum(g for _, _, g in pl["m"]) + 12


def ftxt(x, y, s, cls, colour):
    """Text in a kit class whose CSS sets a fill: the colour goes in an inline style so it wins over the class."""
    return K.txt(x, y, s, cls, extra=f' style="fill:{colour}"')


def zones(pl, res, narrow):
    """Heights (label, problem, band, result) a tile needs."""
    lh, lhc = LH + 2 * narrow, LH_C + 2 * narrow
    zl = lh * (len(pl["l"]) - 1)
    zp = lh * len(pl["p"])
    zb = band_h(pl, lh)
    if len(res) == 1:
        zr = 16 + res[0][1] * .72 + (24 + lhc * (len(pl["c"]) - 1) if pl["c"] else 8) + 16
    else:
        zr = 16 + res[0][1] * .72 + 30 * (len(res) - 1) + 8 + 14
    return zl, zp, zb, zr


def tile_svg(k, t, x, y, tw, pl, zl, zp, zb, zr, narrow):
    """One tile at (x, y), width tw, using the row's zone heights; returns (tile svg, pulse overlay svg, height)."""
    where, label, g, prob, moves, res, ctx = t
    lh, lhc = LH + 2 * narrow, LH_C + 2 * narrow
    tx, box = x + 18, tw - 36
    eb, lb = y + 24, y + 42 + 2 * narrow
    p0 = lb + zl + 22 + narrow * 2
    bt = p0 + zp - lh + 13                                     # band top
    bh = band_h(pl, lh)                                        # this tile's band hugs its text
    bb = bt + zb                                               # row band bottom: results align across the row
    h = bb + zr - y
    o = [f'<rect x="{K.fmt(x)}" y="{K.fmt(y)}" width="{K.fmt(tw)}" height="{K.fmt(h)}" rx="12" fill="#FFFFFF" '
         f'fill-opacity=".03" stroke="#FFFFFF" stroke-opacity=".11"/>']
    # where + domain label (muted), glyph top right
    K.assert_within(tx + K.measure(where, "ey", narrow) + 6, x + tw - 66, f"eyebrow '{where}' vs glyph")
    o.append(K.txt(tx, eb, where, "ey"))
    o.append("".join(K.txt(tx, lb + i * lh, s, "st", K.MUTED) for i, s in enumerate(pl["l"])))
    o.append(glyph(g, x + tw - 16, y + 30))
    # problem (ash grey)
    o.append("".join(ftxt(tx, p0 + i * lh, s, "lb", K.PROBLEM_TEXT) for i, s in enumerate(pl["p"])))
    # agent band (violet), directly under the problem
    bx, bw = x + 9, tw - 18
    o.append(f'<rect x="{K.fmt(bx)}" y="{K.fmt(bt)}" width="{K.fmt(bw)}" height="{K.fmt(bh)}" rx="8" '
             f'fill="{K.AGENT}" fill-opacity=".10" stroke="{K.AGENT}" stroke-opacity=".30"/>'
             f'<rect x="{K.fmt(bx + 1.5)}" y="{K.fmt(bt + 7)}" width="3" height="{K.fmt(bh - 14)}" rx="1.5" '
             f'fill="{K.AGENT}"/>')
    my = bt + 18
    for s, f, gap in pl["m"]:
        my += gap
        o.append(ftxt(tx + 2, my, s, "lb", f))
        my += lh
    pulse = (f'<rect x="{K.fmt(bx)}" y="{K.fmt(bt)}" width="{K.fmt(bw)}" height="{K.fmt(bh)}" rx="8" '
             f'fill="{K.AGENT}" fill-opacity=".16" stroke="{AG_TXT}" stroke-opacity=".85" stroke-width="1.2" '
             f'class="ap"{K.delay(LOOP0 + STAGGER * k)}/>')
    # result (ivory, biggest type); a two-part word result stacks its parts
    yb = bb + 16 + res[0][1] * .72
    for i, (text, size, hue) in enumerate(res):
        fill = "" if hue != K.TRUST else K.name_tint(K.TRUST)
        svg, w = K.numeral(tx, yb + 30 * i, text, hue, size=size, narrow=narrow)
        if fill:
            svg = svg.replace(f'style="font-size:{K.fmt(size)}px"', f'style="font-size:{K.fmt(size)}px;fill:{fill}"', 1)
        o.append(svg)
    last = yb + 30 * (len(res) - 1)
    for i, s in enumerate(pl["c"]):
        last = yb + 24 + i * lhc
        o.append(K.txt(tx, last, s, "ctx"))
    K.assert_within(last + 10, y + h, f"tile {k + 1} result inside the tile")
    return "".join(o), pulse, h


def legend(x, y, narrow, maxw):
    """Colour key: square swatch + mono word, in one row (wide) or two rows (narrow)."""
    o, cx, cy = [], x, y
    rows = [LEGEND] if not narrow else [LEGEND[:2], LEGEND[2:]]
    for row in rows:
        cx = x
        for word, hue in row:
            o.append(f'<rect x="{K.fmt(cx)}" y="{K.fmt(cy - 8)}" width="8" height="8" rx="2" fill="{hue}"/>')
            o.append(K.txt(cx + 14, cy, word, "ey"))
            cx += 14 + K.measure(word, "ey", narrow) + 22
        K.assert_within(cx - 22, x + maxw, "legend row")
        cy += 20
    return "".join(o), cy - 20


def css_motion():
    """Tile build (rise in reading order) + the one calm loop: a soft violet pulse on each agent band."""
    kf = "0%{opacity:0}4%{opacity:1}11%,100%{opacity:0}"
    return (K.css_rise("tb", 8, .6) + K.css_fade("lg", .5, .05) +
            f"@keyframes kap{{{kf}}}.ap{{opacity:0;animation:kap {CYCLE}s ease-in-out infinite}}")


def build(narrow):
    """Wide: 3x2 grid with row-shared zone heights. Narrow: one column, each tile sized to itself."""
    if narrow:
        W, M, COLS, GAP = 400, 18, 1, 14
    else:
        W, M, COLS, GAP = 850, 28, 3, 16
    tw = (W - 2 * M - GAP * (COLS - 1)) / COLS
    leg, leg_last = legend(M, 62 if not narrow else 60, narrow, W - 2 * M)
    y = leg_last + 18
    plans = [plan(t, tw, narrow) for t in TILES]
    zs = [zones(p, t[5], narrow) for p, t in zip(plans, TILES)]
    tiles, pulses = [], []
    for r in range(0, len(TILES), COLS):
        idx = range(r, r + COLS)
        zl, zp, zb, zr = (max(zs[i][j] for i in idx) for j in range(4))
        hmax = 0
        for c, i in enumerate(idx):
            x = M + c * (tw + GAP)
            svg, pulse, h = tile_svg(i, TILES[i], x, y, tw, plans[i], zl, zp, zb, zr, narrow)
            tiles.append(f'<g class="tb"{K.delay(.25 + .18 * i)}>{svg}</g>')
            pulses.append(pulse)
            hmax = max(hmax, h)
        y += hmax + GAP
    H = round(y - GAP + 24)
    body = [K.card(W, H, "AGENTIC USE CASES", lit=LIT),
            K.glow(W / 2, H * .55, W * .42, H * .38, K.VIOLET, .20),
            f'<g class="lg">{leg}</g>'] + tiles + pulses
    return K.svg_doc(W, H, TITLE, DESC_NARROW if narrow else DESC, "", css_motion(), "".join(body))


if __name__ == "__main__":
    K.write(os.path.join(ASSETS, "usecases.svg"), build(False))
    K.write(os.path.join(ASSETS, "usecases-narrow.svg"), build(True))
    print(K.picture("usecases", ALT))
