#!/usr/bin/env python3
"""Scene 'Rules vs. intelligence': a hard-coded if/elif/else workflow beside intelligence in the workflow.

Writes assets/agentic.svg (850 wide) and assets/agentic-narrow.svg (400 wide) from the shared svgkit.
Python 3 stdlib only, deterministic. Never hand-edit the SVGs; change this file and re-run.

Colour grammar: the rules panel is greys only (one muted coral touch on its dead end); on the right,
violet is the model and the steps it drives, azure is the check step and the human-review gate,
ivory is the handled documents. No architecture is shown: only what the intelligence decides.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgkit as K  # noqa: E402

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

AG, TR, CO = K.AGENT, K.TRUST, K.MSG
LIT = ("MSG", "AGENT", "TRUST")
TITLE = "Rules vs. intelligence"
KICKER = "NOT IF-ELSE · INTELLIGENCE"
DOCS = [("clean", "clean"), ("scanned", "scan"), ("new format", "new"), ("amended", "amend")]
RULES = [("if type == A", "template_a()", "clean"), ("elif has_table", "parse_table()", None),
         ("elif scanned", "fix_scan()", None), ("elif …", "+ next rule", "ghost"), ("else", None, "dead")]
STEPS = [("Understand", "what is this, what's being asked", AG), ("Plan", "choose the steps and tools", AG),
         ("Act", "extract, look up, compare", AG), ("Check", "verify against the source", TR)]
CAP_L = "Every new case is another branch. It breaks on the case nobody wrote."
CAP_R = "It reasons about each case. Rules become guardrails, not the logic."
FOOT = "Deterministic where it must be: validation, permissions, audit. Intelligent everywhere else."

ALT = ("Two panels compare a hard-coded workflow with intelligence in the workflow. Left, in grey: four incoming "
       "documents, a clean one, a scanned one, a new format and an amended one, enter an if, elif, else decision "
       "tree. The clean one takes its branch; the new format falls through to a dead end, no rule matched, manual. "
       "Every new case is another branch, and it breaks on the case nobody wrote. Right: the same four documents "
       "enter a loop around a violet model core: understand what this is and what is being asked, plan the steps "
       "and tools, act by extracting, looking up and comparing, and check against the source. All four are handled; "
       "a low-confidence case goes to an azure human-review gate and comes back approved. It reasons about each "
       "case, and rules become guardrails, not the logic. Footer: deterministic where it must be, validation, "
       "permissions and audit; intelligent everywhere else.")
DESC = ("A grey if, elif, else tree that sends a new document format to a manual dead end, beside a violet model "
        "core that runs understand, plan, act and check on every document, with a human-review gate for "
        "low-confidence cases.")

CYCLE, LOOP0, TRAVEL = 10, 2.4, 4.4      # one document pulse round the right-hand loop; >55% of each cycle still


def F(v):
    return K.fmt(v, 1)


class T:
    """Per-variant sizes: scene classes (tag, title, code) plus kit classes; every label is measured."""

    def __init__(self, narrow):
        self.n = narrow
        self.sz = {"tg": 11.5 if narrow else 10.5, "tt": 16 if narrow else 15, "cd": 12 if narrow else 11}
        self.lh = {"sb": 16 if narrow else 14, "an": 18 if narrow else 16}

    def w(self, s, cls):
        if cls == "tg":
            return K.tw_mono(s, self.sz["tg"], 1.4)
        if cls == "cd":
            return K.tw_mono(s, self.sz["cd"])
        if cls == "tt":
            return K.tw(s, self.sz["tt"], bold=True)
        return K.measure(s, cls, self.n)

    def put(self, x, y, s, cls, fill=None, anchor=None, box=None, extra=""):
        wd = self.w(s, cls)
        x0 = x - (wd / 2 if anchor == "middle" else wd if anchor == "end" else 0)
        if box:
            K.assert_within(box[0], x0, f"'{s}' left")
            K.assert_within(x0 + wd, box[1], f"'{s}' right")
        if cls in self.sz:
            a = f' fill="{fill}"' if fill else ""
            a += f' text-anchor="{anchor}"' if anchor else ""
            return f'<text x="{F(x)}" y="{F(y)}" class="{cls}"{a}{extra}>{K.esc(s)}</text>'
        return K.txt(x, y, s, cls, fill, anchor, extra=extra)

    def css(self):
        s = self.sz
        return (f".tg,.cd{{font-family:{K.MONO};font-weight:500}}"
                f".tg{{font-size:{F(s['tg'])}px;letter-spacing:1.4px;fill:{K.MUTED}}}"
                f".tt{{font-size:{F(s['tt'])}px;font-weight:650;fill:{K.TEXT}}}"
                f".cd{{font-size:{F(s['cd'])}px;fill:{K.TEXT2}}}")


# ---------------------------------------------------------------- drawing helpers
def panel_rect(w, h):
    return (f'<rect width="{F(w)}" height="{F(h)}" rx="12" fill="#FFFFFF" fill-opacity=".03" '
            f'stroke="{K.BORDER}" stroke-opacity=".14"/>')


def head(t, w, tag, title, hue, pad=16):
    ty, tt = (25, 50) if t.n else (23, 44)
    return (f'<circle cx="{F(pad + 3)}" cy="{F(ty - (4.4 if t.n else 3.6))}" r="3" fill="{hue}"/>' +
            t.put(pad + 13, ty, tag, "tg", box=(0, w - pad)) + t.put(pad, tt, title, "tt", box=(0, w - pad)))


def page(x, y, w, h, kind, ivory=False):
    """Small upright document (fold top-right). Grey = an incoming case; ivory = a handled one (with a check)."""
    f = 4
    fill, op = (K.RESULT, .92) if ivory else (K.mix(K.TEXT2, K.INK, .1), .5)
    o = [f'<path d="M{F(x)},{F(y)}H{F(x + w - f)}L{F(x + w)},{F(y + f)}V{F(y + h)}H{F(x)}Z" fill="{fill}" '
         f'fill-opacity="{K.fmt(op, 2)}"/>',
         f'<path d="M{F(x + w - f)},{F(y)}V{F(y + f)}H{F(x + w)}Z" fill="{K.mix(fill, K.INK, .4)}"/>']
    L, R = x + 2.5, x + w - 2.5
    ink = f'stroke="{K.INK}" stroke-opacity="{".45" if ivory else ".6"}" stroke-width="1.2" stroke-linecap="round"'
    if ivory:
        cx, cy = x + w / 2, y + h * .58
        o.append(f'<path d="M{F(cx - 3.6)},{F(cy)}L{F(cx - 1)},{F(cy + 2.8)}L{F(cx + 3.8)},{F(cy - 2.6)}" '
                 f'fill="none" stroke="{K.INK}" stroke-opacity=".7" stroke-width="1.6" stroke-linecap="round" '
                 f'stroke-linejoin="round"/>')
        o.append(f'<path d="M{F(L)},{F(y + 4)}H{F(R - 4)}" {ink}/>')
    elif kind == "clean":
        o.append(f'<path d="M{F(L)},{F(y + 6)}H{F(R - 2)}M{F(L)},{F(y + 9.5)}H{F(R)}M{F(L)},{F(y + 13)}H{F(R - 3)}" {ink}/>')
    elif kind == "scan":
        o = [f'<g transform="rotate(-8 {F(x + w / 2)} {F(y + h / 2)})">' + "".join(o) +
             f'<path d="M{F(L)},{F(y + 6)}H{F(R - 2)}M{F(L + 1)},{F(y + 9.5)}H{F(R - 1)}M{F(L)},{F(y + 13)}H{F(R - 4)}" '
             f'{ink} stroke-dasharray="2 1.4"/></g>']
    elif kind == "new":
        gx, gy, gw, gh = L, y + 5.5, R - L, h - 8.5
        o.append(f'<path d="M{F(gx)},{F(gy)}h{F(gw)}v{F(gh)}h-{F(gw)}zM{F(gx + gw / 2)},{F(gy)}v{F(gh)}'
                 f'M{F(gx)},{F(gy + gh / 2)}h{F(gw)}" fill="none" {ink}/>')
    else:   # amended: lines plus a change bar in the margin
        o.append(f'<path d="M{F(L + 1.5)},{F(y + 6)}H{F(R - 2)}M{F(L + 1.5)},{F(y + 9.5)}H{F(R)}M{F(L + 1.5)},{F(y + 13)}H{F(R - 3)}" {ink}/>')
        o.append(f'<path d="M{F(x + 1.6)},{F(y + 8)}V{F(y + 15)}" {ink.replace('width="1.2"', 'width="1.6"')}/>')
    return "".join(o)


def doc_row(t, w, y0, pad=16):
    """The four incoming documents in a row with a bus under them; returns (svg, centres, bus y, page h)."""
    pw, ph = (14, 18) if t.n else (13, 17)
    widths = [pw + 5 + t.w(lbl, "sb") for lbl, _ in DOCS]
    gap = (w - 2 * pad - 4 - sum(widths)) / 3
    K.assert_within(12, gap, "doc row gap")
    x, o, xs = pad + 2, [], []
    for (lbl, kind), wd in zip(DOCS, widths):
        o.append(page(x, y0, pw, ph, kind))
        o.append(t.put(x + pw + 5, y0 + ph / 2 + (4.6 if t.n else 4), lbl, "sb", box=(pad, w - pad)))
        xs.append(x + pw / 2)
        x += wd + gap
    bus = y0 + ph + 9
    d = "".join(f"M{F(c)},{F(y0 + ph + 3)}V{F(bus)}" for c in xs) + f"M{F(xs[0])},{F(bus)}H{F(xs[-1])}"
    o.append(f'<path d="{d}" fill="none" stroke="{K.MUTED}" stroke-opacity=".5" stroke-width="1.2" '
             f'stroke-linecap="round"/>')
    return "".join(o), xs, bus, ph


def diamond(x, y, r, ghost=False):
    dash = ' stroke-dasharray="2 2"' if ghost else ""
    op = ".4" if ghost else ".85"
    return (f'<path d="M{F(x)},{F(y - r)}L{F(x + r)},{F(y)}L{F(x)},{F(y + r)}L{F(x - r)},{F(y)}Z" fill="{K.INK}" '
            f'stroke="{K.MUTED}" stroke-opacity="{op}" stroke-width="1.3"{dash}/>')


def box(x, y, w, h, hue, fop, sop, solid=None, dash=None, rx=6):
    base = (f'<rect x="{F(x)}" y="{F(y)}" width="{F(w)}" height="{F(h)}" rx="{rx}" fill="{solid}"/>'
            if solid else "")
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return base + (f'<rect x="{F(x)}" y="{F(y)}" width="{F(w)}" height="{F(h)}" rx="{rx}" fill="{hue}" '
                   f'fill-opacity="{K.fmt(fop, 2)}" stroke="{hue}" stroke-opacity="{K.fmt(sop, 2)}"{d}/>')


def check(x, y, col, op=.9, s=1):
    return (f'<path d="M{F(x - 4 * s)},{F(y)}L{F(x - 1.2 * s)},{F(y + 3 * s)}L{F(x + 4.5 * s)},{F(y - 3.2 * s)}" '
            f'fill="none" stroke="{col}" stroke-opacity="{K.fmt(op, 2)}" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


def caption(t, w, y_last, text, pad=16):
    lines = K.wrap(text, "an", w - 2 * pad, t.n)
    y0 = y_last - (len(lines) - 1) * t.lh["an"]
    return "".join(t.put(pad, y0 + i * t.lh["an"], s, "an") for i, s in enumerate(lines)), y0, len(lines)


# ---------------------------------------------------------------- left: hard-coded workflow
def left_panel(t, w, h=None):
    """Grey if/elif/else tree. Returns (svg, natural height)."""
    pad, n = 16, t.n
    o = [head(t, w, "BEFORE · RULES", "Hard-coded workflow", K.MUTED, pad)]
    dsv, xs, bus, ph = doc_row(t, w, 66 if n else 60, pad)
    o.append(dsv)
    DX, R = pad + 18, 6.5
    bh = 22 if n else 20
    pitch = 44 if n else 40
    y0 = bus + 30
    if h:   # wide: spread the rows so the tree fills the shared panel height (capped)
        ncap = len(K.wrap(CAP_L, "an", w - 2 * pad, n))
        last_max = h - 18 - (ncap - 1) * t.lh["an"] - t.sz["tt"] - 18
        pitch = max(pitch, min(52, (last_max - (bh + 4) / 2 - y0) / (len(RULES) - 1)))
    ys = [y0 + i * pitch for i in range(len(RULES))]
    # bus drop into the first diamond, then the 'no' spine down through every diamond
    o.append(K.conn([(DX, bus), (DX, ys[0] - R - 2)], K.MUTED, op=.5, w=1.2))
    sp = "".join(f"M{F(DX)},{F(a + R)}V{F(b - R - 2)}" for a, b in zip(ys, ys[1:]))
    o.append(f'<path d="{sp}" stroke="{K.MUTED}" stroke-opacity=".45" stroke-width="1.2"/>')
    for a, b in zip(ys, ys[1:]):
        o.append(K.chevron(DX, b - R - 2, math.pi / 2, K.MUTED, .6, 3.4, 1.2))
    hw = max(t.w(hd, "cd") for _, hd, _ in RULES if hd) + 18 + 16    # room for the clean row's check
    HX = w - pad - hw
    for (cond, hd, tag), y in zip(RULES, ys):
        ghost = tag == "ghost"
        o.append(diamond(DX, y, R, ghost))
        cfill = K.MUTED if ghost else None
        cx = DX + R + 8
        o.append(t.put(cx, y + t.sz["cd"] * .36, cond, "cd", cfill, box=(0, w - pad),
                       extra=' fill-opacity=".7"' if ghost else ""))
        lx = cx + t.w(cond, "cd") + 8
        if tag == "dead":
            continue
        dash = "2 3" if ghost else None
        o.append(K.conn([(lx, y), (HX - 3, y)], K.MUTED, op=.3 if ghost else .5, w=1.2, dash=dash))
        o.append(box(HX, y - bh / 2, hw, bh, K.MUTED, .02 if ghost else .06, .3 if ghost else .45,
                     dash="3 3" if ghost else None, rx=5))
        o.append(t.put(HX + 9, y + t.sz["cd"] * .36, hd, "cd", K.MUTED if ghost else None,
                       box=(HX, w - pad - 4), extra=' fill-opacity=".75"' if ghost else ""))
        if tag == "clean":
            o.append(t.put((lx + HX) / 2, y - 7, "clean", "sb", anchor="middle", box=(lx, HX)))
            o.append(check(w - pad - 12, y, K.TEXT2, .85))
    # dead end: no rule matched -> manual (the one coral touch), with a grey manual-work figure
    y = ys[-1]
    lx = DX + R + 8 + t.w("else", "cd") + 8
    px = w - pad - 14
    lab_w = t.w("new format", "sb")
    msgs = ["no rule matched → manual"]
    if lx + lab_w + 12 > px - 16 - t.w(msgs[0], "sb") - 20:     # phones: break the dead-end label in two
        msgs = ["no rule matched", "→ manual"]
    dw = max(t.w(m, "sb") for m in msgs) + 20
    DXE = px - 16 - dw
    K.assert_within(lx + lab_w + 12, DXE, "dead-end lead-in")
    o.append(K.conn([(lx, y), (DXE - 3, y)], K.MUTED, op=.5, w=1.2))
    o.append(t.put((lx + DXE) / 2, y - 7, "new format", "sb", anchor="middle", box=(lx, DXE)))
    dh = bh + 4 + (len(msgs) - 1) * t.lh["sb"]
    o.append(box(DXE, y - dh / 2, dw, dh, CO, .10, .5, rx=5))
    b0 = y + (4.6 if n else 4) - (len(msgs) - 1) * t.lh["sb"] / 2
    for i, m in enumerate(msgs):
        o.append(t.put(DXE + 10, b0 + i * t.lh["sb"], m, "sb", K.tech_tint(CO), box=(DXE, px - 16)))
    o.append(K.person(px, y + 10, .85, K.MUTED))
    last = y + dh / 2
    ncap = len(K.wrap(CAP_L, "an", w - 2 * pad, n))
    nat = last + 18 + t.sz["tt"] + (ncap - 1) * t.lh["an"] + 18
    hh = h or nat
    cap, cy0, _ = caption(t, w, hh - 18, CAP_L, pad)
    K.assert_within(last + 14, cy0 - t.sz["tt"], "left caption clearance")
    o.append(cap)
    return "".join(o), nat


# ---------------------------------------------------------------- right: intelligence in the workflow
def right_panel(t, w, h=None, cls="pz"):
    """Model core inside an understand -> plan -> act -> check loop; human-review gate for low confidence.
    Returns (svg, css, natural height)."""
    pad, n = 16, t.n
    o = [head(t, w, "HOW I BUILD · INTELLIGENCE", "Intelligence in the workflow", AG, pad)]
    dsv, xs, bus, ph = doc_row(t, w, 66 if n else 60, pad)
    o.append(dsv)
    CG, RG = (50, 30) if n else (64, 30)          # column gap (core sits in it), row gap
    tw_ = (w - 2 * pad - CG) / 2
    TP = 12
    lh = t.lh["sb"]
    subs = [K.wrap(s, "sb", tw_ - 2 * TP, n) for _, s, _ in STEPS]
    th = [(22 if n else 20) + (17 if n else 15) + lh * (len(sl) - 1) + 12 for sl in subs]
    r1, r2 = max(th[0], th[1]), max(th[2], th[3])
    top1 = bus + 22
    top2 = top1 + r1 + RG
    XL, XR = pad, pad + tw_ + CG
    tiles = [(XL, top1, r1), (XR, top1, r1), (XR, top2, r2), (XL, top2, r2)]   # U, P, A, C (clockwise)
    ctr = [(x + tw_ / 2, y + hh / 2) for x, y, hh in tiles]
    ccx, ccy = w / 2, top1 + r1 + RG / 2
    # core first (its glow sits under the tiles)
    ccss, core = K.llm_core(ccx, ccy, 19 if n else 20, "cr", n=10, seed=5, label="LLM", label_size=11, drift=False)
    o.append(K.glow(ccx, ccy, w * .42, r1 + r2, K.VIOLET, .20))
    o.append(core)
    # pulse path (drawn under the tiles, so it vanishes inside each step and reappears in the gaps)
    out_y = top2 + r2 + (52 if n else 46)
    entry = (ctr[0][0], bus)
    pts_ = [entry, ctr[0], ctr[1], ctr[2], ctr[3], (ctr[3][0], out_y - 3)]
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts_, pts_[1:])]
    tot, acc, pcs = sum(seg), 0, [0]
    travel = TRAVEL / CYCLE * 100
    for s in seg:
        acc += s
        pcs.append(acc / tot * travel)
    stops = [(p, x, y) for p, (x, y) in zip(pcs, pts_)]
    hues = [(0, K.MUTED), (pcs[1] * .7, AG), ((pcs[3] + pcs[4]) / 2, TR), (pcs[4] + (pcs[5] - pcs[4]) * .6, K.RESULT)]
    pcss, pulse = K.pulse(cls, stops, hues, CYCLE, LOOP0, core=2.4, halo=10, fade=(2, 4))
    o.append(pulse)
    # feed: bus -> Understand
    o.append(K.conn([entry, (entry[0], top1 - 3)], K.MUTED, op=.55, w=1.3))
    # loop arrows between tiles (visible gap runs of one clockwise loop)
    lo = .6
    o.append(K.conn([(XL + tw_ + 3, ctr[0][1]), (XR - 4, ctr[1][1])], AG, op=lo))
    o.append(K.conn([(ctr[1][0], top1 + r1 + 3), (ctr[2][0], top2 - 4)], AG, op=lo))
    o.append(K.conn([(XR - 3, ctr[2][1]), (XL + tw_ + 4, ctr[3][1])], AG, op=lo))
    o.append(K.conn([(ctr[3][0], top2 - 3), (ctr[0][0], top1 + r1 + 4)], TR, op=lo))
    # step tiles: an opaque ink base hides the pulse while a step works on the document
    for (name, _, hue), sl, (x, y, hh) in zip(STEPS, subs, tiles):
        o.append(box(x, y, tw_, hh, hue, .10, .45, solid=K.INK2, rx=10))
        by = y + (22 if n else 20)
        o.append(t.put(x + TP, by, name, "st", K.name_tint(hue), box=(x, x + tw_ - TP)))
        for i, s in enumerate(sl):
            o.append(t.put(x + TP, by + (17 if n else 15) + i * lh, s, "sb", box=(x, x + tw_ - TP + 2)))
    # outputs: three documents straight through, the low-confidence one via the human-review gate
    yb = top2 + r2
    xc = ctr[3][0]
    pw = 14 if n else 13
    pgap = 7
    x0 = xc - (pw * 1.5 + pgap * 1.5) - pw / 2 - pgap / 2
    x0 = max(pad + 6, xc - 2 * pw - 1.5 * pgap)
    pxs = [x0 + i * (pw + pgap) for i in range(4)]
    o.append(K.conn([(xc, yb + 3), (xc, out_y - 4)], AG, op=.55))
    for i, px in enumerate(pxs):
        o.append(page(px, out_y, pw, ph, "", ivory=True))
    o.append(t.put(pxs[0], out_y + ph + (18 if n else 16), "all four handled", "st", K.RESULT, box=(pad, w - pad)))
    # branch to the gate
    br_y = yb + (24 if n else 20)
    gx = w - pad - (46 if n else 52)
    gs = .85 if n else .8
    gy = out_y + ph / 2 + 14 * gs
    gtop = gy - 32 * gs / .8
    o.append(K.conn([(xc, br_y), (gx - 4, br_y), (gx - 4, gtop - 5)], TR, op=.75, dash="3 3"))
    o.append(t.put(gx - 12, br_y - 6, "low confidence", "sb", K.name_tint(TR), anchor="end",
                   box=(xc + 8, w - pad)))
    o.append(K.gate(gx, gy, gs))
    o.append(t.put(gx, gy + (22 if n else 20), "human review", "sb", K.name_tint(TR), anchor="middle",
                   box=(xc + 40, w - pad)))
    ay = out_y + ph / 2
    ax0 = gx - 18 * gs / .8
    ax1 = pxs[-1] + pw + 5
    o.append(K.conn([(ax0, ay), (ax1, ay)], TR, op=.8))
    o.append(t.put((ax0 + ax1) / 2, ay - 7, "approved", "sb", K.name_tint(TR), anchor="middle", box=(ax1, ax0)))
    K.assert_within(ax1 + t.w("approved", "sb") + 16, ax0, "approved arrow length")
    last = max(out_y + ph + (18 if n else 16), gy + (22 if n else 20))
    ncap = len(K.wrap(CAP_R, "an", w - 2 * pad, n))
    nat = last + 18 + t.sz["tt"] + (ncap - 1) * t.lh["an"] + 18
    hh = h or nat
    cap, cy0, _ = caption(t, w, hh - 18, CAP_R, pad)
    K.assert_within(last + 14, cy0 - t.sz["tt"], "right caption clearance")
    o.append(cap)
    return "".join(o), ccss + pcss, nat


# ---------------------------------------------------------------- board
def group(x, y, svg, d):
    return f'<g class="pb"{K.delay(d)}><g transform="translate({F(x)},{F(y)})">{svg}</g></g>'


def build_wide():
    W, PW, Y0, X1, X2 = 850, 393, 60, 24, 433
    t = T(False)
    _, hl = left_panel(t, PW)
    _, _, hr = right_panel(t, PW)
    H_P = max(hl, hr)
    lsv, _ = left_panel(t, PW, H_P)
    rsv, rcss, _ = right_panel(t, PW, H_P)
    fy = Y0 + H_P + 26
    K.fit(FOOT, "sb", W - 56, what="footer")
    H = round(fy + 22)
    body = [K.card(W, H, KICKER, lit=LIT),
            group(X1, Y0, panel_rect(PW, H_P) + lsv, .1),
            group(X2, Y0, panel_rect(PW, H_P) + rsv, .4),
            f'<g class="ft">{t.put(W / 2, fy, FOOT, "sb", anchor="middle")}</g>']
    css = K.css_rise("pb", 8, .6) + K.css_fade("ft", .6, 1.1) + t.css() + rcss
    return K.svg_doc(W, H, TITLE, DESC, "", css, "".join(body))


def build_narrow():
    W, X, PW, GAP, Y0 = 400, 14, 372, 14, 52
    t = T(True)
    lsv, hl = left_panel(t, PW)
    rsv, rcss, hr = right_panel(t, PW)
    y2 = Y0 + hl + GAP
    lines = K.wrap(FOOT, "sb", W - 2 * 24, True)
    fy = y2 + hr + 26
    foot = "".join(t.put(24, fy + i * t.lh["sb"], s, "sb") for i, s in enumerate(lines))
    H = round(fy + (len(lines) - 1) * t.lh["sb"] + 22)
    body = [K.card(W, H, KICKER, lit=LIT),
            group(X, Y0, panel_rect(PW, hl) + lsv, .1),
            group(X, y2, panel_rect(PW, hr) + rsv, .4),
            f'<g class="ft">{foot}</g>']
    css = K.css_rise("pb", 8, .6) + K.css_fade("ft", .6, 1.1) + t.css() + rcss
    return K.svg_doc(W, H, TITLE, DESC, "", css, "".join(body))


if __name__ == "__main__":
    K.write(os.path.join(ASSETS, "agentic.svg"), build_wide())
    K.write(os.path.join(ASSETS, "agentic-narrow.svg"), build_narrow())
    print(K.picture("agentic", ALT))
