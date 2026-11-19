#!/usr/bin/env python3
"""Scene 1, the hero: 'Probabilistic core, deterministic shell'.

Writes assets/hero.svg (850 wide) and assets/hero-narrow.svg (400 wide) from the shared svgkit.
Raw input wavers into a restless violet LLM core; four still, tick-marked rings (grounded retrieval,
validation rules, human-in-the-loop, audit trail) wrap it; one line leaves, calming at each ring,
tagged cited / validated / audit-ready and ending in a check. Four results sit underneath.
Only the core particles, the core glow and one request pulse move. Python 3 stdlib only,
deterministic: never hand-edit the SVGs, change this file and re-run.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgkit as K  # noqa: E402

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

NAME, ROLE, CITY = "KANNAPPAN SURESH", "Backend & AI Engineer", "Chennai, India"
INPUTS = ("documents", "code", "requests")
RINGS = (("grounded retrieval", K.RETR), ("validation rules", K.TRUST),
         ("human-in-the-loop", K.TRUST), ("audit trail", K.TRUST))
RING_OP = (.7, .7, .6, .5)
TAGS = ("cited", "validated", "audit-ready")
# (numeral parts, underline hue, context line, sub line); 'a' = drawn arrow, ('u', s) = small unit
RESULTS = (
    ([("n", "~70%"), ("a",), ("n", "~90%")], K.RETR, "extraction accuracy", "gold-set harness"),
    ([("n", "weeks"), ("a",), ("n", "~1 day")], K.AGENT, "per new agent", None),
    ([("n", "~30%"), ("u", " faster"), None], K.SVC, "Venmo migration", None),
    ([("n", "60M+"), ("u", " records"), None], K.DATA, "zero data loss", None),
)
LIT = ("DATA", "SVC", "RETR", "AGENT", "TRUST")
IVORY, PROB_INK, DET_INK = K.RESULT, "#C3BCFF", "#A9D4FF"

TITLE = "Kannappan Suresh, Backend & AI Engineer"
ALT = ("Kannappan Suresh, Backend & AI Engineer, Chennai, India. Diagram: raw input (documents, code, requests) "
       "flows into a glowing LLM core whose particles drift at random, labeled probabilistic. The core sits inside "
       "four still, concentric rings labeled grounded retrieval, validation rules, human-in-the-loop and audit "
       "trail, together labeled deterministic. One clean, straight line leaves the rings, tagged cited, validated "
       "and audit-ready, and ends in a check. Below, four results: large-document extraction accuracy from ~70% to "
       "~90% (gold-set harness); a new agent in ~1 day instead of weeks; Venmo's migration ~30% faster; 60M+ "
       "records migrated with zero data loss.")
DESC = ("Raw input wavers into a glowing, probabilistic LLM core held inside four still deterministic rings: "
        "grounded retrieval, validation rules, human-in-the-loop, audit trail. One straight line leaves, tagged "
        "cited, validated, audit-ready. Results: extraction accuracy ~70% to ~90%; weeks to ~1 day per new agent; "
        "Venmo migration ~30% faster; 60M+ records, zero data loss.")

CYCLE, LOOP0 = 6, 2.4           # request pulse: one pass every 6 s, starting after the build


# ---------------------------------------------------------------- helpers (scene-local)
def jitter_d(points, amps, seed, step=6.0):
    """Smooth, hand-jittered path through a polyline; amps[i] is segment i's amplitude, pinned at every vertex."""
    rnd = random.Random(seed)
    ps = [points[0]]
    for (x1, y1), (x2, y2), a in zip(points, points[1:], amps):
        L = math.hypot(x2 - x1, y2 - y1)
        n = max(2, round(L / step))
        nx, ny = -(y2 - y1) / L, (x2 - x1) / L
        f, ph = rnd.uniform(1.6, 2.6), rnd.uniform(0, 2 * math.pi)
        prev = 0.0
        for k in range(1, n + 1):
            t = k / n
            noise = .55 * prev + .45 * rnd.uniform(-1, 1)        # smoothed random walk
            prev = noise
            off = a * math.sin(math.pi * t) * (.6 * math.sin(2 * math.pi * f * t + ph) + .7 * noise)
            ps.append((x1 + (x2 - x1) * t + nx * off, y1 + (y2 - y1) * t + ny * off))
    d = [f"M{K.fmt(ps[0][0])},{K.fmt(ps[0][1])}"]
    for i in range(len(ps) - 1):                                   # Catmull-Rom to cubic Bezier
        p0, p1, p2 = ps[max(0, i - 1)], ps[i], ps[i + 1]
        p3 = ps[min(len(ps) - 1, i + 2)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{K.fmt(c1[0])},{K.fmt(c1[1])} {K.fmt(c2[0])},{K.fmt(c2[1])} {K.fmt(p2[0])},{K.fmt(p2[1])}")
    return "".join(d)


def arc_d(cx, cy, rx, ry, a0, a1):
    """Clockwise elliptical arc path from angle a0 to a1 (deg, y down), for ring-label textPaths."""
    p = lambda a: (cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))
    (x0, y0), (x1, y1) = p(a0), p(a1)
    big = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{K.fmt(x0)},{K.fmt(y0)}A{K.fmt(rx)},{K.fmt(ry)} 0 {big} 1 {K.fmt(x1)},{K.fmt(y1)}"


def ring_labels(cx, cy, rxs, size, narrow):
    """Curved ring names riding each ring's upper arc 3px outside it (textPath defs, text)."""
    defs, out = [], []
    for i, ((label, hue), rx) in enumerate(zip(RINGS, rxs)):
        R, Ry = rx + 3, rx * .8 + 3
        arc_len = math.pi * math.sqrt((R * R + Ry * Ry) / 2) * (156 / 180)
        K.assert_within(K.tw(label, size, True, .6), arc_len * .8, f"ring label '{label}' on its arc")
        defs.append(f'<path id="hr{i}" d="{arc_d(cx, cy, R, Ry, 192, 348)}"/>')
        out.append(f'<text class="hrl" fill="{K.tech_tint(hue)}"><textPath href="#hr{i}" startOffset="50%" '
                   f'text-anchor="middle">{K.esc(label)}</textPath></text>')
    css = f".hrl{{font-size:{K.fmt(size)}px;font-weight:600;letter-spacing:.6px}}"
    return "".join(defs), "".join(out), css


def glyph(kind, x, y, s=1.0):
    """Raw-input glyphs in ivory: a small document stack, a drawn '< >' bracket pair, a speech bubble."""
    st = f'fill="none" stroke="{IVORY}" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "documents":
        return K.sheet_stack(x, y + 4 * s, s=.44 * s, n=3, gap=2.2 * s)
    if kind == "code":
        w, h, g = 8 * s, 7 * s, 5 * s
        return (f'<path d="M{K.fmt(x - g)},{K.fmt(y - h)}l-{K.fmt(w)},{K.fmt(h)} {K.fmt(w)},{K.fmt(h)}'
                f'M{K.fmt(x + g)},{K.fmt(y - h)}l{K.fmt(w)},{K.fmt(h)} -{K.fmt(w)},{K.fmt(h)}" {st} '
                f'stroke-opacity=".9" stroke-width="{K.fmt(2 * min(1.15, s))}"/>')
    # requests: rounded speech bubble with a tail and two text strokes
    bw, bh = 28 * s, 17 * s
    x0, y0 = x - bw / 2, y - bh / 2 - 2 * s
    return (f'<path d="M{K.fmt(x0 + 5 * s)},{K.fmt(y0)}h{K.fmt(bw - 10 * s)}a{K.fmt(5 * s)},{K.fmt(5 * s)} 0 0 1 '
            f'{K.fmt(5 * s)},{K.fmt(5 * s)}v{K.fmt(bh - 10 * s)}a{K.fmt(5 * s)},{K.fmt(5 * s)} 0 0 1 -{K.fmt(5 * s)},'
            f'{K.fmt(5 * s)}h-{K.fmt(bw - 18 * s)}l-{K.fmt(6 * s)},{K.fmt(5 * s)}v-{K.fmt(5 * s)}h-{K.fmt(2 * s)}'
            f'a{K.fmt(5 * s)},{K.fmt(5 * s)} 0 0 1 -{K.fmt(5 * s)},-{K.fmt(5 * s)}v-{K.fmt(bh - 10 * s)}'
            f'a{K.fmt(5 * s)},{K.fmt(5 * s)} 0 0 1 {K.fmt(5 * s)},-{K.fmt(5 * s)}z" {st} stroke-opacity=".9" stroke-width="1.5"/>'
            f'<path d="M{K.fmt(x0 + 7 * s)},{K.fmt(y0 + 6 * s)}h{K.fmt(14 * s)}M{K.fmt(x0 + 7 * s)},{K.fmt(y0 + 11 * s)}'
            f'h{K.fmt(9 * s)}" {st} stroke-opacity=".5" stroke-width="1.3"/>')


def arrow(x, y, length, hue=IVORY, op=.75):
    """Thin drawn arrow (shaft plus open chevron) for numerals; (x, y) is the shaft's left end."""
    return (f'<line x1="{K.fmt(x)}" y1="{K.fmt(y)}" x2="{K.fmt(x + length - 1)}" y2="{K.fmt(y)}" stroke="{hue}" '
            f'stroke-opacity="{K.fmt(op, 2)}" stroke-width="1.6" stroke-linecap="round"/>' +
            K.chevron(x + length, y, 0, hue, op, 5, 1.6))


def numeral(parts, size, unit_size, gap, alen):
    """A result numeral as left text, joint (drawn arrow or unit gap), right text; widths are the kit's
    conservative AFM estimates. Returns a dict with the group width G."""
    (_, left), joint, right = parts[0], parts[1], parts[2]
    rs = unit_size if joint[0] == "u" else size
    rtext = (joint[1] if joint[0] == "u" else right[1]).strip()
    J = unit_size * .3 if joint[0] == "u" else alen + 2 * gap
    wl, wr = K.tw(left, size, True), K.tw(rtext, rs, True)
    return {"L": left, "R": rtext, "rs": rs, "size": size, "arrow": joint[0] == "a", "J": J, "gap": gap,
            "alen": alen, "wl": wl, "wr": wr, "G": wl + J + wr}


def draw_numeral(nd, cx, y, hue):
    """Draw a numeral centred on cx: the left text ends on the joint and the right text starts after it, so the
    arrow or unit gap stays exact on any font; a 2px hue underline spans the group."""
    j0 = cx - nd["G"] / 2 + nd["wl"]
    o = [f'<text x="{K.fmt(j0)}" y="{K.fmt(y)}" class="num" text-anchor="end" style="font-size:{K.fmt(nd["size"])}px">'
         f'{K.esc(nd["L"])}</text>']
    rst = f'font-size:{K.fmt(nd["rs"])}px' + ("" if nd["arrow"] else ";font-weight:600")
    o.append(f'<text x="{K.fmt(j0 + nd["J"])}" y="{K.fmt(y)}" class="num" style="{rst}">{K.esc(nd["R"])}</text>')
    if nd["arrow"]:
        o.append(arrow(j0 + nd["gap"], y - nd["size"] * .36, nd["alen"]))
    o.append(f'<rect x="{K.fmt(cx - nd["G"] / 2)}" y="{K.fmt(y + 6)}" width="{K.fmt(nd["G"])}" height="2" rx="1" '
             f'fill="{hue}"/>')
    return "".join(o)


def pulse_path(cls, stops, hues, cycle, delay, core=2.8, halo=12):
    """Request pulse through [(pct, x, y, opacity)] (linear), halo hue switching at [(pct, hue)]; hidden at rest."""
    x0, y0 = stops[0][1], stops[0][2]
    kf = "".join(f"{K.fmt(pc, 2)}%{{opacity:{K.fmt(op, 2)};transform:translate({K.fmt(x - x0)}px,{K.fmt(y - y0)}px)}}"
                 for pc, x, y, op in stops)
    css = [f"@keyframes k{cls}{{{kf}}}",
           f".{cls}{{opacity:0;animation:k{cls} {K.fmt(cycle, 2)}s linear {K.fmt(delay, 2)}s infinite}}"]
    svg = [f'<g class="{cls}">']
    for i, (pc, hue) in enumerate(hues):
        nxt = hues[i + 1][0] if i + 1 < len(hues) else 100
        d = {0: 1 if pc <= 0 else 0, 100: 1 if nxt >= 100 else 0}
        if pc > 0:
            d[pc - .6], d[pc + .6] = 0, 1
        if nxt < 100:
            d[nxt - .6], d[nxt + .6] = 1, 0
        css.append(f"@keyframes k{cls}h{i}{{" + "".join(f"{K.fmt(k, 2)}%{{opacity:{v}}}" for k, v in sorted(d.items()))
                   + f"}}.{cls}h{i}{{animation:k{cls}h{i} {K.fmt(cycle, 2)}s linear {K.fmt(delay, 2)}s infinite}}")
        svg.append(f'<circle class="{cls}h{i}" cx="{K.fmt(x0)}" cy="{K.fmt(y0)}" r="{halo}" '
                   f'fill="url(#k-pg-{K.mix(hue, hue, 0)[1:]})"/>')
    svg.append(f'<circle cx="{K.fmt(x0)}" cy="{K.fmt(y0)}" r="{core}" fill="#FFFFFF"/></g>')
    return "".join(css), "".join(svg)


def timeline(path_pts, t0, t1):
    """Spread pct between t0 and t1 along a polyline in proportion to distance; returns [(pct, x, y)]."""
    segs = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path_pts, path_pts[1:])]
    tot, acc, out = sum(segs), 0.0, [(t0, *path_pts[0])]
    for s, p in zip(segs, path_pts[1:]):
        acc += s
        out.append((t0 + (t1 - t0) * acc / tot, *p))
    return out


def node_flashes(points, pcts, hue):
    """White flash over each ring node as the pulse crosses it (up in 3%, gone by 14% of the cycle)."""
    o = []
    for (x, y), pc in zip(points, pcts):
        t = LOOP0 + pc / 100 * CYCLE - .03 * CYCLE
        o.append(f'<g class="hfl"{K.delay(t)}><circle cx="{K.fmt(x)}" cy="{K.fmt(y)}" r="9" fill="{hue}" '
                 f'fill-opacity=".55" filter="url(#k-glow)"/><circle cx="{K.fmt(x)}" cy="{K.fmt(y)}" r="4.2" '
                 f'fill="#FFFFFF"/></g>')
    return "".join(o)


def pill_on_line(x, cy, text, narrow, ground):
    """Trust pill threaded on the output line: an opaque ground-coloured underlay hides the line behind it."""
    w = K.pill_width(text, narrow)
    h = 22 if narrow else 20
    under = (f'<rect x="{K.fmt(x)}" y="{K.fmt(cy - h / 2)}" width="{K.fmt(w)}" height="{h}" rx="{K.fmt(h / 2)}" '
             f'fill="{ground}"/>')
    return under + K.pill(x, cy, text, K.TRUST, narrow)[0], w


def check(x, y, size):
    """Azure check tile (rx 3, white check) with its top-left at (x, y)."""
    s = size / 16
    return (f'<rect x="{K.fmt(x)}" y="{K.fmt(y)}" width="{K.fmt(size)}" height="{K.fmt(size)}" rx="3" fill="{K.TRUST}"/>'
            f'<path d="M{K.fmt(x + 4 * s)},{K.fmt(y + 8.4 * s)}l{K.fmt(2.8 * s)},{K.fmt(2.8 * s)} '
            f'{K.fmt(5.4 * s)},-{K.fmt(5.8 * s)}" fill="none" stroke="#FFFFFF" stroke-width="{K.fmt(1.9 * s)}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def llm_label(cx, cy, size):
    """'LLM' set above the drifting particles with a soft deep-violet halo so it stays crisp on the glass."""
    return (f'<text x="{K.fmt(cx)}" y="{K.fmt(cy + size * .36)}" text-anchor="middle" fill="#FFFFFF" '
            f'stroke="#3A2F9A" stroke-opacity=".55" stroke-width="3" stroke-linejoin="round" paint-order="stroke" '
            f'style="font-size:{K.fmt(size)}px;font-weight:700;letter-spacing:.5px">LLM</text>')


def ground_at(y, h):
    """The card gradient's colour at height y (INK2 at the top to INK at the bottom)."""
    return K.mix(K.INK2, K.INK, y / h)


def out_gradient(x1, y1, x2, y2):
    """userSpace gradient taking the output line from the model's violet to the gates' azure."""
    return (f'<linearGradient id="hgo" gradientUnits="userSpaceOnUse" x1="{K.fmt(x1)}" y1="{K.fmt(y1)}" '
            f'x2="{K.fmt(x2)}" y2="{K.fmt(y2)}"><stop offset="0" stop-color="{K.AGENT}" stop-opacity=".7"/>'
            f'<stop offset="1" stop-color="{K.TRUST}"/></linearGradient>')


def motion_css():
    """Builds (input lines, output line, tags, results), then the node flashes; rings never move."""
    return "".join([K.css_draw("hin", .7, .2), K.css_draw("hout", .8, .8), K.css_fade("htag", .4, 1.45),
                    K.css_rise("hres", 6, .6), K.css_flash("hfl", CYCLE)])


def identity_css(narrow):
    """Name, role and city styles (the name is always the largest type on the card)."""
    n, r, c, tr = (27, 15, 13, 1.6) if narrow else (34, 16, 11, 2)
    return (f".hn{{font-size:{n}px;font-weight:750;letter-spacing:{tr}px;fill:{K.TEXT}}}"
            f".hro{{font-size:{r}px;font-weight:500;fill:{K.TEXT2}}}"
            f".hci{{font-family:{K.MONO};font-size:{c}px;letter-spacing:1.4px;fill:{K.MUTED}}}"), n


# ---------------------------------------------------------------- wide
def build_wide():
    """850-wide hero: identity top-left, input left, ringed core centre, output right, results strip."""
    W, H = 850, 520
    CX, CY, R = 400, 262, 34
    RX = (78, 106, 134, 162)
    icss, name_px = identity_css(False)
    nw = K.tw(NAME, name_px, True, 2)
    K.assert_within(32 + nw, W - 28 - 74 - 24, "name vs key strip")

    body = [K.card(W, H, None, LIT), K.glow(CX, CY, 270, 230, K.VIOLET, .20), K.glow(96, 262, 130, 120, K.WARM, .16)]
    ldefs, lsvg, lcss = ring_labels(CX, CY, RX, 11, False)
    body.append(lsvg)

    # raw input: three ivory glyphs with labels, jittery lines converging on the shell's left edge
    gx, ys, lx, x_start, join = 52, (206, 262, 318), 80, 152, (CX - RX[3] + 2, CY)
    body.append(K.txt(40, 178, "raw input", "ey"))
    lines = []
    for i, (kind, y) in enumerate(zip(INPUTS, ys)):
        K.assert_within(lx + K.tw(kind, 12), x_start - 4, f"input label '{kind}'")
        body.append(glyph(kind, gx, y) + K.txt(lx, y + 4, kind, "lb"))
        lines.append(f'<path d="{jitter_d([(x_start, y), join], [5], 11 + i)}" class="hin" pathLength="1" '
                     f'fill="none" stroke="{IVORY}" stroke-opacity=".42" stroke-width="1.5" stroke-linecap="round"/>')
    orb_l = (CX - R, CY)
    lines.append(f'<path d="{jitter_d([join, orb_l], [4.5], 21)}" class="hin" pathLength="1" fill="none" '
                 f'stroke="{K.AGENT}" stroke-opacity=".55" stroke-width="1.6" stroke-linecap="round"/>')
    body.append("".join(lines))

    # output: leaves the orb, calms at every ring crossing, straight azure past the outer ring
    nodes = [(CX + rx, CY) for rx in RX]
    end_x = 808
    out_pts = [(CX + R, CY)] + nodes + [(end_x, CY)]
    body.append(f'<path d="{jitter_d(out_pts, [4, 2.5, 1.2, .5, 0], 31)}" class="hout" pathLength="1" fill="none" '
                f'stroke="url(#hgo)" stroke-width="2" stroke-linecap="round"/>')

    ccss, core = K.llm_core(CX, CY, R, "hc", n=24, seed=3, rings=[(rx, h, op) for rx, (_, h), op in
                                                                    zip(RX, RINGS, RING_OP)], node_angle=0, label="")
    body.append(core + llm_label(CX, CY, 13))

    # trust tags threaded on the straight segment, then the check
    tags, x = [], 580
    ground = ground_at(CY, H)
    for t in TAGS:
        svg, w = pill_on_line(x, CY, t, False, ground)
        tags.append(svg)
        x += w + 10
    K.assert_within(x - 10 + 12, end_x, "tags before the check")
    tags.append(check(end_x, CY - 8, 16))
    K.assert_within(end_x + 16, W - 24, "check tile vs card edge")
    tag_svg = f'<g class="htag">{"".join(tags)}</g>'          # drawn after the pulse: it threads behind the tags

    # the card's two annotations
    body.append(K.txt(CX, 309, "probabilistic", "an", PROB_INK, "middle", size=13))
    body.append(K.txt(522, 160, "deterministic", "an", DET_INK, size=13))

    # identity
    body.append(f'<text x="32" y="78" class="hn">{NAME}</text>'
                f'<text x="32" y="104" class="hro">{K.esc(ROLE)}</text>'
                f'<text x="32" y="124" class="hci">{CITY}</text>')

    # results strip: four content-measured cells, thin dividers, numerals with hue underlines
    body.append(K.hairline(32, 410, W - 32, 410))
    size, usize, gap, alen = 26, 15, 6, 18
    cells = []
    for i, (parts, hue, ctx, sub) in enumerate(RESULTS):
        sz = 24 if i == 1 else size          # shot fallback: cell 2's numeral drops to 24px to keep the slack
        nd = numeral(parts, sz, usize, gap, alen)
        cw = max(nd["G"], K.measure(ctx, "ctx"), K.measure(sub, "ey") if sub else 0)
        cells.append((nd, cw, hue, ctx, sub))
    span = W - 64
    pad = (span - sum(c[1] for c in cells)) / 8
    if pad < 16:
        raise OverflowError(f"results strip: padding {pad:.1f}px is under 16px")
    K.assert_within(sum(c[1] for c in cells) + 8 * 16, span - 24, "results strip with 24px slack")
    x, res = 32, []
    for i, (nd, cw, hue, ctx, sub) in enumerate(cells):
        xc = x + pad + cw / 2
        g = draw_numeral(nd, xc, 452, hue) + K.txt(xc, 478, ctx, "ctx", anchor="middle")
        if sub:
            g += K.txt(xc, 495, sub, "ey", anchor="middle")
        res.append(f'<g class="hres"{K.delay(1.2 + .15 * i)}>{g}</g>')
        x += cw + 2 * pad
        if i < 3:
            res.append(f'<line x1="{K.fmt(x)}" y1="428" x2="{K.fmt(x)}" y2="498" stroke="#FFFFFF" '
                       f'stroke-opacity=".12"/>')
    body.append("".join(res))

    # one request pulse every 6 s: documents line -> core (absorbed) -> out along the line, lighting each node
    tin = timeline([(x_start, ys[0]), join, orb_l, (CX, CY)], 0, 29)
    tout = timeline([(CX + R, CY)] + nodes + [(end_x, CY)], 40, 70)
    stops = ([(0, x_start, ys[0], 0)] + [(3, *[a + (b - a) * 3 / tin[1][0] for a, b in zip(tin[0][1:], tin[1][1:])], 1)] +
             [(pc, x, y, 1) for pc, x, y in tin[1:-1]] + [(29, CX, CY, .9), (31, CX, CY, 0),
                                                          (38, CX + R, CY, 0), (40.5, CX + R, CY, 1)] +
             [(pc, x, y, 1) for pc, x, y in tout[1:]] + [(73, end_x, CY, 0), (100, end_x, CY, 0)])
    pcss, psvg = pulse_path("hp", stops, [(0, IVORY), (tin[1][0], K.AGENT), (tout[1][0] - 2, K.TRUST)], CYCLE, LOOP0)
    body.append(node_flashes(nodes, [pc for pc, _, _ in tout[1:5]], K.TRUST))
    body.append(psvg + tag_svg)

    css = icss + lcss + motion_css() + ccss + pcss
    return K.svg_doc(W, H, TITLE, DESC, ldefs + out_gradient(CX + R, 0, nodes[-1][0], 0), css, "".join(body))


# ---------------------------------------------------------------- narrow
def build_narrow():
    """400-wide re-layout, top to bottom: identity, input row, ringed core, output column, 2x2 results."""
    W, H = 400, 860
    CX, CY, R = 200, 390, 24
    RX = (74, 98, 122, 146)
    icss, name_px = identity_css(True)
    nw = K.tw(NAME, name_px, True, 1.6)
    K.assert_within(nw, W - 48, "narrow name with 24px slack")

    body = [K.card(W, H, None, LIT), K.glow(CX, CY, 220, 230, K.VIOLET, .20), K.glow(CX, 196, 190, 90, K.WARM, .16)]
    ldefs, lsvg, lcss = ring_labels(CX, CY, RX, 13, True)
    body.append(lsvg)

    # identity, centred
    body.append(f'<text x="{CX}" y="66" class="hn" text-anchor="middle">{NAME}</text>'
                f'<text x="{CX}" y="91" class="hro" text-anchor="middle">{K.esc(ROLE)}</text>'
                f'<text x="{CX}" y="111" class="hci" text-anchor="middle">{CITY}</text>')

    # raw input row: label over glyph, three jittery lines funnel into the shell's top
    body.append(K.txt(CX, 148, "raw input", "ey", anchor="middle", size=13))
    xs, gy, tip = (90, 200, 310), 194, (CX, 250)
    lines = []
    for i, (kind, x) in enumerate(zip(INPUTS, xs)):
        K.assert_within(K.measure(kind, "lb", True), 104, f"narrow input label '{kind}'")
        body.append(K.txt(x, 172, kind, "lb", anchor="middle") + glyph(kind, x, gy, 1.1))
        lines.append(f'<path d="{jitter_d([(x, gy + 15), (CX, tip[1] - 4)], [4.5 if i != 1 else 3], 41 + i)}" '
                     f'class="hin" pathLength="1" fill="none" stroke="{IVORY}" stroke-opacity=".42" '
                     f'stroke-width="1.5" stroke-linecap="round"/>')
    body.append("".join(lines) + K.chevron(tip[0], tip[1], math.pi / 2, IVORY, .7, 5, 1.5))

    # output column: starts under 'probabilistic', calms at each ring's bottom crossing, then straight azure
    nodes = [(CX, CY + rx * .8) for rx in RX]
    y_start, end_y = CY + R + 24, 620
    body.append(f'<path d="{jitter_d([(CX, y_start)] + nodes + [(CX, end_y)], [2, 2.5, 1.2, .5, 0], 51)}" '
                f'class="hout" pathLength="1" fill="none" stroke="url(#hgo)" stroke-width="2" stroke-linecap="round"/>')
    ccss, core = K.llm_core(CX, CY, R, "hc", n=20, seed=3, rings=[(rx, h, op) for rx, (_, h), op in
                                                                    zip(RX, RINGS, RING_OP)], node_angle=90, label="")
    body.append(core + llm_label(CX, CY, 13))
    body.append(K.txt(CX, CY + R + 17, "probabilistic", "an", PROB_INK, "middle"))
    body.append(K.txt(W - 18, 296, "deterministic", "an", DET_INK, "end"))

    tags = []
    for i, t in enumerate(TAGS):
        cy = 538 + 31 * i
        w = K.pill_width(t, True)
        tags.append(pill_on_line(CX - w / 2, cy, t, True, ground_at(cy, H))[0])
    tags.append(check(CX - 9, end_y, 18))
    tag_svg = f'<g class="htag">{"".join(tags)}</g>'          # drawn after the pulse: it threads behind the tags

    # results: 2x2 grid with cross dividers, centred cells
    top, cw, rh = 664, (W - 36) / 2, 88
    body.append(K.hairline(18, top - 6, W - 18, top - 6))
    body.append(f'<path d="M{CX},{top + 6}V{top + 2 * rh - 6}M{18 + 10},{top + rh}H{W - 18 - 10}" stroke="#FFFFFF" '
                f'stroke-opacity=".12"/>')
    size, usize, gap, alen = 22, 14, 5, 14
    res = []
    for i, (parts, hue, ctx, sub) in enumerate(RESULTS):
        col, row = i % 2, i // 2
        xc, y0 = 18 + cw * col + cw / 2, top + rh * row
        nd = numeral(parts, size, usize, gap, alen)
        K.assert_within(nd["G"], cw - 12, f"narrow numeral {i}")
        K.fit(ctx, "ctx", cw - 12, True)
        g = draw_numeral(nd, xc, y0 + 34, hue)
        g += K.txt(xc, y0 + 59, ctx, "ctx", anchor="middle")
        if sub:
            K.assert_within(K.tw_mono(sub, 13, 1.6), cw - 12, "narrow sub line")
            g += K.txt(xc, y0 + 78, sub, "ey", anchor="middle", size=13)
        res.append(f'<g class="hres"{K.delay(1.2 + .15 * i)}>{g}</g>')
    body.append("".join(res))
    K.assert_within(top + 2 * rh, H - 16, "narrow results vs card bottom")

    # pulse: documents line -> funnel tip -> through the shell into the core (absorbed) -> down the line
    tin = timeline([(xs[0], gy + 15), (CX, tip[1] - 4), (CX, CY - R), (CX, CY)], 0, 29)
    tout = timeline([(CX, CY + R)] + nodes + [(CX, end_y)], 40, 70)
    stops = ([(0, xs[0], gy + 15, 0)] + [(3, *[a + (b - a) * 3 / tin[1][0] for a, b in zip(tin[0][1:], tin[1][1:])], 1)] +
             [(pc, x, y, 1) for pc, x, y in tin[1:-1]] + [(29, CX, CY, .9), (31, CX, CY, 0),
                                                          (38, CX, CY + R, 0), (40.5, CX, CY + R, 1)] +
             [(pc, x, y, 1) for pc, x, y in tout[1:]] + [(73, CX, end_y, 0), (100, CX, end_y, 0)])
    pcss, psvg = pulse_path("hp", stops, [(0, IVORY), (tin[1][0], K.AGENT), (tout[1][0] - 2, K.TRUST)], CYCLE, LOOP0)
    body.append(node_flashes(nodes, [pc for pc, _, _ in tout[1:5]], K.TRUST))
    body.append(psvg + tag_svg)

    css = icss + lcss + motion_css() + ccss + pcss
    return K.svg_doc(W, H, TITLE, DESC, ldefs + out_gradient(0, CY + R, 0, nodes[-1][1]), css, "".join(body))


if __name__ == "__main__":
    K.write(os.path.join(ASSETS, "hero.svg"), build_wide())
    K.write(os.path.join(ASSETS, "hero-narrow.svg"), build_narrow())
    print(K.picture("hero", ALT))
