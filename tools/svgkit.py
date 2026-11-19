#!/usr/bin/env python3
"""svgkit: the shared visual toolkit for the profile README cards (Python 3 stdlib only).

Every tools/build_<scene>.py imports this module, so all cards speak one design language:
one dusk-ramp hue per system layer, the same dark card, the same isometric glyphs, the same
type scale and the same motion grammar. Scene generators must not edit this file.

Conventions
- Coordinates are SVG user units. Wide cards are 850 wide, narrow cards 400 wide.
- Functions return SVG/CSS text. Functions that need both return (css, svg).
- url(#k-...) references (card ground, lattice, orb, glow, slab and pulse gradients) are
  emitted automatically by svg_doc(); never define ids that start with "k-".
- Reserved CSS class names (typography): ey ix nm st c t lb sb rt ri an ctx num.
"""
import hashlib
import math
import os
import random
import re
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------- page constants
BREAKPOINT = 1011
RAW = "https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/"
WIDE_W, NARROW_W = 850, 400
MAX_BYTES = 40 * 1024

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SERIF = "Georgia,'Iowan Old Style','Times New Roman',serif"

# ---------------------------------------------------------------- palette
INK = "#0B1020"          # card ground, bottom (deepest)
INK2 = "#141B33"         # card ground, top (lift)
WHITE = "#FFFFFF"
TEXT = "#E6E9F2"         # primary text, tool-chip text
TEXT2 = "#AEB5C8"        # secondary text, rail items, annotations
MUTED = "#8E96AD"        # eyebrows, kickers, axis words
HAIR = "#FFFFFF"         # hairlines and standoffs, always at HAIR_OP
HAIR_OP = .16
RULE_OP = .12            # masthead hairline opacity
BORDER = "#8EA0E0"       # card border, at BORDER_OP
BORDER_OP = .22

INFRA = "#E9AE52"        # 01 amber/brass
DATA = "#F38B57"         # 02 tangerine
MSG = "#F2707A"          # 03 coral
SVC = "#E965A6"          # 04 rose
RETR = "#C175E6"         # 05 orchid
AGENT = "#9285FF"        # 06 violet: the model, always and only
TRUST = "#4FAEFF"        # 07 azure: gates, checks, validation, audit, provenance
EVAL = "#3FD8B2"         # aqua-mint: gold-set harness, LLM-as-judge, eval loops
OBS = "#86D08F"          # sage: metrics, logs, tracing, token cost/latency
PROBLEM = "#9A8F8A"      # ash: case-strip problem cells only (fill 14%)
PROBLEM_TEXT = "#B9AFAA"
RESULT = "#FFF4D6"       # ivory: result numerals, document sheets

WARM = "#F0A050"         # warm ambient glow (16%) at the base/origin of a flow
VIOLET = "#7F7BFF"       # violet ambient glow (20%) behind the LLM core
ORB_GLOW = "#A99CFF"
ORB_STOPS = ("#FFFFFF", "#C9C2FF", "#7F72FF")
PARTICLES = ("#FFFFFF", "#E3DEFF")
PULSE_MID = "#BFE3FF"

LAYER_KEYS = ("INFRA", "DATA", "MSG", "SVC", "RETR", "AGENT", "TRUST")
HUE = {"INFRA": INFRA, "DATA": DATA, "MSG": MSG, "SVC": SVC, "RETR": RETR, "AGENT": AGENT,
       "TRUST": TRUST, "EVAL": EVAL, "OBS": OBS}
LAYER_NAMES = {"INFRA": "INFRASTRUCTURE", "DATA": "DATA STORES", "MSG": "MESSAGING & QUEUES",
               "SVC": "SERVICES & APIs", "RETR": "RETRIEVAL", "AGENT": "AGENTS", "TRUST": "TRUST & CONTROLS"}


def _rgb(h):
    """Hex colour to an (r, g, b) tuple."""
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, t):
    """Blend colour c1 toward c2 by t (0..1); returns #RRGGBB."""
    a, b = _rgb(c1), _rgb(c2)
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def name_tint(h):
    """Layer/stage name colour: hue + 28% white."""
    return mix(h, WHITE, .28)


def tech_tint(h):
    """Technique (pattern) text colour: hue + 45% white."""
    return mix(h, WHITE, .45)


def rim_tint(h):
    """Back-edge rim and rim-flash colour: hue + 55% white."""
    return mix(h, WHITE, .55)


def link_tint(h):
    """Glyph link hairlines (sub-agents, graph edges): hue + 35% white."""
    return mix(h, WHITE, .35)


# ---------------------------------------------------------------- text
# Helvetica AFM advance widths for ASCII 32..126 (1/1000 em).
_AFM = [int(w) for w in (
    '278 278 355 556 556 889 667 191 333 333 389 584 278 333 278 278 556 556 556 556 556 556 556 556 556 556 '
    '278 278 584 584 584 556 1015 667 667 722 722 667 611 778 722 278 500 667 556 833 722 778 667 778 722 667 '
    '611 722 667 944 667 667 611 278 278 278 469 556 333 556 556 500 556 556 278 556 556 222 222 500 222 833 '
    '556 556 556 556 333 500 278 556 500 722 500 500 500 334 260 334 584').split()]
_AFM_EXTRA = {"·": 278, "→": 1000, "←": 1000, "×": 584, "−": 584, "–": 556, "—": 1000, "…": 1000,
              "≥": 584, "≤": 584, "’": 222, "‘": 222, "“": 333, "”": 333, "é": 556, "°": 400}

# Type scale per variant (narrow honours the floors: chips/items 13, names 13, mono 11.5).
TYPE = {
    False: {"ey": 10.5, "ix": 10.5, "nm": 12, "st": 12, "c": 11.5, "t": 11.5, "lb": 12, "sb": 11,
            "rt": 10.5, "ri": 10.5, "an": 12.5, "ctx": 11.5, "num": 32},
    True: {"ey": 11.5, "ix": 11.5, "nm": 13, "st": 13, "c": 13, "t": 13, "lb": 13, "sb": 13,
           "rt": 12.5, "ri": 13, "an": 14, "ctx": 13, "num": 32},
}
# class: (family, weight, letter-spacing px, default fill or None = caller must pass a hue fill)
_CLS = {
    "ey": ("mono", 500, 1.6, MUTED),     # masthead kicker, eyebrows, axis words
    "ix": ("mono", 500, 0, None),        # index numbers '01'..'07' in the hue
    "nm": ("sans", 650, 1.5, None),      # UPPERCASE layer names in name_tint(hue)
    "st": ("sans", 650, 0, None),        # sentence-case stage names in name_tint(hue)
    "c": ("sans", 500, 0, TEXT),         # tool-chip text
    "t": ("sans", 400, 0, None),         # technique text in tech_tint(hue)
    "lb": ("sans", 400, 0, TEXT),        # plain labels
    "sb": ("sans", 400, 0, TEXT2),       # sub-labels
    "rt": ("sans", 600, 1.4, None),      # rail titles in the rail hue (always horizontal)
    "ri": ("sans", 400, 0, TEXT2),       # rail items
    "an": ("serif", 400, 0, TEXT2),      # serif italic annotations, words only
    "ctx": ("sans", 400, 0, TEXT2),      # unit/context line under a numeral
    "num": ("sans", 700, 0, RESULT),     # big result numerals, tabular
}
_NARROW_WEIGHT = {"rt": 650}


def tw(text, size, bold=False, track=0.0):
    """Sans text width in px: Helvetica AFM x1.09 regular / x1.13 bold (calibrated to SF Pro), plus tracking."""
    w = sum(_AFM[ord(ch) - 32] if 32 <= ord(ch) < 127 else _AFM_EXTRA.get(ch, 620) for ch in text)
    return w / 1000 * size * (1.13 if bold else 1.09) + track * len(text)


def tw_mono(text, size, track=0.0):
    """Monospace text width in px (0.61 em per cell; arrows counted wider for fallback fonts)."""
    return sum(.8 if ch in "→←" else .61 for ch in text) * size + track * len(text)


def measure(text, cls, narrow=False):
    """Width in px of text set in one of the kit's type classes for the wide or narrow variant."""
    fam, wt, tr, _ = _CLS[cls]
    size = TYPE[narrow][cls]
    if fam == "mono":
        return tw_mono(text, size, tr)
    return tw(text, size, bold=_NARROW_WEIGHT.get(cls, wt) >= 600 if narrow else wt >= 600, track=tr)


def fit(text, cls, maxw, narrow=False, what=""):
    """Measure text in a type class and raise OverflowError if it is wider than maxw; returns the width."""
    w = measure(text, cls, narrow)
    if w > maxw + 1e-6:
        raise OverflowError(f"{what or cls}: '{text}' is {w:.1f}px, box is {maxw:.1f}px")
    return w


def assert_within(value, limit, what):
    """Raise OverflowError if a measured edge (e.g. a chip row's right x) passes a limit."""
    if value > limit + 1e-6:
        raise OverflowError(f"{what}: {value:.1f} passes limit {limit:.1f}")
    return value


def wrap(text, cls, maxw, narrow=False):
    """Greedy word-wrap text into lines that fit maxw in a type class; raises if one word cannot fit."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if measure(trial, cls, narrow) <= maxw:
            cur = trial
        else:
            if not cur:
                fit(word, cls, maxw, narrow, "wrap")
            lines.append(cur)
            cur = word
            fit(cur, cls, maxw, narrow, "wrap")
    if cur:
        lines.append(cur)
    return lines


def esc(s):
    """Escape text for SVG content and attributes."""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def fmt(v, nd=1):
    """Format a number compactly (nd decimals, trailing zeros stripped)."""
    s = ("%." + str(nd) + "f") % v
    s = s.rstrip("0").rstrip(".") if "." in s else s
    if s in ("-0", ""):
        return "0"
    return s.replace("0.", ".", 1) if s.startswith(("0.", "-0.")) else s


def pts(ps):
    """Format [(x, y), ...] as an SVG points string."""
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in ps)


def _attrs(kw):
    """kwargs to SVG attributes (fill_opacity -> fill-opacity)."""
    return "".join(f' {k.rstrip("_").replace("_", "-")}="{fmt(v, 2) if isinstance(v, (int, float)) else v}"'
                   for k, v in kw.items())


def txt(x, y, s, cls, fill=None, anchor=None, size=None, extra=""):
    """One line of text in a kit type class; classes without a default fill require fill (a hue tint)."""
    if fill is None and _CLS[cls][3] is None:
        raise ValueError(f"class '{cls}' needs an explicit fill")
    a = f' fill="{fill}"' if fill else ""
    a += f' text-anchor="{anchor}"' if anchor else ""
    a += f' style="font-size:{fmt(size)}px"' if size else ""
    return f'<text x="{fmt(x)}" y="{fmt(y)}" class="{cls}"{a}{extra}>{esc(s)}</text>'


def type_css(narrow=False, used=None):
    """CSS for the kit's type classes at wide or narrow sizes (svg_doc includes the ones a card uses)."""
    used = set(_CLS) if used is None else set(used) & set(_CLS)
    out = [f"text{{font-family:{SANS}}}"]
    mono = [c for c in ("ey", "ix") if c in used]
    if mono:
        out.append(",".join("." + c for c in mono) + f"{{font-family:{MONO}}}")
    for cls, (fam, wt, tr, fill) in _CLS.items():
        if cls not in used:
            continue
        wt = _NARROW_WEIGHT.get(cls, wt) if narrow else wt
        rule = f".{cls}{{font-size:{fmt(TYPE[narrow][cls])}px;font-weight:{wt}"
        rule += f";font-family:{SERIF};font-style:italic" if fam == "serif" else ""
        rule += f";letter-spacing:{fmt(tr)}px" if tr else ""
        rule += f";fill:{fill}" if fill else ""
        rule += ";font-variant-numeric:tabular-nums" if cls == "num" else ""
        out.append(rule + "}")
    return "".join(out)


# ---------------------------------------------------------------- document
def _def(ref):
    """Build the <defs> entry for one auto-managed k-* id."""
    if ref == "k-bg":
        return (f'<linearGradient id="k-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK2}"/>'
                f'<stop offset="1" stop-color="{INK}"/></linearGradient>')
    if ref == "k-lat":
        return ('<pattern id="k-lat" width="20" height="10" patternUnits="userSpaceOnUse">'
                '<circle cx="0" cy="0" r=".8" fill="#FFFFFF" fill-opacity=".07"/>'
                '<circle cx="10" cy="5" r=".8" fill="#FFFFFF" fill-opacity=".07"/></pattern>')
    if ref == "k-orb":
        return (f'<radialGradient id="k-orb" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="{ORB_STOPS[0]}"/>'
                f'<stop offset=".45" stop-color="{ORB_STOPS[1]}"/><stop offset="1" stop-color="{ORB_STOPS[2]}"/></radialGradient>')
    if ref == "k-glow":
        return ('<filter id="k-glow" x="-50%" y="-50%" width="200%" height="200%">'
                '<feGaussianBlur stdDeviation="3"/></filter>')
    if ref == "k-blur":
        return ('<filter id="k-blur" x="-30%" y="-30%" width="160%" height="160%">'
                '<feGaussianBlur stdDeviation="9"/></filter>')
    m = re.fullmatch(r"k-(top|front|pg)-([0-9A-F]{6})", ref)
    if m:
        kind, hx = m.group(1), "#" + m.group(2)
        if kind == "top":
            return (f'<linearGradient id="{ref}" x1="0" y1="0" x2="1" y2="1">'
                    f'<stop offset="0" stop-color="{hx}" stop-opacity=".62"/>'
                    f'<stop offset=".55" stop-color="{hx}" stop-opacity=".30"/>'
                    f'<stop offset="1" stop-color="{hx}" stop-opacity=".12"/></linearGradient>')
        if kind == "front":
            return (f'<linearGradient id="{ref}" x1="0" y1="0" x2="1" y2="0">'
                    f'<stop offset="0" stop-color="{hx}" stop-opacity=".24"/>'
                    f'<stop offset="1" stop-color="{hx}" stop-opacity=".05"/></linearGradient>')
        return (f'<radialGradient id="{ref}"><stop offset="0" stop-color="#FFFFFF"/>'
                f'<stop offset=".16" stop-color="{PULSE_MID}" stop-opacity=".95"/>'
                f'<stop offset=".42" stop-color="{hx}" stop-opacity=".9"/>'
                f'<stop offset="1" stop-color="{hx}" stop-opacity="0"/></radialGradient>')
    m = re.fullmatch(r"k-amb-([0-9A-F]{6})-(\d{1,3})", ref)
    if m:
        hx, op = "#" + m.group(1), int(m.group(2)) / 100
        return (f'<radialGradient id="{ref}"><stop offset="0" stop-color="{hx}" stop-opacity="{fmt(op, 2)}"/>'
                f'<stop offset="1" stop-color="{hx}" stop-opacity="0"/></radialGradient>')
    raise ValueError(f"unknown kit def {ref}")


def _hx(hue):
    """Hex digits (upper case, no #) of a colour, for auto-def ids."""
    return mix(hue, hue, 0)[1:]


REDUCED_MOTION = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def svg_doc(w, h, title, desc, defs, css, body):
    """Full SVG document: role=img, <title>, <desc>, width/height + viewBox, kit type CSS, caller CSS, REDUCED_MOTION last."""
    narrow = w <= 500
    refs = sorted(set(re.findall(r"url\(#(k-[A-Za-z0-9-]+)\)", css + defs + body)))
    all_defs = "".join(_def(r) for r in refs) + defs
    used = {c for group in re.findall(r'class="([^"]+)"', body) for c in group.split()}
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(w)}" height="{fmt(h)}" '
            f'viewBox="0 0 {fmt(w)} {fmt(h)}" role="img" aria-labelledby="k-title k-desc">'
            f'<title id="k-title">{esc(title)}</title><desc id="k-desc">{esc(desc)}</desc>'
            f'<style>{type_css(narrow, used)}{css}{REDUCED_MOTION}</style>'
            f'<defs>{all_defs}</defs>{body}</svg>')


# Truncated SHA-256 of banned words and word pairs (joined without a space), kept hashed so this
# public file never spells them. Checked on every word and every adjacent word pair.
_BANNED_SHA = {"3030366f967655db", "33b2fca7e32c99ef", "33cd8916347d2576", "35887df77b7c0bd9", "600e02e301214b82",
               "6a48e360c8d089b4", "850a1cf9ccc7e6fb", "86f519b62f871bd1", "aa6e8306562edccc", "b046b3566dc86320",
               "b73b9720f14e75ca", "c8f895a66c55921c", "d86cbaca4e74f57f", "e11eb7aed7e1e373", "f870f840018f21d4",
               "fa5179bbb874bf32"}


def banned_term(text):
    """Return the first banned word or word pair found in text (page content rules), or None."""
    toks = re.findall(r"[a-z0-9]+", text.lower())
    for a, b in zip(toks, toks[1:] + [""]):
        for term in (a, a + b):
            if hashlib.sha256(term.encode()).hexdigest()[:16] in _BANNED_SHA:
                return term
    return None


_FORBIDDEN = (r"<script", r"<foreignObject", r"<animate", r"<set\b", r"<image\b", r"prefers-color-scheme",
              r"@import", r"@font-face", r'href\s*=\s*"(?!#)', r"url\(\s*['\"]?(?!#)", r"var\(--")


def lint(text, what="svg"):
    """Raise ValueError if SVG text breaks a page rule (banned words, scripts, SMIL, external refs, emoji, size, XML)."""
    bad = banned_term(text)
    if bad:
        raise ValueError(f"{what}: banned content '{bad}'")
    for pat in _FORBIDDEN:
        if re.search(pat, text, re.I):
            raise ValueError(f"{what}: forbidden SVG feature /{pat}/")
    for ch in text:
        o = ord(ch)
        if o >= 0x1F000 or 0x2600 <= o <= 0x27BF or 0x2B00 <= o <= 0x2BFF or o == 0xFE0F:
            raise ValueError(f"{what}: emoji/dingbat character U+{o:04X}; draw marks as shapes")
    if REDUCED_MOTION + "</style>" not in text:
        raise ValueError(f"{what}: CSS must end with REDUCED_MOTION")
    if not re.match(r'<svg[^>]*\swidth="(850|400)"', text):
        raise ValueError(f"{what}: width must be 850 (wide) or 400 (narrow)")
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError(f"{what}: {len(text.encode('utf-8')) / 1024:.1f} KB is over the 40 KB budget")
    ET.fromstring(text)


def write(path, text):
    """Lint and write a generated SVG (UTF-8, deterministic bytes); prints path and size, returns byte count."""
    lint(text, os.path.basename(path))
    data = text.encode("utf-8")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)
    print(f"{path}  {len(data) / 1024:.1f} KB")
    return len(data)


def picture(slug, alt):
    """README <picture> embed for a slug with the shared width-only BREAKPOINT; alt must have no double quotes."""
    if '"' in alt:
        raise ValueError("alt text must not contain double quotes")
    if banned_term(alt):
        raise ValueError(f"alt text: banned content '{banned_term(alt)}'")
    return (f'<picture>\n  <source media="(max-width: {BREAKPOINT}px)" srcset="{RAW}{slug}-narrow.svg">\n'
            f'  <img src="{RAW}{slug}.svg" width="100%" alt="{alt}">\n</picture>')


# ---------------------------------------------------------------- card
def key_strip(x_right, y, lit=LAYER_KEYS, size=8, gap=3):
    """The 7-swatch layer key (base to top), right-aligned at x_right; swatches not in lit dim to 25%."""
    x0 = x_right - 7 * size - 6 * gap
    o = []
    for i, k in enumerate(LAYER_KEYS):
        op = "" if k in lit else ' fill-opacity=".25"'
        o.append(f'<rect x="{fmt(x0 + i * (size + gap))}" y="{fmt(y)}" width="{size}" height="{size}" rx="2" '
                 f'fill="{HUE[k]}"{op}/>')
    return "".join(o)


def card(w, h, kicker=None, lit=LAYER_KEYS):
    """Card ground (INK2->INK gradient, dot lattice, periwinkle 22% border) plus masthead kicker, hairline and key strip."""
    narrow = w <= 500
    rx = 16 if narrow else 18
    m = 18 if narrow else 28
    base = 34 if narrow else 36
    o = [f'<rect x=".5" y=".5" width="{fmt(w - 1)}" height="{fmt(h - 1)}" rx="{rx}" fill="url(#k-bg)" '
         f'stroke="{BORDER}" stroke-opacity="{BORDER_OP}"/>',
         f'<rect x="1" y="1" width="{fmt(w - 2)}" height="{fmt(h - 2)}" rx="{rx}" fill="url(#k-lat)"/>']
    sx0 = w - m - 74
    o.append(key_strip(w - m, base - 8, lit))
    if kicker:
        o.append(txt(m, base, kicker, "ey"))
        x1, x2 = m + measure(kicker, "ey", narrow) + 12, sx0 - 12
        assert_within(x1 + 24, x2, "masthead kicker vs key strip")
        o.append(f'<line x1="{fmt(x1)}" y1="{base - 4}" x2="{fmt(x2)}" y2="{base - 4}" stroke="{HAIR}" '
                 f'stroke-opacity="{RULE_OP}"/>')
    return "".join(o)


def glow(cx, cy, rx, ry, hue, op):
    """Ambient radial glow (at most two per card: WARM at 16% at the flow origin, VIOLET at 20% behind the core)."""
    return (f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="{fmt(rx)}" ry="{fmt(ry)}" '
            f'fill="url(#k-amb-{_hx(hue)}-{round(op * 100)})"/>')


def legend(x_right, y, narrow=False):
    """Bottom-right key: a mini pill 'tool' and a hue diamond 'pattern', mono, right-aligned at x_right."""
    wt, wp = measure("tool", "ey", narrow), measure("pattern", "ey", narrow)
    x = x_right - (24 + 6 + wt + 16 + 7 + 6 + wp)
    s = TYPE[narrow]["ey"]
    cy = y - s * .36
    return (f'<rect x="{fmt(x)}" y="{fmt(cy - 6)}" width="24" height="12" rx="6" fill="{TEXT}" fill-opacity=".10" '
            f'stroke="{TEXT}" stroke-opacity=".42"/>' + txt(x + 30, y, "tool", "ey") +
            _diamond(x + 30 + wt + 16 + 3.5, cy, MUTED) + txt(x + 30 + wt + 16 + 13, y, "pattern", "ey"))


# ---------------------------------------------------------------- isometric
class Iso:
    """2:1 isometric frame: unit square u,v in [0,1] centred at (cx, cy), half-diagonals a and b; lengths are given at a=100 and scale with a/100."""

    def __init__(self, cx, cy, a, b=None):
        self.cx, self.cy, self.a = cx, cy, a
        self.b = a / 2 if b is None else b
        self.s = a / 100

    def p(self, u, v, h=0):
        """Screen point of ground coords (u, v) raised by height h (a=100 units)."""
        return (self.cx + (u - v) * self.a, self.cy + (u + v - 1) * self.b - h * self.s)

    def box(self, u, v, du, dv, h, hue, z=0, extra=""):
        """Solid block: top = hue + 38% white, left = hue, right = hue 50% into INK (micro-object recipe)."""
        P = lambda uu, vv, hh=0: self.p(uu, vv, hh + z)
        top = [P(u, v, h), P(u + du, v, h), P(u + du, v + dv, h), P(u, v + dv, h)]
        left = [P(u, v + dv), P(u + du, v + dv), P(u + du, v + dv, h), P(u, v + dv, h)]
        right = [P(u + du, v), P(u + du, v + dv), P(u + du, v + dv, h), P(u + du, v, h)]
        return (f'<polygon points="{pts(left)}" fill="{hue}"/>'
                f'<polygon points="{pts(right)}" fill="{mix(hue, INK, .5)}"/>'
                f'<polygon points="{pts(top)}" fill="{mix(hue, WHITE, .38)}"/>' + extra)

    def drum(self, u, v, r, h, hue, z=0):
        """Database drum (cylinder) with a band line, standing on (u, v)."""
        x, y = self.p(u, v, z)
        r, h = r * self.s, h * self.s
        ry = r / 2
        return (f'<path d="M{fmt(x - r)},{fmt(y - h)}V{fmt(y)}A{fmt(r)},{fmt(ry)} 0 0 0 {fmt(x + r)},{fmt(y)}'
                f'V{fmt(y - h)}Z" fill="{hue}"/>'
                f'<path d="M{fmt(x)},{fmt(y - h + ry)}V{fmt(y + ry)}A{fmt(r)},{fmt(ry)} 0 0 0 {fmt(x + r)},{fmt(y)}'
                f'V{fmt(y - h)}Z" fill="{mix(hue, INK, .45)}"/>'
                f'<path d="M{fmt(x - r)},{fmt(y - h / 2)}A{fmt(r)},{fmt(ry)} 0 0 0 {fmt(x + r)},{fmt(y - h / 2)}" '
                f'fill="none" stroke="{INK}" stroke-opacity=".35"/>'
                f'<ellipse cx="{fmt(x)}" cy="{fmt(y - h)}" rx="{fmt(r)}" ry="{fmt(ry)}" fill="{mix(hue, WHITE, .38)}"/>')

    def flat(self, ps, h=0, **attrs):
        """Flat polygon on the ground (or at height h) through uv points; attrs become SVG attributes."""
        return f'<polygon points="{pts([self.p(u, v, h) for u, v in ps])}"{_attrs(attrs)}/>'

    def line(self, u1, v1, u2, v2, h=0, **attrs):
        """Straight line between two uv points at height h; attrs become SVG attributes."""
        (x1, y1), (x2, y2) = self.p(u1, v1, h), self.p(u2, v2, h)
        return f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}"{_attrs(attrs)}/>'


def slab(iso, t, hue):
    """Glass layer slab on iso's unit square: gradient top (62/30/12%), shaded side faces at 92%, back rim in rim tint."""
    cx, cy, a, b = iso.cx, iso.cy, iso.a, iso.b
    tt = t * iso.s
    top = [(cx, cy - b), (cx + a, cy), (cx, cy + b), (cx - a, cy)]
    left = [(cx - a, cy), (cx, cy + b), (cx, cy + b + tt), (cx - a, cy + tt)]
    right = [(cx, cy + b), (cx + a, cy), (cx + a, cy + tt), (cx, cy + b + tt)]
    rim = rim_tint(hue)
    return (f'<polygon points="{pts(left)}" fill="{mix(hue, INK, .42)}" fill-opacity=".92"/>'
            f'<polygon points="{pts(right)}" fill="{mix(hue, INK, .66)}" fill-opacity=".92"/>'
            f'<polygon points="{pts(top)}" fill="url(#k-top-{_hx(hue)})" stroke="{hue}" stroke-opacity=".9"/>'
            f'<polyline points="{pts([(cx - a, cy), (cx, cy - b), (cx + a, cy)])}" fill="none" stroke="{rim}" '
            f'stroke-opacity=".55"/>'
            f'<line x1="{fmt(cx)}" y1="{fmt(cy + b)}" x2="{fmt(cx)}" y2="{fmt(cy + b + tt)}" stroke="{rim}" '
            f'stroke-opacity=".35"/>')


def floor_shadow(x, y, a, b):
    """One soft floor shadow per object group: an iso diamond, black 55%, blurred (stdDeviation 9)."""
    return (f'<polygon points="{pts([(x, y - b), (x + a, y), (x, y + b), (x - a, y)])}" fill="#000" '
            f'fill-opacity=".55" filter="url(#k-blur)"/>')


def plate(x, y, w, h, hue=None, dx=14, dy=9):
    """Cabinet-oblique plate (narrow layouts, lanes, plinths): front face x..x+w-dx, y+dy..y+dy+h; hue=None is a neutral ink plinth."""
    x2 = x + w - dx
    front = [(x, y + dy), (x2, y + dy), (x2, y + dy + h), (x, y + dy + h)]
    top = [(x, y + dy), (x + dx, y), (x + w, y), (x2, y + dy)]
    side = [(x2, y + dy), (x + w, y), (x + w, y + h), (x2, y + dy + h)]
    if hue is None:
        return (f'<polygon points="{pts(side)}" fill="{mix(INK, WHITE, .015)}" stroke="{HAIR}" stroke-opacity="{HAIR_OP}"/>'
                f'<polygon points="{pts(top)}" fill="{mix(INK, WHITE, .06)}" stroke="{HAIR}" stroke-opacity="{HAIR_OP}"/>'
                f'<polygon points="{pts(front)}" fill="{mix(INK, WHITE, .03)}" stroke="{HAIR}" stroke-opacity="{HAIR_OP}"/>')
    return (f'<polygon points="{pts(side)}" fill="{mix(hue, INK, .62)}"/>'
            f'<polygon points="{pts(top)}" fill="{mix(hue, INK, .42)}" stroke="{mix(hue, WHITE, .4)}" '
            f'stroke-opacity=".6" stroke-width=".8"/>'
            f'<polygon points="{pts(front)}" fill="url(#k-front-{_hx(hue)})" stroke="{hue}" stroke-opacity=".75"/>')


def plate_top(x, y, w, dx=14, dy=9):
    """Outline points of a plate's top face (for rim flashes on narrow plates)."""
    return [(x, y + dy), (x + dx, y), (x + w, y), (x + w - dx, y + dy), (x, y + dy)]


def hairline(x1, y1, x2, y2, op=HAIR_OP):
    """Hairline/standoff: 1px white at 16%."""
    return (f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" stroke="{HAIR}" '
            f'stroke-opacity="{fmt(op, 2)}"/>')


# ---------------------------------------------------------------- glyphs
# Every glyph is drawn around its ground centre (x, y); s=1 is the stack-slab scale (a=100).
# Fixed stroke widths stay crisp at any s. Glyph code never sets text.

def racks(x, y, s=1, n=3, hue=INFRA):
    """INFRA: a row of n server racks / pod blocks with two slot lines each."""
    I = Iso(x, y, 100 * s)
    u0 = .5 - (.14 * (n - 1) + .10) / 2
    o = []
    for i in range(n):
        u, v, h = u0 + i * .14, .45, 18 if i % 2 == 0 else 13
        d = "".join(f"M{pts([I.p(u + .015, v + .10, hh)])}L{pts([I.p(u + .085, v + .10, hh)])}"
                    for hh in (h * .45, h * .75))
        o.append(I.box(u, v, .10, .10, h, hue, extra=f'<path d="{d}" stroke="{INK}" stroke-opacity=".45"/>'))
    return "".join(o)


def drums(x, y, s=1, n=3, hue=DATA, grid=False):
    """DATA: n database drums on a diagonal; grid=True puts a 2x2 key grid on the centre drum (content-hash cache)."""
    I = Iso(x, y, 100 * s)
    offs = {1: [(0, 0)], 2: [(-.09, .05), (.09, -.05)], 3: [(-.18, .10), (0, 0), (.18, -.10)]}[n]
    o = []
    for du, dv in offs:
        o.append(I.drum(.5 + du, .5 + dv, 9, 15, hue))
    if grid:
        cx, cy = I.p(.5 + offs[len(offs) // 2][0], .5 + offs[len(offs) // 2][1], 15)
        r = 9 * s
        o.append(f'<path d="M{fmt(cx - r * .7)},{fmt(cy)}H{fmt(cx + r * .7)}M{fmt(cx)},{fmt(cy - r * .36)}'
                 f'V{fmt(cy + r * .36)}" stroke="{INK}" stroke-opacity=".45" stroke-width="1.1"/>')
    return "".join(o)


def graph_tri(x, y, s=1, hue=DATA):
    """DATA: knowledge-graph motif, three nodes linked in a triangle."""
    I = Iso(x, y, 100 * s)
    lite = link_tint(hue)
    nodes = [(.49, .44), (.61, .52), (.41, .54)]
    o = [I.line(*nodes[i], *nodes[j], stroke=lite, stroke_opacity=.7) for i, j in ((0, 1), (0, 2), (1, 2))]
    rx, ry = max(1.8, 3.2 * s), max(1.1, 1.8 * s)
    for u, v in nodes:
        px, py = I.p(u, v)
        o.append(f'<ellipse cx="{fmt(px)}" cy="{fmt(py)}" rx="{fmt(rx)}" ry="{fmt(ry)}" fill="{lite}"/>')
    return "".join(o)


def lanes(x, y, s=1, n=2, hue=MSG):
    """MSG: n parallel sharded lanes carrying small message tiles."""
    I = Iso(x, y, 100 * s)
    o = []
    for i in range(n):
        v = .5 - .045 + (i - (n - 1) / 2) * .16
        o.append(I.flat([(.12, v), (.88, v), (.88, v + .09), (.12, v + .09)],
                        fill=hue, fill_opacity=.22, stroke=hue, stroke_opacity=.55))
        for u in (.26, .46, .66):
            o.append(I.box(u - .10 * (i % 2), v + .015, .09, .06, 6, hue))
    return "".join(o)


def cubes(x, y, s=1, n=4, hue=SVC):
    """SVC: n linked service cubes (2 in a pair, 3 in a row, 4 as a T)."""
    I = Iso(x, y, 100 * s)
    cells = {2: [(.33, .44), (.55, .44)], 3: [(.22, .44), (.44, .44), (.66, .44)],
             4: [(.22, .54), (.44, .54), (.66, .54), (.44, .34)]}[n]
    links = {2: [(0, 1)], 3: [(0, 1), (1, 2)], 4: [(0, 1), (1, 2), (1, 3)]}[n]
    lite = link_tint(hue)
    o = [I.line(cells[i][0] + .06, cells[i][1] + .06, cells[j][0] + .06, cells[j][1] + .06,
                stroke=lite, stroke_opacity=.7) for i, j in links]
    for u, v in sorted(cells, key=lambda c: c[0] + c[1]):
        o.append(I.box(u, v, .12, .12, 11, hue))
    return "".join(o)


def vectors(x, y, s=1, hue=RETR, n=16, seed=7, link=False):
    """RETR: a seeded scatter of vector points; link=True joins three of them with a 3-node link."""
    I = Iso(x, y, 100 * s)
    rnd = random.Random(seed)
    lite = link_tint(hue)
    o, kept = [], []
    for _ in range(n):
        u, v = rnd.uniform(.08, .83), rnd.uniform(.34, .70)
        if u + v < .70:
            continue
        kept.append((u, v))
        px, py = I.p(u, v)
        o.append(f'<ellipse cx="{fmt(px)}" cy="{fmt(py)}" rx="{fmt(max(1.3, 2 * s))}" ry="{fmt(max(.9, 1.2 * s))}" '
                 f'fill="{lite}" fill-opacity=".75"/>')
    if link and len(kept) >= 3:
        a, b, c = kept[0], kept[len(kept) // 2], kept[-1]
        o.append(f'<polyline points="{pts([I.p(*a), I.p(*b), I.p(*c)])}" fill="none" stroke="{tech_tint(hue)}" '
                 f'stroke-opacity=".85"/>')
        for q in (a, b, c):
            px, py = I.p(*q)
            o.append(f'<circle cx="{fmt(px)}" cy="{fmt(py)}" r="{fmt(max(1.6, 2.4 * s))}" fill="{tech_tint(hue)}"/>')
    return "".join(o)


def lens(x, y, s=1, hue=RETR, seed=7):
    """RETR: a lens ring with a handle over a vector scatter, three picked points lit white."""
    I = Iso(x, y, 100 * s)
    lite = link_tint(hue)
    hx, hy = I.p(.5, .5)
    o = [vectors(x, y, s, hue, 16, seed),
         f'<ellipse cx="{fmt(hx)}" cy="{fmt(hy)}" rx="{fmt(20 * s)}" ry="{fmt(10 * s)}" fill="{hue}" '
         f'fill-opacity=".18" stroke="{lite}" stroke-width="1.2"/>',
         f'<line x1="{fmt(hx + 15 * s)}" y1="{fmt(hy + 7 * s)}" x2="{fmt(hx + 27 * s)}" y2="{fmt(hy + 15 * s)}" '
         f'stroke="{lite}" stroke-width="{fmt(max(1.5, 3 * s))}" stroke-linecap="round"/>']
    for du, dv in ((-.05, .02), (.04, -.03), (.03, .05)):
        px, py = I.p(.5 + du, .5 + dv)
        o.append(f'<circle cx="{fmt(px)}" cy="{fmt(py)}" r="{fmt(max(1.2, 2.3 * s))}" fill="#FFFFFF"/>')
    return "".join(o)


def orb(x, y, r, lift=None, shadow=True, ring=False):
    """AGENT: glowing violet orb hovering over ground point (x, y) with a soft contact shadow; ring=True marks a nested workflow."""
    lift = 1.6 * r if lift is None else lift
    oy = y - lift
    o = []
    if shadow:
        o.append(f'<ellipse cx="{fmt(x)}" cy="{fmt(y)}" rx="{fmt(r * 1.3)}" ry="{fmt(r * .6)}" fill="#000" '
                 f'fill-opacity=".35"/>')
    if ring:
        o.append(f'<circle cx="{fmt(x)}" cy="{fmt(oy)}" r="{fmt(r * 1.75)}" fill="{AGENT}" fill-opacity=".06" '
                 f'stroke="{AGENT}" stroke-opacity=".45"/>')
    o.append(f'<circle cx="{fmt(x)}" cy="{fmt(oy)}" r="{fmt(r * 1.9)}" fill="{ORB_GLOW}" fill-opacity=".45" '
             f'filter="url(#k-glow)"/><circle cx="{fmt(x)}" cy="{fmt(oy)}" r="{fmt(r)}" fill="url(#k-orb)"/>')
    return "".join(o)


def orchestrator(x, y, s=1, n=2):
    """AGENT: a larger orchestrator orb linked by hairlines (hue + 35% white, 75%) to n sub-agent orbs."""
    I = Iso(x, y, 100 * s)
    subs = [(-.26, .14), (.22, -.14), (-.04, .26), (.26, .10)][:n]
    main = (I.p(.5, .5), 15 * s, 7.5 * s)
    spots = [(I.p(.5 + du, .5 + dv), 9 * s, 5.5 * s) for du, dv in subs]
    lite = link_tint(AGENT)
    o = []
    (mx, my), mh, _ = main
    for (px, py), h, r in spots:
        o.append(f'<line x1="{fmt(mx)}" y1="{fmt(my - mh)}" x2="{fmt(px)}" y2="{fmt(py - h)}" stroke="{lite}" '
                 f'stroke-opacity=".75"/>')
    for (px, py), h, r in sorted(spots + [main], key=lambda q: q[0][1]):
        o.append(orb(px, py, r, lift=h))
    return "".join(o)


def person(x, y, s=1, hue=TRUST):
    """TRUST: upright head-and-shoulders human figure standing on ground point (x, y)."""
    r, hr = 7 * s, 4 * s
    return (f'<ellipse cx="{fmt(x)}" cy="{fmt(y)}" rx="{fmt(r * 1.1)}" ry="{fmt(r * .42)}" fill="#000" fill-opacity=".35"/>'
            f'<path d="M{fmt(x - r)},{fmt(y - s)}A{fmt(r)},{fmt(r)} 0 0 1 {fmt(x + r)},{fmt(y - s)}Z" '
            f'fill="{mix(hue, WHITE, .42)}" stroke="{INK}" stroke-opacity=".5" stroke-width=".8"/>'
            f'<circle cx="{fmt(x)}" cy="{fmt(y - s - r - 1.6 * s - hr)}" r="{fmt(hr)}" fill="{mix(hue, WHITE, .7)}" '
            f'stroke="{INK}" stroke-opacity=".5" stroke-width=".8"/>')


def gate(x, y, s=1, hue=TRUST, figure=True):
    """TRUST: human gate, two posts and a lintel, with a head-and-shoulders figure standing just right of it."""
    I = Iso(x, y, 100 * s)
    door = [I.p(.31, .475), I.p(.46, .475), I.p(.46, .475, 20), I.p(.31, .475, 20)]
    o = [I.box(.26, .45, .05, .05, 22, hue),
         f'<polygon points="{pts(door)}" fill="{hue}" fill-opacity=".24"/>',
         I.box(.46, .45, .05, .05, 22, hue), I.box(.26, .45, .25, .05, 4, hue, z=20)]
    if figure:
        o.append(person(*I.p(.66, .53), s=s, hue=hue))
    return "".join(o)


def check_tile(x, y, s=1, hue=TRUST):
    """TRUST: a sealed azure tile carrying a white check."""
    I = Iso(x, y, 100 * s)
    mx, my = I.p(.5, .5)
    return (I.flat([(.31, .31), (.69, .31), (.69, .69), (.31, .69)], fill=hue, fill_opacity=.20,
                   stroke=link_tint(hue), stroke_opacity=.9) +
            f'<path d="M{fmt(mx - 12 * s)},{fmt(my - 3 * s)}L{fmt(mx - 4 * s)},{fmt(my + 5 * s)}L{fmt(mx + 13 * s)},'
            f'{fmt(my - 11 * s)}" fill="none" stroke="#FFFFFF" stroke-width="{fmt(max(1.4, 2.6 * s))}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def ledger(x, y, s=1, hue=TRUST):
    """TRUST: audit ledger, three stacked azure sheets with rule lines on the top one."""
    I = Iso(x, y, 100 * s)
    o = [I.box(.42, .39, .16, .22, 3, hue, z=i * 4.5) for i in range(3)]
    for k in (1, 2, 3):
        v = .39 + .055 * k
        o.append(I.line(.45, v, .55, v, 12, stroke=INK, stroke_opacity=.4))
    return "".join(o)


def bookmark(x, y, s=1, hue=TRUST):
    """TRUST: citation/provenance bookmark ribbon standing on point (x, y)."""
    w, h = 3.2 * s, 12 * s
    return (f'<path d="M{fmt(x - w)},{fmt(y - h)}H{fmt(x + w)}V{fmt(y)}L{fmt(x)},{fmt(y - 3 * s)}L{fmt(x - w)},{fmt(y)}Z" '
            f'fill="{hue}" stroke="{INK}" stroke-opacity=".35" stroke-width=".6"/>')


def _sheet(I, z=0, lines=3, op=.85, mark=None, mark_hue=TRUST, ruled=True):
    """One iso paper sheet on local frame I at height z (helper for the document glyphs)."""
    u0, v0, du, dv = .34, .30, .32, .40
    o = [I.box(u0, v0, du, dv, 1.6, mix(RESULT, INK, .35), z=z).replace(
        f'fill="{mix(mix(RESULT, INK, .35), WHITE, .38)}"', f'fill="{RESULT}" fill-opacity="{fmt(op, 2)}"')]
    if ruled:
        for k in range(1, lines + 1):
            v = v0 + dv * k / (lines + 1)
            u1 = u0 + du - (.12 if k == lines else .06)
            if mark is not None and k - 1 == mark:
                o.append(I.flat([(u0 + .04, v - .025), (u0 + du - .04, v - .025), (u0 + du - .04, v + .025),
                                 (u0 + .04, v + .025)], h=z + 1.6, fill=mark_hue, fill_opacity=.85))
            else:
                o.append(I.line(u0 + .05, v, u1, v, z + 1.6, stroke=INK, stroke_opacity=.25,
                                stroke_width=fmt(max(.8, 1.2 * I.s), 2)))
    return "".join(o)


def sheet(x, y, s=1, lines=3, tab=None, bookmark_tab=False, mark=None, op=.85):
    """Document sheet: ivory top (85%) with rule lines; tab=hue adds an edge tab, bookmark_tab pins a citation, mark=i highlights line i in azure."""
    I = Iso(x, y, 100 * s)
    o = [_sheet(I, 0, lines, op, mark)]
    if tab:
        o.append(I.flat([(.66, .34), (.72, .34), (.72, .44), (.66, .44)], h=1.6, fill=tab))
    if bookmark_tab:
        o.append(bookmark(*I.p(.6, .33, 1.6), s=s))
    return "".join(o)


def sheet_stack(x, y, s=1, n=6, gap=2):
    """Large document set: n sheets stacked with a fixed screen-px offset, rule lines on the top sheet only."""
    I = Iso(x, y, 100 * s)
    return "".join(_sheet(I, i * gap / I.s, ruled=(i == n - 1)) for i in range(n))


def chunk(x, y, s=1, hue=RETR):
    """Chunk: a small sheet with a RETR tab."""
    return sheet(x, y, s * .55, lines=2, tab=hue)


def doc_model(x, y, s=1, hue=DATA):
    """Document model ('digital twin'): a sheet resolving into a small grid of DATA cells."""
    I = Iso(x, y, 100 * s)
    o = [sheet(*I.p(.30, .42), s=s)]
    lite = link_tint(hue)
    o.append(I.line(.53, .50, .60, .50, 1.6, stroke=lite, stroke_opacity=.6, stroke_dasharray="1.5 2"))
    for j in range(3):
        for i in range(2):
            o.append(I.box(.62 + i * .10, .34 + j * .10, .08, .08, 4 + 2 * ((i + j) % 2), hue))
    return "".join(o)


def diff(x, y, s=1, hue=TRUST):
    """Change detection: the old sheet behind, the amended sheet in front with its changed line lit in azure."""
    I = Iso(x, y, 100 * s)
    return (sheet(*I.p(.40, .40), s=s, op=.4) + sheet(*I.p(.56, .58), s=s, mark=1) +
            f'<circle cx="{fmt(I.p(.42, .79)[0])}" cy="{fmt(I.p(.42, .79)[1])}" r="{fmt(max(1.6, 2.4 * s))}" '
            f'fill="{hue}"/>')


def layer_scene(key, iso):
    """The micro-scene that says what a layer does, composed from the glyphs on the visible front half of a slab."""
    s, p = iso.s, iso.p
    if key == "INFRA":
        return racks(*p(.63, .85), s=s, n=5)
    if key == "DATA":
        return drums(*p(.68, .70), s=s) + graph_tri(*p(.213, .98), s=s)
    if key == "MSG":
        return lanes(*p(.60, .825), s=s)
    if key == "SVC":
        return cubes(*p(.58, .76), s=s)
    if key == "RETR":
        return lens(*p(.62, .80), s=s)
    if key == "AGENT":
        return orchestrator(*p(.66, .72), s=s)
    if key == "TRUST":
        return check_tile(*p(.45, .39), s=s) + ledger(*p(.82, .61), s=s) + gate(*p(.54, .83), s=s)
    raise KeyError(key)


# ---------------------------------------------------------------- the LLM core
def tick_ring(cx, cy, rx, hue, op=.7, a0=-10, a1=190, step=6, tick=3):
    """Still flat ellipse ring (ry = 0.8 rx), 1.5px, with fine outward ticks (ring hue 35%) from angle a0 to a1 (deg, y down)."""
    ry = rx * .8
    d = []
    for a in range(a0, a1 + 1, step):
        t = math.radians(a)
        px, py = cx + rx * math.cos(t), cy + ry * math.sin(t)
        nx, ny = math.cos(t) / rx, math.sin(t) / ry
        L = math.hypot(nx, ny)
        d.append(f"M{fmt(px)},{fmt(py)}l{fmt(nx / L * tick)},{fmt(ny / L * tick)}")
    return (f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="{fmt(rx)}" ry="{fmt(ry)}" fill="none" stroke="{hue}" '
            f'stroke-opacity="{fmt(op, 2)}" stroke-width="1.5"/>'
            f'<path d="{"".join(d)}" stroke="{hue}" stroke-opacity=".35"/>')


def ring_point(cx, cy, rx, angle):
    """Point on a tick_ring ellipse at angle (deg, 0 = right, y down)."""
    t = math.radians(angle)
    return cx + rx * math.cos(t), cy + rx * .8 * math.sin(t)


def css_drift(prefix, amp, seed, n=6):
    """Particle drift: n irregular closed translate loops named prefix0..prefix{n-1} (amplitude amp px)."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        q = [(rnd.uniform(-1, 1) * amp, rnd.uniform(-1, 1) * amp) for _ in range(3)]
        out.append(f"@keyframes {prefix}{i}{{0%,100%{{transform:none}}" +
                   "".join(f"{pc}%{{transform:translate({fmt(dx)}px,{fmt(dy)}px)}}"
                           for pc, (dx, dy) in zip((27, 55, 80), q)) + "}")
    return "".join(out)


def llm_core(cx, cy, r, uid, n=24, seed=3, rings=(), node_angle=None, label="LLM", label_size=13,
             drift=True, period=(6.2, 11.0)):
    """The LLM core motif (hero, pipeline, footer): glass violet orb, soft glow, seeded drifting particles, optional still tick rings and ring nodes; returns (css, svg)."""
    rnd = random.Random(seed)
    css, o = [], []
    o.append(f'<circle class="{uid}g" cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r * 1.75)}" '
             f'fill="url(#k-amb-{_hx(ORB_GLOW)}-60)"/>')
    for rx, hue, op in rings:
        o.append(tick_ring(cx, cy, rx, hue, op))
    o.append(f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" fill="url(#k-orb)" fill-opacity=".72" '
             f'stroke="{mix(AGENT, WHITE, .5)}" stroke-opacity=".5"/>')
    amp = max(1.5, min(9, r * .26))
    if drift:
        css.append(css_breath(f"{uid}g", 7))
        css.append(css_drift(f"{uid}p", amp, seed + 1))
    for j in range(n):
        ang = rnd.uniform(0, 2 * math.pi)
        rad = (r - amp - 2) * math.sqrt(rnd.random())
        pr = rnd.uniform(1.1, 2.2) * min(1, math.sqrt(r / 34))
        col = PARTICLES[j % 2]
        op = rnd.uniform(.7, 1)
        st = ""
        if drift:
            st = (f' style="animation:{uid}p{j % 6} {fmt(rnd.uniform(*period), 2)}s ease-in-out '
                  f'-{fmt(rnd.uniform(0, period[1]), 2)}s infinite"')
        o.append(f'<circle cx="{fmt(cx + rad * math.cos(ang))}" cy="{fmt(cy + rad * math.sin(ang))}" r="{fmt(pr)}" '
                 f'fill="{col}" fill-opacity="{fmt(op, 2)}"{st}/>')
    if label:
        o.append(f'<text x="{fmt(cx)}" y="{fmt(cy + label_size * .36)}" text-anchor="middle" '
                 f'style="font:700 {fmt(label_size)}px {SANS}" fill="#FFFFFF">{esc(label)}</text>')
    if node_angle is not None:
        for rx, hue, op in rings:
            o.append(ring_tap(*ring_point(cx, cy, rx, node_angle), hue, fill=hue))
    return "".join(css), "".join(o)


# ---------------------------------------------------------------- flows and labels
def chevron(x, y, angle, hue, op=.85, size=4.5, w=1.5):
    """Open chevron arrowhead with its tip at (x, y), pointing along angle (radians)."""
    a1, a2 = angle + math.pi - .66, angle + math.pi + .66
    return (f'<path d="M{fmt(x + size * math.cos(a1))},{fmt(y + size * math.sin(a1))}L{fmt(x)},{fmt(y)}'
            f'L{fmt(x + size * math.cos(a2))},{fmt(y + size * math.sin(a2))}" fill="none" stroke="{hue}" '
            f'stroke-opacity="{fmt(op, 2)}" stroke-width="{fmt(w)}" stroke-linecap="round" stroke-linejoin="round"/>')


def conn(points, hue, op=.55, w=1.5, arrow=True, dash=None, cls=None):
    """Connector polyline in the source hue (1.5px, round caps) with a chevron; cls on an undashed line adds pathLength=1 for css_draw."""
    d = "M" + "L".join(f"{fmt(x)},{fmt(y)}" for x, y in points)
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    if cls:
        extra += f' class="{cls}"' + ("" if dash else ' pathLength="1"')
    o = (f'<path d="{d}" fill="none" stroke="{hue}" stroke-opacity="{fmt(op, 2)}" stroke-width="{fmt(w)}" '
         f'stroke-linecap="round" stroke-linejoin="round"{extra}/>')
    if arrow:
        (x1, y1), (x2, y2) = points[-2], points[-1]
        o += chevron(x2, y2, math.atan2(y2 - y1, x2 - x1), hue, min(1, op + .3))
    return o


_ISO_AXES = {"u": (2 / math.sqrt(5), 1 / math.sqrt(5)), "v": (-2 / math.sqrt(5), 1 / math.sqrt(5)), "z": (0, -1)}


def iso_points(x, y, moves):
    """Points along iso axes from (x, y): moves = [('u'|'v'|'z', signed px), ...]; u runs down-right, v down-left, z up."""
    ps = [(x, y)]
    for axis, d in moves:
        ax, ay = _ISO_AXES[axis]
        x, y = x + ax * d, y + ay * d
        ps.append((x, y))
    return ps


def iso_conn(x, y, moves, hue, **kw):
    """Connector that runs along iso axes (+-26.57 deg and vertical); kwargs as conn()."""
    return conn(iso_points(x, y, moves), hue, **kw)


def eval_loop(points, arrow=True, cls=None):
    """Feedback/eval loop: EVAL mint dashed (2 4) connector."""
    return conn(points, EVAL, op=.8, arrow=arrow, dash="2 4", cls=cls)


def cache_arc(x1, y1, x2, y2, bend, cls=None):
    """Cache-hit bypass: DATA tangerine dashed (2 4) quadratic arc from (x1, y1) to (x2, y2), bowed by bend px (+ = down)."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + bend
    c = f' class="{cls}"' if cls else ""
    return (f'<path d="M{fmt(x1)},{fmt(y1)}Q{fmt(mx)},{fmt(my)} {fmt(x2)},{fmt(y2)}" fill="none" stroke="{DATA}" '
            f'stroke-opacity=".85" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="2 4"{c}/>' +
            chevron(x2, y2, math.atan2(y2 - my, x2 - mx), DATA, 1))


def ring_tap(x, y, hue, r=4, fill=INK):
    """Instrument ring tap: r 4, 2px stroke in the rail hue, ink fill."""
    return (f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}" fill="{fill}" stroke="{hue}" stroke-width="2"/>')


def feeder(x1, y1, x2, y2, hue, op=.45):
    """Dotted feeder (1.5 3) joining a tap to what it measures."""
    return (f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" stroke="{hue}" '
            f'stroke-opacity="{fmt(op, 2)}" stroke-dasharray="1.5 3"/>')


def conduit(x1, y1, x2, y2, hue, cls=None):
    """Measurement conduit (OBS/EVAL rail): 5px stroke at 90% plus a 2px ink inner line at 45%; cls adds pathLength=1."""
    c = f' class="{cls}" pathLength="1"' if cls else ""
    ln = f'x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}"'
    return (f'<line {ln} stroke="{hue}" stroke-opacity=".9" stroke-width="5" stroke-linecap="round"{c}/>'
            f'<line {ln} stroke="{INK}" stroke-opacity=".45" stroke-width="2"{c}/>')


def leader(x1, y1, x2, y2, hue, op=.55):
    """Callout leader: dotted hue line (1.5 3) ending in a 2.5px hue dot at (x2, y2)."""
    return (f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" stroke="{hue}" '
            f'stroke-opacity="{fmt(op, 2)}" stroke-dasharray="1.5 3"/>'
            f'<circle cx="{fmt(x2)}" cy="{fmt(y2)}" r="2.5" fill="{hue}"/>')


def _diamond(cx, cy, hue, r=3.4):
    """Small filled diamond marker (technique), drawn as a shape."""
    return f'<path d="M{fmt(cx)},{fmt(cy - r)}l{fmt(r)},{fmt(r)} -{fmt(r)},{fmt(r)} -{fmt(r)},-{fmt(r)}z" fill="{hue}"/>'


def pill_width(text, narrow=False, pad=9):
    """Width of a tool pill."""
    return measure(text, "c", narrow) + 2 * pad


def tech_width(text, narrow=False):
    """Width of a technique label (diamond + text)."""
    return 13 + measure(text, "t", narrow)


def pill(x, cy, text, hue, narrow=False, pad=9):
    """Tool chip: pill (hue fill 13%, stroke 42%, 20px tall wide / 22 narrow) with neutral text; returns (svg, width)."""
    w = pill_width(text, narrow, pad)
    h = 22 if narrow else 20
    return (f'<rect x="{fmt(x)}" y="{fmt(cy - h / 2)}" width="{fmt(w)}" height="{h}" rx="{fmt(h / 2)}" fill="{hue}" '
            f'fill-opacity=".13" stroke="{hue}" stroke-opacity=".42"/>' +
            txt(x + pad, cy + TYPE[narrow]["c"] * .36, text, "c"), w)


def tech(x, cy, text, hue, narrow=False):
    """Technique label: hue diamond plus text in tech_tint(hue), no box; returns (svg, width)."""
    return (_diamond(x + 3.4, cy, hue) + txt(x + 13, cy + TYPE[narrow]["t"] * .36, text, "t", tech_tint(hue)),
            tech_width(text, narrow))


def chips_layout(tools, techs, maxw, narrow=False, first=None, gap=6):
    """Lay tools (in order) then techniques into the fewest lines of width maxw (first: width of line 1); returns [[(kind, text, w)], ...]."""
    T = [("tool", s, pill_width(s, narrow)) for s in tools]
    P = [("tech", s, tech_width(s, narrow)) for s in techs]
    for it in T + P:
        assert_within(it[2], min(maxw, first or maxw), f"chip '{it[1]}'")
    best = [None]

    def solve(ti, rem, lines):
        if ti == len(T) and not rem:
            if best[0] is None or len(lines) < len(best[0]):
                best[0] = lines
            return
        if best[0] is not None and len(lines) + 1 >= len(best[0]):
            return
        cap = first if (first and not lines) else maxw
        kmax, used = 0, 0
        while ti + kmax < len(T) and used + T[ti + kmax][2] + (gap if kmax else 0) <= cap:
            used += T[ti + kmax][2] + (gap if kmax else 0)
            kmax += 1
        for k in range(kmax, -1 if ti == len(T) else 0, -1):   # technique-only lines come after all tools
            line = T[ti:ti + k]
            base = sum(i[2] for i in line) + gap * max(0, k - 1)
            tried = []
            # first-fit in script order, then best-fit decreasing; the first layout with the fewest lines wins
            for order in (sorted(rem), sorted(rem, key=lambda j: (-P[j][2], j))):
                u, pick = base, []
                for j in order:
                    need = P[j][2] + (2 * gap if (line or pick) else 0)
                    if u + need <= cap:
                        pick.append(j)
                        u += need
                if (not line and not pick) or sorted(pick) in tried:
                    continue
                tried.append(sorted(pick))
                solve(ti + k, tuple(j for j in rem if j not in pick), lines + [line + [P[j] for j in sorted(pick)]])

    solve(0, tuple(range(len(P))), [])
    return best[0] or []


def chips_svg(lines, x0, y0, lh, hue, narrow=False, gap=6):
    """Draw chips_layout lines from (x0, y0 = first line centre) at line pitch lh; returns (svg, max right x)."""
    o, right = [], x0
    for li, line in enumerate(lines):
        x, cy = x0, y0 + li * lh
        for i, (kind, s, w) in enumerate(line):
            if i:
                x += 2 * gap if kind == "tech" else gap
            o.append((pill if kind == "tool" else tech)(x, cy, s, hue, narrow)[0])
            x += w
        right = max(right, x)
    return "".join(o), right


def numeral(x, y, text, hue, size=None, anchor="start", narrow=False):
    """Big result numeral (sans 700 tabular, ivory) with a 2px underline in the stage hue; returns (svg, width)."""
    size = size or TYPE[narrow]["num"]
    w = tw(text, size, bold=True)
    x0 = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    st = f' style="font-size:{fmt(size)}px"' if size != TYPE[narrow]["num"] else ""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{fmt(x)}" y="{fmt(y)}" class="num"{a}{st}>{esc(text)}</text>'
            f'<rect x="{fmt(x0)}" y="{fmt(y + 6)}" width="{fmt(w)}" height="2" rx="1" fill="{hue}"/>', w)


def note(x, y, text, narrow=False, fill=None, anchor=None):
    """Serif italic annotation (words only, at most 3 per card)."""
    return txt(x, y, text, "an", fill, anchor)


# ---------------------------------------------------------------- motion (CSS text, literal values)
EASE = "cubic-bezier(.2,.8,.2,1)"


def delay(t):
    """Inline style attribute setting one element's animation-delay (seconds)."""
    return f' style="animation-delay:{fmt(t, 2)}s"'


def css_drop(cls, dist=22, dur=.75, delay=0):
    """Build: fade in while dropping dist px into place (fill both: the base attributes are the finished frame)."""
    return (f"@keyframes k{cls}{{from{{opacity:0;transform:translateY(-{fmt(dist)}px)}}to{{opacity:1;transform:none}}}}"
            f".{cls}{{animation:k{cls} {fmt(dur, 2)}s {EASE} {fmt(delay, 2)}s both}}")


def css_rise(cls, dist=8, dur=.6, delay=0):
    """Build: fade in while rising dist px (fill both)."""
    return (f"@keyframes k{cls}{{from{{opacity:0;transform:translateY({fmt(dist)}px)}}to{{opacity:1;transform:none}}}}"
            f".{cls}{{animation:k{cls} {fmt(dur, 2)}s {EASE} {fmt(delay, 2)}s both}}")


def css_fade(cls, dur=.4, delay=0, dx=0):
    """Build: fade in, optionally sliding dx px in from the left (fill both)."""
    fr = f"opacity:0;transform:translateX(-{fmt(dx)}px)" if dx else "opacity:0"
    to = "opacity:1;transform:none" if dx else "opacity:1"
    return (f"@keyframes k{cls}{{from{{{fr}}}to{{{to}}}}}"
            f".{cls}{{animation:k{cls} {fmt(dur, 2)}s ease-out {fmt(delay, 2)}s both}}")


def css_draw(cls, dur=1.1, delay=0):
    """Build: line draw on elements with pathLength=1 (dashoffset 1 -> 0, fill both)."""
    return (f"@keyframes k{cls}{{from{{stroke-dashoffset:1;opacity:0}}8%{{opacity:1}}to{{stroke-dashoffset:0;opacity:1}}}}"
            f".{cls}{{stroke-dasharray:1;animation:k{cls} {fmt(dur, 2)}s ease-out {fmt(delay, 2)}s both}}")


def css_dash(cls, cycle, t0, t1, delay=0):
    """Loop: a short dash travels a pathLength=100 path between t0% and t1% of each cycle; hidden otherwise."""
    return (f"@keyframes k{cls}{{0%{{opacity:0;stroke-dashoffset:0}}{fmt(t0, 2)}%{{opacity:0;stroke-dashoffset:0}}"
            f"{fmt(t0 + .5, 2)}%{{opacity:1}}{fmt(t1 - .5, 2)}%{{opacity:1}}"
            f"{fmt(t1, 2)}%{{opacity:0;stroke-dashoffset:-96}}100%{{opacity:0;stroke-dashoffset:-96}}}}"
            f".{cls}{{opacity:0;stroke-dasharray:4 96;animation:k{cls} {fmt(cycle, 2)}s linear {fmt(delay, 2)}s infinite}}")


def css_move(cls, cycle, stops, delay=0):
    """Loop: translate a token through stops [(pct, dx, dy, opacity)] each cycle (linear); hidden at rest and in reduced motion."""
    stops = sorted(stops)
    if stops[0][0] > 0:
        stops = [(0, stops[0][1], stops[0][2], 0)] + stops
    if stops[-1][0] < 100:
        stops = stops + [(100, stops[-1][1], stops[-1][2], 0)]
    kf = "".join(f"{fmt(pc, 2)}%{{opacity:{fmt(op, 2)};transform:translate({fmt(dx)}px,{fmt(dy)}px)}}"
                 for pc, dx, dy, op in stops)
    return (f"@keyframes k{cls}{{{kf}}}"
            f".{cls}{{opacity:0;animation:k{cls} {fmt(cycle, 2)}s linear {fmt(delay, 2)}s infinite}}")


def css_flash(cls, cycle, up=3, gone=14, peak=1):
    """Loop: rim flash, up in `up`% and gone by `gone`% of the cycle; set each element's delay to t_cross - up/100*cycle."""
    return (f"@keyframes k{cls}{{0%{{opacity:0}}{fmt(up, 2)}%{{opacity:{fmt(peak, 2)}}}{fmt(gone, 2)}%,100%{{opacity:0}}}}"
            f".{cls}{{opacity:0;animation:k{cls} {fmt(cycle, 2)}s linear infinite}}")


def css_breath(cls, cycle=7, lo=.84):
    """Loop: glow breath, opacity 1 -> lo -> 1 (about +-8%); base state is fully lit."""
    return (f"@keyframes k{cls}{{0%,100%{{opacity:1}}50%{{opacity:{fmt(lo, 2)}}}}}"
            f".{cls}{{animation:k{cls} {fmt(cycle, 2)}s ease-in-out infinite}}")


def pulse(cls, stops, hues, cycle, delay=0, core=2.6, halo=11, fade=(4, 6)):
    """Hue-tracking request pulse: white core, halo whose hue switches at hues [(pct, hue)], moving through stops [(pct, x, y)]; returns (css, svg)."""
    (p0, x0, y0), pl = stops[0], stops[-1][0]

    def at(pc):
        for (a, xa, ya), (b, xb, yb) in zip(stops, stops[1:]):
            if a <= pc <= b:
                t = 0 if b == a else (pc - a) / (b - a)
                return xa + (xb - xa) * t - x0, ya + (yb - ya) * t - y0
        return (stops[0][1] - x0, stops[0][2] - y0) if pc < p0 else (stops[-1][1] - x0, stops[-1][2] - y0)

    keys = sorted(set([0, 100, p0, min(p0 + fade[0], pl), pl, min(pl + fade[1], 100)] + [s[0] for s in stops]))
    kf = []
    for pc in keys:
        op = 0 if (pc <= p0 or pc >= pl + fade[1]) else (min(1, (pc - p0) / fade[0]) if pc < p0 + fade[0] else 1)
        dx, dy = at(pc)
        kf.append(f"{fmt(pc, 2)}%{{opacity:{fmt(op, 2)};transform:translate({fmt(dx)}px,{fmt(dy)}px)}}")
    css = [f"@keyframes k{cls}{{{''.join(kf)}}}",
           f".{cls}{{opacity:0;animation:k{cls} {fmt(cycle, 2)}s linear {fmt(delay, 2)}s infinite}}"]
    svg = [f'<g class="{cls}">']
    for i, (pc, hue) in enumerate(hues):
        nxt = hues[i + 1][0] if i + 1 < len(hues) else 100
        if len(hues) > 1:
            d = {}
            if pc <= 0:
                d[0] = 1
            else:
                d[pc - .8], d[pc + .8] = 0, 1
            if nxt >= 100:
                d[100] = 1
            else:
                d[nxt - .8], d[nxt + .8] = 1, 0
            d.setdefault(0, 0)
            d.setdefault(100, 0)
            kf = "".join(f"{fmt(k, 2)}%{{opacity:{v}}}" for k, v in sorted(d.items()))
            css.append(f"@keyframes k{cls}h{i}{{{kf}}}"
                       f".{cls}h{i}{{animation:k{cls}h{i} {fmt(cycle, 2)}s linear {fmt(delay, 2)}s infinite}}")
        svg.append(f'<circle class="{cls}h{i}" cx="{fmt(x0)}" cy="{fmt(y0)}" r="{fmt(halo)}" '
                   f'fill="url(#k-pg-{_hx(hue)})"/>')
    svg.append(f'<circle cx="{fmt(x0)}" cy="{fmt(y0)}" r="{fmt(core)}" fill="#FFFFFF"/></g>')
    return "".join(css), "".join(svg)
