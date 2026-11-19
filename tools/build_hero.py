#!/usr/bin/env python3
"""Build the hero schematic SVGs into assets/.

One template (TEMPLATE), two layouts (WIDE 850x400, NARROW 400x660) and three
colour themes give the five files. The hero opens the drawing sheet that the
footer title block closes: same insets, stroke weights, colours and font.

The static file IS the final frame. Everything that will move has a stable id,
every path that will draw has pathLength="1", and each rotating part is a parent
<g transform="translate(pivot) rotate(final)"> around an empty child <g id=...>,
so the child can be animated with a plain CSS rotate about its own origin
(the pivot). Moving ids: noise, loop, loop-head, validated, valve-fill,
valve-lever, clean, clean-head, check-1, check-2, check-3, needle-live.
The same CSS works in every file, with no transform-origin needed: frame zero is
#needle-live rotate(-48deg) (back to 70), #valve-lever rotate(-90deg) (closed,
across the pipe), #valve-fill opacity 1, drawn paths dashoffset 1, heads opacity 0.
The dashed #tap must not get pathLength (it would rescale its dashes).
The animation CSS goes in MOTION_CSS; while it is empty the files are still.

Run from the repo root:  python3 tools/build_hero.py
"""
import math
from pathlib import Path
from string import Template

ASSETS = Path(__file__).resolve().parent.parent / "assets"

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "light": {"ink": "#1f2328", "muted": "#59636e", "frame": "#818b98", "accent": "#1a7f37"},
    "dark": {"ink": "#e6edf3", "muted": "#9198a1", "frame": "#656c76", "accent": "#3fb950"},
    "neutral": {"ink": "#6e7781", "muted": "#8c959f", "frame": "#8c959f", "accent": "#2da44e"},
}

# file name -> (layout, theme)
FILES = {
    "hero-schematic-light.svg": ("wide", "light"),
    "hero-schematic-dark.svg": ("wide", "dark"),
    "hero-schematic-narrow-light.svg": ("narrow", "light"),
    "hero-schematic-narrow-dark.svg": ("narrow", "dark"),
    "hero-schematic.svg": ("wide", "neutral"),
}

# Animation CSS (@keyframes plus the reduced-motion rule). Empty = still frame.
# Plays once: every keyframe holds only the 'from' state and uses fill-mode
# backwards, so each element ends on its own static attributes (the final frame).
# Rotations need no transform-origin: each child <g>'s local origin is already the pivot.
MOTION_CSS = """
#noise,#loop,#validated,#clean,#check-1,#check-2,#check-3{stroke-dasharray:1}
#noise{animation:draw .8s linear backwards}
#loop{animation:draw .8s ease-out .8s backwards}
#loop-head{animation:show .15s linear 1.45s backwards}
#validated{animation:draw .4s ease-out 1.2s backwards}
#valve-fill{animation:solid .6s cubic-bezier(.45,0,.55,1) 1.6s backwards}
#valve-lever{animation:closed .6s cubic-bezier(.45,0,.55,1) 1.6s backwards}
#clean{animation:draw 1s ease-out 2.2s backwards}
#clean-head{animation:show .1s linear 3.1s backwards}
#check-1{animation:draw .2s ease-out 3s backwards}
#check-2{animation:draw .2s ease-out 3.3s backwards}
#check-3{animation:draw .2s ease-out 3.6s backwards}
#needle-live{animation:at70 3s cubic-bezier(.22,1,.36,1) .8s backwards}
@keyframes draw{from{stroke-dashoffset:1}}
@keyframes show{from{opacity:0}}
@keyframes solid{from{opacity:1}}
@keyframes closed{from{transform:rotate(-90deg)}}
@keyframes at70{from{transform:rotate(-48deg)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""

TITLE = ("Process schematic: a noisy, probabilistic signal from an LLM passes through "
         "deterministic validation (a control loop), then "
         "through a human-in-the-loop gate, and comes out as a clean record written to an "
         "audit trail (extracted, validated, reviewed; 21 CFR Part 11). A gauge labeled "
         "yield shows gap-assessment extraction accuracy rising from ~70% to ~90%, "
         "measured against a gold-set harness.")

NAME, ROLE, PLACE = "KANNAPPAN SURESH", "BACKEND &amp; AI ENGINEER", "CHENNAI, INDIA"

# The noisy trace: (position along the trace 0..1, offset across it -1..1).
# Irregular spacing, calm stretches and sharp spikes both ways, so it reads as
# measurement noise, not a wave or a resistor zigzag.
NOISE = ((0, 0), (.029, .29), (.06, .05), (.086, -.25), (.111, -.09), (.134, .25), (.17, .37),
         (.191, -.21), (.209, -.35), (.23, .89), (.25, .86), (.272, -1), (.292, .03), (.31, -.02),
         (.332, -.04), (.353, -.25), (.38, .86), (.399, .98), (.416, -.8), (.435, -.36),
         (.461, .19), (.484, .12), (.514, .37), (.546, .93), (.569, .12), (.586, .06),
         (.616, -.24), (.647, -.07), (.67, .25), (.699, .41), (.72, .27), (.754, .1), (.786, -.9),
         (.817, -.32), (.851, -.1), (.871, -.21), (.897, -.16), (.927, -.14), (.959, .1),
         (.982, -.06), (1, 0))

# Every coordinate of the drawing, per canvas. Labels are (x, baseline, anchor).
WIDE = {
    "w": 850, "h": 400, "trim": 8, "frame": 36, "fade": 40,
    "zone_size": 14, "zone_base": 27, "letters": (("A", 152), ("B", 312)), "side_ticks": (232,),
    "track": .08,                                 # header letter-spacing, em
    "header": (  # (x, baseline, anchor, size, colour, ((text, weight), ...))
        (56, 62, "start", 16, "ink", ((NAME, 600), (" &#183; " + ROLE, 400))),
        (794, 62, "end", 16, "muted", ((PLACE, 400),)),
    ),
    "rule": 76,
    "size": {"llm": 24, "primary": 16, "secondary": 16, "row": 16, "readout": 22},
    "vessel": (74, 206, 92, 124, 24),             # x, y, w, h, ry (rx = w/2)
    "nozzle": ((166, 266), (178, 266)),
    "noise": ((178, 266), (310, 266), 10, 1),     # start, end, amplitude, point stride
    "station": (310, 232, 156, 68),
    "loop": ((388, 300), (388, 314)),             # leaves the station, then runs to the vessel wall
    "loop_y": 314,
    "validated": ((466, 266), (514, 266)),
    "valve": (536, 266, 22, 16, "h"),             # centre, half-length, half-width, pipe direction
    "stem": (536, 238),                           # stem top = lever pivot
    "lever": (26, "rotate(0)"),                   # length, final pose
    "clean": ((558, 266), (656, 266)),
    "head": (11, 4.5),
    "ledger": (656, 212, 138, 124, 34),           # x, y, w, h, header band
    "checks": (770, 14, 10),                      # x, width, height
    "gauge": (607, 148, 50, 42, 37, 33, 37, 6, 3.5),  # cx, cy, bezel r, scale r, minor, major, needle, tail, cap
    "tap": ((607, 198), (607, 266)),
    "labels": {
        "llm": (120, 274, "middle"),
        "reactor": (120, 356, "middle"),
        "probabilistic": (238, 242, "middle"),
        "station1": (388, 261, "middle"), "station2": (388, 283, "middle"),
        "loop": (277, 338, "middle"),
        "valve1": (536, 324, "middle"), "valve2": (536, 344, "middle"),
        "ledger": (668, 236, "start"),
        "rows": (668, (267, 297, 327)),
        "cfr": (725, 356, "middle"),
        "yield": (607, 179, "middle"),
        "readout": (544, 138, "end"),
        "caption1": (544, 164, "end"), "caption2": (544, 186, "end"),
    },
}

NARROW = {
    "w": 400, "h": 660, "trim": 6, "frame": 24, "fade": 40,
    "zone_size": 12, "zone_base": 19, "letters": (("A", 200), ("B", 520)), "side_ticks": (360,),
    "track": .06,                                 # a touch tighter so name and place keep a clear gap
    "header": (
        (44, 50, "start", 15, "ink", ((NAME, 600),)),
        (356, 50, "end", 14, "muted", ((PLACE, 400),)),
        (44, 72, "start", 14, "ink", ((ROLE, 400),)),
    ),
    "rule": 86,
    "size": {"llm": 20, "primary": 15, "secondary": 14, "row": 15, "readout": 18},
    "vessel": (74, 104, 72, 84, 18),
    "nozzle": ((110, 188), (110, 196)),
    "noise": ((110, 196), (110, 268), 8, 1),
    "station": (44, 268, 132, 52),
    "loop": ((176, 294), (330, 294), (330, 132)),
    "loop_y": 132,
    "validated": ((110, 320), (110, 338)),
    "valve": (110, 356, 18, 14, "v"),
    "stem": (82, 356),
    "lever": (22, "rotate(90) scale(1 -1)"),      # mirrored so the animation's start offset matches the wide file
    "clean": ((110, 374), (110, 416)),
    "head": (10, 4),
    "ledger": (44, 416, 132, 114, 30),
    "checks": (150, 12, 9),
    "gauge": (310, 480, 46, 39, 35, 31, 34, 5, 3),
    "tap": ((110, 395), (310, 395), (310, 434)),
    "labels": {
        "llm": (110, 153, "middle"),
        "reactor": (162, 153, "start"),
        "probabilistic": (134, 237, "start"),
        "station1": (110, 290, "middle"), "station2": (110, 310, "middle"),
        "loop": (238, 121, "middle"),
        "valve1": (142, 352, "start"), "valve2": (142, 372, "start"),
        "ledger": (56, 436, "start"),
        "rows": (56, (466, 494, 522)),
        "cfr": (110, 552, "middle"),
        "yield": (310, 508, "middle"),
        "readout": (356, 552, "end"),
        "caption1": (356, 580, "end"), "caption2": (356, 600, "end"),
    },
}

LAYOUTS = {"wide": WIDE, "narrow": NARROW}

TEMPLATE = Template("""<svg xmlns="http://www.w3.org/2000/svg" width="$w" height="$h" viewBox="0 0 $w $h" role="img" font-family="$font">
<title>$title</title>$style
<defs><linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="0" y1="$fade_y" x2="0" y2="$h"><stop offset="0" stop-color="$frame"/><stop offset="1" stop-color="$frame" stop-opacity="0"/></linearGradient></defs>
<g fill="none" stroke-linecap="round" stroke-linejoin="round">
<path id="trim" d="$trim_d" stroke="url(#fade)" stroke-width=".75"/>
<path id="frame" d="$frame_d" stroke="url(#fade)" stroke-width="1.5"/>
<path id="zone-ticks" d="$ticks_d" stroke="$frame" stroke-width=".75"/>
<path id="header-rule" d="$rule_d" stroke="$frame" stroke-width=".75"/>
<path id="ledger-rules" d="$ledger_rules_d" stroke="$frame" stroke-width=".75"/>
<path id="tap" d="$tap_d" stroke="$frame" stroke-dasharray="3 3"/>
<path id="gauge-ticks" d="$scale_d" stroke="$muted"/>
<path id="gauge-marks" d="$marks_d" stroke="$muted" stroke-width="1.5"/>
<path id="valve-fill" d="$valve_d" fill="$ink" opacity="0"/>
<g stroke="$ink" stroke-width="1.5">
<rect id="vessel" $vessel_a/>
<path id="nozzle" d="$nozzle_d"/>
<rect id="station" $station_a rx="4"/>
<path id="valve" d="$valve_d"/>
<path id="valve-stem" d="$stem_d"/>
<rect id="ledger" $ledger_a rx="2"/>
<circle id="gauge" $bezel_a/>
<g transform="$lever_tf"><g id="valve-lever"><path d="M0 0H$lever_len"/></g></g>
</g>
<path id="noise" d="$noise_d" pathLength="1" stroke="$muted" stroke-width="1.5"/>
<path id="loop" d="$loop_d" pathLength="1" stroke="$ink" stroke-width="1.25"/>
<path id="validated" d="$validated_d" pathLength="1" stroke="$ink" stroke-width="2"/>
<path id="clean" d="$clean_d" pathLength="1" stroke="$accent" stroke-width="2.5"/>
<g stroke="$accent" stroke-width="2">
<path id="check-1" d="$check1_d" pathLength="1"/>
<path id="check-2" d="$check2_d" pathLength="1"/>
<path id="check-3" d="$check3_d" pathLength="1"/>
</g>
<g transform="$ghost_tf"><g id="needle-ghost"><path d="$needle_d" stroke="$muted" stroke-width="1.5"/></g></g>
<g transform="$live_tf"><g id="needle-live"><path d="$needle_d" stroke="$accent" stroke-width="2.5"/></g></g>
</g>
<path id="loop-head" d="$loop_head_d" fill="$ink"/>
<path id="clean-head" d="$clean_head_d" fill="$accent"/>
<circle id="lever-pivot" $lever_pivot_a fill="$ink"/>
<circle id="gauge-pivot" $gauge_pivot_a fill="$ink"/>
<g fill="$muted" font-size="$zone_size" text-anchor="middle">$zones</g>
$header
<g fill="$muted" font-size="$secondary">
<text $reactor>reactor</text>
<text $probabilistic>probabilistic</text>
<text $loop>control loop</text>
<text $cfr>21 CFR Part 11</text>
<text $caption1>gap-assessment extraction accuracy</text>
<text $caption2>gold-set harness</text>
</g>
<g fill="$ink" font-size="$primary" font-weight="600">
<text $station1>deterministic</text>
<text $station2>validation</text>
<text $valve1>human-in-the-loop</text>
<text $valve2>gate</text>
<text $ledger>audit trail</text>
<text $yield>yield</text>
</g>
<g fill="$ink" font-size="$row">
<text $row1>extracted</text>
<text $row2>validated</text>
<text $row3>reviewed</text>
</g>
<text $llm fill="$ink" font-size="$llm_size" font-weight="700">LLM</text>
<text $readout fill="$ink" font-size="$readout_size" font-weight="600" style="font-variant-numeric:tabular-nums">~70% &#8594; ~90%</text>
</svg>
""")


def n(v):
    """Compact number: at most 2 decimals, no trailing zeros."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def pts(points):
    """Polyline as path data: M x y L x y ..."""
    head, *rest = points
    return f"M{n(head[0])} {n(head[1])}" + "".join(f"L{n(x)} {n(y)}" for x, y in rest)


def attrs(**kw):
    return " ".join(f'{k.replace("_", "-")}="{n(v) if isinstance(v, (int, float)) else v}"'
                    for k, v in kw.items())


def label(spec):
    x, y, anchor = spec
    a = f'x="{n(x)}" y="{n(y)}"'
    return a if anchor == "start" else a + f' text-anchor="{anchor}"'


def arrowhead(tip, direction, length, half):
    """Filled triangle with its tip at `tip`, pointing along `direction`."""
    dx, dy = direction
    bx, by = tip[0] - dx * length, tip[1] - dy * length
    return pts([tip, (bx - dy * half, by + dx * half), (bx + dy * half, by - dx * half)]) + "Z"


def capsule_wall_x(vessel, y):
    """Right wall of the capsule vessel at height y (dished heads are elliptical)."""
    x, top, w, h, ry = vessel
    rx, cx = w / 2, x + w / 2
    if top + ry <= y <= top + h - ry:
        return x + w
    cy = top + ry if y < top + ry else top + h - ry
    return cx + rx * math.sqrt(max(0.0, 1 - ((y - cy) / ry) ** 2))


def render(L, theme):
    c = THEMES[theme]
    w, h, t, f = L["w"], L["h"], L["trim"], L["frame"]
    v = {"w": w, "h": h, "font": FONT, "title": TITLE, "fade_y": h - L["fade"],
         "style": f"\n<style>{MOTION_CSS}</style>" if MOTION_CSS else "", **c}

    # Sheet: top edge closed, sides open (they fade out at the bottom).
    v["trim_d"] = pts([(t, h), (t, t), (w - t, t), (w - t, h)])
    v["frame_d"] = pts([(f, h), (f, f), (w - f, f), (w - f, h)])
    col = (w - 2 * f) / 4
    ticks = [((f + col * i, t), (f + col * i, f)) for i in (1, 2, 3)]
    ticks += [((a, y), (b, y)) for y in L["side_ticks"] for a, b in ((t, f), (w - f, w - t))]
    v["ticks_d"] = "".join(pts(seg) for seg in ticks)
    v["rule_d"] = pts([(f, L["rule"]), (w - f, L["rule"])])
    zs = L["zone_size"]
    zones = [f'<text x="{n(f + col * (i + .5))}" y="{L["zone_base"]}">{i + 1}</text>' for i in range(4)]
    zones += [f'<text x="{n(x)}" y="{n(y + zs * .35)}">{ch}</text>'
              for ch, y in L["letters"] for x in ((t + f) / 2, w - (t + f) / 2)]
    v["zones"], v["zone_size"] = "".join(zones), zs

    # Header strip: sheet furniture, uppercase and tracked.
    lines = []
    for x, y, anchor, size, colour, runs in L["header"]:
        body = "".join(txt if wt == 400 else f'<tspan font-weight="{wt}">{txt}</tspan>' for txt, wt in runs)
        anchor_a = "" if anchor == "start" else f' text-anchor="{anchor}"'
        lines.append(f'<text x="{x}" y="{y}"{anchor_a} fill="{c[colour]}" font-size="{size}" '
                     f'letter-spacing="{n(size * L["track"])}">{body}</text>')
    v["header"] = "\n".join(lines)

    # Equipment.
    vx, vy, vw, vh, vry = L["vessel"]
    v["vessel_a"] = attrs(x=vx, y=vy, width=vw, height=vh, rx=vw / 2, ry=vry)
    v["nozzle_d"] = pts(L["nozzle"])
    sx, sy, sw, sh = L["station"]
    v["station_a"] = attrs(x=sx, y=sy, width=sw, height=sh)
    cx, cy, hl, hw, axis = L["valve"]
    if axis == "h":   # bowtie: two triangles meeting at the centre, pipe runs through
        v["valve_d"] = (pts([(cx - hl, cy - hw), (cx, cy), (cx - hl, cy + hw)]) + "Z"
                        + pts([(cx + hl, cy - hw), (cx, cy), (cx + hl, cy + hw)]) + "Z")
    else:
        v["valve_d"] = (pts([(cx - hw, cy - hl), (cx, cy), (cx + hw, cy - hl)]) + "Z"
                        + pts([(cx - hw, cy + hl), (cx, cy), (cx + hw, cy + hl)]) + "Z")
    px, py = L["stem"]
    v["stem_d"] = pts([(cx, cy), (px, py)])
    v["lever_len"], pose = L["lever"]
    v["lever_tf"] = f"translate({n(px)} {n(py)}) {pose}"
    v["lever_pivot_a"] = attrs(cx=px, cy=py, r=2.25)
    lx, ly, lw, lh, band = L["ledger"]
    v["ledger_a"] = attrs(x=lx, y=ly, width=lw, height=lh)
    row_h = (lh - band) / 3
    v["ledger_rules_d"] = "".join(pts([(lx, ly + band + row_h * i), (lx + lw, ly + band + row_h * i)])
                                  for i in range(3))
    kx, kw, kh = L["checks"]
    for i in range(3):
        mid = ly + band + row_h * (i + .5)
        v[f"check{i + 1}_d"] = pts([(kx, mid), (kx + kw * .36, mid + kh / 2), (kx + kw, mid - kh / 2)])

    # Signal path: noise -> station -> validated -> valve -> clean -> ledger.
    (ax, ay), (bx, by), amp, stride = L["noise"]
    length = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / length, (by - ay) / length
    v["noise_d"] = pts([(ax + ux * length * p + uy * amp * o, ay + uy * length * p - ux * amp * o)
                        for p, o in NOISE[:-1:stride] + NOISE[-1:]])
    v["validated_d"] = pts(L["validated"])
    hlen, hhalf = L["head"]
    (c0x, c0y), (c1x, c1y) = L["clean"]
    clen = math.hypot(c1x - c0x, c1y - c0y)
    cd = ((c1x - c0x) / clen, (c1y - c0y) / clen)
    ctip = (c1x - cd[0] * .75, c1y - cd[1] * .75)          # touches the ledger's outer stroke edge
    v["clean_d"] = pts([(c0x, c0y), (ctip[0] - cd[0] * (hlen - 1), ctip[1] - cd[1] * (hlen - 1))])
    v["clean_head_d"] = arrowhead(ctip, cd, hlen, hhalf)

    # Control loop: from the station back into the vessel wall, arrow into the vessel.
    ly_ = L["loop_y"]
    ltip = (capsule_wall_x(L["vessel"], ly_) + .75, ly_)
    lhead = hlen * .8
    v["loop_d"] = pts(list(L["loop"]) + [(ltip[0] + lhead - 1, ly_)])
    v["loop_head_d"] = arrowhead(ltip, (-1, 0), lhead, hhalf * .78)

    # Instrument tap (dashed signal line) from the clean line up to the gauge.
    v["tap_d"] = pts(L["tap"])

    # Gauge: 240 degree dial, 0-100 linear and untruncated.
    gx, gy, br, sr, minor, major, needle, tail, cap = L["gauge"]
    v["bezel_a"] = attrs(cx=gx, cy=gy, r=br)

    def polar(r, value):
        a = math.radians(-120 + 2.4 * value)
        return gx + r * math.sin(a), gy - r * math.cos(a)

    s0, s1 = polar(sr, 0), polar(sr, 100)
    scale = f"M{n(s0[0])} {n(s0[1])}A{n(sr)} {n(sr)} 0 1 1 {n(s1[0])} {n(s1[1])}"
    scale += "".join(pts([polar(sr, val), polar(minor, val)]) for val in range(0, 101, 10)
                     if val not in (70, 90))
    v["scale_d"] = scale
    v["marks_d"] = "".join(pts([polar(sr, val), polar(major, val)]) for val in (70, 90))
    v["needle_d"] = f"M0 {n(tail)}V-{n(needle)}"
    v["ghost_tf"] = f"translate({n(gx)} {n(gy)}) rotate({n(-120 + 2.4 * 70)})"
    v["live_tf"] = f"translate({n(gx)} {n(gy)}) rotate({n(-120 + 2.4 * 90)})"
    v["gauge_pivot_a"] = attrs(cx=gx, cy=gy, r=cap)

    # Text.
    s = L["size"]
    v.update(primary=s["primary"], secondary=s["secondary"], row=s["row"],
             llm_size=s["llm"], readout_size=s["readout"])
    lab = L["labels"]
    for key in ("llm", "reactor", "probabilistic", "station1", "station2", "loop", "valve1",
                "valve2", "ledger", "cfr", "yield", "readout", "caption1", "caption2"):
        v[key] = label(lab[key])
    rx_, rys = lab["rows"]
    for i, y in enumerate(rys):
        v[f"row{i + 1}"] = label((rx_, y, "start"))
    return TEMPLATE.substitute(v)


def main():
    ASSETS.mkdir(exist_ok=True)
    for name, (layout, theme) in FILES.items():
        svg = render(LAYOUTS[layout], theme)
        (ASSETS / name).write_text(svg, encoding="utf-8")
        print(f"assets/{name}  {len(svg.encode('utf-8')) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
