#!/usr/bin/env python3
"""Scene 6, 'Where I've shipped': the career staircase that climbs the stack.

Writes assets/journey.svg (850 wide) and assets/journey-narrow.svg (400 wide) from the shared svgkit.
Python 3 stdlib only, deterministic. Never hand-edit the SVGs; change this file and re-run.

Five evenly spaced stops (no date axis). Each stop is a tower of glass layers that grows by one per role:
neutral plates for the earlier roles, capped by a slab in the layer key that role built most, which carries
that layer's micro-scene from the stack. The tops rise toward ValGenesis, and one career line, riding on
poles above the tops, shifts colour SVC -> DATA -> RETR -> AGENT -> TRUST.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgkit as K  # noqa: E402

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

# key, thread phrase, company, role, years, domain, punchline (wide lines), punchline (narrow lines)
STOPS = [
    ("SVC", "backend", "Saama", "Software Engineer", "2021–2023", "clinical SaaS",
     ["API efficiency", "+20%"], ["API efficiency +20%"]),
    ("DATA", "data at scale", "Kissflow", "Software Engineer", "2024", "no-code platform",
     ["60M+ records,", "zero loss"], ["60M+ records,", "zero loss"]),
    ("RETR", "agentic RAG", "PayPal", "Software Engineer 2", "2024–2025", "code intelligence",
     ["migration", "~30% faster"], ["migration ~30% faster"]),
    ("AGENT", "agent platforms", "Enegma", "Founding team", "2025–2026", "agent platform",
     ["weeks →", "~1 day"], ["weeks → ~1 day"]),
    ("TRUST", "regulated AI", "ValGenesis", "Senior SWE, AI/ML", "2026–now", "GxP document AI",
     ["~70% → ~90%"], ["~70% → ~90%"]),
]
LIT = ("SVC", "DATA", "RETR", "AGENT", "TRUST")
KICKER = "CAREER · 2021 TO NOW"

TITLE = "Where I've shipped"
ALT = ("Career staircase from 2021 to now: five evenly spaced steps, oldest to newest, each a tower of glass "
       "layers that grows by one layer per role, capped in the colour of the layer that role built most and "
       "carrying a small scene of what that role built. One line joins the steps and shifts colour from rose "
       "to tangerine, orchid, violet and azure, with a phrase at each stop: backend, data at scale, agentic RAG, "
       "agent platforms, regulated AI. Saama, Software Engineer, "
       "2021–2023, clinical SaaS, API efficiency +20%. Kissflow, Software Engineer, 2024, no-code platform, 60M+ "
       "records, zero loss, flagged where LLMs enter. PayPal, Software Engineer 2, 2024–2025, code intelligence, "
       "migration ~30% faster. Enegma, Founding team, 2025–2026, agent platform, weeks to ~1 day. ValGenesis, "
       "Senior SWE, AI/ML, 2026 to now, GxP document AI, ~70% to ~90%, ringed as now.")
DESC = ("Career staircase: Saama, Kissflow, PayPal, Enegma and ValGenesis as five towers of glass layers rising "
        "left to right, each role adding a layer capped in the services, data, retrieval, agents or trust colour, "
        "joined by one line, each with role, years, domain and one result.")
DESC_NARROW = ("Career timeline, oldest at the top: Saama, Kissflow, PayPal, Enegma and ValGenesis on one line, each "
               "a column of glass layers that grows by one per role, capped in the services, data, retrieval, "
               "agents or trust colour, with role, years, domain and one result.")

LINE_D0, LINE_DUR = .5, 2.9    # career line draw (ease-in-out); cards fade in as it reaches each stop
CARD_FADE = .4
NOW_START, NOW_CYCLE = 4.0, 4  # after the build only the 'now' ring breathes
SLAB_D0, SLAB_STEP = .1, .33


def ease_in_out_time(p):
    """Time fraction at which CSS ease-in-out (cubic-bezier(.42,0,.58,1)) reaches progress p (bisection)."""
    bx = lambda t: 3 * (1 - t) ** 2 * t * .42 + 3 * (1 - t) * t * t * .58 + t ** 3
    by = lambda t: 3 * (1 - t) * t * t + t ** 3
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if by(mid) < p else (lo, mid)
    return bx((lo + hi) / 2)


STOP_T = [LINE_D0 + LINE_DUR * ease_in_out_time(i / 4) for i in range(5)]
assert STOP_T[-1] + CARD_FADE < NOW_START, "build must finish before the 'now' loop starts"


def motion_css():
    """Builds once (towers drop, line draws, stops fade in as it arrives), then only the 'now' ring breathes."""
    return "".join([
        K.css_drop("s"),
        K.css_fade("cd", CARD_FADE),
        f"@keyframes kln{{from{{stroke-dashoffset:1;opacity:0}}3%{{opacity:1}}to{{stroke-dashoffset:0;opacity:1}}}}"
        f".ln{{stroke-dasharray:1;animation:kln {K.fmt(LINE_DUR, 2)}s ease-in-out {K.fmt(LINE_D0, 2)}s both}}",
        f"@keyframes knw{{0%,100%{{opacity:1}}50%{{opacity:.45}}}}"
        f".nw{{animation:knw {NOW_CYCLE}s ease-in-out {K.fmt(NOW_START, 2)}s infinite}}",
    ])


def gradient(gid, p0, p1):
    """userSpace linear gradient along the career line, one stop per role at that stop's position."""
    stops = "".join(f'<stop offset="{K.fmt(i / 4, 2)}" stop-color="{K.HUE[s[0]]}"/>' for i, s in enumerate(STOPS))
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{K.fmt(p0[0])}" y1="{K.fmt(p0[1])}" '
            f'x2="{K.fmt(p1[0])}" y2="{K.fmt(p1[1])}">{stops}</linearGradient>')


def career_line(nodes, gid, width):
    """The one career polyline (pathLength=1 for the draw)."""
    d = "M" + "L".join(f"{K.fmt(x)},{K.fmt(y)}" for x, y in nodes)
    return (f'<path class="ln" pathLength="1" d="{d}" fill="none" stroke="url(#{gid})" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def node(x, y, hue):
    """Stop node: r 5, ink fill, 2px stroke in the hue."""
    return f'<circle cx="{K.fmt(x)}" cy="{K.fmt(y)}" r="5" fill="{K.INK}" stroke="{hue}" stroke-width="2"/>'


def pole(x, y_top, y_bot, hue, dotted=False):
    """Pole planting a node on its step's back corner (Kissflow's is the dotted flag pole)."""
    dash = ' stroke-dasharray="1.5 2.5"' if dotted else ""
    return (f'<line x1="{K.fmt(x)}" y1="{K.fmt(y_top)}" x2="{K.fmt(x)}" y2="{K.fmt(y_bot)}" stroke="{K.link_tint(hue)}" '
            f'stroke-opacity="{".85" if dotted else ".5"}"{dash}/>')


def pennant(x, y):
    """Small matte violet pennant flying right from a pole at (x, y = top of the pennant): where LLMs enter."""
    return (f'<path d="M{K.fmt(x + .5)},{K.fmt(y)}L{K.fmt(x + 12)},{K.fmt(y + 4.5)}L{K.fmt(x + .5)},{K.fmt(y + 9)}Z" '
            f'fill="{K.AGENT}" fill-opacity=".9"/>')


def now_ring(x, y):
    """The white 'now' ring (not azure, so azure stays still); it breathes after the build."""
    return f'<circle class="nw" cx="{K.fmt(x)}" cy="{K.fmt(y)}" r="9" fill="none" stroke="#FFFFFF" stroke-width="1.5"/>'


def punch(x, y, lines, size, hue, lh):
    """Punchline: ivory sans 700 lines with a 2px hue underline under the last (result) line; returns svg."""
    o = []
    for j, s in enumerate(lines):
        o.append(f'<text x="{K.fmt(x)}" y="{K.fmt(y + j * lh)}" class="num" style="font-size:{K.fmt(size)}px">'
                 f'{K.esc(s)}</text>')
    yl = y + (len(lines) - 1) * lh
    o.append(f'<rect x="{K.fmt(x)}" y="{K.fmt(yl + 6)}" width="{K.fmt(K.tw(lines[-1], size, True))}" height="2" '
             f'rx="1" fill="{hue}"/>')
    return "".join(o)


def card_box(x, y, w, h, hue, rx):
    """Role card panel: faint lift, hairline border in the stop's hue."""
    return (f'<rect x="{K.fmt(x)}" y="{K.fmt(y)}" width="{K.fmt(w)}" height="{K.fmt(h)}" rx="{rx}" fill="#FFFFFF" '
            f'fill-opacity=".03" stroke="{hue}" stroke-opacity=".34"/>')


def card_text(stop, x, y, maxw, h, narrow):
    """Company, role, years, domain and a bottom-anchored punchline (underlines align across cards); measured.

    Wide stacks company / role / years / domain. Narrow puts the years top-right on the company line."""
    key, _, company, role, years, domain, pw, pn = stop
    hue = K.HUE[key]
    sz = dict(co=17, ro=13, yr=13, do=13, pu=20, plh=23) if narrow else \
        dict(co=15, ro=11.5, yr=10.5, do=11.5, pu=17, plh=20)
    lines = pn if narrow else pw
    wco = K.tw(company, sz["co"], True)
    wyr = K.tw_mono(years, sz["yr"])
    K.assert_within(wco + (wyr + 12 if narrow else 0), maxw, f"{company} company")
    K.assert_within(K.tw(role, sz["ro"]), maxw, f"{company} role")
    K.assert_within(wyr, maxw, f"{company} years")
    K.assert_within(K.tw(domain, sz["do"]), maxw, f"{company} domain")
    for s in lines:
        K.assert_within(K.tw(s, sz["pu"], True), maxw, f"{company} punchline")
    y_last = y + h - (18 if narrow else 17)
    y_first = y_last - (len(lines) - 1) * sz["plh"]
    if narrow:
        o = (K.txt(x, y + 25, company, "st", K.TEXT, size=sz["co"]) +
             K.txt(x + maxw, y + 25, years, "ix", K.MUTED, anchor="end", size=sz["yr"]) +
             K.txt(x, y + 45, role, "lb", K.TEXT2) +
             K.txt(x, y + 64, domain, "t", K.tech_tint(hue)))
        K.assert_within(y + 64 + 26, y_first, f"{company} punchline clears the domain")
    else:
        o = (K.txt(x, y + 22, company, "st", K.TEXT, size=sz["co"]) +
             K.txt(x, y + 38, role, "lb", K.TEXT2, size=sz["ro"]) +
             K.txt(x, y + 53, years, "ix", K.MUTED) +
             K.txt(x, y + 69, domain, "t", K.tech_tint(hue)))
        K.assert_within(y + 69 + 23, y_first, f"{company} punchline clears the domain")
    return o + punch(x, y_first, lines, sz["pu"], hue, sz["plh"])


# ---------------------------------------------------------------- shared step glyph
def ghost_slab(iso, t):
    """Neutral ink glass plate (an earlier role's layer) under a step, so each role visibly adds a layer."""
    cx, cy, a, b = iso.cx, iso.cy, iso.a, iso.b
    tt = t * iso.s
    left = [(cx - a, cy), (cx, cy + b), (cx, cy + b + tt), (cx - a, cy + tt)]
    right = [(cx, cy + b), (cx + a, cy), (cx + a, cy + tt), (cx, cy + b + tt)]
    top = [(cx, cy - b), (cx + a, cy), (cx, cy + b), (cx - a, cy)]
    return (f'<polygon points="{K.pts(top)}" fill="{K.mix(K.INK, K.WHITE, .09)}" fill-opacity=".9" stroke="#FFFFFF" '
            f'stroke-opacity=".2"/>'
            f'<polygon points="{K.pts(left)}" fill="{K.mix(K.INK, K.WHITE, .07)}" fill-opacity=".95"/>'
            f'<polygon points="{K.pts(right)}" fill="{K.mix(K.INK, K.WHITE, .035)}" fill-opacity=".95"/>'
            f'<polyline points="{K.pts(left[:3])}" fill="none" stroke="#FFFFFF" stroke-opacity=".14"/>')


def tower(x, cy, a, b, t, key, below, pitch, pole_top, backing=False):
    """One career step: `below` neutral plates (earlier roles) under the role's slab in its layer key, the layer's
    micro-scene from the stack on top, and the pole that plants the career-line node on the back corner.
    backing=True lays an opaque ground-coloured silhouette first, so a line passing behind stays hidden."""
    hue = K.HUE[key]
    iso = K.Iso(x, cy, a, b)
    tt = t * a / 100
    base = cy + below * pitch + b + tt
    o = [K.floor_shadow(x, base + 2, a, b * .3)]
    if backing:
        yb = cy + below * pitch + tt
        sil = [(x, cy - b), (x + a, cy), (x + a, yb), (x, base), (x - a, yb), (x - a, cy)]
        o.append(f'<polygon points="{K.pts(sil)}" fill="{K.mix(K.INK, K.INK2, .5)}"/>')
    o += [ghost_slab(K.Iso(x, cy + k * pitch, a, b), t) for k in range(below, 0, -1)]
    o.append(K.slab(iso, t, hue) + K.layer_scene(key, iso) + pole(x, pole_top, cy - b, hue, dotted=(key == "DATA")))
    return "".join(o), base


# ---------------------------------------------------------------- wide
def build_wide():
    """850-wide iso staircase: five towers on one base, each role adding a layer; the career line rides on poles
    above the tops and the role cards sit on a fixed row beneath."""
    W, A, B, T = 850, 62, 31, 18            # slab half-diagonals; T in kit units (x .62 = 11px thick)
    XS = [105, 265, 425, 585, 745]
    RISE, POLE, PHRASE = 24, 26, 18
    CY0 = 236
    CYS = [CY0 - RISE * i for i in range(5)]
    BASE = CY0 + B + T * A / 100
    CARD_Y, CARD_W, CARD_H, PAD = BASE + 18, 152, 130, 11
    H = round(CARD_Y + CARD_H + 16)
    nodes = [(x, cy - B - POLE) for x, cy in zip(XS, CYS)]
    K.assert_within(64, nodes[-1][1] - PHRASE, "top phrase clears the masthead")

    body = [K.card(W, H, KICKER, lit=LIT),
            K.glow(XS[0], BASE - 10, 230, 120, K.WARM, .16)]
    slabs, stops = [], []
    for i, (stop, x, cy) in enumerate(zip(STOPS, XS, CYS)):
        key, phrase = stop[0], stop[1]
        hue = K.HUE[key]
        nx, ny = nodes[i]
        svg, base = tower(x, cy, A, B, T, key, i, RISE, ny + 5)
        K.assert_within(abs(base - BASE), .01, "every tower stands on the shared base")
        slabs.append(f'<g class="s"{K.delay(SLAB_D0 + SLAB_STEP * i)}>{svg}</g>')
        # stop: node, thread phrase, leader and card, revealed when the line reaches it
        K.assert_within(K.tw(phrase, 12, True) / 2 + x, W - 28, f"{phrase} phrase")
        cx0 = x - CARD_W / 2
        g = [K.leader(x, BASE + 3, x, CARD_Y, hue),
             card_box(cx0, CARD_Y, CARD_W, CARD_H, hue, 10),
             card_text(stop, cx0 + PAD, CARD_Y, CARD_W - 2 * PAD, CARD_H, False),
             node(nx, ny, hue),
             K.txt(nx, ny - PHRASE, phrase, "st", K.tech_tint(hue), anchor="middle")]
        if key == "DATA":
            g.append(pennant(nx, ny + 6) + K.note(nx + 17, ny + 15, "LLMs enter"))
        if key == "TRUST":
            g.append(now_ring(nx, ny) + K.note(nx + 15, ny + 4.5, "now"))
            K.assert_within(nx + 15 + K.measure("now", "an"), W - 28, "now note")
        stops.append(f'<g class="cd"{K.delay(STOP_T[i])}>{"".join(g)}</g>')
    body += slabs
    body.append(career_line(nodes, "jl", 2.5))
    body += stops
    defs = gradient("jl", nodes[0], nodes[-1])
    return K.svg_doc(W, H, TITLE, DESC, defs, motion_css(), "".join(body))


# ---------------------------------------------------------------- narrow
def build_narrow():
    """400-wide re-layout: the line runs top (Saama) to bottom (ValGenesis); each step glyph sits 8px further
    right on a column of neutral plates, one per earlier role, so the steps visibly grow toward now."""
    W, A, B, T = 400, 36, 18, 25            # glyph slab (T x .36 = 9px thick)
    X0, XSTEP, POLE, PLATE = 42, 8, 13, 14  # PLATE: pitch of the neutral plates under each step
    CARD_X, CARD_R, PAD = 118, 382, 13
    CARD_H, PITCH, Y0 = 131, 171, 76        # card holds a two-line punchline; Y0 = first phrase row
    H = Y0 + 4 * PITCH + 9 + CARD_H + 18
    nodes = [(X0 + XSTEP * i, Y0 + i * PITCH - 4.5) for i in range(5)]

    body = [K.card(W, H, KICKER, lit=LIT),
            K.glow(X0 + 20, Y0 + 60, 170, 150, K.WARM, .16)]
    slabs, stops = [], []
    for i, stop in enumerate(STOPS):
        key, phrase = stop[0], stop[1]
        hue = K.HUE[key]
        nx, ny = nodes[i]
        yp = Y0 + i * PITCH
        yc = yp + 9
        cy = ny + POLE + B
        K.assert_within(nx + A + 8, CARD_X, "glyph clears the card")
        svg, bottom = tower(nx, cy, A, B, T, key, i, PLATE, ny + 5, backing=True)
        K.assert_within(bottom + 10, Y0 + (i + 1) * PITCH - 4.5 - 6, "tower clears the next node")
        slabs.append(f'<g class="s"{K.delay(SLAB_D0 + SLAB_STEP * i)}>{svg}</g>')
        g = [card_box(CARD_X, yc, CARD_R - CARD_X, CARD_H, hue, 12),
             card_text(stop, CARD_X + PAD, yc, CARD_R - CARD_X - 2 * PAD, CARD_H, True),
             K.txt(CARD_X + 2, yp, phrase, "st", K.tech_tint(hue)),
             node(nx, ny, hue)]
        wph = K.measure(phrase, "st", True)
        K.assert_within(CARD_X + 2 + wph, CARD_R, f"{phrase} narrow phrase")
        if key == "DATA":
            g.append(pennant(nx, ny + 6) + K.note(CARD_R - 2, yp, "LLMs enter", narrow=True, anchor="end"))
            K.assert_within(CARD_X + 2 + wph + 16, CARD_R - 2 - K.measure("LLMs enter", "an", True),
                            "phrase vs LLMs enter")
        if key == "TRUST":
            g.append(now_ring(nx, ny) + K.note(nx - 14, ny + 4.5, "now", narrow=True, anchor="end"))
            K.assert_within(28, nx - 14 - K.measure("now", "an", True), "now note inside the card")
        stops.append(f'<g class="cd"{K.delay(STOP_T[i])}>{"".join(g)}</g>')
    body.append(career_line(nodes, "jl", 2.5))
    body += slabs + stops
    defs = gradient("jl", nodes[0], nodes[-1])
    return K.svg_doc(W, H, TITLE, DESC_NARROW, defs, motion_css(), "".join(body))


if __name__ == "__main__":
    K.write(os.path.join(ASSETS, "journey.svg"), build_wide())
    K.write(os.path.join(ASSETS, "journey-narrow.svg"), build_narrow())
    print(K.picture("journey", ALT))
