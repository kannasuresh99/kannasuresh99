#!/usr/bin/env python3
"""Build the footer title-block SVGs into assets/.

One template (render), two layouts (wide 850, narrow 400) and three colour
themes give the five files. The footer closes the drawing sheet the hero opens:
same insets, stroke weights, colours and font. It is fully static.

Run from the repo root:  python3 tools/build_title_block.py
"""
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "light": {"ink": "#1f2328", "muted": "#59636e", "frame": "#818b98"},
    "dark": {"ink": "#e6edf3", "muted": "#9198a1", "frame": "#656c76"},
    "neutral": {"ink": "#6e7781", "muted": "#8c959f", "frame": "#8c959f"},
}

TITLE = ("Engineering drawing title block: drawn by Kannappan Suresh; discipline, "
         "Chemical Engineering; Anna University (ACT Campus), 2016&#8211;2020; "
         "awards, 4x Shining Star and INSPIRE Science Camp; sheet 1 of 1.")

# Every word in the drawing. "|" is a line break in layouts that wrap, a space otherwise.
COPY = {
    "drawn": ("DRAWN BY", "Kannappan Suresh"),
    "discipline": ("DISCIPLINE", "Chemical Engineering"),
    "sheet": ("SHEET", "1 OF 1"),
    "institution": ("INSTITUTION", "Anna University (ACT Campus),|2016&#8211;2020"),
    "awards": ("AWARDS", "4x Shining Star &#183;|INSPIRE Science Camp"),
}
BOLD = {"drawn"}

# rows: (top, bottom, ((left, right, field), ...)); the block's right and bottom
# edges are the sheet frame itself.
WIDE = {
    "w": 850, "h": 252, "trim": 8, "frame": 36, "fade": 40, "zone_size": 14,
    "letters": (("C", 96), ("D", 176)), "side_ticks": (136,),
    "rows": (
        (60, 112, ((294, 484, "drawn"), (484, 720, "discipline"), (720, 814, "sheet"))),
        (112, 164, ((294, 814, "institution"),)),
        (164, 216, ((294, 814, "awards"),)),
    ),
    "field_size": 14, "value_size": 16, "inset": 12,
    "field_dy": 20, "value_dy": 42, "line_h": 0, "wrap": False,
}
NARROW = {
    "w": 400, "h": 330, "trim": 6, "frame": 24, "fade": 36, "zone_size": 12,
    "letters": (("C", 126), ("D", 246)), "side_ticks": (186,),
    "rows": (
        (62, 112, ((24, 256, "drawn"), (256, 376, "sheet"))),
        (112, 162, ((24, 376, "discipline"),)),
        (162, 234, ((24, 376, "institution"),)),
        (234, 306, ((24, 376, "awards"),)),
    ),
    "field_size": 12, "value_size": 15, "inset": 10,
    "field_dy": 18, "value_dy": 38, "line_h": 20, "wrap": True,
}

OUTPUTS = (
    ("title-block-light.svg", WIDE, "light"),
    ("title-block-dark.svg", WIDE, "dark"),
    ("title-block-narrow-light.svg", NARROW, "light"),
    ("title-block-narrow-dark.svg", NARROW, "dark"),
    ("title-block.svg", WIDE, "neutral"),
)


def n(v):
    return f"{v:g}"


def text(x, y, s, extra=""):
    return f'<text x="{n(x)}" y="{n(y)}"{extra}>{s}</text>'


def render(L, T):
    w, h, t, f = L["w"], L["h"], L["trim"], L["frame"]
    right, bottom, trim_bottom = w - f, h - f, h - t
    rows = L["rows"]
    left, top = rows[0][2][0][0], rows[0][0]
    assert rows[-1][1] == bottom and all(r[2][-1][1] == right for r in rows)

    # Sheet: trim and frame, sides fading in from the top, bottom edge closed.
    zone = (w - 2 * f) / 4
    ticks = "".join(f"M{n(f + zone * i)} {bottom}V{trim_bottom}" for i in (1, 2, 3))
    ticks += "".join(f"M{t} {y}H{f}M{right} {y}H{w - t}" for y in L["side_ticks"])

    # Title block: heavy outline on its open sides, light cell lines inside.
    outline = (f"M{left} {bottom}V{top}" if left != f else f"M{left} {top}") + f"H{right}"
    cells = ""
    for i, (y0, y1, row) in enumerate(rows):
        if i:
            cells += f"M{left} {y0}H{right}"
        cells += "".join(f"M{x1} {y0}V{y1}" for _, x1, _ in row[:-1])

    # Zone markers, centred in the bands.
    zs = L["zone_size"]
    off = round(0.36 * zs)
    band_mid = (bottom + trim_bottom) / 2
    side = (t + f) / 2
    zones = [text(round(f + zone * (i + 0.5)), band_mid + off, str(i + 1)) for i in range(4)]
    for letter, y in L["letters"]:
        zones += [text(side, y + off, letter), text(w - side, y + off, letter)]

    names, values = [], []
    for y0, _, row in rows:
        for x0, _, key in row:
            name, value = COPY[key]
            x = x0 + L["inset"]
            names.append(text(x, y0 + L["field_dy"], name))
            lines = value.split("|") if L["wrap"] else [value.replace("|", " ")]
            weight = ' font-weight="600"' if key in BOLD else ""
            for j, line in enumerate(lines):
                values.append(text(x, y0 + L["value_dy"] + j * L["line_h"], line, weight))

    fs = L["field_size"]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">',
        f"<title>{TITLE}</title>",
        f'<defs><linearGradient id="tb-fade" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{L["fade"]}">'
        f'<stop offset="0" stop-color="{T["frame"]}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{T["frame"]}"/></linearGradient></defs>',
        '<g fill="none" stroke-linecap="round">',
        f'<path d="M{t} 0V{trim_bottom}H{w - t}V0" stroke="url(#tb-fade)" stroke-width="0.75"/>',
        f'<path d="M{f} 0V{bottom}H{right}V0" stroke="url(#tb-fade)" stroke-width="1.5"/>',
        f'<path d="{ticks}{cells}" stroke="{T["frame"]}" stroke-width="0.75"/>',
        f'<path d="{outline}" stroke="{T["frame"]}" stroke-width="1.5"/>',
        "</g>",
        f'<g font-family="{FONT}">',
        f'<g font-size="{zs}" fill="{T["muted"]}" text-anchor="middle">',
        *zones,
        "</g>",
        f'<g font-size="{fs}" fill="{T["muted"]}" letter-spacing="{n(round(fs * 0.08, 2))}">',
        *names,
        "</g>",
        f'<g font-size="{L["value_size"]}" fill="{T["ink"]}">',
        *values,
        "</g>",
        "</g>",
        "</svg>",
        "",
    ])


def main():
    ASSETS.mkdir(exist_ok=True)
    for name, layout, theme in OUTPUTS:
        svg = render(layout, THEMES[theme])
        assert len(svg.encode()) < 20 * 1024, name
        (ASSETS / name).write_text(svg, encoding="ascii")
        print(f"assets/{name}  {len(svg.encode())} bytes")


if __name__ == "__main__":
    main()
