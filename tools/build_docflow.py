#!/usr/bin/env python3
"""Scene: 'Intelligence inside a large-document workflow' - the judgments the model makes at each step.

Writes assets/docflow.svg (850 wide) and assets/docflow-narrow.svg (400 wide) from the shared svgkit.
Python 3 stdlib only, deterministic. Never hand-edit the SVGs; change this file and re-run.

Shows the WORKFLOW, not the system: a thick stack of long regulated documents runs through five steps
(Read, Find, Extract, Verify, Decide). Each step carries a violet callout phrased as the question the model
answers. Decide ships a cited result or routes to a human reviewer whose correction flows back. Underneath, a
mint loop measures every change against a gold set (extraction accuracy ~70% to ~90%, the card's one metric).

Colour grammar: violet = the model's judgment only; azure = verification, review and citations; mint =
measurement; ivory = outcomes; greys = documents, rails and plain workflow steps.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgkit as K  # noqa: E402

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
fmt = K.fmt

TITLE = "Intelligence inside a large-document workflow"
KICKER = "LARGE-DOCUMENT WORKFLOWS · WHERE THE INTELLIGENCE SITS"
KICKER_NARROW = "LARGE-DOCUMENT WORKFLOWS"
LIT = ("AGENT", "TRUST")

# (verb, hue, question the model answers, sub-label under the step)
STEPS = [
    ("Read", None, "What is this document? Which parts matter?", None),
    ("Find", None, "Where is the evidence for this field?", None),
    ("Extract", None, "What does it actually say?", "each value stays tied to its page"),
    ("Verify", K.TRUST, "Does it agree with the rest of the document?", "rules act as guardrails"),
    ("Decide", K.TRUST, "Sure enough to ship?", None),
]
NUM_A, NUM_B = "~70%", "~90%"
NUM_CTX = "extraction accuracy"
GOLD = "Every change is measured against a gold set"

ALT = ("A large-document workflow and where the intelligence sits in it. A thick stack of long regulated "
       "documents enters from the left and moves through five steps on one lane, each with a violet callout "
       "giving the question the model answers there. Read: what is this document, which parts matter? Find: "
       "where is the evidence for this field? Extract: what does it actually say? Each value stays tied to its "
       "page. Verify: does it agree with the rest of the document? Rules act as guardrails. Decide: sure enough "
       "to ship? If yes, a structured, page-cited result; if not sure, a human reviewer checks it and the "
       "correction flows back. Underneath, a mint measurement loop: every change is measured against a gold set, "
       "and a gauge shows extraction accuracy rising from ~70% to ~90%.")
DESC = ("Five workflow steps, Read, Find, Extract, Verify and Decide, each with the question the model answers; "
        "confident results ship page-cited, uncertain ones go to a human reviewer and back; every change is "
        "measured against a gold set, extraction accuracy ~70% to ~90%.")
DESC_NARROW = ("The same workflow top to bottom: five steps with the model's question at each, a human-review "
               "detour, a page-cited result, and a gold-set measurement loop showing ~70% to ~90% extraction "
               "accuracy.")

CYCLE = 22                      # two pulses share a 22 s cycle, 11 s apart: one mover at a time, ~70% still
SPEED = 240                     # px/s for the document pulse
PAUSE = .7                      # s the pulse rests at the reviewer
GREY = K.TEXT2


# ---------------------------------------------------------------- helpers
def pct(t):
    return t / CYCLE * 100


def path_stops(points, t0, pauses=None):
    """[(pct, x, y)] for a pulse moving at SPEED through points from time t0 (s); pauses = {index: seconds}."""
    pauses = pauses or {}
    out, t = [(pct(t0), *points[0])], t0
    for i, ((x1, y1), (x2, y2)) in enumerate(zip(points, points[1:])):
        if i in pauses:
            t += pauses[i]
            out.append((pct(t), x1, y1))
        t += math.hypot(x2 - x1, y2 - y1) / SPEED
        out.append((pct(t), x2, y2))
    return out


def arrival(points, idx):
    """Seconds for the pulse to reach points[idx] from points[0]."""
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points[:idx], points[1:idx + 1])) / SPEED


def title_fill(hue):
    return K.TEXT if hue is None else K.name_tint(hue)


def callout(x0, y0, w, lines, narrow, tail=None, flash_delay=None):
    """Violet judgment callout: tinted box, question lines, orb badge on the top-left border, optional tail
    (x, y_tip) pointing down; returns (svg, height)."""
    lh = 17 if narrow else 14
    top = 18 if narrow else 17
    pad_b = 10 if narrow else 9
    px = 12 if narrow else 6
    h = top + lh * (len(lines) - 1) + pad_b
    fill = K.tech_tint(K.AGENT)
    o = [f'<rect x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(w)}" height="{fmt(h)}" rx="8" fill="{K.AGENT}" '
         f'fill-opacity=".10" stroke="{K.AGENT}" stroke-opacity=".5"/>']
    if tail:
        tx, ty = tail
        o.append(f'<path d="M{fmt(tx - 5)},{fmt(y0 + h)}L{fmt(tx)},{fmt(ty)}L{fmt(tx + 5)},{fmt(y0 + h)}" '
                 f'fill="{K.mix(K.AGENT, K.INK, .62)}" stroke="{K.AGENT}" stroke-opacity=".5" stroke-linejoin="round"/>'
                 f'<path d="M{fmt(tx - 4)},{fmt(y0 + h)}H{fmt(tx + 4)}" stroke="{K.mix(K.AGENT, K.INK, .62)}" '
                 f'stroke-width="1.6"/>')
    for i, ln in enumerate(lines):
        o.append(K.txt(x0 + px, y0 + top + i * lh, ln, "t", fill))
    bx, by = x0 + (16 if narrow else 13), y0
    o.append(f'<circle cx="{fmt(bx)}" cy="{fmt(by)}" r="6" fill="{K.INK}"/>' + K.orb(bx, by, 3.4, lift=0, shadow=False))
    if flash_delay is not None:
        o.append(f'<circle cx="{fmt(bx)}" cy="{fmt(by)}" r="8.5" fill="none" stroke="{K.ORB_GLOW}" stroke-width="1.5" '
                 f'class="bf"{K.delay(flash_delay)}/>')
    return "".join(o), h


def magnifier(x, y, s):
    """Grey 'find' lens: ring plus handle (screen space)."""
    r = 5.6 * s
    hx, hy = x - r * .72, y + r * .72
    return (f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}" fill="{K.INK}" fill-opacity=".35" stroke="{K.TEXT}" '
            f'stroke-width="1.7"/><path d="M{fmt(hx)},{fmt(hy)}L{fmt(hx - 5 * s)},{fmt(hy + 5 * s)}" stroke="{K.TEXT}" '
            f'stroke-width="2.4" stroke-linecap="round"/>')


def step_glyph(k, x, y, s):
    """Glyph standing on a step's slab top centre (x, y)."""
    if k == 0:      # Read: two sheets, the front one tabbed
        return K.sheet(x - 7 * s, y - 3 * s, .5 * s, op=.45) + K.sheet(x + 3 * s, y + 2 * s, .5 * s, tab=GREY)
    if k == 1:      # Find: a sheet with a lens over it
        return K.sheet(x - 2 * s, y + 1 * s, .52 * s) + magnifier(x + 9 * s, y - 9 * s, s)
    if k == 2:      # Extract: a cited sheet with one value lifting off it
        vx, vy = x + 13 * s, y - 17 * s
        return (K.sheet(x - 4 * s, y + 1 * s, .52 * s, bookmark_tab=True) +
                f'<path d="M{fmt(x + 4 * s)},{fmt(y - 4 * s)}L{fmt(vx - 4 * s)},{fmt(vy + 3 * s)}" stroke="{K.TEXT}" '
                f'stroke-opacity=".6" stroke-dasharray="1.5 2"/>'
                f'<rect x="{fmt(vx - 8 * s)}" y="{fmt(vy - 3.5 * s)}" width="{fmt(16 * s)}" height="{fmt(7 * s)}" '
                f'rx="{fmt(2 * s)}" fill="{K.TEXT}" fill-opacity=".92"/>')
    if k == 3:      # Verify: sealed azure tile with a check
        return K.check_tile(x, y, .62 * s)
    if k == 4:      # Decide: the gate the document must pass
        return K.gate(x + 7 * s, y + 3 * s, .8 * s, figure=False)
    return K.sheet(x, y, .56 * s, bookmark_tab=True)        # output


def slab_for(x, y, a, hue):
    return K.slab(K.Iso(x, y, a), 10, hue)


def gauge(cx, cy, r):
    """240-degree accuracy gauge: muted 0-70 arc, mint 70-90 arc, ticks, ghost needle at 70, white needle at 90
    that sweeps up from 70 once on load; returns (svg, css)."""
    a0, span = 150, 240
    ang = lambda v: math.radians(a0 + span * v / 100)
    P = lambda v, rr: (cx + rr * math.cos(ang(v)), cy + rr * math.sin(ang(v)))

    def arc(v0, v1, rr):
        (x0, y0), (x1, y1) = P(v0, rr), P(v1, rr)
        big = 1 if span * (v1 - v0) / 100 > 180 else 0
        return f"M{fmt(x0)},{fmt(y0)}A{fmt(rr)},{fmt(rr)} 0 {big} 1 {fmt(x1)},{fmt(y1)}"

    ticks = "".join(f"M{fmt(P(v, r - 7.5)[0])},{fmt(P(v, r - 7.5)[1])}L{fmt(P(v, r - 4)[0])},{fmt(P(v, r - 4)[1])}"
                    for v in range(0, 101, 10))
    (nx, ny), (gx, gy) = P(90, r - 9), P(70, r - 9)
    svg = (f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r + 6)}" fill="{K.INK}" fill-opacity=".6" '
           f'stroke="{K.EVAL}" stroke-opacity=".25"/>'
           f'<path d="{arc(0, 100, r)}" fill="none" stroke="#FFFFFF" stroke-opacity=".1" stroke-width="4" '
           f'stroke-linecap="round"/>'
           f'<path d="{arc(0, 70, r)}" fill="none" stroke="{K.MUTED}" stroke-opacity=".5" stroke-width="4" '
           f'stroke-linecap="round"/>'
           f'<path d="{arc(70, 90, r)}" fill="none" stroke="{K.EVAL}" stroke-width="4" stroke-linecap="round"/>'
           f'<path d="{ticks}" stroke="{K.EVAL}" stroke-opacity=".55" stroke-width="1.2"/>'
           f'<path d="M{fmt(cx)},{fmt(cy)}L{fmt(gx)},{fmt(gy)}" stroke="{K.MUTED}" stroke-opacity=".7" '
           f'stroke-width="1.5" stroke-linecap="round" stroke-dasharray="2 3"/>'
           f'<g class="nd"><path d="M{fmt(cx)},{fmt(cy)}L{fmt(nx)},{fmt(ny)}" stroke="#FFFFFF" stroke-width="2.2" '
           f'stroke-linecap="round"/></g>'
           f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="3.6" fill="#FFFFFF"/>'
           f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="1.4" fill="{K.INK}"/>')
    css = (f"@keyframes knd{{from{{transform:rotate(-48deg)}}to{{transform:none}}}}"
           f".nd{{transform-origin:{fmt(cx)}px {fmt(cy)}px;animation:knd 1.6s {K.EASE} 2.9s both}}")
    return svg, css


def readout(x, y, small, big):
    """'~70%' (small, muted) arrow '~90%' (big, ivory, mint underline); y = baseline; returns (svg, w)."""
    wa, wb = K.tw(NUM_A, small, True), K.tw(NUM_B, big, True)
    g, aw = 9, 22
    ay = y - small * .36
    ax0, ax1 = x + wa + g, x + wa + g + aw
    bx = ax1 + g
    return (f'<text x="{fmt(x)}" y="{fmt(y)}" class="num" style="font-size:{fmt(small)}px;fill:{K.TEXT2}">{NUM_A}</text>'
            f'<path d="M{fmt(ax0)},{fmt(ay)}H{fmt(ax1 - 1)}M{fmt(ax1 - 5)},{fmt(ay - 4.2)}L{fmt(ax1)},{fmt(ay)}'
            f'L{fmt(ax1 - 5)},{fmt(ay + 4.2)}" fill="none" stroke="{K.TEXT2}" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<text x="{fmt(bx)}" y="{fmt(y)}" class="num" style="font-size:{fmt(big)}px">{NUM_B}</text>'
            f'<rect x="{fmt(bx)}" y="{fmt(y + 7)}" width="{fmt(wb)}" height="2" rx="1" fill="{K.EVAL}"/>', bx + wb - x)


def gold_glyph(x, y, s):
    """Gold set: a small sheet stack with a mint check badge."""
    bx, by = x + 15 * s, y - 20 * s
    return (K.sheet_stack(x, y, .42 * s, n=4, gap=2) +
            f'<circle cx="{fmt(bx)}" cy="{fmt(by)}" r="{fmt(6.5 * s)}" fill="{K.EVAL}"/>'
            f'<path d="M{fmt(bx - 3 * s)},{fmt(by)}L{fmt(bx - .8 * s)},{fmt(by + 2.4 * s)}L{fmt(bx + 3.2 * s)},'
            f'{fmt(by - 2.4 * s)}" fill="none" stroke="{K.INK}" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


BUILD_CSS = "".join([
    K.css_drop("dp", 14, .7), K.css_rise("sr", 8, .6), K.css_fade("ln", .5),
    K.css_rise("cl", 6, .55), K.css_fade("br", .6), K.css_draw("cd", 1.0, 2.5), K.css_fade("ev", .6),
    K.css_flash("bf", CYCLE / 2, 3, 16, .9),
])


# ---------------------------------------------------------------- wide
def build_wide():
    W = 850
    PL, PW = 18, 814                          # lane platform, front face x 18..818
    SX = 66                                   # document stack
    CW, CG = 112, 6                           # callout width and gap
    XS = [106 + CG + CW / 2 + i * (CW + CG) for i in range(5)]      # 168, 286, 404, 522, 640
    OX = XS[4] + CW + CG                      # 758: cited output
    A = 29                                    # slab half-width
    CY0 = 62                                  # callout row top
    TXW = CW - 11
    qlines = [K.wrap(q, "t", TXW) for _, _, q, _ in STEPS]
    assert max(len(q) for q in qlines) <= 3, qlines
    CH = 17 + 14 * 2 + 9                      # 3-line callouts, all the same height
    PY = CY0 + CH + 14                        # plate top
    FT = PY + 9                               # plate front face top
    TY = FT + 19                              # title baseline
    LY = TY + 38                              # lane (slab top centre)
    SUB = LY + 31                             # first sub-label baseline
    FB = SUB + 13.5 + 12                      # plate front face bottom
    RY = FB + 54                              # reviewer ground point
    EV = RY + 36                              # measurement conduit
    GY = EV + 64                              # gauge centre
    H = int(GY + 36 + 24)
    RX_RET = 702                              # return path joins the lane here

    body = [K.card(W, H, KICKER, lit=LIT),
            K.glow(SX + 10, LY, 140, 80, K.WARM, .16),
            K.glow((XS[0] + XS[4]) / 2, CY0 + CH / 2, 330, 70, K.VIOLET, .20)]

    # ---- lane platform, stack, steps, output
    lane = [K.plate(PL, PY, PW, FB - FT),
            K.floor_shadow(SX, LY + 8, 34, 13), K.sheet_stack(SX, LY + 10, .74, n=11, gap=2.1)]
    lane.append(K.txt(SX, TY, "Documents", "st", K.TEXT, "middle"))
    lane.append(K.txt(SX, SUB, "long, regulated", "sb", anchor="middle"))
    body.append(f'<g class="dp"{K.delay(.1)}>{"".join(lane)}</g>')

    for k, (verb, hue, _, sub) in enumerate(STEPS):
        x = XS[k]
        g = [slab_for(x, LY, A, hue or GREY), step_glyph(k, x, LY, 1),
             K.txt(x, TY, verb, "st", title_fill(hue), "middle")]
        if sub:
            for i, ln in enumerate(K.wrap(sub, "sb", CW - 8)):
                g.append(K.txt(x, SUB + i * 13.5, ln, "sb", anchor="middle"))
                K.assert_within(SUB + i * 13.5 + 4, FB - 4, f"{verb} sub inside the lane")
        body.append(f'<g class="sr"{K.delay(.35 + .12 * k)}>{"".join(g)}</g>')
    out = [slab_for(OX, LY, A, K.RESULT), step_glyph(5, OX, LY, 1),
           K.txt(OX, TY, "Cited output", "st", K.RESULT, "middle")]
    for i, ln in enumerate(("structured,", "page-cited result")):
        out.append(K.txt(OX, SUB + i * 13.5, ln, "sb", K.mix(K.RESULT, K.TEXT2, .35), "middle"))
        K.assert_within(OX + K.measure(ln, "sb") / 2, PL + PW - 14 - 10, "output label inside the lane")
    body.append(f'<g class="sr"{K.delay(.95)}>{"".join(out)}</g>')

    # ---- lane connectors (source hue)
    nodes = [SX] + XS + [OX]
    links = []
    for i in range(6):
        x1 = nodes[i] + (34 if i == 0 else A + 4)
        x2 = nodes[i + 1] - A - 5
        hue = K.TRUST if i >= 4 else GREY
        links.append(f'<g class="ln"{K.delay(.9 + .1 * i)}>'
                     f'{K.conn([(x1, LY), (x2, LY)], hue, op=.6 if hue == K.TRUST else .45)}</g>')
    body.append("".join(links))
    body.append(f'<g class="ln"{K.delay(1.5)}>{K.txt(XS[4] + A + 6, LY - 7, "yes", "sb", K.tech_tint(K.TRUST))}</g>')

    # ---- judgment callouts (violet), one per step, tail down to the lane top
    t_arr = [arrival([(SX + 34, LY)] + [(x, LY) for x in XS], k + 1) for k in range(5)]
    loop0 = 3.6
    calls = [K.txt(28, CY0 + 18, "THE MODEL", "ey", K.tech_tint(K.AGENT)),
             K.txt(28, CY0 + 33, "ASKS", "ey", K.tech_tint(K.AGENT))]
    K.assert_within(28 + K.measure("THE MODEL", "ey"), XS[0] - CW / 2 - 8, "model eyebrow")
    body.append(f'<g class="cl"{K.delay(1.15)}>{"".join(calls)}</g>')
    for k in range(5):
        x0 = XS[k] - CW / 2
        for ln in qlines[k]:
            K.fit(ln, "t", TXW, what=f"callout {k + 1}")
        svg, _ = callout(x0, CY0, CW, qlines[k], False, (XS[k], PY + 3),
                         loop0 + t_arr[k] - .03 * CYCLE / 2)
        body.append(f'<g class="cl"{K.delay(1.25 + .15 * k)}>{svg}</g>')

    # ---- not sure -> human reviewer, correction flows back
    dx = XS[4]
    br = [K.conn([(dx, LY + 19), (dx, RY - 33)], K.TRUST, op=.6),
          K.txt(dx + 8, FB + 15, "not sure", "sb", K.tech_tint(K.TRUST)),
          K.person(dx, RY, 1.45),
          K.txt(dx - 17, RY - 13, "Human reviewer", "st", K.name_tint(K.TRUST), "end"),
          K.note(dx - 17, RY + 4, "correction flows back", fill=K.tech_tint(K.TRUST), anchor="end"),
          K.conn([(dx + 14, RY - 9), (RX_RET, RY - 9), (RX_RET, LY + 5)], K.TRUST, op=.6, dash="3 3")]
    K.assert_within(dx + 8 + K.measure("not sure", "sb"), RX_RET - 6, "not-sure label clear of the return path")
    body.append(f'<g class="br"{K.delay(1.9)}>{"".join(br)}</g>')

    # ---- measurement loop (mint)
    GX, GR = 70, 30
    ev = [K.eval_loop([(XS[0], EV - 4), (XS[0], FB + 5)]), K.ring_tap(XS[0], EV, K.EVAL),
          K.feeder(OX, FB + 2, OX, EV - 4, K.EVAL, .75), K.ring_tap(OX, EV, K.EVAL),
          K.feeder(GX, EV + 4, GX, GY - GR - 8, K.EVAL, .75), K.ring_tap(GX, EV, K.EVAL),
          K.txt(XS[0] + 12, EV - 11, "MEASUREMENT LOOP", "ey", K.tech_tint(K.EVAL))]
    gsx = 548
    ev.append(K.feeder(gsx, EV + 4, gsx, GY - 24, K.EVAL, .75) + K.ring_tap(gsx, EV, K.EVAL))
    gl = K.wrap(GOLD, "st", 200)
    for i, ln in enumerate(gl):
        ev.append(K.txt(gsx + 32, GY - 6 + i * 16, ln, "st", K.name_tint(K.EVAL)))
        K.assert_within(gsx + 32 + K.measure(ln, "st"), W - 30, "gold-set sentence")
    body.append(K.conduit(OX, EV, GX, EV, K.EVAL, "cd"))
    body.append(f'<g class="ev"{K.delay(2.8)}>{"".join(ev)}</g>')
    gsvg, gcss = gauge(GX, GY, GR)
    rsvg, rw = readout(GX + GR + 26, GY + 12, 22, 46)
    K.assert_within(GX + GR + 26 + rw, gsx - 30, "readout clear of the gold set")
    body.append(f'<g class="ev"{K.delay(2.9)}>{gold_glyph(gsx, GY + 10, 1)}{gsvg}{rsvg}'
                f'{K.txt(GX + GR + 26, GY + 34, NUM_CTX, "ctx")}</g>')

    # ---- loop motion: the document pulse along the lane; every other pass detours via the reviewer
    lane_pts = [(SX + 34, LY)] + [(x, LY) for x in XS]
    a_pts = lane_pts + [(OX - A - 4, LY)]
    b_pts = lane_pts + [(dx, RY - 14), (dx + 14, RY - 9), (RX_RET, RY - 9), (RX_RET, LY), (OX - A - 4, LY)]
    hues_a, hues_b = [], []
    sa, sb = path_stops(a_pts, 0), path_stops(b_pts, 0, {6: PAUSE})
    for stops, hl in ((sa, hues_a), (sb, hues_b)):
        hl += [(0, GREY), ((stops[3][0] + stops[4][0]) / 2, K.TRUST)]
    hues_a.append(((sa[5][0] + sa[6][0]) / 2, K.RESULT))
    hues_b.append(((sb[-2][0] + sb[-1][0]) / 2, K.RESULT))
    ca, pa = K.pulse("pa", sa, hues_a, CYCLE, loop0, core=2.6, halo=11, fade=(1.2, 2))
    cb, pb = K.pulse("pb", sb, hues_b, CYCLE, loop0 + CYCLE / 2, core=2.6, halo=11, fade=(1.2, 2))
    body.append(pa + pb)
    css = BUILD_CSS + gcss + ca + cb
    return K.svg_doc(W, H, TITLE, DESC, "", css, "".join(body))


# ---------------------------------------------------------------- narrow
def build_narrow():
    W = 400
    RX = 60                                   # rail
    TX, TX1 = 100, 382                        # text / callout column
    A = 22
    S = .8                                    # glyph scale
    CW = TX1 - TX
    TXW = CW - 24
    ROWGAP = 22
    LH_S = 17

    y = 66
    # ---- stack row
    stack_y = y + 30
    rows = []
    y = stack_y + 46
    for k, (verb, hue, q, sub) in enumerate(STEPS):
        ql = K.wrap(q, "t", TXW, True)
        ch = 18 + 17 * (len(ql) - 1) + 10
        top = y
        cy0 = top + 26
        subs = K.wrap(sub, "sb", CW - 4, True) if sub else []
        bottom = cy0 + ch + (8 + LH_S * len(subs) if subs else 0)
        rows.append((top, ql, cy0, ch, subs, bottom))
        y = bottom + ROWGAP
    d_end = rows[-1][5]
    B1 = d_end + 26
    PXR = 252                                 # reviewer x
    RYN = B1 + 54
    B2 = RYN + 30
    OY = B2 + 44                              # output node
    EV = OY + 70
    SY = EV + 34                              # gold-set sentence row
    GY = SY + 72
    H = int(GY + 36 + 26)

    body = [K.card(W, H, KICKER_NARROW, lit=LIT),
            K.glow(RX, stack_y, 110, 60, K.WARM, .16),
            K.glow(TX + CW / 2, (rows[0][2] + rows[2][5]) / 2, 170, 160, K.VIOLET, .20)]
    body.append(K.txt(18, 58, "WHERE THE INTELLIGENCE SITS", "ey"))

    # stack
    st = [K.floor_shadow(RX, stack_y + 8, 30, 12), K.sheet_stack(RX, stack_y + 10, .62, n=11, gap=2),
          K.txt(TX, stack_y - 4, "Documents", "st", K.TEXT), K.txt(TX, stack_y + 14, "long, regulated", "sb")]
    body.append(f'<g class="dp"{K.delay(.1)}>{"".join(st)}</g>')

    node_y = []
    t0 = stack_y + 22
    for k, (verb, hue, q, sub) in enumerate(STEPS):
        top, ql, cy0, ch, subs, bottom = rows[k]
        ny = top + 12
        node_y.append(ny)
        g = [slab_for(RX, ny, A, hue or GREY), step_glyph(k, RX, ny, S),
             K.txt(TX, top + 17, verb, "st", title_fill(hue))]
        for i, ln in enumerate(subs):
            g.append(K.txt(TX, cy0 + ch + 8 + LH_S * (i + 1) - 4, ln, "sb"))
        body.append(f'<g class="sr"{K.delay(.3 + .12 * k)}>{"".join(g)}</g>')
    ON = OY
    out = [slab_for(RX, ON, A, K.RESULT), step_glyph(5, RX, ON, S),
           K.txt(TX, ON - 4, "Cited output", "st", K.RESULT),
           K.txt(TX, ON + 14, "structured, page-cited result", "sb", K.mix(K.RESULT, K.TEXT2, .35))]
    K.fit("structured, page-cited result", "sb", TX1 - TX, True, "narrow output sub")
    body.append(f'<g class="sr"{K.delay(.95)}>{"".join(out)}</g>')

    # rail connectors (vertical, source hue)
    ys = [t0] + node_y + [ON]
    links = []
    for i in range(6):
        y1 = ys[i] + (8 if i == 0 else 14)
        y2 = ys[i + 1] - 15
        hue = K.TRUST if i >= 4 else GREY
        links.append(f'<g class="ln"{K.delay(.9 + .1 * i)}>'
                     f'{K.conn([(RX, y1), (RX, y2)], hue, op=.6 if hue == K.TRUST else .45)}</g>')
    body.append("".join(links))
    body.append(f'<g class="ln"{K.delay(1.5)}>{K.txt(RX - 10, (B1 + B2) / 2 + 4, "yes", "sb", K.tech_tint(K.TRUST), "end")}</g>')

    # callouts
    t_lane = [(RX, t0 + 8)] + [(RX, n) for n in node_y]
    loop0 = 3.6
    for k in range(5):
        top, ql, cy0, ch, subs, bottom = rows[k]
        for ln in ql:
            K.fit(ln, "t", TXW, True, f"narrow callout {k + 1}")
        svg, _ = callout(TX, cy0, CW, ql, True, None, loop0 + arrival(t_lane, k + 1) - .03 * CYCLE / 2)
        body.append(f'<g class="cl"{K.delay(1.2 + .15 * k)}>{svg}</g>')

    # reviewer detour
    br = [K.conn([(RX, B1), (PXR, B1), (PXR, RYN - 33)], K.TRUST, op=.6),
          K.txt(RX + 14, B1 - 7, "not sure", "sb", K.tech_tint(K.TRUST)),
          K.person(PXR, RYN, 1.45),
          K.txt(PXR - 20, RYN - 12, "Human reviewer", "st", K.name_tint(K.TRUST), "end"),
          K.conn([(PXR, RYN + 8), (PXR, B2), (RX + 6, B2)], K.TRUST, op=.6, dash="3 3"),
          K.note(PXR - 12, B2 - 8, "correction flows back", True, K.tech_tint(K.TRUST), "end")]
    K.assert_within(K.measure("Human reviewer", "st", True), PXR - 20 - RX - 14, "narrow reviewer label")
    K.assert_within(K.measure("correction flows back", "an", True), PXR - 12 - RX - 12, "narrow note")
    body.append(f'<g class="br"{K.delay(1.9)}>{"".join(br)}</g>')

    # measurement loop
    LX = 24
    ev = [K.feeder(RX, ON + 16, RX, EV - 4, K.EVAL, .75), K.ring_tap(RX, EV, K.EVAL),
          K.eval_loop([(LX, EV - 4), (LX, node_y[0]), (RX - A - 5, node_y[0])]),
          K.txt(RX + 12, EV - 12, "MEASUREMENT LOOP", "ey", K.tech_tint(K.EVAL))]
    gx = 60
    gl = ["Every change is measured", "against a gold set"]            # balanced break, no orphan
    for ln in gl:
        K.fit(ln, "st", W - 24 - 92, True, "narrow gold-set sentence")
    for i, ln in enumerate(gl):
        ev.append(K.txt(92, SY + i * 17, ln, "st", K.name_tint(K.EVAL)))
    GXN, GR = 60, 28
    ev.append(K.feeder(GXN, EV + 4, GXN, GY - GR - 8, K.EVAL, .75))
    body.append(K.conduit(TX1 - 8, EV, LX, EV, K.EVAL, "cd"))
    body.append(f'<g class="ev"{K.delay(2.8)}>{"".join(ev)}</g>')
    gsvg, gcss = gauge(GXN, GY, GR)
    rx0 = GXN + GR + 22
    rsvg, rw = readout(rx0, GY + 12, 20, 42)
    K.assert_within(rx0 + rw, W - 24, "narrow readout")
    body.append(f'<g class="ev"{K.delay(2.9)}>{gold_glyph(gx, SY + 9, .9)}{gsvg}{rsvg}'
                f'{K.txt(rx0, GY + 34, NUM_CTX, "ctx")}</g>')

    # pulses
    a_pts = t_lane + [(RX, ON - 15)]
    b_pts = t_lane + [(RX, B1), (PXR, B1), (PXR, RYN - 10), (PXR, B2), (RX, B2), (RX, ON - 15)]
    sa, sb = path_stops(a_pts, 0), path_stops(b_pts, 0, {7: PAUSE})
    hues_a = [(0, GREY), ((sa[3][0] + sa[4][0]) / 2, K.TRUST), ((sa[5][0] + sa[6][0]) / 2, K.RESULT)]
    hues_b = [(0, GREY), ((sb[3][0] + sb[4][0]) / 2, K.TRUST), ((sb[-2][0] + sb[-1][0]) / 2, K.RESULT)]
    ca, pa = K.pulse("pa", sa, hues_a, CYCLE, loop0, core=2.6, halo=11, fade=(1.2, 2))
    cb, pb = K.pulse("pb", sb, hues_b, CYCLE, loop0 + CYCLE / 2, core=2.6, halo=11, fade=(1.2, 2))
    body.append(pa + pb)
    css = BUILD_CSS + gcss + ca + cb
    return K.svg_doc(W, H, TITLE, DESC_NARROW, "", css, "".join(body))


if __name__ == "__main__":
    K.write(os.path.join(ASSETS, "docflow.svg"), build_wide())
    K.write(os.path.join(ASSETS, "docflow-narrow.svg"), build_narrow())
    print(K.picture("docflow", ALT))
