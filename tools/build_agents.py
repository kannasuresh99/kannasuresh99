#!/usr/bin/env python3
"""Scene 4, 'Agentic systems I've built': five working-diagram panels on one board.

Writes assets/agents.svg (850 wide) and assets/agents-narrow.svg (400 wide) from the shared svgkit.
Python 3 stdlib only, deterministic. Never hand-edit the SVGs; change this file and re-run.

Panels: 1 agent framework (LangGraph), 2 micro-prompting, 3 SOP -> AOP DSL, 4 CodexMap and the Venmo
decomposition (PayPal), 5 the document -> computable model pattern (technique only: no name, no metric).
Every panel reads alone: tag (where), title (what), a working diagram (how), and a punchline strip whose
numeral is the panel's largest type. Each panel loops on its own (8-12 s, still at least 55%); the base
attributes are the finished frame, so reduced motion shows every final state.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgkit as K  # noqa: E402

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

TITLE = "Agentic systems I've built"
ALT = ("Five agentic systems drawn as working diagrams, each with its result. "
       "1. Agent framework (Enegma, LangGraph): lifecycle, memory, tools and orchestration modules dock into one "
       "framework core, which sends out new agents that hand off to each other; new-agent development went from "
       "weeks to ~1 day. 2. Micro-prompting (Enegma, real-time agents): one big prompt splits into short 200 to "
       "800-token prompts, with before and after bars drawn to scale; ~5× faster first token and ~90% fewer prompt "
       "tokens. 3. SOP to AOP (Enegma): a DSL turns a numbered standard operating procedure into an agent flow on an "
       "agent canvas; when a step changes, the flow re-routes while the locked core code stays untouched; iteration "
       "time cut ~60%. 4. Agents that read code (PayPal, CodexMap): a codebase goes through AST parsing, semantic "
       "embeddings and reasoning agents and comes out as service maps and call graphs; architectural analysis cut "
       "~60% and dependency discovery cut ~70%. Beside it, the Venmo decomposition: a 9-month manual process became "
       "an agentic workflow, and the migration ran ~30% faster. 5. Document to computable model (side-project "
       "pattern): a long spec PDF becomes a computable model; drafting agents write forms, specs and mappings; a "
       "human approves before anything goes live; you can ask the document and the answer cites its section; when "
       "an amendment arrives, the changes are detected and ripple out to every artifact to be re-drafted and "
       "re-approved. AI drafts. Humans approve.")
DESC = ("Five panels: an agent framework that sends out agents, micro-prompting with before and after bars, a DSL "
        "from SOP to an agent flow, agents that map a codebase into services beside the Venmo decomposition, and a "
        "document turned into a computable model with drafting agents, a human gate and change propagation.")

AG, TR, DA, RE, SV = K.AGENT, K.TRUST, K.DATA, K.RETR, K.SVC
IVORY = K.RESULT
LIT = ("DATA", "SVC", "RETR", "AGENT", "TRUST")


def F(v):
    """Coordinate (1 decimal)."""
    return K.fmt(v, 1)


def O(v):
    """Opacity (2 decimals)."""
    return K.fmt(v, 2)


# ---------------------------------------------------------------- shared defs
ORB_R = 7


def orb_def():
    """One glowing agent orb (r 7, kit recipe) defined once and reused with <use>."""
    return f'<g id="ob">{K.orb(0, 0, ORB_R)}</g>'


def orb(x, y, r=ORB_R):
    """Agent orb standing on ground point (x, y) at radius r (reuses #ob)."""
    if abs(r - ORB_R) < 1e-6:
        return f'<use href="#ob" x="{F(x)}" y="{F(y)}"/>'
    return f'<use href="#ob" transform="translate({F(x)},{F(y)}) scale({O(r / ORB_R)})"/>'


# ---------------------------------------------------------------- small drawing helpers (scene-local)
def panel_rect(w, h):
    """Inner panel: rx 12, white 3% fill, periwinkle 14% stroke."""
    return (f'<rect width="{F(w)}" height="{F(h)}" rx="12" fill="#FFFFFF" fill-opacity=".03" '
            f'stroke="{K.BORDER}" stroke-opacity=".14"/>')


def plinth(x, y, w, h=6, dx=10, dy=7):
    """Low neutral cabinet plinth (ink + 6% white top) with one soft floor shadow."""
    return (f'<rect x="{F(x + 6)}" y="{F(y + dy + h - 2)}" width="{F(w - 12)}" height="7" fill="#000" '
            f'fill-opacity=".5" filter="url(#k-blur)"/>' + K.plate(x, y, w, h, None, dx, dy))


def contact(x, y, rx, op=.38):
    """Small contact shadow under a glyph."""
    return f'<ellipse cx="{F(x)}" cy="{F(y)}" rx="{F(rx)}" ry="{F(max(2.4, rx * .09))}" fill="#000" fill-opacity="{O(op)}"/>'


def hex_prism(cx, gy, rx, ry, h, hue=AG):
    """Matte hexagonal prism standing on (cx, gy): top = hue + 38% white, three shaded front faces, rim on the back edges."""
    def v(k, z):
        a = math.radians(60 * k)
        return (cx + rx * math.cos(a), gy + ry * math.sin(a) - z)
    cols = {0: K.mix(hue, K.INK, .5), 1: K.mix(hue, K.INK, .28), 2: hue}
    o = [f'<polygon points="{K.pts([v(k, 0), v(k + 1, 0), v(k + 1, h), v(k, h)])}" fill="{cols[k]}"/>' for k in (0, 1, 2)]
    o.append(f'<polygon points="{K.pts([v(k, h) for k in range(6)])}" fill="{K.mix(hue, K.WHITE, .38)}"/>')
    inner = [(cx + (x - cx) * .55, gy - h + (y - gy + h) * .55) for x, y in (v(k, h) for k in range(6))]
    o.append(f'<polygon points="{K.pts(inner)}" fill="none" stroke="{K.INK}" stroke-opacity=".22"/>')
    o.append(f'<polyline points="{K.pts([v(3, h), v(4, h), v(5, h), v(6, h)])}" fill="none" '
             f'stroke="{K.rim_tint(hue)}" stroke-opacity=".7"/>')
    return "".join(o)


def bar(x, y, w, h, hue, d=5, ghost=False):
    """Small cabinet bar (front x..x+w, y..y+h) with a top and an end face; ghost = matte outline only."""
    top = [(x, y), (x + d, y - d * .7), (x + w + d, y - d * .7), (x + w, y)]
    side = [(x + w, y), (x + w + d, y - d * .7), (x + w + d, y + h - d * .7), (x + w, y + h)]
    if ghost:
        st = f' stroke="{hue}" stroke-opacity=".55" stroke-linejoin="round"'
        return (f'<polygon points="{K.pts(top)}" fill="{hue}" fill-opacity=".22"{st}/>'
                f'<polygon points="{K.pts(side)}" fill="{hue}" fill-opacity=".14"{st}/>'
                f'<rect x="{F(x)}" y="{F(y)}" width="{F(w)}" height="{F(h)}" fill="{hue}" fill-opacity=".12"{st}/>')
    return (f'<polygon points="{K.pts(top)}" fill="{K.mix(hue, K.WHITE, .38)}"/>'
            f'<polygon points="{K.pts(side)}" fill="{K.mix(hue, K.INK, .5)}"/>'
            f'<rect x="{F(x)}" y="{F(y)}" width="{F(w)}" height="{F(h)}" fill="{hue}"/>')


def page(x, y, w, h, fold=8, op=.9, shadow=True):
    """Upright ivory document sheet with a folded top-right corner and a contact shadow."""
    o = contact(x + w / 2, y + h + 1, w * .58, .4) if shadow else ""
    return (o + f'<path d="M{F(x)},{F(y)}H{F(x + w - fold)}L{F(x + w)},{F(y + fold)}V{F(y + h)}H{F(x)}Z" '
            f'fill="{IVORY}" fill-opacity="{O(op)}"/>'
            f'<path d="M{F(x + w - fold)},{F(y)}V{F(y + fold)}H{F(x + w)}Z" fill="{K.mix(IVORY, K.INK, .38)}"/>')


def rules(x, ys, lens_, op=.28, w=1.6, col=None):
    """Rule lines (one path) at heights ys with lengths lens_, ink by default."""
    d = "".join(f"M{F(x)},{F(y)}h{F(L)}" for y, L in zip(ys, lens_))
    return (f'<path d="{d}" stroke="{col or K.INK}" stroke-opacity="{O(op)}" stroke-width="{F(w)}" '
            f'stroke-linecap="round"/>')


def code_lines(x, y, pitch, spec, col=K.TEXT2, op=.6, w=1.7):
    """Code-like line stubs: spec = [(indent, length), ...] drawn as one path."""
    d = "".join(f"M{F(x + ind)},{F(y + i * pitch)}h{F(L)}" for i, (ind, L) in enumerate(spec))
    return f'<path d="{d}" stroke="{col}" stroke-opacity="{O(op)}" stroke-width="{F(w)}" stroke-linecap="round"/>'


def node(x, y, s=7, hue=AG, h=60):
    """Tiny matte iso block (flow node, micro-object recipe)."""
    return K.Iso(x, y, s).box(0, 0, 1, 1, h, hue)


def arrow(x1, y1, x2, y2, hue, op=.55, w=1.4, size=4):
    """Straight connector with an open chevron, drawn as one path (class .ar: round caps/joins, no fill)."""
    a = math.atan2(y2 - y1, x2 - x1)
    c1 = (x2 + size * math.cos(a + math.pi - .66), y2 + size * math.sin(a + math.pi - .66))
    c2 = (x2 + size * math.cos(a + math.pi + .66), y2 + size * math.sin(a + math.pi + .66))
    sw = "" if abs(w - 1.4) < 1e-6 else f' stroke-width="{F(w)}"'
    return (f'<path class="ar" d="M{F(x1)},{F(y1)}L{F(x2)},{F(y2)}M{K.pts([c1])}L{F(x2)},{F(y2)}L{K.pts([c2])}" '
            f'stroke="{hue}" stroke-opacity="{O(min(1, op + .15))}"{sw}/>')


def diff_glyph(cx, gy, s=1, hue=DA):
    """Detect changes: the old sheet (faded outline) behind the amended sheet, its changed line marked in the hue."""
    w, h = 24 * s, 30 * s
    ox, oy = cx - 14 * s, gy - h - 9 * s
    nx, ny = cx - 6 * s, gy - h
    return (f'<rect x="{F(ox)}" y="{F(oy)}" width="{F(w)}" height="{F(h)}" rx="1.5" fill="{IVORY}" fill-opacity=".14" '
            f'stroke="{IVORY}" stroke-opacity=".45"/>' + page(nx, ny, w, h, 6 * s) +
            rules(nx + 4 * s, [ny + 9 * s, ny + 23 * s], [14 * s, 11 * s], .3, 1.4) +
            f'<rect x="{F(nx + 3 * s)}" y="{F(ny + 13 * s)}" width="{F(w - 6 * s)}" height="{F(5 * s)}" rx="1.2" '
            f'fill="{hue}"/>')


def check_badge(cx, cy, r=7, hue=TR):
    """Azure check badge: tinted disc, azure ring, white check."""
    return (f'<circle cx="{F(cx)}" cy="{F(cy)}" r="{F(r)}" fill="{hue}" fill-opacity=".22" stroke="{hue}" '
            f'stroke-width="1.4"/>'
            f'<path d="M{F(cx - r * .45)},{F(cy)}l{F(r * .3)},{F(r * .32)} {F(r * .55)},{F(-r * .62)}" fill="none" '
            f'stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')


def padlock(cx, cy, s=1, hue=SV):
    """Flat upright padlock (body plus shackle) in the hue's light tint."""
    bw, bh = 11 * s, 8.5 * s
    lite = K.mix(hue, K.WHITE, .55)
    return (f'<path d="M{F(cx - 3.4 * s)},{F(cy - bh / 2)}v{F(-3 * s)}a{F(3.4 * s)},{F(3.4 * s)} 0 0 1 {F(6.8 * s)},0'
            f'v{F(3 * s)}" fill="none" stroke="{lite}" stroke-width="{F(1.6 * s)}"/>'
            f'<rect x="{F(cx - bw / 2)}" y="{F(cy - bh / 2)}" width="{F(bw)}" height="{F(bh)}" rx="{F(1.6 * s)}" '
            f'fill="{lite}"/><circle cx="{F(cx)}" cy="{F(cy + .3 * s)}" r="{F(1.3 * s)}" fill="{K.mix(hue, K.INK, .6)}"/>')


def bubble(x, y, w, h, tail, side="up"):
    """Neutral speech-bubble outline with a small tail: side 'up' (tail = x of tip) or 'left' (tail = y of tip)."""
    r = h / 2
    if side == "up":
        d = (f"M{F(x + r)},{F(y)}H{F(tail - 5)}l5,-7 5,7H{F(x + w - r)}a{F(r)},{F(r)} 0 0 1 0,{F(h)}"
             f"H{F(x + r)}a{F(r)},{F(r)} 0 0 1 0,{F(-h)}Z")
    else:
        d = (f"M{F(x + r)},{F(y)}H{F(x + w - r)}a{F(r)},{F(r)} 0 0 1 0,{F(h)}H{F(x + r)}"
             f"a{F(r)},{F(r)} 0 0 1 {F(-r * .62)},{F(-r * .22)}l-7,{F(-r * .45)} 7,{F(-r * .45)}"
             f"a{F(r)},{F(r)} 0 0 1 {F(r * .62)},{F(-r * .88)}Z")
    return (f'<path d="{d}" fill="#FFFFFF" fill-opacity=".04" stroke="{K.TEXT2}" stroke-opacity=".7" '
            f'stroke-linejoin="round"/>')


def tree(cx, y0, dx1, dx2, dy, hue=RE, r=3.2):
    """AST glyph: a 1-2-4 node tree, edges in the link tint, nodes in the hue."""
    lite = K.link_tint(hue)
    root = (cx, y0)
    kids = [(cx - dx1, y0 + dy), (cx + dx1, y0 + dy)]
    leaves = [(kx + sx * dx2, y0 + 2 * dy) for kx, _ in kids for sx in (-1, 1)]
    d = "".join(f"M{F(root[0])},{F(root[1])}L{F(k[0])},{F(k[1])}" for k in kids)
    d += "".join(f"M{F(kids[i // 2][0])},{F(kids[i // 2][1])}L{F(q[0])},{F(q[1])}" for i, q in enumerate(leaves))
    o = [f'<path d="{d}" stroke="{lite}" stroke-opacity=".8" stroke-width="1.2"/>']
    for i, (px, py) in enumerate([root] + kids + leaves):
        fill = K.mix(hue, K.WHITE, .38) if i == 0 else hue if i < 3 else K.mix(hue, K.INK, .15)
        o.append(f'<circle cx="{F(px)}" cy="{F(py)}" r="{F(r + .8 if i == 0 else r)}" fill="{fill}"/>')
    return "".join(o)


def scatter(cx, cy, w, h, seed, n=33, hue=RE):
    """Semantic-embedding cloud: three seeded clusters of points (dots as zero-length round-capped strokes, grouped by tint)."""
    rnd = random.Random(seed)
    cents = [(cx - w * .27, cy + h * .14), (cx + w * .2, cy - h * .2), (cx + w * .18, cy + h * .26)]
    groups = {}
    for i in range(n):
        ccx, ccy = cents[i % 3]
        px = min(max(ccx + rnd.gauss(0, w * .1), cx - w / 2), cx + w / 2)
        py = min(max(ccy + rnd.gauss(0, h * .11), cy - h / 2), cy + h / 2)
        r = rnd.choice((2.6, 3.4, 4.2))
        col = (K.link_tint(hue), K.tech_tint(hue), hue)[i % 3]
        groups.setdefault((col, r), []).append((px, py))
    o = []
    for (col, r), ps in sorted(groups.items()):
        d = "".join(f"M{F(x)},{F(y)}h0" for x, y in ps)
        o.append(f'<path d="{d}" stroke="{col}" stroke-opacity="{O(.5 + r / 12)}" stroke-width="{F(r)}" '
                 f'stroke-linecap="round"/>')
    return "".join(o)


def grid_model(cx, cy, a, hue=DA, n=3):
    """Computable model: an n x n grid of DATA cells (iso) with entity links across their tops."""
    I = K.Iso(cx, cy, a)
    step = 1 / n
    hs = [10, 16, 12, 18, 10, 14, 16, 12, 10]
    hmap = {(i, j): hs[(j * n + i) % len(hs)] for j in range(n) for i in range(n)}
    o = [I.box(i * step + .05, j * step + .05, step - .1, step - .1, h, hue)
         for (i, j), h in sorted(hmap.items(), key=lambda c: (c[0][0] + c[0][1], c[0][0]))]
    top = lambda i, j: I.p(i * step + step / 2, j * step + step / 2, hmap[(i, j)])
    links = [((0, 0), (1, 1)), ((1, 1), (2, 0)), ((1, 1), (2, 2)), ((0, 2), (1, 1)), ((2, 0), (2, 2))]
    d = "".join(f"M{K.pts([top(*p)])}L{K.pts([top(*q)])}" for p, q in links)
    o.append(f'<path d="{d}" stroke="{K.mix(hue, K.WHITE, .6)}" stroke-opacity=".9" stroke-width="1.1"/>')
    d = "".join(f"M{K.pts([top(*p)])}h0" for p in ((0, 0), (1, 1), (2, 0), (2, 2), (0, 2)))
    o.append(f'<path d="{d}" stroke="#FFFFFF" stroke-width="3.6" stroke-linecap="round"/>')
    return "".join(o)


def service_tile(x, y, w, h, stubs, hue=SV):
    """A rose service cluster: tinted tile holding regrouped code stubs, with a small service cube on its corner."""
    return (f'<rect x="{F(x)}" y="{F(y)}" width="{F(w)}" height="{F(h)}" rx="3" fill="{hue}" fill-opacity=".16" '
            f'stroke="{hue}" stroke-opacity=".75"/>' +
            code_lines(x + 6, y + 7, 5, stubs, K.TEXT2, .65, 1.6) + node(x + w - 1, y + 1, 6.5, hue, 70))


def artifact(cx, y0, kind, pw=30, ph=38):
    """Draft artifact page: 0 form (field boxes), 1 spec (rule lines), 2 mapping (two columns, crossing links)."""
    x0 = cx - pw / 2
    o = [page(x0, y0, pw, ph, 7)]
    k = pw / 30
    if kind == 0:
        d = "".join(f"M{F(x0 + 5 * k)},{F(y0 + (10 + i * 9) * k)}h{F(pw - 10 * k)}v{F(5 * k)}h{F(-(pw - 10 * k))}z"
                    for i in range(3))
        o.append(f'<path d="{d}" fill="none" stroke="{K.INK}" stroke-opacity=".38"/>')
    elif kind == 1:
        o.append(rules(x0 + 5 * k, [y0 + (11 + i * 5.5) * k for i in range(5)], [18 * k, 14 * k, 18 * k, 10 * k, 16 * k],
                       .3, 1.4))
    else:
        ys = [y0 + (12 + i * 8) * k for i in range(3)]
        a, b = x0 + 11 * k, x0 + pw - 11 * k
        o.append(rules(x0 + 4 * k, ys, [6 * k] * 3, .4, 2) + rules(b + 1 * k, ys, [6 * k] * 3, .4, 2) +
                 f'<path d="M{F(a)},{F(ys[0])}L{F(b)},{F(ys[1])}M{F(a)},{F(ys[1])}L{F(b)},{F(ys[2])}M{F(a)},{F(ys[2])}'
                 f'L{F(b)},{F(ys[0])}" stroke="{K.INK}" stroke-opacity=".35"/>')
    return "".join(o)


def spec_pdf(px, py, pw, ph, ms):
    """Long spec PDF: ivory page with three section marks and rule lines."""
    o = [page(px, py, pw, ph, 10 * pw / 48)]
    ys = [py + ph * f for f in (.36, .6, .84)]
    o.extend(f'<text x="{F(px + pw * .15)}" y="{F(y)}" class="ps" fill="{K.INK}" fill-opacity=".55">§</text>' for y in ys)
    o.append(rules(px + pw * .4, [y - ms * .32 for y in ys], [pw * .42, pw * .33, pw * .46], .28, 1.6))
    return "".join(o)


def amendment_page(cx, y, w, h):
    """The amended document: a page with one azure-highlighted section (the change)."""
    x0 = cx - w / 2
    return (page(x0, y, w, h, 8 * w / 34) + rules(x0 + 6, [y + h * .27, y + h * .68, y + h * .82], [w * .53, w * .47, w * .59],
                                                  .28, 1.5) +
            f'<rect x="{F(x0 + 4)}" y="{F(y + h * .39)}" width="{F(w - 8)}" height="{F(h * .16)}" rx="1.5" fill="{TR}" '
            f'fill-opacity=".85"/>')


# ---------------------------------------------------------------- text with bounds checks
class Txt:
    """Text placement for one variant: scene classes plus kit classes, each label measured and asserted in a box."""

    def __init__(self, narrow):
        self.n = narrow
        self.size = {"tt": 16 if narrow else 15, "tg": 13 if narrow else 10.5, "sl": 13 if narrow else 10.5,
                     "mo": 13 if narrow else 10.5, "pq": 20 if narrow else 18, "ps": 15 if narrow else 13}

    def width(self, s, cls):
        """Width of s in a scene or kit class."""
        z = self.size.get(cls)
        if cls == "tt":
            return K.tw(s, z, bold=True)
        if cls == "tg":
            return K.tw_mono(s, z, 1.4)
        if cls == "mo":
            return K.tw_mono(s, z)
        if cls == "sl":
            return K.tw(s, z)
        if cls == "pq":
            return K.tw(s, z) * 1.04
        return K.measure(s, cls, self.n)

    def put(self, x, y, s, cls, fill=None, anchor=None, box=None, what=""):
        """Place one label and assert its extent lies inside box=(x0, x1)."""
        w = self.width(s, cls)
        x0 = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        if box:
            K.assert_within(box[0], x0, f"{what or s} left")
            K.assert_within(x0 + w, box[1], f"{what or s} right")
        if cls in self.size:
            a = f' fill="{fill}"' if fill else ""
            a += f' text-anchor="{anchor}"' if anchor else ""
            return f'<text x="{F(x)}" y="{F(y)}" class="{cls}"{a}>{K.esc(s)}</text>'
        return K.txt(x, y, s, cls, fill, anchor)

    def css(self):
        """CSS for the scene's own text classes."""
        s = self.size
        return (f".tg,.mo{{font-family:{K.MONO};font-weight:500;fill:{K.MUTED}}}.pq,.ps{{font-family:{K.SERIF}}}"
                f".tt{{font-size:{F(s['tt'])}px;font-weight:650;fill:{K.TEXT}}}"
                f".tg{{font-size:{F(s['tg'])}px;letter-spacing:1.4px}}.mo{{font-size:{F(s['mo'])}px}}"
                f".sl{{font-size:{F(s['sl'])}px;fill:{K.TEXT2}}}"
                f".pq{{font-style:italic;font-size:{F(s['pq'])}px;fill:{IVORY}}}"
                f".ps{{font-size:{F(s['ps'])}px;font-weight:700}}")


def head(T, w, tag, title, hue, pad=16):
    """Panel tag (6px hue dot + mono caps) and title, in panel-local coordinates."""
    ty, tt = (25, 50) if T.n else (23, 44)
    return (f'<circle cx="{F(pad + 3)}" cy="{F(ty - (4.4 if T.n else 3.6))}" r="3" fill="{hue}"/>' +
            T.put(pad + 13, ty, tag, "tg", box=(0, w - pad)) + T.put(pad, tt, title, "tt", box=(0, w - pad)))


def rule(w, y, pad=16):
    """Hairline above a strip."""
    return K.hairline(pad, y, w - pad, y, .12)


def num(x, y, text, hue, size, box, anchor="start"):
    """Result numeral with its hue underline; asserted inside box."""
    svg, wd = K.numeral(x, y, text, hue, size=size, anchor=anchor)
    x0 = x - (wd / 2 if anchor == "middle" else wd if anchor == "end" else 0)
    K.assert_within(box[0], x0, f"numeral {text} left")
    K.assert_within(x0 + wd, box[1], f"numeral {text} right")
    return svg, wd


# ---------------------------------------------------------------- motion (opacity, transform, dash offset only)
def kf(name, frames):
    """@keyframes from [(pct, css)]."""
    return f"@keyframes {name}{{" + "".join(f"{F(p) if p % 1 else int(p)}%{{{c}}}" for p, c in frames) + "}"


def loop(cls, cycle, delay, extra="", ease="ease-in-out", hidden=False):
    """Infinite loop on class cls (keyframes k<cls>); backwards fill holds the 0% state through the build delay."""
    return (f".{cls}{{{'opacity:0;' if hidden else ''}{extra}animation:k{cls} {F(cycle)}s {ease} {F(delay)}s infinite"
            f"{'' if hidden else ' backwards'}}}")


def flash_kf(cls, t_up, t_peak, t_gone):
    """Transient flash keyframes (hidden at rest)."""
    return kf(f"k{cls}", [(0, "opacity:0")] + ([(t_up, "opacity:0")] if t_up else []) +
              [(t_peak, "opacity:1"), (t_gone, "opacity:0"), (100, "opacity:0")])


def dash_kf(cls, t0, t1, seg):
    """Travelling short dash on a pathLength=100 path between t0% and t1% (hidden at rest)."""
    e = 100 - seg if seg else 100
    return kf(f"k{cls}", [(0, "opacity:0;stroke-dashoffset:0")] + ([(t0, "opacity:0;stroke-dashoffset:0")] if t0 else []) +
              [(t0 + .5, "opacity:1"), (t1 - .5, "opacity:1"), (t1, f"opacity:0;stroke-dashoffset:-{e}"),
               (100, f"opacity:0;stroke-dashoffset:-{e}")])


# ---------------------------------------------------------------- panel 1: agent framework
def p1_framework(T, w, d0):
    """Panel 1: a matte hex framework with four docked modules; three agents leave it on a rising diagonal."""
    n = T.n
    o, css = [head(T, w, "ENEGMA · LANGGRAPH", "Agent framework", AG)], []
    lite = K.link_tint(AG)
    mods = ["lifecycle", "memory", "tools", "orchestration"]
    if not n:
        cx, gy, rx, ry, hh = 132, 202, 22, 11, 62
        orbs, r, lab_dy = [(173, 208), (202, 193.5), (231, 179)], 8, -15
        o.append(plinth(108, gy - 2, 136))
        pitch = 30
        cy0 = gy - hh / 2 - 1.5 * pitch + 2
        docks = [gy - hh + 8 + i * (hh - 16) / 3 for i in range(4)]
        for i, m in enumerate(mods):
            cy = cy0 + i * pitch
            svg, pw = K.pill(16, cy, m, AG, False, 8)
            K.assert_within(16 + pw + 3, cx - rx, f"module {m} vs hex")
            o.append(svg + f'<path d="M{F(16 + pw)},{F(cy)}C{F(16 + pw + 8)},{F(cy)} {F(cx - rx - 8)},{F(docks[i])} '
                           f'{F(cx - rx)},{F(docks[i])}" fill="none" stroke="{lite}" stroke-opacity=".75"/>'
                           f'<circle cx="{F(cx - rx)}" cy="{F(docks[i])}" r="2" fill="{lite}"/>')
        strip_y, nsize = 252, 26
    else:
        cx, gy, rx, ry, hh = 128, 150, 30, 15, 52
        orbs, r, lab_dy = [(212, 154), (260, 130), (308, 106)], 9, -17
        o.append(plinth(84, gy - 3, 262))
        # modules: 2 x 2 grid beneath, docked to a spine from the hex base
        spine, rows = cx, (gy + 52, gy + 82)
        o.append(f'<path d="M{F(spine)},{F(gy + ry * .87)}V{F(rows[1])}" stroke="{lite}" stroke-opacity=".75"/>'
                 f'<circle cx="{F(spine)}" cy="{F(gy + ry * .87)}" r="2" fill="{lite}"/>')
        for i, m in enumerate(mods):
            cy = rows[i // 2]
            pw = K.pill_width(m, True)
            x = spine - 12 - pw if i % 2 == 0 else spine + 12
            K.assert_within(16, x, f"module {m} left")
            K.assert_within(x + pw, w - 16, f"module {m} right")
            o.append(K.pill(x, cy, m, AG, True)[0])
            ex = x + pw if i % 2 == 0 else x
            o.append(f'<path d="M{F(spine)},{F(cy)}H{F(ex)}" stroke="{lite}" stroke-opacity=".75"/>'
                     f'<circle cx="{F(ex)}" cy="{F(cy)}" r="2" fill="{lite}"/>')
        strip_y, nsize = rows[1] + 30, 28
    o.append(T.put(cx, gy - hh - ry - 10, "framework", "st", K.name_tint(AG), "middle", (0, w), "framework"))
    o.append(hex_prism(cx, gy, rx, ry, hh))
    # three agents: appear in sequence (scale .6 -> 1 + fade, 0.4 s each, 0.5 s apart), hold, fade together
    prev = None
    for i, (ox, og) in enumerate(orbs):
        oyc = og - 1.6 * r
        if prev is None:   # leaves the right facet at the orb's height: an arrow when there is room, else a port tether
            fx = cx + rx + 1
            K.assert_within(gy - hh, oyc, "first agent above hex base")
            ln = (arrow(fx + 2, oyc, ox - r - 5, oyc, AG, .7, 1.3, 3.6) if ox - r - 5 - fx > 24 else
                  f'<path d="M{F(fx)},{F(oyc)}H{F(ox - r - 2)}" stroke="{lite}" stroke-opacity=".8" stroke-width="1.3"/>')
            ln += f'<circle cx="{F(fx)}" cy="{F(oyc)}" r="2" fill="{lite}"/>'
        else:
            a = math.atan2(oyc - prev[1], ox - prev[0])
            ln = arrow(prev[0] + math.cos(a) * (r + 5), prev[1] + math.sin(a) * (r + 5), ox - math.cos(a) * (r + 5),
                       oyc - math.sin(a) * (r + 5), AG, .7, 1.3, 3.6)
        g = (ln + orb(ox, og, r) +
             T.put(ox, oyc + lab_dy, "agent", "sb" if n else "sl", K.tech_tint(AG), "middle", (0, w - 8), f"agent {i}"))
        o.append(f'<g class="a1o{i}">{g}</g>')
        t0 = 6.25 * i
        css.append(kf(f"ka1o{i}", [(0, "opacity:0;transform:scale(.6)")] + ([(t0, "opacity:0;transform:scale(.6)")] if t0 else []) +
                      [(t0 + 5, "opacity:1;transform:none"), (88, "opacity:1;transform:none"),
                       (96, "opacity:0;transform:none"), (100, "opacity:0;transform:none")]))
        css.append(loop(f"a1o{i}", 8, d0, "transform-box:fill-box;transform-origin:50% 100%;", "ease-out"))
        prev = (ox, oyc)
    o.append(rule(w, strip_y))
    svg, _ = num(16, strip_y + (40 if n else 36), "weeks → ~1 day", AG, nsize, (0, w - 16))
    o.append(svg + T.put(16, strip_y + (64 if n else 58), "per new agent", "ctx", box=(0, w - 16)))
    return "".join(o), "".join(css), strip_y + (82 if n else 78)


# ---------------------------------------------------------------- panel 2: micro-prompting
def p2_microprompt(T, w, d0):
    """Panel 2: one big prompt splits into short prompts; before/after bars drawn to the stated ratios."""
    n = T.n
    o, css = [head(T, w, "ENEGMA · REAL-TIME", "Micro-prompting", AG)], []
    x0, x1 = 16, w - 22
    if not n:
        y_lab, y_big, y_small, y_tl, bh_big = 72, 82, 112, 134, 11
        unit, by0, bh, gap_pair, gap_group, strip_y = 15, 162, 8, 5, 22, 252
        lens_ = [16, 38, 26, 50]
    else:
        y_lab, y_big, y_small, y_tl, bh_big = 80, 90, 124, 152, 13
        unit, by0, bh, gap_pair, gap_group, strip_y = 28, 186, 10, 6, 26, None
        lens_ = [28, 64, 44, 86]
    o.append(T.put(x0, y_lab, "one big prompt", "sb", box=(0, w - 16)))
    o.append(bar(x0, y_big, x1 - x0, bh_big, AG, 5, ghost=True))
    gap = (x1 - x0 - sum(lens_)) / 3
    xs, x = [], x0
    for L in lens_:
        xs.append(x)
        x += L + gap
    mid = (x0 + x1) / 2
    o.append(arrow(mid, y_big + bh_big + 4, mid, y_small - 9, AG, .5, 1.3, 4))
    for j, (bx, L) in enumerate(zip(xs, lens_)):
        o.append(f'<g class="a2q"{K.delay(d0 + .16 * j)}>{bar(bx, y_small, L, bh_big, AG, 5)}</g>')
    tsvg, tw_ = K.tech(x0, y_tl, "200 to 800-token prompts", AG, n)
    K.assert_within(x0 + tw_, w - 16, "token label")
    o.append(tsvg)
    dy = y_small - y_big
    css.append(kf("ka2q", [(0, f"opacity:0;transform:translateY(-{dy}px)"), (1, f"opacity:0;transform:translateY(-{dy}px)"),
                           (3, "opacity:1"), (10, "opacity:1;transform:none"), (92, "opacity:1;transform:none"),
                           (98, "opacity:0;transform:none"), (100, "opacity:0;transform:none")]))
    css.append(loop("a2q", 8, d0, "", "cubic-bezier(.2,.8,.2,1)"))
    # comparison bars (no axis, no numbers): before = muted 35%, after = AGENT + 38% white, unit-exact widths
    lab_w = max(T.width("before", "mo"), T.width("after", "mo"))
    bx0 = x0 + lab_w + (10 if n else 8)
    after_col = K.mix(AG, K.WHITE, .38)
    y = by0
    for name, ratio, cls, t0, t1 in (("first token", 5, "a2f", 14, 22), ("prompt tokens", 10, "a2p", 22, 30)):
        o.append(T.put(x0, y - (9 if n else 7), name, "sb", box=(0, w - 16)))
        wb, wa = ratio * unit, unit
        K.assert_within(bx0 + wb, w - 16, f"{name} before bar")
        ya = y + bh + gap_pair
        o.append(T.put(x0, y + bh - .5, "before", "mo") +
                 f'<rect x="{F(bx0)}" y="{F(y)}" width="{F(wb)}" height="{F(bh)}" rx="2" fill="{K.MUTED}" '
                 f'fill-opacity=".35"/>' + T.put(x0, ya + bh - .5, "after", "mo") +
                 f'<rect class="{cls}" x="{F(bx0)}" y="{F(ya)}" width="{F(wa)}" height="{F(bh)}" rx="2" '
                 f'fill="{after_col}"/>')
        css.append(kf(f"k{cls}", [(0, f"opacity:0;transform:scaleX({ratio})"), (t0 - 2, f"opacity:0;transform:scaleX({ratio})"),
                                  (t0, f"opacity:1;transform:scaleX({ratio})"), (t1, "opacity:1;transform:none"),
                                  (92, "opacity:1;transform:none"), (98, "opacity:0;transform:none"),
                                  (100, "opacity:0;transform:none")]))
        css.append(loop(cls, 8, d0, "transform-box:fill-box;transform-origin:0 50%;"))
        last = ya + bh
        y = ya + bh + gap_group + (9 if n else 7)
    if strip_y is None:
        strip_y = last + 26
    K.assert_within(last + 10, strip_y, "P2 bars vs strip")
    o.append(rule(w, strip_y))
    size = 28 if n else 24
    ys = (strip_y + 36, strip_y + 72) if n else (strip_y + 32, strip_y + 64)
    for (val, ctx), yy in zip((("~5×", "faster first token"), ("~90%", "fewer prompt tokens")), ys):
        svg, wd = num(16, yy, val, AG, size, (0, w - 16))
        o.append(svg + T.put(16 + wd + 9, yy, ctx, "lb", box=(0, w - 16)))
    return "".join(o), "".join(css), ys[1] + (20 if n else 14)


# ---------------------------------------------------------------- panel 3: SOP -> AOP
def p3_dsl(T, w, d0):
    """Panel 3: an SOP sheet, a DSL bracket and an agent canvas whose flow re-routes; the locked core never moves."""
    n = T.n
    o, css = [head(T, w, "ENEGMA · DSL", "SOP → AOP", AG)], []
    k = 1.3 if n else 1.0
    if not n:
        px, py, pw, ph, bx, ccx, ccy, ca, lab_y, core, strip_y = 16, 90, 52, 68, 78, 178, 124, 58, 78, (180, 222, 24), 252
    else:
        px, py, pw, ph, bx, ccx, ccy, ca, lab_y, core, strip_y = 16, 100, 70, 92, 100, 262, 144, 82, 86, (262, 258, 28), 300
    mid = py + ph / 2
    # SOP sheet with numbered steps; step 2 is the edited one (violet line, flashes at the loop start)
    o.append(page(px, py, pw, ph, 10 * k))
    step_ys = [py + ph * f for f in (.34, .58, .82)]
    o.append(rules(px + pw * .38, [step_ys[0] - 3.5 * k, step_ys[2] - 3.5 * k], [pw * .48, pw * .36], .3, 1.8 * k))
    s2 = step_ys[1] - 3.5 * k
    o.append(f'<path d="M{F(px + pw * .38)},{F(s2)}h{F(pw * .44)}" stroke="{K.mix(AG, K.INK, .1)}" '
             f'stroke-width="{F(2.2 * k)}" stroke-linecap="round"/>')
    o.extend(f'<text x="{F(px + pw * .14)}" y="{F(y)}" class="mo" fill="{K.INK}" fill-opacity=".72">{i + 1}</text>'
             for i, y in enumerate(step_ys))
    o.append(f'<rect class="a3s" x="{F(px + 4)}" y="{F(s2 - 7 * k)}" width="{F(pw - 8)}" height="{F(13 * k)}" rx="3" '
             f'fill="{AG}" fill-opacity=".35"/>')
    css.append(flash_kf("a3s", 0, 2, 8) + loop("a3s", 8, d0, "", "linear", hidden=True))
    o.append(T.put(px + pw / 2, lab_y, "SOP", "st", K.TEXT, "middle", (0, w)))
    # DSL bracket
    bw = 14 * k
    bt, bb, hx = py, py + ph, bx + bw / 2
    o.append(f'<path d="M{F(bx)},{F(bt)}Q{F(hx)},{F(bt)} {F(hx)},{F(bt + 8)}V{F(mid - 8)}Q{F(hx)},{F(mid)} {F(bx + bw)},'
             f'{F(mid)}Q{F(hx)},{F(mid)} {F(hx)},{F(mid + 8)}V{F(bb - 8)}Q{F(hx)},{F(bb)} {F(bx)},{F(bb)}" fill="none" '
             f'stroke="{K.tech_tint(AG)}" stroke-width="1.6" stroke-linecap="round"/>')
    o.append(T.put(hx, lab_y, "DSL", "st", K.tech_tint(AG), "middle", (0, w)))
    # agent canvas: violet glass plate holding a 4-node flow with one branch
    I = K.Iso(ccx, ccy, ca)
    o.append(arrow(bx + bw + 4, mid, ccx - ca - 3, mid, AG, .6))
    o.append(K.slab(I, 12, AG))
    A, B, C, D = I.p(.16, .84), I.p(.44, .56), I.p(.8, .42), I.p(.66, .86)
    lite = K.link_tint(AG)
    o.append(f'<path d="M{K.pts([A])}L{K.pts([B])}L{K.pts([C])}" fill="none" stroke="{lite}" stroke-width="1.4" '
             f'stroke-opacity=".9"/>')
    o.append(f'<path class="a3n" d="M{K.pts([B])}L{K.pts([D])}" fill="none" stroke="{lite}" stroke-width="1.4"/>')
    o.append(f'<path class="a3o" d="M{K.pts([C])}L{K.pts([D])}" fill="none" stroke="{lite}" stroke-width="1.4" '
             f'stroke-dasharray="3 3"/>')
    o.extend(node(x, y, 7 * k) for x, y in sorted([A, B, C, D], key=lambda p: p[1]))
    css.append(kf("ka3o", [(0, "opacity:1"), (10, "opacity:1"), (24, "opacity:0"), (92, "opacity:0"), (100, "opacity:1")]))
    css.append(f".a3o{{opacity:0;animation:ka3o 8s ease-in-out {F(d0)}s infinite backwards}}")
    css.append(kf("ka3n", [(0, "opacity:0"), (10, "opacity:0"), (24, "opacity:1"), (92, "opacity:1"), (100, "opacity:0")]))
    css.append(loop("a3n", 8, d0))
    o.append(T.put(ccx, lab_y, "agent canvas", "st", K.name_tint(AG), "middle", (0, w - 12)))
    tw_ = K.tech_width("AOP flow", n)
    ax, ay = ccx - tw_ / 2, ccy + ca / 2 + 12 * k + (9 if not n else 13)
    o.append(K.tech(ax, ay, "AOP flow", AG, n)[0])
    K.assert_within(ax + tw_, w - 16, "AOP flow")
    # core code: matte rose box with a padlock, never animated
    cx2, cy2, ca2 = core
    J = K.Iso(cx2, cy2, ca2)
    K.assert_within(ay + 8, cy2 - ca2 * .4 - 70 * ca2 / 100, "AOP flow vs core box")
    o.append(f'<ellipse cx="{F(cx2)}" cy="{F(cy2 + ca2 * .5)}" rx="{F(ca2 * 1.1)}" ry="{F(ca2 * .3)}" fill="#000" '
             f'fill-opacity=".45" filter="url(#k-blur)"/>')
    o.append(J.box(.1, .1, .8, .8, 70, SV))
    lx, ly = J.p(.5, .9, 35)
    o.append(padlock(lx - ca2 * .38, ly + ca2 * .02, k * 1.05))
    right = cx2 - ca2 - 12
    o.append(T.put(right, cy2 - 2, "core code", "st", K.name_tint(SV), "end", (16, w)))
    tw_ = K.tech_width("untouched", n)
    K.assert_within(16, right - tw_, "untouched")
    o.append(K.tech(right - tw_, cy2 + (14 if not n else 18) - (11.5 if not n else 13) * .36 + 2, "untouched", SV, n)[0])
    # punchline: context above the numeral
    o.append(rule(w, strip_y))
    o.append(T.put(16, strip_y + (24 if not n else 28), "iteration time cut", "ctx", box=(0, w - 16)))
    o.append(num(16, strip_y + (56 if not n else 64), "~60%", AG, 28 if n else 26, (0, w - 16))[0])
    return "".join(o), "".join(css), strip_y + (78 if not n else 84)


# ---------------------------------------------------------------- panel 4: CodexMap + Venmo
STUBS = [(0, 30), (6, 38), (6, 22), (12, 30), (6, 34), (0, 18), (6, 40), (0, 26)]
TILES = [(-46, -54, 34, 24, [(0, 16), (4, 20), (0, 12)]), (14, -48, 34, 24, [(0, 20), (4, 14), (0, 18)]),
         (-22, -22, 34, 20, [(0, 18), (4, 12)])]


def codexmap_glyphs(xs, ys, gy_list, d0):
    """The five CodexMap stations at centres (xs[i], ys[i]) on ground lines gy_list[i]; cluster flashes at 30/34/38% of 10 s."""
    o = []
    # 1 codebase: neutral code lines on an ink tile (64 x 52)
    x, y = xs[0], ys[0]
    o.append(contact(x, gy_list[0] + 1, 36, .4) +
             f'<rect x="{F(x - 32)}" y="{F(y - 22)}" width="64" height="48" rx="4" fill="{K.mix(K.INK, K.WHITE, .07)}" '
             f'stroke="#FFFFFF" stroke-opacity=".22"/>' + code_lines(x - 24, y - 15, 4.8, STUBS))
    # 2 AST parsing: 1-2-4 tree (about 48 x 46)
    x, y = xs[1], ys[1]
    o.append(contact(x, gy_list[1] + 1, 30, .35) + tree(x, y - 20, 16, 8, 19))
    # 3 semantic embeddings: point cloud (72 x 44)
    x, y = xs[2], ys[2]
    o.append(contact(x, gy_list[2] + 1, 36, .3) + scatter(x, y, 72, 44, 11))
    # 4 reasoning agents: three linked orbs
    x, y = xs[3], ys[3]
    g = gy_list[3]
    ob = [(x - 19, g - 2, 6.5), (x + 3, g - 22, 7.5), (x + 21, g, 6.5)]
    oc = [(px, py - 1.6 * r) for px, py, r in ob]
    o.append(f'<path d="M{K.pts([oc[0]])}L{K.pts([oc[1]])}L{K.pts([oc[2]])}Z" fill="none" stroke="{K.link_tint(AG)}" '
             f'stroke-opacity=".75"/>' + "".join(orb(px, py, r) for px, py, r in ob))
    # 5 service maps, call graphs: the stubs regrouped into 3 rose clusters joined by call edges
    x, y = xs[4], ys[4]
    o.append(contact(x, gy_list[4] + 1, 44, .35))
    sl = K.link_tint(SV)
    bx, by = x, gy_list[4]
    o.append(arrow(bx - 12, by - 42, bx + 12, by - 38, sl, .8, 1.2, 3.4) + arrow(bx - 30, by - 30, bx - 18, by - 22, sl, .8, 1.2, 3.4) +
             arrow(bx + 26, by - 24, bx + 14, by - 16, sl, .8, 1.2, 3.4))
    for i, (dx, dy, tw2, th2, st) in enumerate(TILES):
        tx, ty = bx + dx, by + dy
        o.append(service_tile(tx, ty, tw2, th2, st))
        o.append(f'<rect class="a4c" x="{F(tx - 1.5)}" y="{F(ty - 1.5)}" width="{F(tw2 + 3)}" height="{F(th2 + 3)}" rx="4" '
                 f'fill="{SV}" fill-opacity=".22" stroke="{K.rim_tint(SV)}" stroke-width="1.6"{K.delay(d0 + 3 + .4 * i)}/>')
    return "".join(o)


def p4_codexmap(T, w, d0):
    """Panel 4: CodexMap chain codebase -> AST -> embeddings -> agents -> service maps; Venmo row beneath; three results."""
    n = T.n
    o, css = [head(T, w, "PAYPAL · CODEXMAP", "Agents that read code", RE)], []
    labels = [("codebase", K.TEXT2), ("AST parsing", K.name_tint(RE)), ("semantic embeddings", K.name_tint(RE)),
              ("reasoning agents", K.name_tint(AG)), ("service maps, call graphs", K.name_tint(SV))]
    hues = [RE, RE, RE, AG]
    css.append(flash_kf("a4c", 30, 32, 38) + f".a4c{{opacity:0;animation:ka4c 10s linear infinite}}")
    css.append(dash_kf("a4d", 0, 7.5, 14) + f".a4d{{opacity:0;stroke-dasharray:14 86;animation:ka4d 10s linear infinite}}")
    if not n:
        gy = 108
        o.append(plinth(16, gy - 4, w - 32, 6, 10, 7))
        xs = [96, 252, 410, 566, 708]
        ys = [78, 80, 80, 80, 80]
        o.append(codexmap_glyphs(xs, ys, [gy] * 5, d0))
        segs = [(xs[0] + 38, xs[1] - 30), (xs[1] + 30, xs[2] - 40), (xs[2] + 40, xs[3] - 34), (xs[3] + 32, xs[4] - 52)]
        for i, ((a, b), hue) in enumerate(zip(segs, hues)):
            o.append(arrow(a, 80, b, 80, hue, .6) +
                     f'<path class="a4d" d="M{F(a)},80H{F(b - 3)}" pathLength="100" stroke="{K.tech_tint(hue)}" '
                     f'stroke-width="2.6" stroke-linecap="round"{K.delay(d0 + .75 * i)}/>')
        prev_r = 0
        for x, (s, col) in zip(xs, labels):
            wd = T.width(s, "st")
            K.assert_within(prev_r + 10, x - wd / 2, f"station label {s} spacing")
            prev_r = x + wd / 2
            o.append(T.put(x, gy + 28, s, "st", col, "middle", (16, w - 16)))
        # row B: Venmo decomposition (no arrow joins rows A and B)
        o.append(rule(w, 150))
        yb = 178
        o.append(T.put(16, yb - 1, "VENMO DECOMPOSITION", "tg"))
        x = 16 + T.width("VENMO DECOMPOSITION", "tg") + 28
        s1 = "9-month manual process"
        w1 = T.width(s1, "lb")
        o.append(T.put(x, yb, s1, "lb", K.MUTED) +
                 f'<path d="M{F(x - 2)},{F(yb - 4)}H{F(x + w1 + 2)}" stroke="{K.MUTED}" stroke-width="1.3"/>')
        x += w1 + 14
        o.append(arrow(x, yb - 4, x + 26, yb - 4, K.MUTED, .7))
        x += 40
        o.append(orb(x + 5, yb + 4, 5))
        x += 16
        o.append(T.put(x, yb, "agentic workflow", "st", K.tech_tint(AG)))
        x += T.width("agentic workflow", "st") + 14
        o.append(arrow(x, yb - 4, x + 26, yb - 4, AG, .6))
        x += 38
        o.append(T.put(x, yb, "migration ~30% faster", "st", IVORY, box=(0, w - 16)))
        o.append(rule(w, 198))
        cells = [("~60%", "architectural analysis cut", RE), ("~70%", "dependency discovery cut", RE),
                 ("~30% faster", "Venmo migration", SV)]
        cw = (w - 32) / 3
        for i, (val, ctx, hue) in enumerate(cells):
            cx0 = 16 + i * cw + (16 if i else 0)
            o.append(num(cx0, 234, val, hue, 26, (cx0, cx0 + cw - 16))[0] + T.put(cx0, 256, ctx, "ctx", box=(cx0, cx0 + cw - 16)))
            if i:
                o.append(K.hairline(16 + i * cw, 212, 16 + i * cw, 262, .12))
        H = 280
    else:
        # vertical chain: glyph column at x 64, labels to the right; extents (top, bottom, ground) per station
        gx, lx = 64, 124
        ext = [(-22, 26, 27), (-24, 21, 22), (-22, 22, 24), (-23, 22, 20), (-30, 26, 26)]
        cys, y = [], 70
        for top, bot, _ in ext:
            cys.append(y - top)
            y = y - top + bot + 20
        gys = [c + g for c, (_, _, g) in zip(cys, ext)]
        o.append(codexmap_glyphs([gx] * 5, cys, gys, d0))
        for i in range(4):
            a, b, hue = cys[i] + ext[i][1] + 4, cys[i + 1] + ext[i + 1][0] - 3, hues[i]
            o.append(arrow(gx, a, gx, b, hue, .6) +
                     f'<path class="a4d" d="M{gx},{F(a)}V{F(b - 3)}" pathLength="100" stroke="{K.tech_tint(hue)}" '
                     f'stroke-width="2.6" stroke-linecap="round"{K.delay(d0 + .75 * i)}/>')
        for cy, (s_, col) in zip(cys, labels):
            o.append(T.put(lx, cy + 5, s_, "st", col, box=(0, w - 16)))
        yr = cys[4] + ext[4][1] + 18
        o.append(rule(w, yr))
        yb = yr + 26
        o.append(T.put(16, yb, "VENMO DECOMPOSITION", "tg", box=(0, w - 16)))
        y1, y2, y3 = yb + 28, yb + 56, yb + 84
        s1 = "9-month manual process"
        w1 = T.width(s1, "lb")
        o.append(T.put(40, y1, s1, "lb", K.MUTED, box=(0, w - 16)) +
                 f'<path d="M38,{F(y1 - 4.5)}H{F(40 + w1 + 2)}" stroke="{K.MUTED}" stroke-width="1.3"/>')
        o.append(arrow(24, y1 - 4, 24, y2 - 14, K.MUTED, .7))
        o.append(orb(24, y2 + 5, 5.5) + T.put(40, y2, "agentic workflow", "st", K.tech_tint(AG), box=(0, w - 16)))
        o.append(arrow(24, y2 + 8, 24, y3 - 10, AG, .6))
        o.append(T.put(40, y3, "migration ~30% faster", "st", IVORY, box=(0, w - 16)))
        y2 = y3
        yr2 = y2 + 20
        o.append(rule(w, yr2))
        cells = [("~60%", "architectural analysis cut", RE), ("~70%", "dependency discovery cut", RE),
                 ("~30% faster", "Venmo migration", SV)]
        y = yr2 + 40
        for val, ctx, hue in cells:
            svg, wd = num(16, y, val, hue, 28, (0, w - 16))
            o.append(svg + T.put(16 + wd + 10, y, ctx, "ctx", box=(0, w - 16)))
            y += 42
        H = y - 42 + 24
    return "".join(o), "".join(css), H


# ---------------------------------------------------------------- panel 5: document -> computable model
def ripple(sx, sy, ex, ey, c1):
    """One azure change-propagation curve (dashed, still) plus a travelling ring along it (transient)."""
    path = f"M{F(sx)},{F(sy)}Q{F(c1[0])},{F(c1[1])} {F(ex)},{F(ey)}"
    return (f'<path d="{path}" fill="none" stroke="{TR}" stroke-opacity=".8" stroke-width="1.4" stroke-dasharray="2 4" '
            f'stroke-linecap="round"/>' + K.chevron(ex, ey, math.atan2(ey - c1[1], ex - c1[0]), TR, .95, 4, 1.4) +
            f'<path class="a5r" d="{path}" pathLength="100" fill="none" stroke="{K.rim_tint(TR)}" stroke-width="7" '
            f'stroke-linecap="round"/><path class="a5r" d="{path}" pathLength="100" fill="none" stroke="{K.INK}" '
            f'stroke-width="3.4" stroke-linecap="round"/>')


def gate_block(gx, gy, s, lab):
    """Human approval: azure gate with its figure, a check badge (flashes once per loop) and its label."""
    bx, by = gx + 4 * s, gy - 55 * s
    return (K.gate(gx, gy, s) + check_badge(bx, by, 8 * s) +
            f'<circle class="a5k" cx="{F(bx)}" cy="{F(by)}" r="{F(13 * s)}" fill="none" stroke="{K.rim_tint(TR)}" '
            f'stroke-width="2" filter="url(#k-glow)"/>' + lab)


def p5_model(T, w, d0):
    """Panel 5: spec PDF -> computable model -> drafting agents -> artifacts -> human gate -> live; Q&A; amendment ripple."""
    n = T.n
    o, css = [head(T, w, "SIDE PROJECT · PATTERN", "Document → computable model", AG)], []
    css.append(flash_kf("a5k", 36, 38, 42) + loop("a5k", 12, d0, "", "linear", True))
    css.append(kf("ka5a", [(0, f"opacity:0;transform:translateX({18 if n else -18}px)"), (8, "opacity:1;transform:none"),
                           (94, "opacity:1;transform:none"), (100, "opacity:0;transform:none")]) +
               loop("a5a", 12, d0, "", "cubic-bezier(.2,.8,.2,1)"))
    css.append(flash_kf("a5p", 8, 10, 14) + loop("a5p", 12, d0, "", "linear", True))
    css.append(dash_kf("a5r", 16, 34, 0) + f".a5r{{opacity:0;stroke-dasharray:0 100;animation:ka5r 12s linear {F(d0)}s infinite}}")
    arts = ["forms", "specs", "mappings"]
    if not n:
        gy = 124
        o.append(plinth(16, gy - 4, w - 32, 6, 10, 7))
        lab_y = gy + 28
        px, py, pw, ph = 42, 60, 48, 62
        o.append(spec_pdf(px, py, pw, ph, 13))
        o.append(T.put(px + pw / 2, lab_y, "long spec PDF", "st", K.TEXT, "middle", (16, w)))
        mx = 196
        o.append(contact(mx, gy + 2, 40, .35) + grid_model(mx, gy - 22, 34))
        o.append(T.put(mx, lab_y, "computable model", "st", K.name_tint(DA), "middle", (16, w)))
        o.append(arrow(px + pw + 10, 96, mx - 46, 96, K.TEXT2, .5))
        ax = [298, 322, 346]
        o.append("".join(orb(x, gy - 2) for x in ax))
        o.append(arrow(mx + 46, 96, ax[0] - 14, 96, DA, .6))
        o.append(T.put(ax[1], lab_y, "drafting agents", "st", K.name_tint(AG), "middle", (16, w)))
        axs, pw2, ph2 = [404, 456, 508], 30, 38
        o.append(arrow(ax[2] + 14, 96, axs[0] - pw2 / 2 - 8, 96, AG, .6))
        prev_r = 0
        for kind, (name, cx) in enumerate(zip(arts, axs)):
            o.append(artifact(cx, gy - ph2 - 2, kind, pw2, ph2))
            wd = T.width(name, "lb")
            K.assert_within(prev_r + 6, cx - wd / 2, f"artifact label {name}")
            prev_r = cx + wd / 2
            o.append(T.put(cx, gy - ph2 - 10, name, "lb", K.TEXT, "middle", (16, w)))
        gx = 612
        o.append(arrow(axs[2] + pw2 / 2 + 10, 96, gx - 34, 96, K.TEXT2, .5))
        o.append(gate_block(gx, gy + 2, 1.0, T.put(gx + 2, lab_y, "human approval", "st", K.name_tint(TR), "middle", (16, w))))
        lx = 726
        o.append(arrow(gx + 36, 96, lx - 30, 96, TR, .6))
        o.append(K.check_tile(lx, gy - 8, .62))
        o.append(T.put(lx, lab_y, "live", "st", K.name_tint(TR), "middle", (16, w - 16)))
        # Q&A under the PDF
        qy = 178
        qs = "ask the document"
        qw = T.width(qs, "lb") + 22
        o.append(bubble(16, qy, qw, 22, px + pw / 2, "up") + T.put(27, qy + 15, qs, "lb", K.TEXT))
        o.append(f'<path d="M30,{qy + 24}V{qy + 41}H40" fill="none" stroke="{K.TEXT2}" stroke-opacity=".5" '
                 f'stroke-dasharray="1.5 3"/>')
        o.append(K.bookmark(47, qy + 47, 1.0) + T.put(57, qy + 45, "cites its section", "t", K.tech_tint(TR), box=(16, 180)))
        # amendment lane
        ay, amx, amw, amh = 178, 200, 34, 44
        o.append(f'<g class="a5a">{amendment_page(amx, ay, amw, amh)}</g>')
        o.append(f'<rect class="a5p" x="{F(amx - amw / 2 + 1)}" y="{F(ay + amh * .39 - 3)}" width="{F(amw - 2)}" '
                 f'height="{F(amh * .16 + 6)}" rx="3" fill="none" stroke="{K.rim_tint(TR)}" stroke-width="2" '
                 f'filter="url(#k-glow)"/>')
        o.append(T.put(amx, ay + amh + 18, "amendment", "st", K.name_tint(TR), "middle", (16, w)))
        dx_ = 302
        o.append(arrow(amx + amw / 2 + 10, ay + 22, dx_ - 30, ay + 22, TR, .55))
        o.append(diff_glyph(dx_, ay + amh))
        o.append(T.put(dx_, ay + amh + 18, "detect changes", "st", K.name_tint(DA), "middle", (16, w)))
        sx, sy = dx_ + 26, ay + 14
        for i, cx in enumerate(axs):
            ex, ey = cx, gy + 16
            o.append(ripple(sx, sy, ex, ey, (sx + (ex - sx) * .55, sy + 4)))
        o.append(T.put(axs[2] + 20, gy + 56, "re-draft → re-approve", "t", K.tech_tint(TR), box=(16, w - 16)))
        sy2 = 248
        o.append(rule(w, sy2))
        o.append(T.put(16, sy2 + 34, "AI drafts. Humans approve.", "pq", box=(16, w - 16)))
        H = 300
    else:
        col, lx = 46, 92            # main lane glyph column and label column
        # row 1: spec PDF, its label, and the Q&A beside it
        px, py, pw, ph = 16, 68, 60, 76
        o.append(spec_pdf(px, py, pw, ph, 15))
        o.append(T.put(lx, 86, "long spec PDF", "st", K.TEXT, box=(0, w - 16)))
        qs = "ask the document"
        qw = T.width(qs, "lb") + 26
        o.append(bubble(lx + 8, 102, qw, 26, 115, "left") + T.put(lx + 21, 119.5, qs, "lb", K.TEXT, box=(0, w - 16)))
        o.append(f'<path d="M{lx + 22},130V145H{lx + 30}" fill="none" stroke="{K.TEXT2}" stroke-opacity=".5" '
                 f'stroke-dasharray="1.5 3"/>')
        o.append(K.bookmark(lx + 38, 153, 1.1) + T.put(lx + 49, 150, "cites its section", "t", K.tech_tint(TR), box=(0, w - 16)))
        o.append(arrow(col, py + ph + 8, col, 170, K.TEXT2, .5))
        # row 2: computable model -> drafting agents
        ry = 206
        o.append(contact(col, ry + 16, 34, .35) + grid_model(col, ry - 4, 30))
        o.append(T.put(lx, ry - 10, "computable model", "st", K.name_tint(DA), box=(0, w - 16)))
        ax = [256, 280, 304]
        o.append(arrow(col + 36, ry + 2, ax[0] - 16, ry + 2, DA, .6))
        o.append("".join(orb(x, ry + 14) for x in ax))
        o.append(T.put(ax[1], ry - 22, "drafting agents", "st", K.name_tint(AG), "middle", (0, w - 16)))
        # row 3: artifacts -> human gate -> live on a plinth
        gy = 322
        o.append(plinth(10, gy - 4, w - 20, 6, 10, 7))
        axs, pw2, ph2 = [30, 82, 140], 32, 40
        for i, cx in enumerate(axs):
            o.append(arrow(ax[1] - 8 + 8 * i, ry + 20, cx + 4, gy - ph2 - 8, AG, .55))
        prev_r = 0
        for kind, (name, cx) in enumerate(zip(arts, axs)):
            o.append(artifact(cx, gy - ph2 - 2, kind, pw2, ph2))
            wd = T.width(name, "lb")
            K.assert_within(prev_r + 6, cx - wd / 2, f"artifact label {name}")
            prev_r = cx + wd / 2
            o.append(T.put(cx, gy + 30, name, "lb", K.TEXT, "middle", (8, w)))
        gx = 238
        o.append(arrow(axs[2] + pw2 / 2 + 8, gy - 22, gx - 34, gy - 22, K.TEXT2, .5))
        o.append(gate_block(gx, gy + 2, 1.05, T.put(gx + 2, gy + 30, "human approval", "st", K.name_tint(TR), "middle",
                                                    (0, w - 8))))
        tx = 330
        o.append(arrow(gx + 34, gy - 22, tx - 26, gy - 22, TR, .6))
        o.append(K.check_tile(tx, gy - 10, .56))
        o.append(T.put(tx, gy + 30, "live", "st", K.name_tint(TR), "middle", (0, w - 16)))
        # row 4: amendment (right) -> detect changes -> ripple up-left to the three artifacts
        ay, amw, amh = gy + 66, 38, 48
        amx, dx_ = 314, 210
        o.append(f'<g class="a5a">{amendment_page(amx, ay, amw, amh)}</g>')
        o.append(f'<rect class="a5p" x="{F(amx - amw / 2 + 1)}" y="{F(ay + amh * .39 - 3)}" width="{F(amw - 2)}" '
                 f'height="{F(amh * .16 + 6)}" rx="3" fill="none" stroke="{K.rim_tint(TR)}" stroke-width="2" '
                 f'filter="url(#k-glow)"/>')
        o.append(T.put(amx, ay + amh + 22, "amendment", "st", K.name_tint(TR), "middle", (0, w - 16)))
        o.append(arrow(amx - amw / 2 - 8, ay + 24, dx_ + 26, ay + 24, TR, .55))
        o.append(diff_glyph(dx_, ay + amh, 1.15))
        o.append(T.put(dx_, ay + amh + 22, "detect changes", "st", K.name_tint(DA), "middle", (0, amx - 46)))
        sx, sy = dx_ - 26, ay + 16
        for i, cx in enumerate(axs):
            ex, ey = cx, gy + 40
            o.append(ripple(sx, sy, ex, ey, (ex + (sx - ex) * .3, sy + 2)))
        o.append(T.put(16, ay + amh + 22, "re-draft → re-approve", "t", K.tech_tint(TR), box=(0, dx_ - 48)))
        sy2 = ay + amh + 44
        o.append(rule(w, sy2))
        o.append(T.put(16, sy2 + 36, "AI drafts. Humans approve.", "pq", box=(0, w - 16)))
        H = sy2 + 56
    return "".join(o), "".join(css), H


# ---------------------------------------------------------------- board
def panel_group(x, y, svg, d):
    """A panel's build group (fade + rise 8px); the translate sits on an inner group so it never animates."""
    return f'<g class="pb"{K.delay(d)}><g transform="translate({F(x)},{F(y)})">{svg}</g></g>'


def css_common(T):
    """Build + scene text CSS shared by both variants."""
    return K.css_rise("pb", 8, .6) + T.css() + ".ar{fill:none;stroke-width:1.4px;stroke-linecap:round;stroke-linejoin:round}"


def build_wide():
    """850-wide board: three small panels in row 1, then CodexMap and the document-model pattern full width."""
    W, H = 850, 1030
    T = Txt(False)
    body = [K.card(W, H, "AGENTIC SYSTEMS · HOW THEY WORK", lit=LIT),
            K.glow(425, 230, 380, 190, K.VIOLET, .20), K.glow(150, 900, 260, 150, K.WARM, .16)]
    css = [css_common(T)]
    specs = [(p1_framework, 24, 64, 254, 330), (p2_microprompt, 298, 64, 254, 330), (p3_dsl, 572, 64, 254, 330),
             (p4_codexmap, 24, 410, 802, 280), (p5_model, 24, 706, 802, 300)]
    for i, (fn, x, y, w, h) in enumerate(specs):
        svg, c, used = fn(T, w, 1.4 + .25 * i)
        K.assert_within(used, h, f"panel {i + 1} content height")
        body.append(panel_group(x, y, panel_rect(w, h) + svg, .1 + .25 * i))
        css.append(c)
    K.assert_within(706 + 300, H - 24, "board bottom")
    return K.svg_doc(W, H, TITLE, DESC, orb_def(), "".join(css), "".join(body))


def build_narrow():
    """400-wide re-layout: the five panels stacked in reading order, flows turned top to bottom."""
    W, X, PW, GAP = 400, 14, 372, 14
    T = Txt(True)
    parts, css, y = [], [css_common(T)], 52
    for i, fn in enumerate((p1_framework, p2_microprompt, p3_dsl, p4_codexmap, p5_model)):
        svg, c, h = fn(T, PW, 1.4 + .25 * i)
        parts.append(panel_group(X, y, panel_rect(PW, h) + svg, .1 + .25 * i))
        css.append(c)
        y += h + GAP
    H = y - GAP + 16
    body = [K.card(W, H, "AGENTIC SYSTEMS", lit=LIT), K.glow(200, 260, 230, 200, K.VIOLET, .20),
            K.glow(120, H - 300, 220, 160, K.WARM, .16)] + parts
    return K.svg_doc(W, H, TITLE, DESC, orb_def(), "".join(css), "".join(body))


if __name__ == "__main__":
    K.write(os.path.join(ASSETS, "agents.svg"), build_wide())
    K.write(os.path.join(ASSETS, "agents-narrow.svg"), build_narrow())
    print(K.picture("agents", ALT))
