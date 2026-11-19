#!/usr/bin/env python3
"""Scene 5, 'How I work a problem': three problem -> diagnose -> move -> result strips.

Writes assets/cases.svg (850 wide) and assets/cases-narrow.svg (400 wide) from the shared svgkit.
Python 3 stdlib only, deterministic. Never hand-edit the SVGs; change this file and re-run.

Colour grammar: PROBLEM is ash, DIAGNOSE is always EVAL mint (he measures first), MOVE takes the
strip's layer hue, RESULT is ivory with the biggest type and an underline in the layer hue.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgkit as K  # noqa: E402

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

COLS = ("PROBLEM", "DIAGNOSE", "MOVE", "RESULT")
# key, tag word, employer, [(title, [subs]) x 3], (result text, result kind, [context lines])
# Every word and number is from the resume (scene 5 facts); each strip stays inside one employer.
CASES = [
    ("RETR", "ACCURACY", "ValGenesis",
     [("Extraction stuck at ~70%", ["long regulated documents"]),
      ("Gold-set regression harness", ["measure before tuning"]),
      ("Rebuilt evidence retrieval", ["plus targeted model tuning"])],
     ("~90%", "num", ["extraction accuracy"])),
    ("DATA", "DATA", "Kissflow",
     [("60M+ records to move", ["GCS → MongoDB"]),
      ("Zero loss, faster reads", ["two hard constraints"]),
      ("Batch + optimized indexing", ["batch processing"])],
     ("Zero data loss", "word", ["15% ahead of schedule", "retrieval time −40%"])),
    ("SVC", "BACKEND", "Saama",
     [("Slow REST APIs", ["two clinical SaaS products"]),
      ("Profiled the hot paths", ["queries and data model"]),
      ("Query optimization", ["data modeling"])],
     ("+20%", "num", ["API efficiency"])),
]
LIT = ("SVC", "DATA", "RETR")

TITLE = "How I work a problem"
ALT = ("Three problem-solving cases, each read in order as problem, diagnose, move, result: a grey problem tile, a "
       "mint diagnosis tile, a move tile in its colour and an ivory result tile with the biggest type, each stage "
       "marked by a small staircase that gains a step. 1. Accuracy at ValGenesis: extraction stuck at ~70% on long "
       "regulated documents; a gold-set regression harness, measure before tuning; rebuilt evidence retrieval plus "
       "targeted model tuning; ~90% extraction accuracy. 2. Data at Kissflow: 60M+ records to move from GCS to "
       "MongoDB; two hard constraints, zero loss and faster reads; batch processing and optimized indexing; zero data "
       "loss, 15% ahead of schedule, retrieval time down 40%. 3. Backend at Saama: slow REST APIs on two clinical "
       "SaaS products; profiled the hot paths in queries and the data model; query optimization and data modeling; "
       "+20% API efficiency.")
DESC = ("Three problem, diagnose, move, result strips rising left to right: accuracy at ValGenesis, data at Kissflow "
        "and backend at Saama, each ending in its measured result.")
DESC_NARROW = ("Three stacked cards, each reading problem, diagnose, move, result from top to bottom, for accuracy, "
               "data and backend, each ending in its measured result.")

CYCLE, LOOP0, STAGGER = 12, 2.3, 1.5     # one pulse per strip, strips 1.5 s apart, loop starts after the build
TRAVEL = 1.15                            # seconds for a pulse to run PROBLEM -> RESULT
FADE = (2, 2.5)                          # pulse fade in / out, % of the cycle (ends before the next strip starts)


# ---------------------------------------------------------------- shared helpers
def tones(key):
    """Per column: (tile fill hue, fill opacity, stroke opacity, title colour, glyph hue) for one strip."""
    hue = K.HUE[key]
    return [(K.PROBLEM, .14, .35, K.PROBLEM_TEXT, K.PROBLEM),
            (K.EVAL, .12, .40, K.tech_tint(K.EVAL), K.EVAL),
            (hue, .13, .42, K.tech_tint(hue), hue),
            (K.RESULT, .08, .40, K.RESULT, K.RESULT)]


def tw_title(s, narrow):
    """Width of a tile title (sans 650, 12.5px wide / 14px narrow)."""
    return K.tw(s, 14 if narrow else 12.5, bold=True)


def wrap_title(s, maxw, narrow):
    """A title on one line if it fits, else the balanced two-line split (each line asserted to fit)."""
    if tw_title(s, narrow) <= maxw:
        return [s]
    words = s.split()
    best = min(((" ".join(words[:i]), " ".join(words[i:])) for i in range(1, len(words))),
               key=lambda ab: max(tw_title(ab[0], narrow), tw_title(ab[1], narrow)))
    for line in best:
        K.assert_within(tw_title(line, narrow), maxw, f"title line '{line}'")
    return list(best)


def wrap_sub(s, maxw, narrow):
    """A sub-label on one line if it fits; a ' · ' list breaks at its separators; else a measured word wrap."""
    if K.measure(s, "sb", narrow) <= maxw:
        return [s]
    if " · " in s:
        items = s.split(" · ")
        for it in items:
            K.fit(it, "sb", maxw, narrow, "sub item")
        return items
    return K.wrap(s, "sb", maxw, narrow)


STEP_A, STEP_DU, STEP_DV, STEP_H = 10, .8, .36, 6     # staircase glyph: iso scale, run width, tread depth, riser px


def stairs_extent(n):
    """(left, right, height) of an n-step staircase glyph, measured from its bottom vertex."""
    v = STEP_DV * n
    return STEP_DU * STEP_A, v * STEP_A, (STEP_DU + v) * STEP_A / 2 + STEP_H * n


def stairs(x, y_bottom, n, hue):
    """The iso step glyph: n steps (6 px risers, so 6/12/18/24 px tall) climbing to the upper right; bottom vertex at (x, y_bottom)."""
    v = STEP_DV * n
    iso = K.Iso(0, 0, STEP_A)
    px, py = iso.p(STEP_DU, v)
    iso = K.Iso(x - px, y_bottom - py, STEP_A)
    return "".join(iso.box(0, j * STEP_DV, STEP_DU, STEP_DV, (n - j) * STEP_H / iso.s, hue) for j in range(n))


def tile(x, y, w, h, hue, fop, sop):
    """A flat case tile (rx 10) in its column tone."""
    return (f'<rect x="{K.fmt(x)}" y="{K.fmt(y)}" width="{K.fmt(w)}" height="{K.fmt(h)}" rx="10" fill="{hue}" '
            f'fill-opacity="{K.fmt(fop, 2)}" stroke="{hue}" stroke-opacity="{K.fmt(sop, 2)}"/>')


def bright(x, y, w, h, k):
    """RESULT brightening layer: +8% ivory, lit in the still frame, dimmed by the loop until its pulse arrives."""
    return (f'<rect x="{K.fmt(x)}" y="{K.fmt(y)}" width="{K.fmt(w)}" height="{K.fmt(h)}" rx="10" fill="{K.RESULT}" '
            f'fill-opacity=".08" class="rb"{K.delay(LOOP0 + STAGGER * k)}/>')


def underline_glow(x, y, w, hue, k):
    """Transient glow on a result underline (hidden at rest and in reduced motion)."""
    return (f'<rect x="{K.fmt(x - 2)}" y="{K.fmt(y - 1.5)}" width="{K.fmt(w + 4)}" height="5" rx="2.5" fill="{hue}" '
            f'filter="url(#k-glow)" class="ug"{K.delay(LOOP0 + STAGGER * k)}/>')


def result_text(x, y_top, text, kind, hue, narrow):
    """Result numeral (30px) or word result (18px wide / 20px narrow) with its hue underline; returns (svg, w, base)."""
    size = 30 if kind == "num" else (20 if narrow else 18)
    base = y_top + size * .72
    svg, w = K.numeral(x, base, text, hue, size=size)
    return svg, w, base


def lines_svg(x, y, lines, cls, fill=None, lh=14):
    """Stacked text lines in one kit class starting at baseline y; returns (svg, last baseline)."""
    o = [K.txt(x, y + i * lh, s, cls, fill) for i, s in enumerate(lines)]
    return "".join(o), y + (len(lines) - 1) * lh


def title_svg(x, y, lines, fill, lh):
    """Tile title lines in the scene's title class."""
    return "".join(f'<text x="{K.fmt(x)}" y="{K.fmt(y + i * lh)}" class="tl" fill="{fill}">{K.esc(s)}</text>'
                   for i, s in enumerate(lines))


def arrive_css(k_arr):
    """Result brighten + underline glow keyframes, peaking as the pulse arrives (k_arr = arrival, % of cycle)."""
    a = k_arr
    kf = (f"0%,{K.fmt(a - 1, 2)}%{{opacity:0}}{K.fmt(a + 2.5, 2)}%{{opacity:1}}{K.fmt(a + 6, 2)}%{{opacity:1}}"
          f"{K.fmt(a + 13, 2)}%,100%{{opacity:0}}")    # strip 4 settles by ~7.2 s of the 12 s loop
    return (f"@keyframes krb{{{kf}}}.rb{{animation:krb {CYCLE}s ease-in-out both infinite}}"
            f"@keyframes kug{{{kf}}}.ug{{opacity:0;animation:kug {CYCLE}s ease-in-out infinite}}")


def path_pcts(points, travel_pct):
    """Cumulative-length percentages (0..travel_pct) for a polyline, so a pulse moves at constant speed."""
    seg = [math.hypot(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in zip(points, points[1:])]
    tot, acc, out = sum(seg), 0, [0]
    for s in seg:
        acc += s
        out.append(acc / tot * travel_pct)
    return out


# ---------------------------------------------------------------- wide
def build_wide():
    """850-wide card: header row, rising strips of four tiles, a stepped track and a pulse per strip."""
    W, Y0, BAND, GAP, RISE, TW, TH = 850, 88, 118, 14, 6, 160, 100
    XS = (144, 316, 488, 660)                   # 160-wide tiles, 12 px gaps; margins 26 left (tag) / 30 right
    PADL, PADR = 9, 7
    BOXW = TW - PADL - PADR                     # 144: titles and subs wrap inside this
    GB = 16                                     # staircase glyph's bottom vertex sits GB px below the tile top
    TL1 = 31                                    # first title baseline below the tile top
    TRK = 9                                     # track runs TRK px above each tile's bottom edge
    gl, _, gh4 = stairs_extent(4)
    # the tallest glyph pops gh4 - GB px above its tile; keep >= 10 px from the strip above
    K.assert_within(gh4 - GB + 10, GAP + (BAND - TH), "staircase glyph clearance to the strip above")
    H = Y0 + len(CASES) * BAND + (len(CASES) - 1) * GAP + 26
    css_title = (".tl{font-size:12.5px;font-weight:650}")
    body = [K.card(W, H, "PROBLEM → RESULT", lit=LIT)]

    # header row: column words centred over the tile columns, chevrons between them
    hdr = []
    for i, word in enumerate(COLS):
        hdr.append(K.txt(XS[i] + TW / 2, 70, word, "ey", anchor="middle"))
        if i:
            hdr.append(K.chevron(XS[i] - 6 + 2.5, 66.5, 0, K.MUTED, .9, 4, 1.3))
    body.append(f'<g class="hd">{"".join(hdr)}</g>')

    travel = TRAVEL / CYCLE * 100
    pulses, pcss = [], []
    for k, (key, word, org, cells, (rtext, rkind, rctx)) in enumerate(CASES):
        hue = K.HUE[key]
        y0 = Y0 + k * (BAND + GAP)
        tn = tones(key)
        g = []
        # tag column: swatch, layer word, employer (aligned with the first tile's title line)
        t1 = y0 + BAND - TH
        ty = t1 + TL1 + 4
        g.append(f'<rect x="26" y="{K.fmt(ty - 9.5)}" width="10" height="10" rx="2" fill="{hue}"/>')
        K.assert_within(41 + K.tw(word, 11.5, True, 1.5), XS[0] - 10, f"{word} tag")
        g.append(K.txt(41, ty, word, "nm", K.name_tint(hue), size=11.5))
        g.append(K.txt(41, ty + 17, org, "ctx"))

        track = []
        for i in range(4):
            x, top = XS[i], y0 + BAND - TH - RISE * i
            bot = top + TH
            fh, fop, sop, tcol, ghue = tn[i]
            g.append(tile(x, top, TW, TH, fh, fop, sop))
            if i == 3:
                g.append(bright(x, top, TW, TH, k))
            track.append((x, bot - TRK))
            if i < 3:
                tl = wrap_title(cells[i][0], BOXW, False)
                g.append(title_svg(x + PADL, top + TL1, tl, tcol, 15))
                subs = [ln for s in cells[i][1] for ln in wrap_sub(s, BOXW, False)]
                sv, last = lines_svg(x + PADL, top + TL1 + 15 * (len(tl) - 1) + 16, subs, "sb")
                g.append(sv)
                K.assert_within(last + 3, bot - TRK - 7, f"strip {k + 1} {COLS[i]} text above the track")
            else:
                rsvg, rw, base = result_text(x + PADL, top + 24, rtext, rkind, hue, False)
                K.assert_within(rw, BOXW, f"result '{rtext}'")
                g.append(underline_glow(x + PADL, base + 6, rw, hue, k) + rsvg)
                for s in rctx:
                    K.fit(s, "sb", BOXW, what="result context")
                sv, last = lines_svg(x + PADL, base + 20, rctx, "sb")
                g.append(sv)
                K.assert_within(last + 3, bot - TRK - 7, f"strip {k + 1} result text above the track")
            # staircase glyph rising out of the tile's top-left corner: 1 to 4 steps, 6 to 24 px tall
            g.append(stairs(x + PADL + gl, top + GB, i + 1, ghue))

        # stepped track along the tile bottoms: tile segments in the tile tone, gap risers + chevrons in the source hue
        tr = []
        for i in range(4):
            x, y = track[i]
            fh = tn[i][0]
            x1 = x + (14 if i == 0 else 0)
            x2 = x + 24 if i == 3 else x + TW
            tr.append(f'<path d="M{K.fmt(x1)},{K.fmt(y)}H{K.fmt(x2)}" stroke="{fh}" stroke-opacity=".42" '
                      f'stroke-width="1.5" stroke-linecap="round"/>')
            if i == 0:
                tr.append(f'<circle cx="{K.fmt(x1)}" cy="{K.fmt(y)}" r="2.5" fill="{K.PROBLEM}"/>')
            if i < 3:
                xn, yn = track[i + 1]
                tr.append(K.conn([(x + TW, y), (xn, yn)], fh if i else K.PROBLEM_TEXT, op=.75, arrow=False) +
                          K.chevron(xn + 3, yn, 0, fh if i else K.PROBLEM_TEXT, .95, 3.6, 1.4))
        x4, y4 = track[3]
        tr.append(f'<circle cx="{K.fmt(x4 + 24)}" cy="{K.fmt(y4)}" r="3" fill="{K.RESULT}"/>')
        g.append("".join(tr))
        body.append(f'<g class="sr"{K.delay(.2 + .3 * k)}>{"".join(g)}</g>')

        # pulse: runs the track PROBLEM -> RESULT, halo in each passed cell's tone
        pts_ = [(XS[0] + 14, track[0][1])]
        for i in range(3):
            pts_ += [(XS[i] + TW, track[i][1]), (XS[i + 1], track[i + 1][1])]
        pts_.append((XS[3] + 24, track[3][1]))
        pc = path_pcts(pts_, travel)
        stops = [(p, x, y) for p, (x, y) in zip(pc, pts_)]
        hues = [(0, K.PROBLEM), ((pc[1] + pc[2]) / 2, K.EVAL), ((pc[3] + pc[4]) / 2, hue),
                ((pc[5] + pc[6]) / 2, K.RESULT)]
        c, s = K.pulse(f"p{k}", stops, hues, CYCLE, LOOP0 + STAGGER * k, core=2.4, halo=10, fade=FADE)
        pcss.append(c)
        pulses.append(s)
    body.extend(pulses)
    css = (css_title + K.css_rise("sr", 8, .6) + K.css_fade("hd", .5, .05) + "".join(pcss) +
           arrive_css(travel))
    return K.svg_doc(W, H, TITLE, DESC, "", css, "".join(body))


# ---------------------------------------------------------------- narrow
def build_narrow():
    """400-wide re-layout: stacked cards, each a vertical stepper (column word, rail, tile) top to bottom."""
    W, CX0, CX1 = 400, 14, 386
    COLX, RAILX, TX0, TX1 = 26, 107, 115, 372
    PADL = 12
    gl, gr, gh4 = stairs_extent(4)
    BOXW = TX1 - 10 - gr - gl - 8 - (TX0 + PADL)  # text box, clear of the 4-step glyph at the right edge
    TL1, LH_T, LH_S = 23, 18, 17
    ROWGAP, CARDGAP, TAGH = 11, 12, 40          # gaps between rows and cards; rows start TAGH below a card top
    GBOT = 41                                   # staircase glyph's bottom vertex, below the tile top
    css_title = (".tl{font-size:14px;font-weight:650}"
                 f".cw{{font:500 13px {K.MONO};letter-spacing:1.2px;fill:{K.MUTED}}}")
    for word in COLS:     # column words: 13 px mono (the phone floor), clear of the rail
        K.assert_within(COLX + K.tw_mono(word, 13, 1.2), RAILX - 6, f"column word {word}")

    # pre-layout each card to know its height
    cards, y = [], 54
    for k, (key, word, org, cells, (rtext, rkind, rctx)) in enumerate(CASES):
        rows, ry = [], y + TAGH
        for i in range(4):
            if i < 3:
                tl = wrap_title(cells[i][0], BOXW, True)
                subs = [ln for s in cells[i][1] for ln in wrap_sub(s, BOXW, True)]
                last = TL1 + LH_T * (len(tl) - 1) + 18 + LH_S * (len(subs) - 1)
                h = max(last + 13, GBOT + 8)
                rows.append((ry, h, tl, subs))
            else:
                size = 30 if rkind == "num" else 20
                base = 11 + size * .72
                last = base + 25 + LH_S * (len(rctx) - 1)
                h = last + 14
                rows.append((ry, h, None, None))
            ry += h + ROWGAP
        ch = ry - ROWGAP + 13 - y
        cards.append((y, ch, rows))
        y += ch + CARDGAP
    H = y - CARDGAP + 22

    body = [K.card(W, H, "PROBLEM → RESULT", lit=LIT)]
    pulses, pcss = [], []
    travel = TRAVEL / CYCLE * 100
    for k, (key, word, org, cells, (rtext, rkind, rctx)) in enumerate(CASES):
        hue = K.HUE[key]
        tn = tones(key)
        cy, ch, rows = cards[k]
        g = [f'<rect x="{CX0}" y="{K.fmt(cy)}" width="{CX1 - CX0}" height="{K.fmt(ch)}" rx="12" fill="#FFFFFF" '
             f'fill-opacity=".025" stroke="{hue}" stroke-opacity=".28"/>']
        # tag row: swatch, layer word, employer
        tb = cy + 25
        g.append(f'<rect x="{COLX}" y="{K.fmt(tb - 10)}" width="10" height="10" rx="2" fill="{hue}"/>')
        ww = K.measure(word, "nm", True)
        g.append(K.txt(COLX + 17, tb, word, "nm", K.name_tint(hue)))
        K.assert_within(COLX + 17 + ww + 12 + K.measure(org, "ctx", True), CX1 - 14, f"{word} narrow tag")
        g.append(K.txt(COLX + 17 + ww + 12, tb, org, "ctx"))

        nodes = []
        for i, (ry, h, tl, subs) in enumerate(rows):
            fh, fop, sop, tcol, ghue = tn[i]
            g.append(tile(TX0, ry, TX1 - TX0, h, fh, fop, sop))
            if i == 3:
                g.append(bright(TX0, ry, TX1 - TX0, h, k))
            g.append(f'<text x="{COLX}" y="{K.fmt(ry + TL1)}" class="cw">{COLS[i]}</text>')
            if i < 3:
                g.append(title_svg(TX0 + PADL, ry + TL1, tl, tcol, LH_T))
                sv, last = lines_svg(TX0 + PADL, ry + TL1 + LH_T * (len(tl) - 1) + 18, subs, "sb", lh=LH_S)
                g.append(sv)
                K.assert_within(last + 4, ry + h - 6, f"narrow strip {k + 1} {COLS[i]} text")
            else:
                rsvg, rw, base = result_text(TX0 + PADL, ry + 11, rtext, rkind, hue, True)
                K.assert_within(rw, BOXW, f"narrow result '{rtext}'")
                g.append(underline_glow(TX0 + PADL, base + 6, rw, hue, k) + rsvg)
                for s in rctx:
                    K.fit(s, "ctx", BOXW, True, "narrow result context")
                sv, last = lines_svg(TX0 + PADL, base + 25, rctx, "ctx", lh=LH_S)
                g.append(sv)
                K.assert_within(last + 4, ry + h - 6, f"narrow strip {k + 1} result text")
            # staircase glyph at the tile's right edge, one more step each row
            g.append(stairs(TX1 - 10 - STEP_DV * (i + 1) * STEP_A, ry + GBOT, i + 1, ghue))
            nodes.append(ry + TL1 - 4.5)

        # rail: segments in the source tone, down chevrons arriving at each row's node
        rl = []
        for i in range(3):
            fh = tn[i][0] if i else K.PROBLEM_TEXT
            ya, yb = nodes[i], nodes[i + 1]
            rl.append(K.conn([(RAILX, ya + 5), (RAILX, yb - 6)], fh, op=.6, arrow=False) +
                      K.chevron(RAILX, yb - 6, math.pi / 2, fh, .95, 3.6, 1.4))
        for i, yn in enumerate(nodes):
            col = (K.PROBLEM, K.EVAL, hue, K.RESULT)[i]
            rl.append(f'<circle cx="{RAILX}" cy="{K.fmt(yn)}" r="{3 if i == 3 else 2.5}" fill="{col}"/>')
        g.append("".join(rl))
        body.append(f'<g class="sr"{K.delay(.2 + .3 * k)}>{"".join(g)}</g>')

        pts_ = [(RAILX, n) for n in nodes]
        pc = path_pcts(pts_, travel)
        stops = [(p, x, y) for p, (x, y) in zip(pc, pts_)]
        hues = [(0, K.PROBLEM)] + [((pc[i] + pc[i + 1]) / 2, c) for i, c in enumerate((K.EVAL, hue, K.RESULT))]
        c, s = K.pulse(f"p{k}", stops, hues, CYCLE, LOOP0 + STAGGER * k, core=2.4, halo=10, fade=FADE)
        pcss.append(c)
        pulses.append(s)
    body.extend(pulses)
    css = css_title + K.css_rise("sr", 8, .6) + "".join(pcss) + arrive_css(travel)
    return K.svg_doc(W, H, TITLE, DESC_NARROW, "", css, "".join(body))


def guard(svg, what):
    """Refuse bytes that even look like a side-project figure (a coordinate such as 675.8 would trip a reviewer's grep)."""
    for bad in ("675", "13 min"):
        if bad in svg:
            raise ValueError(f"{what}: contains '{bad}'; nudge the layout")
    return svg


if __name__ == "__main__":
    K.write(os.path.join(ASSETS, "cases.svg"), guard(build_wide(), "wide"))
    K.write(os.path.join(ASSETS, "cases-narrow.svg"), guard(build_narrow(), "narrow"))
    print(K.picture("cases", ALT))
