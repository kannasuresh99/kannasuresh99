#!/usr/bin/env python3
"""Scene 8, the footer: 'Same discipline'.

Writes assets/footer.svg (850 wide) and assets/footer-narrow.svg (400 wide) from the shared svgkit.
A generic jacketed reactor (gauge, valve, chart recorder) and a small LLM core (eval harness,
validation + gate, audit trail) are bridged by three verbs: measure, control, prove. It mirrors the
hero's core motif. Only one soft pulse and the core particles move. Python 3 stdlib only,
deterministic: never hand-edit the SVGs, change this file and re-run.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgkit as K  # noqa: E402

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

LINE = K.TEXT2                                   # reactor line art
PROVE = K.mix(K.TRUST, K.WHITE, .3)              # 'prove' connectors: azure + 30% white
# verb, connector hue, reactor instrument, core part
ROWS = (("measure", K.EVAL, "gauge", "eval harness"),
        ("control", K.TRUST, "valve", "validation + gate"),
        ("prove", PROVE, "chart recorder", "audit trail"))
LIT = ("AGENT", "TRUST")
KICKER = "THEN → NOW"

TITLE = "Same discipline"
ALT = ("Two systems mirrored across three shared verbs. Left: a chemical reactor with a gauge (measure), a valve "
       "(control) and a chart recorder (prove), captioned Chemical Engineering, 2016–2020. Right: an LLM core with "
       "an eval harness (measure), validation and a human gate (control) and an audit trail (prove), captioned "
       "Production AI, today.")
DESC = ("A reactor with a gauge, a valve and a chart recorder, and an LLM core with an eval harness, a validation "
        "gate and an audit trail, joined by the verbs measure, control and prove.")

CYCLE, LOOP0 = 10, .9            # pulse loop: 10 s, starting just after the 0.6 s fade-in
WINDOWS = ((0, 12), (18, 30), (36, 48))


# ---------------------------------------------------------------- reactor parts (scene-local line art)
def vessel(cx, top, w, body, jacket=True, label_y=None, label_cls="lb"):
    """Generic jacketed reactor in fine line art: motor, agitator shaft and impeller, dished heads, jacket, legs.
    Returns (svg, geometry dict)."""
    hw, hr = w / 2, w * .22                       # half width, head depth
    xl, xr = cx - hw, cx + hw
    y0, y1 = top + hr, top + hr + body            # body shoulders
    st = f'fill="none" stroke="{LINE}" stroke-width="1.25" stroke-linejoin="round" stroke-linecap="round"'
    shell = (f'M{K.fmt(xl)},{K.fmt(y0)}A{K.fmt(hw)},{K.fmt(hr)} 0 0 1 {K.fmt(xr)},{K.fmt(y0)}V{K.fmt(y1)}'
             f'A{K.fmt(hw)},{K.fmt(hr)} 0 0 1 {K.fmt(xl)},{K.fmt(y1)}Z')
    o = [f'<path d="{shell}" fill="{K.mix(K.INK, K.WHITE, .05)}" fill-opacity=".9" stroke="{LINE}" '
         f'stroke-width="1.25"/>']
    g = {"xl": xl, "xr": xr, "y0": y0, "y1": y1, "bot": y1 + hr, "top": top}
    if jacket:
        jy0, jo = y0 + body * .3, 5
        o.append(f'<path d="M{K.fmt(xl)},{K.fmt(jy0)}H{K.fmt(xl - jo)}V{K.fmt(y1)}A{K.fmt(hw + jo)},{K.fmt(hr + jo)} '
                 f'0 0 0 {K.fmt(xr + jo)},{K.fmt(y1)}V{K.fmt(jy0)}H{K.fmt(xr)}" {st} stroke-opacity=".7"/>')
        g.update(jxl=xl - jo, jxr=xr + jo, jy0=jy0, jbot=y1 + hr + jo)
    # legs from the lower body to the floor line given later (drawn by caller via g)
    mw, mh = w * .3, 10
    o.append(f'<rect x="{K.fmt(cx - mw / 2)}" y="{K.fmt(top - mh - 2)}" width="{K.fmt(mw)}" height="{mh}" rx="2" {st}/>')
    yi = y1 - 4
    shaft = [(top - 2, yi)]
    if label_y is not None:                         # break the shaft around the label on the vessel
        shaft = [(top - 2, label_y - 13), (label_y + 5, yi)]
    o.append(f'<path d="{"".join(f"M{K.fmt(cx)},{K.fmt(a)}V{K.fmt(b)}" for a, b in shaft)}'
             f'M{K.fmt(cx - w * .24)},{K.fmt(yi + 3)}L{K.fmt(cx)},{K.fmt(yi)}L{K.fmt(cx + w * .24)},{K.fmt(yi + 3)}" '
             f'{st} stroke-opacity=".8"/>')
    if label_y is not None:
        o.append(K.txt(cx, label_y, "reactor", label_cls, anchor="middle"))
    return "".join(o), g


def legs(cx, w, y_from, y_to, splay=5):
    """Two splayed legs from the lower head down to the floor."""
    hw = w / 2 - 5
    return (f'<path d="M{K.fmt(cx - hw)},{K.fmt(y_from)}L{K.fmt(cx - hw - splay)},{K.fmt(y_to)}'
            f'M{K.fmt(cx + hw)},{K.fmt(y_from)}L{K.fmt(cx + hw + splay)},{K.fmt(y_to)}" fill="none" stroke="{LINE}" '
            f'stroke-width="1.25" stroke-linecap="round"/>')


def pipe(points, op=.85):
    """Neutral process or impulse line."""
    return (f'<path d="M{"L".join(f"{K.fmt(x)},{K.fmt(y)}" for x, y in points)}" fill="none" stroke="{LINE}" '
            f'stroke-opacity="{K.fmt(op, 2)}" stroke-width="1.25" stroke-linejoin="round"/>')


def gauge(x, y, r=8.5):
    """Pressure gauge: neutral dial with ticks and a mint needle (measurement)."""
    ticks = "".join(f"M{K.fmt(x + (r - 2.2) * math.cos(math.radians(a)))},{K.fmt(y + (r - 2.2) * math.sin(math.radians(a)))}"
                    f"L{K.fmt(x + (r - .6) * math.cos(math.radians(a)))},{K.fmt(y + (r - .6) * math.sin(math.radians(a)))}"
                    for a in range(150, 391, 48))
    nx, ny = x + (r - 2.5) * math.cos(math.radians(-50)), y + (r - 2.5) * math.sin(math.radians(-50))
    return (f'<circle cx="{K.fmt(x)}" cy="{K.fmt(y)}" r="{K.fmt(r)}" fill="{K.INK}" stroke="{LINE}" stroke-width="1.25"/>'
            f'<path d="{ticks}" stroke="{LINE}" stroke-opacity=".7"/>'
            f'<path d="M{K.fmt(x)},{K.fmt(y)}L{K.fmt(nx)},{K.fmt(ny)}" stroke="{K.EVAL}" stroke-width="1.6" '
            f'stroke-linecap="round"/><circle cx="{K.fmt(x)}" cy="{K.fmt(y)}" r="1.4" fill="{K.EVAL}"/>')


def valve(x, y, s=1, vertical=False):
    """Control valve: azure bowtie with a lever (control)."""
    a, b = 7 * s, 6 * s
    if vertical:
        body = (f'M{K.fmt(x - b)},{K.fmt(y - a)}H{K.fmt(x + b)}L{K.fmt(x - b)},{K.fmt(y + a)}H{K.fmt(x + b)}Z')
        lever = f'M{K.fmt(x)},{K.fmt(y)}H{K.fmt(x + 10 * s)}M{K.fmt(x + 10 * s)},{K.fmt(y - 5 * s)}V{K.fmt(y + 5 * s)}'
    else:
        body = (f'M{K.fmt(x - a)},{K.fmt(y - b)}V{K.fmt(y + b)}L{K.fmt(x + a)},{K.fmt(y - b)}V{K.fmt(y + b)}Z')
        lever = f'M{K.fmt(x)},{K.fmt(y)}V{K.fmt(y - 10 * s)}M{K.fmt(x - 5 * s)},{K.fmt(y - 10 * s)}H{K.fmt(x + 5 * s)}'
    return (f'<path d="{body}" fill="{K.TRUST}" fill-opacity=".28" stroke="{K.TRUST}" stroke-width="1.3" '
            f'stroke-linejoin="round"/><path d="{lever}" stroke="{K.TRUST}" stroke-width="1.3" stroke-linecap="round"/>')


def recorder(x, y, w=28, h=18):
    """Chart recorder: azure-framed box with a recorded trace (prove), centred on (x, y)."""
    x0, y0 = x - w / 2, y - h / 2
    tr = [(x0 + 4, y + 3), (x0 + 8, y - 1), (x0 + 11, y + 2), (x0 + 15, y - 4), (x0 + 19, y), (x0 + 24, y - 2)]
    return (f'<rect x="{K.fmt(x0)}" y="{K.fmt(y0)}" width="{w}" height="{h}" rx="2" fill="{K.INK}" stroke="{K.TRUST}" '
            f'stroke-opacity=".85" stroke-width="1.25"/>'
            f'<path d="M{K.fmt(x0 + 3)},{K.fmt(y0 + h - 4)}H{K.fmt(x0 + w - 3)}" stroke="{K.TRUST}" stroke-opacity=".3"/>'
            f'<polyline points="{K.pts(tr)}" fill="none" stroke="{K.TRUST}" stroke-width="1.3" stroke-linejoin="round"/>')


def llm_label(cx, cy, size):
    """'LLM' set above the drifting particles with a soft deep-violet halo (same treatment as the hero)."""
    return (f'<text x="{K.fmt(cx)}" y="{K.fmt(cy + size * .36)}" text-anchor="middle" fill="#FFFFFF" '
            f'stroke="#3A2F9A" stroke-opacity=".55" stroke-width="3" stroke-linejoin="round" paint-order="stroke" '
            f'style="font-size:{K.fmt(size)}px;font-weight:700;letter-spacing:.5px">LLM</text>')


def dotted(p1, p2, hue, op=.55):
    """Dotted (1.5 3) bridge connector in the verb's hue (55% wide; stronger on the short narrow bridges)."""
    return (f'<line x1="{K.fmt(p1[0])}" y1="{K.fmt(p1[1])}" x2="{K.fmt(p2[0])}" y2="{K.fmt(p2[1])}" stroke="{hue}" '
            f'stroke-opacity="{K.fmt(op, 2)}" stroke-width="1.5" stroke-dasharray="1.5 3" stroke-linecap="round"/>')


def end_dot(x, y, hue):
    """Small hue dot where a bridge meets its instrument or part."""
    return f'<circle cx="{K.fmt(x)}" cy="{K.fmt(y)}" r="2.3" fill="{hue}"/>'


def pulse(cls, a, b, c, d, hue, t0, t1):
    """One bridge pulse: a -> b (verb's near side), hidden behind the verb, c -> d; white core, hue halo."""
    L1, L2 = math.dist(a, b), math.dist(c, d)
    span = t1 - t0
    tb = t0 + span * .84 * L1 / (L1 + L2)        # 84% of the window travelling, 16% hidden behind the verb
    tc = tb + span * .16
    st = [(0, a, 0), (t0, a, 0), (t0 + 1, None, 1), (tb - .6, None, 1), (tb, b, 0), (tc, c, 0), (tc + .6, None, 1),
          (t1 - 1, None, 1), (t1, d, 0), (100, d, 0)]

    def at(pc):
        if pc <= t0:
            return a
        if pc <= tb:
            f = (pc - t0) / (tb - t0)
            return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        if pc <= tc:
            return c
        if pc <= t1:
            f = (pc - tc) / (t1 - tc)
            return (c[0] + (d[0] - c[0]) * f, c[1] + (d[1] - c[1]) * f)
        return d
    kf = "".join(f"{K.fmt(pc, 2)}%{{opacity:{op};transform:translate({K.fmt(at(pc)[0] - a[0])}px,"
                 f"{K.fmt(at(pc)[1] - a[1])}px)}}" for pc, _, op in st)
    css = (f"@keyframes k{cls}{{{kf}}}.{cls}{{opacity:0;animation:k{cls} {CYCLE}s linear {K.fmt(LOOP0, 2)}s infinite}}")
    svg = (f'<g class="{cls}"><circle cx="{K.fmt(a[0])}" cy="{K.fmt(a[1])}" r="10" fill="url(#k-pg-{K.mix(hue, hue, 0)[1:]})"/>'
           f'<circle cx="{K.fmt(a[0])}" cy="{K.fmt(a[1])}" r="2.4" fill="#FFFFFF"/></g>')
    return css, svg, (tb + tc) / 2


def verb_flash(x, y, text, hue, t_mid, size):
    """The verb brightens as its pulse passes: a soft hue glow and a white overlay, hidden at rest."""
    t = LOOP0 + t_mid / 100 * CYCLE - .03 * CYCLE
    w = K.tw(text, size)
    return (f'<g class="fvf"{K.delay(t)}>' + K.glow(x, y - size * .3, w * .75, size * 1.1, hue, .5) +
            f'<text x="{K.fmt(x)}" y="{K.fmt(y)}" class="fvb" text-anchor="middle" fill="#FFFFFF">{text}</text></g>')


def verb_css(size):
    """Verb style: Georgia italic in ivory, the card's three annotations."""
    return (f".fvb{{font-family:{K.SERIF};font-style:italic;font-size:{K.fmt(size)}px;fill:{K.RESULT}}}"
            + K.css_flash("fvf", CYCLE, 3, 12, .6))


def caption(x, y, name, when, narrow):
    """Two-line caption: name (650) over a muted mono date."""
    n, m = (13, 13) if narrow else (12, 10.5)
    return (f'<text x="{K.fmt(x)}" y="{K.fmt(y)}" text-anchor="middle" style="font-size:{n}px;font-weight:650" '
            f'fill="{K.TEXT}">{K.esc(name)}</text>'
            f'<text x="{K.fmt(x)}" y="{K.fmt(y + (17 if narrow else 16))}" text-anchor="middle" '
            f'style="font-family:{K.MONO};font-size:{m}px;letter-spacing:1px" fill="{K.MUTED}">{K.esc(when)}</text>')


def serif_w(text, size):
    """Conservative width for Georgia italic (the sans AFM estimate runs ~8% wide of it)."""
    return K.tw(text, size)


# ---------------------------------------------------------------- wide
def build_wide():
    """850x260 strip: reactor left, verbs centre, small ringed core right, all on one shared plinth."""
    W, H = 850, 260
    VX, CX, CY, MID = 140, 716, 122, 425
    RY = (86, 122, 158)
    vsz, lsz = 17, 11.5
    body = [K.card(W, H, KICKER, LIT), K.glow(VX + 20, 140, 150, 90, K.WARM, .16),
            K.glow(CX, CY, 130, 95, K.VIOLET, .20)]
    body.append(K.plate(48, 184, W - 96, 10, None, 14, 8))
    body.append(f'<ellipse cx="{CX}" cy="189" rx="34" ry="4.5" fill="#000" fill-opacity=".35"/>')

    # reactor and its three instruments, on the right side at the three row heights
    vs, g = vessel(VX, 64, 56, 72, label_y=118)
    react = [legs(VX, 56, g["bot"] - 8, 188), vs]
    react.append(pipe([(g["xr"], RY[0]), (178.5, RY[0])]) + gauge(187, RY[0]))
    react.append(pipe([(g["jxr"], RY[1]), (210, RY[1])]) + valve(196, RY[1]) +
                 f'<path d="M210,{RY[1] - 4}V{RY[1] + 4}" stroke="{LINE}" stroke-width="1.25"/>')
    react.append(pipe([(g["jxr"], 140), (180, 140), (180, RY[2]), (186, RY[2])], .7) + recorder(200, RY[2]))
    body.append("".join(react))
    left_end = (196, 211, 215)

    # small LLM core in still azure rings, with its three parts on the left at the row heights
    ccss, core = K.llm_core(CX, CY, 20, "fc", n=10, seed=5, rings=[(40, K.TRUST, .7), (58, K.TRUST, .55)],
                            label="", period=(8.5, 13))
    ex = CX - 58 * math.sqrt(1 - (36 / 46.4) ** 2)          # outer ring's x at the measure / prove rows
    parts = [K.conduit(652, RY[0], ex, RY[0], K.EVAL) + K.ring_tap(648, RY[0], K.EVAL),
             K.gate(642, RY[1] + 6, s=.6),
             K.ledger(646, RY[2] + 6, s=.7) + f'<line x1="660" y1="{RY[2]}" x2="{K.fmt(ex)}" y2="{RY[2]}" '
                                                f'stroke="{K.TRUST}" stroke-opacity=".45"/>']
    body.append(core + llm_label(CX, CY, 11) + "".join(parts))
    right_end = (643, 626, 632)

    # the bridge: instrument -> verb -> part, labels riding above each connector
    css, pulses = [verb_css(vsz)], []
    for i, ((verb, hue, inst, part), y) in enumerate(zip(ROWS, RY)):
        vw = serif_w(verb, vsz)
        a, b = (left_end[i] + 8, y), (MID - vw / 2 - 10, y)
        c, d = (MID + vw / 2 + 10, y), (right_end[i] - 8, y)
        lw, rw = K.tw(inst, lsz), K.tw(part, lsz)
        K.assert_within(a[0] + 4 + lw, b[0] - 8, f"label '{inst}' vs verb")
        K.assert_within(c[0] + 8, d[0] - 4 - rw, f"label '{part}' vs verb")
        body.append(dotted(a, b, hue) + dotted(c, d, hue) + end_dot(a[0] - 3, y, hue) + end_dot(d[0] + 3, y, hue))
        body.append(K.txt(a[0] + 4, y - 7, inst, "lb", size=lsz) + K.txt(d[0] - 4, y - 7, part, "lb", anchor="end",
                                                                          size=lsz))
        body.append(f'<text x="{MID}" y="{y + 5.5}" class="fvb" text-anchor="middle">{verb}</text>')
        pc, ps, tmid = pulse(f"fp{i}", a, b, c, d, hue, *WINDOWS[i])
        css.append(pc)
        pulses.append(verb_flash(MID, y + 5.5, verb, hue, tmid, vsz) + ps)

    body.append(caption(VX, 224, "Chemical Engineering", "2016–2020", False))
    body.append(caption(CX, 224, "Production AI", "today", False))
    body.extend(pulses)
    css += [ccss, K.css_fade("fin", .6)]
    return K.svg_doc(W, H, TITLE, DESC, "", "".join(css), f'<g class="fin">{"".join(body)}</g>')


# ---------------------------------------------------------------- narrow
def build_narrow():
    """400-wide re-layout, top to bottom: reactor with instruments in three columns, the verbs row, the core."""
    W, H = 400, 590
    X = (80, 200, 320)
    VX, CX, CY = 200, 200, 452
    vsz, lsz = 16, 13
    body = [K.card(W, H, KICKER, LIT), K.glow(VX, 160, 170, 90, K.WARM, .16), K.glow(CX, CY, 170, 110, K.VIOLET, .20)]
    body.append(caption(VX, 64, "Chemical Engineering", "2016–2020", True))

    # reactor: instruments spread underneath it in the three verb columns
    vs, g = vessel(VX, 108, 52, 62, label_y=148, label_cls="lb")
    yi = 214                                                     # instrument row
    react = [K.plate(VX - 50, 222, 34, 7, None, 8, 5), K.plate(VX + 16, 222, 34, 7, None, 8, 5),
             legs(VX, 52, g["bot"] - 8, 226, 8), vs]
    react.append(pipe([(g["xl"], 132), (X[0], 132), (X[0], yi - 8.5)]) + gauge(X[0], yi))
    react.append(pipe([(VX, g["jbot"]), (VX, yi - 7)]) + valve(VX, yi, vertical=True))
    react.append(pipe([(g["jxr"], 176), (X[2], 176), (X[2], yi - 9)], .7) + recorder(X[2], yi))
    body.append("".join(react))
    body.append(K.plate(CX - 44, 512, 88, 7, None, 8, 5))
    body.append(f'<ellipse cx="{CX}" cy="516" rx="30" ry="4" fill="#000" fill-opacity=".35"/>')

    # core and its three parts: the eval tap and the ledger feed the outer ring, the gate stands on top
    ccss, core = K.llm_core(CX, CY, 22, "fc", n=12, seed=5, rings=[(44, K.TRUST, .7), (64, K.TRUST, .55)],
                            label="", period=(8.5, 13))
    yl = 356                                                     # part labels' baseline
    ring = lambda a: K.ring_point(CX, CY, 64, a)                 # outer ring point (deg)
    (ex, ey), (lx, ly) = ring(215), ring(325)
    parts = [K.conduit(X[0] + 4, yl + 18, X[0] + 20, yl + 18, K.EVAL) + K.ring_tap(X[0], yl + 18, K.EVAL) +
             K.feeder(X[0] + 24, yl + 18, ex, ey, K.EVAL, .7),
             K.gate(CX - 4, CY - 51.2 - 11, s=.62),
             K.ledger(X[2], yl + 30, s=.75) + K.feeder(X[2] - 14, yl + 30, lx, ly, K.TRUST, .7)]
    body.append(core + llm_label(CX, CY, 12) + "".join(parts))

    # labels under the instruments and over the parts; verbs in a row; vertical bridges
    css, pulses = [verb_css(vsz)], []
    yv = 300
    for i, ((verb, hue, inst, part), x) in enumerate(zip(ROWS, X)):
        lw = max(K.measure(inst, "lb", True), K.measure(part, "lb", True))
        K.assert_within(x + lw / 2, W - 18, f"narrow label column {i} right")
        K.assert_within(18, x - lw / 2, f"narrow label column {i} left")
        top_l, bot_l = yi + 30, yl
        body.append(K.txt(x, top_l, inst, "lb", anchor="middle") + K.txt(x, bot_l, part, "lb", anchor="middle"))
        a, b = (x, top_l + 9), (x, yv - 16)
        c, d = (x, yv + 9), (x, bot_l - 15)
        body.append(dotted(a, b, hue, .8) + dotted(c, d, hue, .8))
        body.append(f'<text x="{x}" y="{yv}" class="fvb" text-anchor="middle">{verb}</text>')
        pc, ps, tmid = pulse(f"fp{i}", a, b, c, d, hue, *WINDOWS[i])
        css.append(pc)
        pulses.append(verb_flash(x, yv, verb, hue, tmid, vsz) + ps)
    for x in ((X[0] + X[1]) / 2, (X[1] + X[2]) / 2):
        body.append(f'<circle cx="{K.fmt(x)}" cy="{yv - 5}" r="1.6" fill="{K.MUTED}"/>')

    body.append(caption(CX, 552, "Production AI", "today", True))
    body.extend(pulses)
    css += [ccss, K.css_fade("fin", .6)]
    return K.svg_doc(W, H, TITLE, DESC, "", "".join(css), f'<g class="fin">{"".join(body)}</g>')


if __name__ == "__main__":
    K.write(os.path.join(ASSETS, "footer.svg"), build_wide())
    K.write(os.path.join(ASSETS, "footer-narrow.svg"), build_narrow())
    print(K.picture("footer", ALT))
