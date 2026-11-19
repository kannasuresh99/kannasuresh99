#!/usr/bin/env python3
"""Scene 3, 'How I build large-document pipelines': the centrepiece factory floor.

Writes assets/pipeline.svg (850 wide) and assets/pipeline-narrow.svg (400 wide) from the shared svgkit.
Python 3 stdlib only, deterministic (fixed seeds). Never hand-edit the SVGs; change this file and re-run.

Story: long PDFs enter the ingest path, which builds a shared knowledge layer (a content-hash cache
skips repeat work); the answer path searches it, re-ranks, lets the LLM extract (the only
probabilistic stage and the only glowing object), validates deterministically, passes a human gate
and writes cited, page-anchored output to an audit trail; an eval loop measures and tunes it.
Every stage stands on a mini glass slab in its layer hue, the same slabs the stack card teaches.

Bytes: the shared glyphs are redrawn here in a face-merged form (one path per face colour) and slabs
and tokens are defined once and reused with <use>, so each file stays under the 40 KB budget.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgkit as K  # noqa: E402

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
fmt = K.fmt

TITLE = "How I build large-document pipelines"
DESC = ("Large-document pipeline as an isometric factory floor: an ingest path with a cache-hit bypass builds a "
        "knowledge graph and vector layer; an answer path searches, re-ranks, extracts with the LLM, validates, "
        "passes a human gate and writes cited output to an audit trail; an eval loop tunes retrieval and the "
        "model. Extraction accuracy ~70% to ~90%.")
ALT = ("Large-document pipeline drawn as a factory floor in three lanes plus an eval loop, each stage tinted by "
       "its system layer. Ingest path: a stack of long PDFs goes to an ingest service (FastAPI), through a "
       "tenant-fair queue, to a content-hash cache, then OCR and chunking, then embedding and linking into a "
       "shared knowledge graph and vector layer; a dashed cache-hit arc drops from the cache straight into that "
       "layer, skipping OCR and embedding. Answer path: hybrid and graph search reads the knowledge layer, then "
       "re-ranking, then LLM extraction by agents with batch inference (a glowing orb, the only probabilistic "
       "stage), deterministic validation, a human review and approval gate, and cited, page-anchored output "
       "written to an audit trail whose rows read source page, extracted, validated and approved (21 CFR Part "
       "11). Eval loop: the output feeds a gold-set harness and an LLM-as-judge, dashed feedback lines tune "
       "retrieval and tune the model, and a gauge beside the large figure ~70% to ~90% shows extraction "
       "accuracy on the gold-set harness. Small document tokens travel the path and change form at each stage.")

INGEST = [  # id, layer key, stage name, sub-label (the queue is a technique on the connector)
    ("pdf", None, "long PDFs", None),
    ("ing", "SVC", "Ingest", "FastAPI service"),
    ("que", "MSG", "tenant-fair queue", None),
    ("cch", "DATA", "Content-hash cache", "seen? reuse it"),
    ("ocr", "RETR", "OCR + chunking", "long-document aware"),
    ("emb", "RETR", "Embed + link", "vectors · graph edges"),
]
ANSWER = [
    ("srch", "RETR", "Hybrid + graph search", "reads the graph"),
    ("rr", "RETR", "Re-rank", "best context first"),
    ("llm", "AGENT", "LLM extraction", "agents · batch inference"),
    ("val", "TRUST", "Deterministic validation", "rules · schemas"),
    ("gate", "TRUST", "Human gate", "review · approve"),
    ("out", "TRUST", "Cited output", "page-anchored answers"),
]
LEDGER_ROWS = ("source page", "extracted", "validated", "approved")
BAND_LABEL = "knowledge graph + vectors"
NUM_A, NUM_B = "~70%", "~90%"            # resume: 'from ~70% to ~90%'
NUM_CTX = "extraction accuracy · gold-set harness"

CYCLE, MASTER, LOOP0 = 12, 36, 4.0       # answer path every 12 s; ingest + cache hit on a 36 s master
EPS = .04                                # % used for instant opacity steps
LIT = ("DATA", "MSG", "SVC", "RETR", "AGENT", "TRUST")
SLABS = ("DATA", "SVC", "RETR", "AGENT", "TRUST")   # the queue has no slab
SIDE = K.mix(K.RESULT, K.INK, .35)       # paper sheet edge colour (the kit's sheet recipe)


# ---------------------------------------------------------------- small helpers
def pct(t, cycle):
    """Seconds into a cycle -> keyframe percent (clamped)."""
    return max(0.0, min(100.0, t / cycle * 100))


def pf(v):
    """Keyframe percent text (3 decimals)."""
    return fmt(v, 3)


def plen(ps):
    """Length of a polyline."""
    return sum(math.hypot(bx - ax, by - ay) for (ax, ay), (bx, by) in zip(ps, ps[1:]))


def bez(ps, n=48):
    """Sample a quadratic (3 points) or cubic (4 points) Bezier into a polyline."""
    def at(t):
        q = list(ps)
        while len(q) > 1:
            q = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(q, q[1:])]
        return q[0]
    return [at(i / n) for i in range(n + 1)]


def pd(ps, close=True):
    """Polygon/polyline as path data."""
    return "M" + "L".join(f"{fmt(x)},{fmt(y)}" for x, y in ps) + ("Z" if close else "")


def text(x, y, s, size, fill, weight=400, anchor=None, mono=False, extra=""):
    """A one-off text line outside the kit classes (mono caption, ledger rows)."""
    a = f' text-anchor="{anchor}"' if anchor else ""
    fam = f"font-family:{K.MONO};" if mono else ""
    return (f'<text x="{fmt(x)}" y="{fmt(y)}"{a} fill="{fill}" style="{fam}font-size:{fmt(size)}px;'
            f'font-weight:{weight}"{extra}>{K.esc(s)}</text>')


def stage_label(x, y, name, sub, hue, box, narrow=False, anchor="middle"):
    """Stage name (sentence case, hue + 28% white; ivory for documents) and sub-label wrapped in a measured box;
    returns (svg, last baseline)."""
    fill = K.RESULT if hue is None else K.name_tint(hue)
    lh_n, lh_s = (16, 16) if narrow else (14, 13.5)
    out, yy, last = [], y, y
    for ln in K.wrap(name, "st", box, narrow):
        out.append(K.txt(x, yy, ln, "st", fill, anchor=anchor))
        last, yy = yy, yy + lh_n
    for ln in (K.wrap(sub, "sb", box, narrow) if sub else []):
        out.append(K.txt(x, yy, ln, "sb", anchor=anchor))
        last, yy = yy, yy + lh_s
    return "".join(out), last


def check_mark(x, y, s, w=1.6, col="#FFFFFF"):
    """Check stroke centred on (x, y), s = half-width."""
    return (f'<path d="M{fmt(x - s)},{fmt(y)}L{fmt(x - s * .3)},{fmt(y + s * .65)}L{fmt(x + s)},{fmt(y - s * .7)}" '
            f'fill="none" stroke="{col}" stroke-width="{fmt(w)}" stroke-linecap="round" stroke-linejoin="round"/>')


# ---------------------------------------------------------------- face-merged glyphs
class Faces:
    """Accumulates iso box faces by colour so a glyph emits one path per face colour."""

    def __init__(self):
        self.d = {}

    def add(self, key, ps):
        self.d.setdefault(key, []).append(pd(ps))

    def box(self, I, u, v, du, dv, h, hue, z=0, top=None):
        """An iso block in the micro-object recipe (top = hue + 38% white, left = hue, right = hue 50% into ink)."""
        P = lambda uu, vv, hh=0: I.p(uu, vv, hh + z)
        self.add(("f", hue), [P(u, v + dv), P(u + du, v + dv), P(u + du, v + dv, h), P(u, v + dv, h)])
        self.add(("f", K.mix(hue, K.INK, .5)), [P(u + du, v), P(u + du, v + dv), P(u + du, v + dv, h), P(u + du, v, h)])
        self.add(top or ("f", K.mix(hue, K.WHITE, .38)), [P(u, v, h), P(u + du, v, h), P(u + du, v + dv, h), P(u, v + dv, h)])

    def svg(self):
        out = []
        for (kind, val), ds in self.d.items():
            attrs = f'fill="{val}"' if kind == "f" else f'fill="{K.RESULT}" fill-opacity=".88"'
            out.append(f'<path d="{"".join(ds)}" {attrs}/>')
        return "".join(out)


def paper(F, I, z, h, lines, rules, mark=None):
    """One sheet (or a block of stacked sheets of height h) on frame I: ivory top, shaded edges, ruled top."""
    u0, v0, du, dv = .34, .30, .32, .40
    F.box(I, u0, v0, du, dv, h, SIDE, z, top=("p", 0))
    for k in range(1, lines + 1):
        v = v0 + dv * k / (lines + 1)
        u1 = u0 + du - (.12 if k == lines else .06)
        (x1, y1), (x2, y2) = I.p(u0 + .05, v, z + h), I.p(u1, v, z + h)
        rules.append((k - 1 == mark, f"M{fmt(x1)},{fmt(y1)}L{fmt(x2)},{fmt(y2)}"))


def rules_svg(rules, s):
    """Rule lines of the sheets (ink 28%), a marked line lit."""
    plain = "".join(d for m, d in rules if not m)
    lit = "".join(d for m, d in rules if m)
    o = (f'<path d="{plain}" stroke="{K.INK}" stroke-opacity=".28" stroke-width="{fmt(max(.8, 1.2 * s), 2)}"/>'
         if plain else "")
    return o + (f'<path d="{lit}" stroke="{K.RETR}" stroke-width="{fmt(max(1.6, 3 * s), 2)}" '
                f'stroke-linecap="round"/>' if lit else "")


def g_sheet(x, y, s, lines=3, tab=None, bookmark=False, mark=None):
    """Document sheet (ivory top, rule lines); tab = edge tab hue; bookmark pins an azure citation."""
    I, F, R = K.Iso(x, y, 100 * s), Faces(), []
    paper(F, I, 0, 1.6, lines, R, mark)
    o = F.svg() + rules_svg(R, s)
    if tab:
        o += I.flat([(.66, .34), (.72, .34), (.72, .44), (.66, .44)], h=1.6, fill=tab)
    if bookmark:
        o += K.bookmark(*I.p(.6, .33, 1.6), s=s)
    return o


def g_stack(x, y, s, n=6, gap=2):
    """Large PDF set: one block of n sheets with page edges drawn along the front faces, ruled top sheet."""
    I, F, R = K.Iso(x, y, 100 * s), Faces(), []
    paper(F, I, 0, n * gap / I.s, 3, R)
    u0, v0, du, dv = .34, .30, .32, .40
    edges = "".join(pd([I.p(u0, v0 + dv, k * gap / I.s), I.p(u0 + du, v0 + dv, k * gap / I.s),
                        I.p(u0 + du, v0, k * gap / I.s)], close=False) for k in range(1, n))
    return (F.svg() + f'<path d="{edges}" fill="none" stroke="{K.RESULT}" stroke-opacity=".6" stroke-width=".8"/>' +
            rules_svg(R, s))


def g_chunks(x, y, s, n=3, step=(7, 6)):
    """Chunk sheets with orchid tabs, fanned along a diagonal."""
    F, R, tabs = Faces(), [], []
    for i in range(n):
        I = K.Iso(x + step[0] * i * s, y + step[1] * i * s - 9 * s, 55 * s)
        paper(F, I, 0, 1.6, 2, R)
        tabs.append(pd([I.p(u, v, 1.6) for u, v in ((.66, .34), (.72, .34), (.72, .44), (.66, .44))]))
    return F.svg() + rules_svg(R, .55 * s) + f'<path d="{"".join(tabs)}" fill="{K.RETR}"/>'


def g_lanes(x, y, s, n=3, hue=K.MSG):
    """MSG sharded lanes carrying small message tiles (the kit's lanes, face-merged)."""
    I, F = K.Iso(x, y, 100 * s), Faces()
    strips = []
    for i in range(n):
        v = .5 - .045 + (i - (n - 1) / 2) * .16
        strips.append(pd([I.p(u, vv) for u, vv in ((.12, v), (.88, v), (.88, v + .09), (.12, v + .09))]))
        for u in (.26, .46, .66):
            F.box(I, u - .10 * (i % 2), v + .015, .09, .06, 6, hue)
    return (f'<path d="{"".join(strips)}" fill="{hue}" fill-opacity=".22" stroke="{hue}" stroke-opacity=".55"/>' +
            F.svg())


def scatter(seed, n=16):
    """The kit's vector scatter points in uv (same seeded draw as svgkit.vectors)."""
    rnd = random.Random(seed)
    kept = []
    for _ in range(n):
        u, v = rnd.uniform(.08, .83), rnd.uniform(.34, .70)
        if u + v >= .70:
            kept.append((u, v))
    return kept


def dots(points, r, fill, op=1):
    """Round dots as zero-length round-capped segments in one path."""
    d = "".join(f"M{fmt(x)},{fmt(y)}h0" for x, y in points)
    o = f' stroke-opacity="{fmt(op, 2)}"' if op < 1 else ""
    return f'<path d="{d}" stroke="{fill}"{o} stroke-width="{fmt(2 * r)}" stroke-linecap="round"/>'


def g_vectors(x, y, s, seed, link=False, hue=K.RETR):
    """RETR vector scatter, optional 3-node link (svgkit.vectors geometry, compact)."""
    I = K.Iso(x, y, 100 * s)
    kept = scatter(seed)
    o = dots([I.p(u, v) for u, v in kept], max(1.2, 1.7 * s), K.link_tint(hue), .75)
    if link and len(kept) >= 3:
        tri = [I.p(*kept[0]), I.p(*kept[len(kept) // 2]), I.p(*kept[-1])]
        o += (f'<path d="{pd(tri, False)}" fill="none" stroke="{K.tech_tint(hue)}" stroke-opacity=".85"/>' +
              dots(tri, max(1.6, 2.4 * s), K.tech_tint(hue)))
    return o


def g_lens(x, y, s, seed, hue=K.RETR):
    """RETR lens ring with handle over the vector scatter, three picked points lit white (svgkit.lens, compact)."""
    I = K.Iso(x, y, 100 * s)
    lite = K.link_tint(hue)
    hx, hy = I.p(.5, .5)
    picks = [I.p(.5 + du, .5 + dv) for du, dv in ((-.05, .02), (.04, -.03), (.03, .05))]
    return (g_vectors(x, y, s, seed, hue=hue) +
            f'<ellipse cx="{fmt(hx)}" cy="{fmt(hy)}" rx="{fmt(20 * s)}" ry="{fmt(10 * s)}" fill="{hue}" '
            f'fill-opacity=".18" stroke="{lite}" stroke-width="1.2"/>'
            f'<path d="M{fmt(hx + 15 * s)},{fmt(hy + 7 * s)}L{fmt(hx + 27 * s)},{fmt(hy + 15 * s)}" stroke="{lite}" '
            f'stroke-width="{fmt(max(1.5, 3 * s))}" stroke-linecap="round"/>' + dots(picks, max(1.2, 2.3 * s), "#FFFFFF"))


def g_rerank(x, y, a):
    """RETR re-rank: three orchid iso bars of descending length."""
    I, F = K.Iso(x, y, a), Faces()
    for i, L in enumerate((.74, .52, .30)):
        F.box(I, .13, .16 + .25 * i, L, .14, 13, K.RETR)
    return F.svg()


def g_ocr(x, y, s):
    """OCR + chunking: a sheet fanning into three chunk sheets with orchid tabs."""
    return g_sheet(x - 9 * s, y + 2 * s, .52 * s) + g_chunks(x + 6 * s, y, .62 * s)


def g_validate(x, y, s):
    """Deterministic validation: a ruled schema sheet behind an azure check tile."""
    return g_sheet(x - 8 * s, y - 3 * s, .46 * s) + K.check_tile(x + 7 * s, y + 4 * s, .42 * s)


def g_goldset(x, y, s):
    """Gold-set harness: a small ivory sheet set with a mint check badge."""
    return (g_stack(x, y, .36 * s, n=3, gap=2 * s) +
            f'<circle cx="{fmt(x + 11 * s)}" cy="{fmt(y - 9 * s)}" r="{fmt(5.6 * s)}" fill="{K.EVAL}"/>' +
            check_mark(x + 11 * s, y - 9 * s, 2.6 * s, 1.4, K.INK))


def g_judge(x, y, s):
    """LLM-as-judge: a small violet orb inside a mint ring, no glow (the pipeline's LLM core is the only glow)."""
    return (f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(11 * s)}" fill="{K.INK}" stroke="{K.EVAL}" '
            f'stroke-width="2"/><circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(6.2 * s)}" fill="url(#k-orb)"/>')


def slab_defs(a, keys):
    """One mini glass slab per layer hue, defined once at the origin (reused with <use>)."""
    return "".join(f'<g id="s{k[0]}{k[-1]}">{K.slab(K.Iso(0, 0, a), 5 / (a / 100), K.HUE[k])}</g>' for k in keys)


def slab(x, y, key):
    """A stage's slab: <use> of the hue's defined slab, top-face centre at (x, y)."""
    return f'<use href="#s{key[0]}{key[-1]}" x="{fmt(x)}" y="{fmt(y)}"/>'


def band_plate(x, y, w, h, dx=14, dy=9):
    """The knowledge band: a DATA glass plate (slab top gradient, faint front gradient, dark side)."""
    x2 = x + w - dx
    top = [(x, y + dy), (x + dx, y), (x + w, y), (x2, y + dy)]
    front = [(x, y + dy), (x2, y + dy), (x2, y + dy + h), (x, y + dy + h)]
    side = [(x2, y + dy), (x + w, y), (x + w, y + h), (x2, y + dy + h)]
    return (f'<path d="{pd(side)}" fill="{K.mix(K.DATA, K.INK, .66)}" fill-opacity=".92"/>'
            f'<path d="{pd(top)}" fill="url(#k-top-{K.DATA[1:]})" stroke="{K.DATA}" stroke-opacity=".9"/>'
            f'<path d="{pd(front)}" fill="url(#bandg)" stroke="{K.DATA}" stroke-opacity=".55"/>')


def band_field(x0, y0, x1, y1, avoid, seed, n_nodes, n_dots, mind):
    """Knowledge texture: seeded graph nodes linked to their two nearest neighbours, plus orchid vector dots."""
    rnd = random.Random(seed)
    free = lambda x, y: not any(ax0 <= x <= ax1 and ay0 <= y <= ay1 for ax0, ay0, ax1, ay1 in avoid)
    nodes, tries = [], 0
    while len(nodes) < n_nodes and tries < 20000:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if free(x, y) and all(math.hypot(x - a, (y - b) * 1.5) > mind for a, b in nodes):
            nodes.append((x, y))
    edges = set()
    for i, (x, y) in enumerate(nodes):
        near = sorted(range(len(nodes)), key=lambda j: (math.hypot(nodes[j][0] - x, nodes[j][1] - y), j))[1:3]
        edges.update((min(i, j), max(i, j)) for j in near)
    pts, tries = [], 0
    while len(pts) < n_dots and tries < 20000:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if free(x, y) and all(math.hypot(x - a, y - b) > 8 for a, b in nodes):
            pts.append((x, y))
    lite = K.link_tint(K.DATA)
    e = "".join(f"M{fmt(nodes[i][0])},{fmt(nodes[i][1])}L{fmt(nodes[j][0])},{fmt(nodes[j][1])}" for i, j in sorted(edges))
    return (f'<path d="{e}" stroke="{lite}" stroke-opacity=".55"/>' + dots(pts, 1.3, K.link_tint(K.RETR), .65) +
            dots(nodes, 3, lite))


def ledger_card(x, y, w, narrow=False):
    """The audit trail: a flat ruled card, header plus four rows each ending in a solid azure check;
    returns (svg, height, row baselines)."""
    row, top, pitch, pad, cb = (13, 23, 20, 10, 12) if narrow else (11, 19, 16.5, 7, 10)
    h = top + 7 + pitch * len(LEDGER_ROWS) + 3
    o = [f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="4" fill="{K.INK}" '
         f'stroke="{K.TRUST}" stroke-opacity=".6"/>',
         K.txt(x + pad, y + top - 5, "audit trail", "st", K.name_tint(K.TRUST)),
         K.hairline(x + pad - 2, y + top + 2, x + w - pad + 2, y + top + 2)]
    ys, tiles, ticks = [], [], []
    for i, r in enumerate(LEDGER_ROWS):
        ry = y + top + 7 + pitch * i + pitch * .66
        K.assert_within(x + pad + K.tw(r, row) + 5, x + w - pad - cb, f"ledger row '{r}'")
        bx, by = x + w - pad - cb, ry - cb * .86
        o.append(text(x + pad, ry, r, row, K.TEXT))
        tiles.append(f"M{fmt(bx + 2)},{fmt(by)}h{cb - 4}q2,0 2,2v{cb - 4}q0,2 -2,2h-{cb - 4}q-2,0 -2,-2v-{cb - 4}q0,-2 2,-2z")
        q = cb * .28
        cx, cy = bx + cb / 2, by + cb / 2
        ticks.append(f"M{fmt(cx - q)},{fmt(cy)}L{fmt(cx - q * .3)},{fmt(cy + q * .65)}L{fmt(cx + q)},{fmt(cy - q * .7)}")
        ys.append(ry)
    o.append(f'<path d="{"".join(tiles)}" fill="{K.TRUST}"/><path d="{"".join(ticks)}" fill="none" stroke="#FFFFFF" '
             f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(o), h, ys


def gauge(cx, cy, r):
    """240-degree accuracy gauge: track, muted 0-70 arc, mint 70-90 arc, ticks, dashed ghost needle at 70 and a
    white needle at 90 that sweeps up from 70 once on load; returns (svg, css)."""
    a0, span = 150, 240
    ang = lambda v: math.radians(a0 + span * v / 100)
    P = lambda v, rr: (cx + rr * math.cos(ang(v)), cy + rr * math.sin(ang(v)))

    def arc(v0, v1, rr):
        (x0, y0), (x1, y1) = P(v0, rr), P(v1, rr)
        return f"M{fmt(x0)},{fmt(y0)}A{fmt(rr)},{fmt(rr)} 0 {1 if span * (v1 - v0) / 100 > 180 else 0} 1 {fmt(x1)},{fmt(y1)}"

    ticks = "".join(f"M{fmt(P(v, r - 7.5)[0])},{fmt(P(v, r - 7.5)[1])}L{fmt(P(v, r - 4)[0])},{fmt(P(v, r - 4)[1])}"
                    for v in range(0, 101, 10))
    (nx, ny), (gx, gy) = P(90, r - 9), P(70, r - 9)
    svg = (f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r + 6)}" fill="{K.INK}" fill-opacity=".6" '
           f'stroke="{K.EVAL}" stroke-opacity=".22"/>'
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
           f".nd{{transform-origin:{fmt(cx)}px {fmt(cy)}px;animation:knd 1.6s {K.EASE} 2.1s both}}")
    return svg, css


def numeral(x, y, size, hue):
    """'~70%' drawn arrow '~90%': ivory 700 tabular numerals, the arrow a shape, 2px hue underline; returns (svg, w)."""
    wa, wb = K.tw(NUM_A, size, True), K.tw(NUM_B, size, True)
    ga, aw = size * .28, size * .74
    w = wa + ga + aw + ga + wb
    st = f' style="font-size:{fmt(size)}px"'
    ay, ax0, ax1 = y - size * .34, x + wa + ga, x + wa + ga + aw
    return (f'<text x="{fmt(x)}" y="{fmt(y)}" class="num"{st}>{NUM_A}</text>'
            f'<path d="M{fmt(ax0)},{fmt(ay)}H{fmt(ax1 - 1)}M{fmt(ax1 - size * .25)},{fmt(ay - size * .21)}'
            f'L{fmt(ax1)},{fmt(ay)}L{fmt(ax1 - size * .25)},{fmt(ay + size * .21)}" fill="none" stroke="{K.RESULT}" '
            f'stroke-width="{fmt(size * .085)}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<text x="{fmt(ax1 + ga)}" y="{fmt(y)}" class="num"{st}>{NUM_B}</text>'
            f'<rect x="{fmt(x)}" y="{fmt(y + 7)}" width="{fmt(w)}" height="2" rx="1" fill="{hue}"/>', w)


# ---------------------------------------------------------------- connectors
def link(points, hue, d, op=.55):
    """Connector (1.5px, round caps, source hue) that draws itself at delay d; returns (path, chevron path data)."""
    st = f' style="animation-delay:{fmt(d, 2)}s"'
    path = f'<path d="{pd(points, False)}" class="ln cn" stroke="{hue}" stroke-opacity="{fmt(op, 2)}" pathLength="1"{st}/>'
    (x1, y1), (x2, y2) = points[-2], points[-1]
    a, s = math.atan2(y2 - y1, x2 - x1), 4.5
    chev = (f'M{fmt(x2 + s * math.cos(a + math.pi - .66))},{fmt(y2 + s * math.sin(a + math.pi - .66))}'
            f'L{fmt(x2)},{fmt(y2)}L{fmt(x2 + s * math.cos(a + math.pi + .66))},{fmt(y2 + s * math.sin(a + math.pi + .66))}')
    return path, chev


def links(specs):
    """Draw (points, hue, delay[, op]) connectors; their chevrons (one path per colour) fade in once the lines draw."""
    paths, chevs = [], {}
    for sp in specs:
        p, c = link(*sp)
        paths.append(p)
        op = sp[3] if len(sp) > 3 else .55
        chevs.setdefault((sp[1], fmt(min(1, op + .3), 2)), []).append(c)
    ch = "".join(f'<path d="{"".join(ds)}" class="cn" stroke="{hue}" stroke-opacity="{op}"/>'
                 for (hue, op), ds in chevs.items())
    return "".join(paths) + f'<g class="ar">{ch}</g>'


# ---------------------------------------------------------------- tokens (defined once, reused with <use>)
def chunk_sprites(sc):
    """Three flat chunk sheets (ivory faces, one rule line each) with orchid tabs, fanned on a diagonal."""
    faces, tabs, rule = [], [], []
    for i in range(3):
        I = K.Iso((-8 + 8 * i) * sc, (3 - 4.2 * i) * sc, 32 * sc)
        faces.append(pd([I.p(u, v) for u, v in ((.30, .25), (.70, .25), (.70, .75), (.30, .75))]))
        tabs.append(pd([I.p(u, v) for u, v in ((.70, .30), (.80, .30), (.80, .45), (.70, .45))]))
        rule.append(pd([I.p(.36, .5), I.p(.62, .5)], close=False))
    return (f'<path d="{"".join(faces)}" fill="{K.RESULT}" stroke="{K.INK}" stroke-width=".8"/>'
            f'<path d="{"".join(tabs)}" fill="{K.RETR}"/>'
            f'<path d="{"".join(rule)}" stroke="{K.INK}" stroke-opacity=".35"/>')


def token_defs(sc):
    """Token sprites around (0, 0): page, chunks, dots, snippet, field card, and its check, stamp and citation marks."""
    def card(w, h):
        return (f'<rect x="{fmt(-w / 2)}" y="{fmt(-h / 2)}" width="{fmt(w)}" height="{fmt(h)}" rx="2" '
                f'fill="{K.RESULT}" stroke="{K.INK}" stroke-width="1.2"/>')
    w, h = 18 * sc, 13 * sc
    keys = "".join(f"M{fmt(-w / 2 + 2.6 * sc)},{fmt(-h / 2 + (3.2 + 3.2 * i) * sc)}h{fmt(3.4 * sc)}" for i in range(3))
    vals = "".join(f"M{fmt(-w / 2 + 7.6 * sc)},{fmt(-h / 2 + (3.2 + 3.2 * i) * sc)}h{fmt((7.4 - 2 * (i % 2)) * sc)}"
                   for i in range(3))
    halo = f'<circle r="{fmt(11 * sc)}" fill="{K.INK}" fill-opacity=".55"/>'
    dp = [(-6 * sc, 2 * sc), (0, -2.5 * sc), (6 * sc, 1.5 * sc)]
    return "".join([
        f'<g id="tp">{halo}{g_sheet(0, 2 * sc, .34 * sc)}</g>',
        f'<g id="tc">{halo}{chunk_sprites(sc)}</g>',
        f'<g id="td">{dots(dp, 3.6 * sc, K.INK, .6)}{dots(dp, 2.5 * sc, K.link_tint(K.RETR))}</g>',
        f'<g id="ts">{card(w, h * .82)}<rect x="{fmt(-w / 2 + 2.6 * sc)}" y="{fmt(-1.7 * sc)}" '
        f'width="{fmt(w - 5.2 * sc)}" height="{fmt(3.4 * sc)}" rx="1" fill="{K.RETR}"/></g>',
        f'<g id="tf">{card(w, h)}<path d="{keys}" stroke="{K.INK}" stroke-opacity=".6" stroke-width="{fmt(1.6 * sc)}"/>'
        f'<path d="{vals}" stroke="{K.INK}" stroke-opacity=".28" stroke-width="{fmt(1.6 * sc)}"/></g>',
        f'<g id="tk"><circle cx="{fmt(w / 2)}" cy="{fmt(-h / 2)}" r="{fmt(4.6 * sc)}" fill="{K.TRUST}" '
        f'stroke="{K.INK}"/>{check_mark(w / 2, -h / 2, 2.2 * sc, 1.3)}</g>',
        f'<g id="tr"><circle cx="{fmt(-w / 2 + 1.5 * sc)}" cy="{fmt(h / 2 - 1.5 * sc)}" r="{fmt(4.8 * sc)}" '
        f'fill="{K.INK}" fill-opacity=".5" stroke="{K.TRUST}" stroke-width="{fmt(1.6 * sc)}"/>'
        f'<circle cx="{fmt(-w / 2 + 1.5 * sc)}" cy="{fmt(h / 2 - 1.5 * sc)}" r="{fmt(1.7 * sc)}" fill="{K.TRUST}"/></g>',
        f'<g id="tb">{K.bookmark(-w / 2 + 6 * sc, -h / 2 + 3 * sc, sc)}</g>',
    ])


TOKEN_PARTS = {"page": ("tp",), "chunks": ("tc",), "dots": ("td",), "snip": ("ts",), "field": ("tf",),
               "checked": ("tf", "tk"), "stamped": ("tf", "tk", "tr"), "cited": ("tf", "tk", "tr", "tb")}
TOKEN_CLS = {"page": "pa", "chunks": "ck", "dots": "dt", "snip": "sn", "field": "fd", "checked": "cc",
             "stamped": "sp", "cited": "ci"}


def token(kind, x, y, cls=None):
    """A token sprite at (x, y): a <g> (optionally classed for motion) of <use> references."""
    c = f' class="{cls}"' if cls else ""
    return f'<g{c}>' + "".join(f'<use href="#{p}" x="{fmt(x)}" y="{fmt(y)}"/>' for p in TOKEN_PARTS[kind]) + "</g>"


# ---------------------------------------------------------------- motion
def track_css(cls, cycle, wins, origin, morph):
    """Token motion: each window (t0, t1, path) fades in at path[0] over `morph` s, travels the polyline at constant
    speed from t0 to t1, then fades out in place over `morph` s; hidden otherwise. Times in seconds of the cycle."""
    ox, oy = origin
    fr = [(0, 0, *wins[0][2][0])]
    for t0, t1, path in wins:
        L = [0]
        for (ax, ay), (bx, by) in zip(path, path[1:]):
            L.append(L[-1] + math.hypot(bx - ax, by - ay))
        fr.append((pct(t0 - morph, cycle), 0, *path[0]))
        fr.extend((pct(t0 + (t1 - t0) * l / L[-1], cycle), 1, x, y) for (x, y), l in zip(path, L))
        fr.append((pct(t1 + morph, cycle), 0, *path[-1]))
    fr.append((100, 0, *fr[-1][2:]))
    kf, last = [], -1
    for pc, op, x, y in fr:
        pc = max(pc, last + .001)
        last = pc
        dx, dy = fmt(x - ox), fmt(y - oy)
        tr = "none" if dx == dy == "0" else f"translate({dx}px)" if dy == "0" else f"translate({dx}px,{dy}px)"
        kf.append(f"{pf(pc)}%{{opacity:{op};transform:{tr}}}")
    return (f"@keyframes k{cls}{{{''.join(kf)}}}"
            f".{cls}{{opacity:0;animation:k{cls} {cycle}s linear {fmt(LOOP0, 2)}s infinite}}")


def dash_css(cls, cycle, t0, t1, length, dash):
    """A single bright dash travels a path of `length` px between t0 and t1 s of the cycle; hidden otherwise."""
    a, b = pct(t0, cycle), pct(t1, cycle)
    return (f"@keyframes k{cls}{{0%,{pf(a)}%{{opacity:0;stroke-dashoffset:{fmt(dash)}}}"
            f"{pf(a + EPS)}%{{opacity:1}}{pf(b - EPS)}%{{opacity:1}}"
            f"{pf(b)}%,100%{{opacity:0;stroke-dashoffset:{fmt(-length)}}}}}"
            f".{cls}{{opacity:0;stroke-dasharray:{fmt(dash)} {fmt(length + dash)};"
            f"animation:k{cls} {cycle}s linear {fmt(LOOP0, 2)}s infinite}}")


def schedule(stops, speed, morph, start):
    """[(kind, points, dwell), ...] -> timed windows [(kind, t0, t1, points)], one mover at a time."""
    out, t = [], start
    for kind, path, dwell in stops:
        t1 = t + plen(path) / speed
        out.append((kind, t, t1, path))
        t = t1 + morph + dwell
    return out, t


def loop_motion(ingest, cache_page, cache_arc, answer, ledger, eval_paths, speed, morph):
    """All loop motion of one variant. Ingest tokens run on the 36 s master: sub-cycles 1 and 2 take the long way
    (page -> chunks at OCR -> dots into the band); in sub-cycle 3 the page stops at the cache and a dash pulse takes
    the cache-hit arc instead. Answer tokens, the audit-row flashes and the eval dashes run every 12 s.
    Returns (css, svg, seconds of translation per 12 s cycle, end of motion in s)."""
    css, svg = [], []
    w1, t_ans = schedule(ingest, speed, morph, .25)
    moving = 0
    for kind, t0, t1, path in w1:
        wins = [(k * CYCLE + t0, k * CYCLE + t1, path) for k in (0, 1)]
        if kind == "page":
            wins.append((2 * CYCLE + t0, 2 * CYCLE + t0 + plen(cache_page) / speed, cache_page))
        cls = TOKEN_CLS[kind]
        css.append(track_css(cls, MASTER, wins, path[0], morph))
        svg.append(token(kind, *path[0], cls))
        moving += t1 - t0
    arc_d, arc_len = cache_arc
    a0 = .25 + plen(cache_page) / speed + morph * .5
    css.append(dash_css("ca", MASTER, 2 * CYCLE + a0, 2 * CYCLE + a0 + arc_len / speed, arc_len, 12))
    svg.append(f'<path class="ca" d="{arc_d}" fill="none" stroke="{K.rim_tint(K.DATA)}" stroke-width="2.6" '
               f'stroke-linecap="round"/>')
    w3, t_end = schedule(answer, speed, morph, t_ans - morph * .5)
    for kind, t0, t1, path in w3:
        cls = TOKEN_CLS[kind]
        css.append(track_css(cls, CYCLE, [(t0, t1, path)], path[0], morph))
        svg.append(token(kind, *path[0], cls))
        moving += t1 - t0
    # arrival: the cited card rests on the output while the four audit rows tick in turn
    ox, oy = w3[-1][3][-1]
    h0, h1 = t_end - morph, t_end + 1.0
    css.append(f"@keyframes kci{{0%,{pf(pct(h0, CYCLE))}%{{opacity:0}}{pf(pct(h0 + morph, CYCLE))}%,"
               f"{pf(pct(h1, CYCLE))}%{{opacity:1}}{pf(pct(h1 + .3, CYCLE))}%,100%{{opacity:0}}}}"
               f".ci{{opacity:0;animation:kci {CYCLE}s linear {fmt(LOOP0, 2)}s infinite}}")
    svg.append(token("cited", ox, oy, "ci"))
    css.append(f"@keyframes kfl{{0%{{opacity:0}}3%{{opacity:1}}14%,100%{{opacity:0}}}}"
               f".fl{{opacity:0;animation:kfl {CYCLE}s linear infinite}}")
    fx, fw, fh, ys = ledger
    for i, ry in enumerate(ys):
        d = LOOP0 + h0 + .15 + .18 * i - CYCLE * .03
        svg.append(f'<rect class="fl" style="animation-delay:{fmt(d, 2)}s" x="{fmt(fx)}" y="{fmt(ry - fh * .74)}" '
                   f'width="{fmt(fw)}" height="{fmt(fh)}" rx="2" fill="{K.rim_tint(K.TRUST)}" fill-opacity=".24"/>')
    # eval: one bright dash at a time (output -> harness -> judge -> 'tune model', then on to 'tune retrieval')
    t = h1 + .3
    for i, (d, L) in enumerate(eval_paths):
        dur = L / (speed * 2.4)
        css.append(dash_css(f"e{i}", CYCLE, t, t + dur, L, 16))
        svg.append(f'<path class="e{i}" d="{d}" fill="none" stroke="{K.rim_tint(K.EVAL)}" stroke-width="3" '
                   f'stroke-linecap="round" stroke-linejoin="round"/>')
        t += dur
        moving += dur
    return "".join(css), "".join(svg), moving, t


BUILD_CSS = "".join([
    ".cn{fill:none;stroke-width:1.5px;stroke-linecap:round;stroke-linejoin:round}",
    K.css_drop("dp"), K.css_draw("ln", 1.1), K.css_fade("ar", .4, 3.2), K.css_fade("fa", .6), K.css_draw("cd", 1.2, 2.4),
    "@keyframes khd{0%,100%{opacity:0}}.hd{animation:khd 1s step-end infinite}",
])


def band_defs():
    """Front-face gradient of the knowledge band."""
    return (f'<linearGradient id="bandg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{K.DATA}" '
            f'stop-opacity=".2"/><stop offset="1" stop-color="{K.DATA}" stop-opacity=".05"/></linearGradient>')


# ---------------------------------------------------------------- wide
def build_wide():
    """850-wide factory floor: ingest lane, knowledge band, answer lane, and the eval loop with the big numeral."""
    W, H = 850, 716
    PL, PW = 24, 802                         # lane platforms span x 24..826 (front face to 812)
    L1, L1H, YC1 = 78, 126, 134              # ingest platform top, front height, glyph row (slab centre)
    BY, BH = 246, 88                         # knowledge band
    L3, L3H, YC3 = 374, 152, 430             # answer platform
    EV = 578                                 # eval conduit
    A, BOX = 29, 108                         # mini slab half-width, label box
    X1 = {"pdf": 66, "ing": 178, "que": 268, "cch": 372, "ocr": 530, "emb": 700}
    X3 = {"srch": 136, "rr": 244, "llm": 352, "val": 462, "gate": 568, "out": 664}
    LEDX, LEDW = 714, 96
    TURN = 762                               # the embed connector turns down into the band here
    BYF, BYB = BY + 9, BY + 9 + BH           # band front face top and bottom
    XG, XJ = 640, 516                        # gold-set harness, LLM-as-judge instruments under the conduit
    GX, GY, GR = X3["srch"], EV + 72, 34     # the gauge hangs under the 'tune retrieval' junction
    ev_top = L3 + 9 + L3H                    # bottom of the answer platform

    body = [K.card(W, H, "LARGE-DOCUMENT PIPELINE", lit=LIT),
            K.glow(X1["pdf"] + 10, YC1 + 6, 150, 95, K.WARM, .16),
            K.glow(X3["llm"], YC3 - 14, 120, 80, K.VIOLET, .20)]

    # ---- lane 1: ingest path
    l1 = [K.txt(28, L1 - 8, "INGEST PATH", "ey"), K.plate(PL, L1, PW, L1H),
          K.floor_shadow(X1["pdf"], YC1 + 8, 30, 12), g_stack(X1["pdf"], YC1 + 6, .62),
          ]
    lab1 = [stage_label(X1["pdf"], YC1 + 36, "long PDFs", None, None, BOX, anchor=None)[0]]
    glyph1 = {"ing": lambda x, y: K.cubes(x, y - 1, .78, n=2),
              "cch": lambda x, y: K.drums(x, y + 2, 1.45, n=1, grid=True),
              "ocr": lambda x, y: g_ocr(x, y, 1.0),
              "emb": lambda x, y: g_vectors(x - 2, y + 1, .56, 11, link=True)}
    for sid, key, name, sub in INGEST:
        if sid in glyph1:
            x = X1[sid]
            lb, last = stage_label(x, YC1 + 36, name, sub, K.HUE[key], BOX, anchor=None)
            K.assert_within(last + 6, L1 + 9 + L1H, f"{sid} label inside lane 1")
            l1.append(slab(x, YC1, key) + glyph1[sid](x, YC1))
            lab1.append(lb)
    tq = "tenant-fair queue"
    l1.append(g_lanes(X1["que"], YC1 + 2, .40) + K.tech(X1["que"] - K.tech_width(tq) / 2, YC1 + 32, tq, K.MSG)[0])
    l1.append(f'<g text-anchor="middle">{"".join(lab1)}</g>')
    body.append(f'<g class="dp"{K.delay(.15)}>{"".join(l1)}</g>')

    # ---- knowledge band
    lw = K.measure(BAND_LABEL, "st")
    avoid = [(PL + 6, BYF + 2, PL + 32 + lw, BYF + 31), (TURN - 16, BYF, TURN + 16, BYF + 18),
             (X3["srch"] - 14, BYB - 16, X3["srch"] + 14, BYB), (444, BYF, 476, BYF + 16)]
    body.append(f'<g class="dp"{K.delay(.48)}>{K.txt(28, BY - 8, "KNOWLEDGE", "ey")}{band_plate(PL, BY, PW, BH)}'
                f'{band_field(PL + 14, BYF + 10, PL + PW - 30, BYB - 9, avoid, 23, 24, 46, 38)}'
                f'<rect x="{PL + 10}" y="{BYF + 8}" width="{fmt(lw + 18)}" height="21" rx="10.5" fill="{K.INK}" '
                f'fill-opacity=".85" stroke="{K.DATA}" stroke-opacity=".5"/>'
                f'{K.txt(PL + 19, BYF + 22.5, BAND_LABEL, "st", K.name_tint(K.DATA))}</g>')

    # ---- lane 3: answer path
    l3 = [K.txt(28, L3 - 8, "ANSWER PATH", "ey"), K.plate(PL, L3, PW, L3H)]
    glyph3 = {"srch": lambda x, y: g_lens(x, y + 1, .56, 5),
              "rr": lambda x, y: g_rerank(x, y, A),
              "val": lambda x, y: g_validate(x, y, 1.0),
              "gate": lambda x, y: K.gate(x, y + 1, .62),
              "out": lambda x, y: g_sheet(x, y + 1, .52, bookmark=True)}
    lab3 = []
    for sid, key, name, sub in ANSWER:
        x = X3[sid]
        lb, last = stage_label(x, YC3 + 36, name, sub, K.HUE[key], BOX, anchor=None)
        K.assert_within(last + 6, ev_top, f"{sid} label inside lane 3")
        l3.append(slab(x, YC3, key) + (glyph3[sid](x, YC3) if sid in glyph3 else ""))
        lab3.append(lb)
    l3.append(f'<g text-anchor="middle">{"".join(lab3)}</g>')
    ccss, core = K.llm_core(X3["llm"], YC3 - 25, 15, "lc", n=8, seed=9, label=None, period=(6.4, 10))
    core += K.txt(X3["llm"], YC3 - 21.2, "LLM", "st", "#FFFFFF", "middle", 10.5)
    l3.append(f'<ellipse cx="{X3["llm"]}" cy="{YC3}" rx="13" ry="5" fill="#000" fill-opacity=".4"/>' + core)
    led_y = L3 + 18
    led, led_h, led_ys = ledger_card(LEDX, led_y, LEDW)
    K.assert_within(LEDX + LEDW, PL + PW - 14 - 2, "ledger inside the platform front face")
    l3.append(led + K.txt(LEDX + LEDW / 2, led_y + led_h + 16, "21 CFR Part 11", "ey", anchor="middle",
                          extra=' style="letter-spacing:0"'))
    body.append(f'<g class="dp"{K.delay(.81)}>{"".join(l3)}</g>')

    # ---- connectors draw after the platforms land
    y1 = YC1
    spec = [([(X1["pdf"] + 28, y1), (X1["ing"] - A - 2, y1)], K.TEXT2, 1.5, .45),
            ([(X1["ing"] + A + 2, y1), (X1["que"] - 27, y1)], K.SVC, 1.6),
            ([(X1["que"] + 27, y1), (X1["cch"] - A - 2, y1)], K.MSG, 1.7),
            ([(X1["cch"] + A + 2, y1), (X1["ocr"] - A - 2, y1)], K.DATA, 1.8),
            ([(X1["ocr"] + A + 2, y1), (X1["emb"] - A - 2, y1)], K.RETR, 1.9),
            ([(X1["emb"] + A + 2, y1), (TURN, y1), (TURN, BY + 3)], K.RETR, 2.0),
            ([(X3["srch"], BYB + 2), (X3["srch"], YC3 - 34)], K.RETR, 2.1)]
    for i, (a, b, hue) in enumerate((("srch", "rr", K.RETR), ("rr", "llm", K.RETR), ("llm", "val", K.AGENT),
                                     ("val", "gate", K.TRUST), ("gate", "out", K.TRUST))):
        spec.append(([(X3[a] + A + 2, YC3), (X3[b] - A - 2, YC3)], hue, 2.2 + .1 * i))
    body.append(links(spec) + K.hairline(X3["out"] + A + 2, YC3, LEDX - 1, YC3, .4))

    # ---- cache-hit bypass: from the cache's right corner, curving down past the labels into the band
    c0, cc, c1 = (X1["cch"] + A + 2, YC1 + 3), (X1["cch"] + 82, YC1 + 8), (X1["cch"] + 84, BY + 2)
    arc_d = f"M{fmt(c0[0])},{fmt(c0[1])}Q{fmt(cc[0])},{fmt(cc[1])} {fmt(c1[0])},{fmt(c1[1])}"
    body.append(f'<g class="fa"{K.delay(2.3)}><path d="{arc_d}" fill="none" stroke="{K.DATA}" stroke-opacity=".85" '
                f'stroke-width="1.5" stroke-linecap="round" stroke-dasharray="2 4"/>' +
                K.chevron(*c1, math.atan2(c1[1] - cc[1], c1[0] - cc[0]), K.DATA, 1) +
                K.note(c1[0] + 10, BY - 9, "cache hit", fill=K.tech_tint(K.DATA)) + "</g>")

    # ---- eval loop: conduit under the floor, stations on it, risers back into the answer path, the readout
    xs, xe = X3["srch"], X3["out"]
    taps = [K.feeder(xe, ev_top - 20, xe, EV - 4, K.EVAL, .75) + K.ring_tap(xe, EV, K.EVAL)]
    for x, word in ((xs, "tune retrieval"), (X3["llm"], "tune model")):
        taps.append(K.eval_loop([(x, EV - 4), (x, ev_top + 4)]) + K.ring_tap(x, EV, K.EVAL) +
                    K.note(x + 9, EV - 17, word, fill=K.tech_tint(K.EVAL)))
    taps.append(K.feeder(GX, EV + 4, GX, GY - GR - 7, K.EVAL, .75))
    st = []
    IY = GY - 4                              # instrument row under the conduit
    for x, name, glyph, top in ((XG, "Gold-set harness", g_goldset(XG, IY + 8, 1.35), IY - 18),
                                (XJ, "LLM-as-judge", g_judge(XJ, IY, 1.35), IY - 17)):
        taps.append(K.feeder(x, EV + 4, x, top, K.EVAL, .75) + K.ring_tap(x, EV, K.EVAL))
        st.append(glyph + stage_label(x, IY + 36, name, None, K.EVAL, BOX)[0])
    gsvg, gcss = gauge(GX, GY, GR)
    nx = GX + GR + 26
    nsvg, nw = numeral(nx, GY + 13, 34, K.EVAL)
    K.assert_within(nx + nw + 14, XJ - K.measure("LLM-as-judge", "st") / 2, "numeral clear of the judge label")
    K.fit(NUM_CTX, "ctx", W - 28 - nx, what="numeral context")
    body.append(K.conduit(xe, EV, xs, EV, K.EVAL, "cd"))
    body.append(f'<g class="fa"{K.delay(2.6)}>{K.txt(28, EV - 14, "EVAL LOOP", "ey", K.tech_tint(K.EVAL))}'
                f'{"".join(taps)}</g>')
    body.append(f'<g class="dp"{K.delay(1.14)}>{"".join(st)}{gsvg}{nsvg}{K.txt(nx, GY + 39, NUM_CTX, "ctx")}</g>')

    # ---- parked tokens: shown only when motion is off (reduced motion / static frame)
    ty = YC1 - 5
    park = [token("page", (X1["pdf"] + X1["ing"]) / 2 + 2, ty), token("chunks", (X1["ocr"] + X1["emb"]) / 2, ty),
            token("snip", X3["srch"], (BYB + YC3 - 34) / 2 + 3),
            token("checked", (X3["val"] + X3["gate"]) / 2, YC3 - 6), token("cited", X3["out"] + 2, YC3 - 20)]
    body.append(f'<g class="hd">{"".join(park)}</g>')

    # ---- loop motion
    t3 = YC3 - 6
    ingest = [("page", [(X1["pdf"] + 6, ty), (X1["ocr"], ty)], .1),
              ("chunks", [(X1["ocr"], ty), (X1["emb"], ty)], .05),
              ("dots", [(X1["emb"], ty), (TURN, ty), (TURN, BYF + 14)], 0)]
    answer = [("snip", [(xs, BYB - 4), (xs, t3), (X3["llm"], t3)], .15),
              ("field", [(X3["llm"], t3), (X3["val"], t3)], .05),
              ("checked", [(X3["val"], t3), (X3["gate"], t3)], .05),
              ("stamped", [(X3["gate"], t3), (X3["out"], t3)], 0)]
    ev_paths = [(f"M{xe},{ev_top - 20}V{EV}H{X3['llm']}V{ev_top + 4}",
                 (EV - ev_top + 20) + (xe - X3["llm"]) + (EV - ev_top - 4)),
                (f"M{X3['llm']},{EV}H{xs}V{ev_top + 4}", (X3["llm"] - xs) + (EV - ev_top - 4))]
    mcss, msvg, moving, t_end = loop_motion(
        ingest, [(X1["pdf"] + 6, ty), (X1["cch"], ty)], (arc_d, plen(bez([c0, cc, c1]))), answer,
        (LEDX + 4, LEDW - 8, 15.5, led_ys), ev_paths, 330, .22)
    body.append(msvg)
    defs = band_defs() + slab_defs(A, SLABS) + token_defs(1.0)
    return K.svg_doc(W, H, TITLE, DESC, defs, BUILD_CSS + ccss + gcss + mcss, "".join(body)), moving, t_end


# ---------------------------------------------------------------- narrow
def build_narrow():
    """400-wide re-layout: one vertical column of stations, the cache-hit arc down the left edge, the eval conduit
    down the column and back up the right edge into the answer path."""
    W = 400
    PX, PW = 40, 326                         # plates span x 40..366 (front face to 352)
    GX, A, LX = 86, 22, 128                  # glyph column, slab half-width, label column
    BOX = 344 - LX
    RP = 58                                  # row pitch
    ARC_X, RAIL_X = 16, 382
    nar = True

    e1 = 66
    P1 = e1 + 8                              # lane 1 plate top
    r1 = [P1 + 9 + 33 + RP * i for i in range(6)]
    P1H = r1[-1] + 31 - (P1 + 9)
    e2 = P1 + 9 + P1H + 30
    BY, BH = e2 + 8, 98
    BYF, BYB = BY + 9, BY + 9 + BH
    e3 = BYB + 30
    P3 = e3 + 8
    r3 = [P3 + 9 + 33 + RP * i for i in range(6)]
    led_y, led_w = r3[-1] + 30, 344 - LX
    led_svg, led_h, led_ys = ledger_card(LX, led_y, led_w, narrow=True)
    cfr_y = led_y + led_h + 19
    P3H = cfr_y + 14 - (P3 + 9)
    e4 = P3 + 9 + P3H + 32
    rg, rj = e4 + 34, e4 + 90                # gold-set and judge rows on the conduit
    EVB = rj + 34                            # bottom run of the conduit
    GY, GR = EVB + 56, 30
    H = GY + 80

    rows1 = dict(zip([s[0] for s in INGEST], r1))
    rows3 = dict(zip([s[0] for s in ANSWER], r3))
    ans = {s[0]: s for s in ANSWER}
    body = [K.card(W, H, "LARGE-DOCUMENT PIPELINE", lit=LIT),
            K.glow(GX + 30, r1[0] + 10, 150, 110, K.WARM, .16),
            K.glow(GX + 20, rows3["llm"] - 10, 140, 90, K.VIOLET, .20)]

    def row_label(yc, name, sub, hue):
        return stage_label(LX, yc - 3, name, sub, hue, BOX, nar, anchor="start")[0]

    # ---- lane 1
    l1 = [K.txt(PX, e1, "INGEST PATH", "ey"), K.plate(PX, P1, PW, P1H),
          K.floor_shadow(GX, r1[0] + 8, 28, 11), g_stack(GX, r1[0] + 6, .6),
          row_label(r1[0] + 6, "long PDFs", None, None)]
    glyph1 = {"ing": lambda x, y: K.cubes(x, y - 1, .62, n=2),
              "cch": lambda x, y: K.drums(x, y + 2, 1.15, n=1, grid=True),
              "ocr": lambda x, y: g_ocr(x, y, .8),
              "emb": lambda x, y: g_vectors(x - 2, y + 1, .46, 11, link=True)}
    for sid, key, name, sub in INGEST:
        if sid in glyph1:
            yc = rows1[sid]
            l1.append(slab(GX, yc, key) + glyph1[sid](GX, yc) + row_label(yc, name, sub, K.HUE[key]))
    tq = "tenant-fair queue"
    l1.append(g_lanes(GX, rows1["que"] + 2, .36) + K.tech(LX, rows1["que"] + 1, tq, K.MSG, narrow=True)[0])
    body.append(f'<g class="dp"{K.delay(.15)}>{"".join(l1)}</g>')

    # ---- band
    lw = K.measure(BAND_LABEL, "st", nar)
    avoid = [(PX + 4, BYF + 2, PX + 34 + lw, BYF + 33), (GX - 14, BYF, GX + 14, BYF + 18),
             (GX - 14, BYB - 16, GX + 14, BYB), (PX, BYF, PX + 22, BYF + 24)]
    body.append(f'<g class="dp"{K.delay(.48)}>{K.txt(PX, e2, "KNOWLEDGE", "ey")}{band_plate(PX, BY, PW, BH)}'
                f'{band_field(PX + 12, BYF + 12, PX + PW - 26, BYB - 10, avoid, 31, 13, 24, 34)}'
                f'<rect x="{PX + 10}" y="{BYF + 9}" width="{fmt(lw + 20)}" height="24" rx="12" fill="{K.INK}" '
                f'fill-opacity=".85" stroke="{K.DATA}" stroke-opacity=".5"/>'
                f'{K.txt(PX + 20, BYF + 25.5, BAND_LABEL, "st", K.name_tint(K.DATA))}</g>')

    # ---- lane 3
    l3 = [K.txt(PX, e3, "ANSWER PATH", "ey"), K.plate(PX, P3, PW, P3H)]
    glyph3 = {"srch": lambda x, y: g_lens(x, y + 1, .46, 5),
              "rr": lambda x, y: g_rerank(x, y, A),
              "val": lambda x, y: g_validate(x, y, .82),
              "gate": lambda x, y: K.gate(x, y + 1, .52),
              "out": lambda x, y: g_sheet(x, y + 1, .44, bookmark=True)}
    for sid, key, name, sub in ANSWER:
        yc = rows3[sid]
        l3.append(slab(GX, yc, key) + (glyph3[sid](GX, yc) if sid in glyph3 else "") +
                  row_label(yc, name, sub, K.HUE[key]))
    ccss, core = K.llm_core(GX, rows3["llm"] - 21, 13, "lc", n=7, seed=9, label=None, period=(6.4, 10))
    core += K.txt(GX, rows3["llm"] - 17.2, "LLM", "st", "#FFFFFF", "middle", 10.5)
    l3.append(f'<ellipse cx="{GX}" cy="{rows3["llm"]}" rx="11" ry="4.5" fill="#000" fill-opacity=".4"/>' + core)
    l3.append(led_svg + K.txt(LX + 10, cfr_y, "21 CFR Part 11", "ey", extra=' style="letter-spacing:0"'))
    body.append(f'<g class="dp"{K.delay(.81)}>{"".join(l3)}</g>')

    # ---- connectors down the column
    spec = []
    seq1 = ["pdf", "ing", "que", "cch", "ocr", "emb"]
    hue1 = {"pdf": K.TEXT2, "ing": K.SVC, "que": K.MSG, "cch": K.DATA, "ocr": K.RETR, "emb": K.RETR}
    below = {"pdf": 14, "que": 12}
    for i, (a, b) in enumerate(zip(seq1, seq1[1:])):
        spec.append(([(GX, rows1[a] + below.get(a, 20)), (GX, rows1[b] - (9 if b == "que" else 16))],
                     hue1[a], 1.5 + .08 * i, .45 if a == "pdf" else .55))
    spec.append(([(GX, rows1["emb"] + 20), (GX, BY + 3)], K.RETR, 1.95))
    spec.append(([(GX, BYB + 2), (GX, rows3["srch"] - 26)], K.RETR, 2.05))
    seq3 = [s[0] for s in ANSWER]
    for i, (a, b) in enumerate(zip(seq3, seq3[1:])):
        spec.append(([(GX, rows3[a] + 20), (GX, rows3[b] - (38 if b == "llm" else 18))],
                     K.HUE[ans[a][1]], 2.15 + .08 * i))
    body.append(links(spec))
    body.append(f'<path d="M{GX + A + 3},{rows3["out"]}H{LX - 8}V{led_y + 12}H{LX - 1}" fill="none" stroke="#FFFFFF" '
                f'stroke-opacity=".4"/>')

    # ---- cache-hit bypass down the left edge, its label set along it
    yc = rows1["cch"]
    arc = [(GX - A - 2, yc + 2), (ARC_X + 14, yc + 2), (ARC_X, yc + 8), (ARC_X, yc + 26)]
    tail = [(ARC_X, BYF + 4), (ARC_X, BYF + 18), (ARC_X + 22, BYF + 18)]
    arc_d = (f"M{fmt(arc[0][0])},{fmt(arc[0][1])}C{fmt(arc[1][0])},{fmt(arc[1][1])} {fmt(arc[2][0])},{fmt(arc[2][1])} "
             f"{fmt(arc[3][0])},{fmt(arc[3][1])}V{fmt(tail[0][1])}Q{fmt(tail[1][0])},{fmt(tail[1][1])} "
             f"{fmt(tail[2][0])},{fmt(tail[2][1])}")
    arc_len = plen(bez(arc)) + (tail[0][1] - arc[3][1]) + plen(bez(tail))
    ny = (rows1["ocr"] + rows1["emb"]) / 2 + 26
    body.append(f'<g class="fa"{K.delay(2.3)}><path d="{arc_d}" fill="none" stroke="{K.DATA}" stroke-opacity=".85" '
                f'stroke-width="1.5" stroke-linecap="round" stroke-dasharray="2 4"/>' +
                K.chevron(*tail[2], 0, K.DATA, 1) +
                f'<text transform="translate({ARC_X + 16},{fmt(ny)}) rotate(-90)" class="an" '
                f'fill="{K.tech_tint(K.DATA)}">cache hit</text></g>')

    # ---- eval loop: conduit from the output down the column through the stations, along the bottom, up the right
    yo = rows3["out"] + 22
    ytap = {"llm": rows3["llm"] + 8, "srch": rows3["srch"] + 8}
    taps = [K.feeder(GX, yo, GX, e4 + 4, K.EVAL, .75) + K.ring_tap(GX, e4 + 8, K.EVAL)]
    for sid, word in (("srch", "tune retrieval"), ("llm", "tune model")):
        yt = ytap[sid]
        _, _, name, sub = ans[sid]
        K.assert_within(LX + max(K.measure(sub, "sb", nar), K.measure(name, "st", nar)) + 10, RAIL_X - 34,
                        f"{sid} label clear of its feedback tap")
        K.assert_within(LX + K.measure(name, "st", nar) + 10, RAIL_X - 8 - K.measure(word, "an", nar),
                        f"{sid} name clear of '{word}'")
        taps.append(K.eval_loop([(RAIL_X - 4, yt), (RAIL_X - 34, yt)]) + K.ring_tap(RAIL_X, yt, K.EVAL) +
                    K.note(RAIL_X - 8, yt - 9, word, nar, K.tech_tint(K.EVAL), "end"))
    taps.append(K.feeder(GX, EVB + 4, GX, GY - GR - 7, K.EVAL, .75))
    conduit = (K.conduit(GX, e4 + 8, GX, EVB, K.EVAL, "cd") + K.conduit(GX, EVB, RAIL_X, EVB, K.EVAL, "cd") +
               K.conduit(RAIL_X, EVB, RAIL_X, ytap["srch"], K.EVAL, "cd"))
    st = [g_goldset(GX, rg + 4, 1.15) + stage_label(LX, rg + 5, "Gold-set harness", None, K.EVAL, BOX, nar, "start")[0],
          g_judge(GX, rj, 1.15) + stage_label(LX, rj + 5, "LLM-as-judge", None, K.EVAL, BOX, nar, "start")[0]]
    gsvg, gcss = gauge(GX, GY, GR)
    nsvg, nw = numeral(LX, GY + 9, 30, K.EVAL)
    K.assert_within(LX + nw, RAIL_X - 24, "narrow numeral")
    ctx = NUM_CTX.split(" · ")
    for ln in ctx:
        K.fit(ln, "ctx", RAIL_X - 24 - LX, nar, "narrow numeral context")
    ctx_svg = "".join(K.txt(LX, GY + 34 + 16 * i, ln, "ctx") for i, ln in enumerate(ctx))
    body.append(conduit)
    body.append(f'<g class="fa"{K.delay(2.6)}>{K.txt(PX, e4, "EVAL LOOP", "ey", K.tech_tint(K.EVAL))}'
                f'{"".join(taps)}</g>')
    body.append(f'<g class="dp"{K.delay(1.14)}>{"".join(st)}{gsvg}{nsvg}{ctx_svg}</g>')

    # ---- parked tokens
    park = [token("page", GX, (rows1["pdf"] + rows1["ing"]) / 2 + 4),
            token("chunks", GX, (rows1["ocr"] + rows1["emb"]) / 2),
            token("snip", GX, (BYB + rows3["srch"] - 26) / 2 + 2),
            token("checked", GX, (rows3["val"] + rows3["gate"]) / 2),
            token("cited", GX + A + 14, rows3["out"] - 14)]
    body.append(f'<g class="hd">{"".join(park)}</g>')

    # ---- loop motion down the column
    ingest = [("page", [(GX, rows1["pdf"] + 4), (GX, rows1["ocr"] - 2)], .1),
              ("chunks", [(GX, rows1["ocr"] - 2), (GX, rows1["emb"] - 2)], .05),
              ("dots", [(GX, rows1["emb"] - 2), (GX, BYF + 14)], 0)]
    answer = [("snip", [(GX, BYB - 4), (GX, rows3["llm"] - 4)], .15),
              ("field", [(GX, rows3["llm"] - 4), (GX, rows3["val"] - 4)], .05),
              ("checked", [(GX, rows3["val"] - 4), (GX, rows3["gate"] - 4)], .05),
              ("stamped", [(GX, rows3["gate"] - 4), (GX, rows3["out"] - 4)], 0)]
    ev_paths = [(f"M{GX},{yo}V{EVB}H{RAIL_X}V{ytap['llm']}", (EVB - yo) + (RAIL_X - GX) + (EVB - ytap["llm"])),
                (f"M{RAIL_X},{ytap['llm']}V{ytap['srch']}", ytap["llm"] - ytap["srch"])]
    mcss, msvg, moving, t_end = loop_motion(
        ingest, [(GX, rows1["pdf"] + 4), (GX, rows1["cch"] - 2)], (arc_d, arc_len), answer,
        (LX + 4, led_w - 8, 19, led_ys), ev_paths, 240, .24)
    body.append(msvg)
    defs = band_defs() + slab_defs(A, SLABS) + token_defs(1.25)
    return K.svg_doc(W, H, TITLE, DESC, defs, BUILD_CSS + ccss + gcss + mcss, "".join(body)), moving, t_end


if __name__ == "__main__":
    for name, fn in (("pipeline.svg", build_wide), ("pipeline-narrow.svg", build_narrow)):
        svg, moving, t_end = fn()
        K.write(os.path.join(ASSETS, name), svg)
        print(f"  translation {moving:.2f}s of {CYCLE}s ({moving / CYCLE * 100:.0f}%), motion ends at {t_end:.2f}s")
    print(K.picture("pipeline", ALT))
