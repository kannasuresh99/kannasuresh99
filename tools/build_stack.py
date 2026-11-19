#!/usr/bin/env python3
"""Scene 2, 'Built from the base up': the layered architecture tower.

Writes assets/stack.svg (850 wide) and assets/stack-narrow.svg (400 wide) from the shared svgkit.
Python 3 stdlib only, deterministic. Never hand-edit the SVGs; change this file and re-run.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgkit as K  # noqa: E402

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

# key, tools, techniques (wide), (narrow tools, narrow techniques). Bottom (01) to top (07).
LAYERS = [
    ("INFRA", ["Azure AKS", "GCP Vertex AI", "AWS", "Kubernetes", "Docker", "Terraform"],
     ["pod auto-scaling"],
     (["Azure AKS", "Vertex AI", "AWS", "Terraform"], [])),
    ("DATA", ["PostgreSQL", "MongoDB", "Redis", "Neo4j", "LanceDB"],
     ["knowledge graph", "optimized indexing"],
     (["PostgreSQL", "MongoDB", "Redis", "Neo4j"], [])),
    ("MSG", ["Azure Service Bus", "Kafka", "Celery"],
     ["shuffle-sharding", "outbox", "idempotent consumers"],
     (["Azure Service Bus", "Kafka"], ["shuffle-sharding", "outbox", "idempotent consumers"])),
    ("SVC", ["FastAPI", "Flask", "Django", "gRPC / REST"],
     ["event-driven microservices", "multi-tenant isolation", "permission-aware access"],
     (["FastAPI", "gRPC / REST"], ["multi-tenant isolation"])),
    ("RETR", ["embeddings", "hybrid search", "re-ranking", "OCR chunking"],
     ["graph-RAG", "content-hash cache"],
     (["hybrid search", "re-ranking"], ["graph-RAG", "hash cache"])),
    ("AGENT", ["LangGraph", "LangChain", "Pipecat", "Gemini", "Azure OpenAI"],
     ["multi-agent orchestration", "micro-prompting", "context caching", "thinking budgets"],
     (["LangGraph", "Pipecat"], ["multi-agent", "micro-prompting"])),
    ("TRUST", ["21 CFR Part 11 / GxP"],
     ["deterministic validation", "human-in-the-loop", "audit trails", "provenance"],
     (["21 CFR Part 11"], ["validation", "human-in-the-loop", "audit trails"])),
]
OBS_ITEMS = "metrics · structured logs · tracing · token cost / latency"
EVAL_ITEMS = "gold-set harness · LLM-as-judge"

TITLE = "Built from the base up"
ALT = ("Isometric tower of seven glass layers built from the bottom up, one colour per layer, each layer showing a "
       "small scene of what it does. 1 Infrastructure (server racks): Azure AKS, GCP Vertex AI, AWS, Kubernetes, "
       "Docker, Terraform; pattern: pod auto-scaling. 2 Data stores (database drums and a graph): PostgreSQL, "
       "MongoDB, Redis, Neo4j, LanceDB; patterns: knowledge graph, optimized indexing. 3 Messaging and queues "
       "(sharded lanes): Azure Service Bus, Kafka, Celery; patterns: shuffle-sharding, outbox, idempotent consumers. "
       "4 Services and APIs (linked service cubes): FastAPI, Flask, Django, gRPC and REST; patterns: event-driven "
       "microservices, multi-tenant isolation, permission-aware access. 5 Retrieval (a lens over vectors): "
       "embeddings, hybrid search, re-ranking, OCR chunking; patterns: graph-RAG, content-hash cache. 6 Agents "
       "(glowing linked agent orbs): LangGraph, LangChain, Pipecat, Gemini, Azure OpenAI; patterns: multi-agent "
       "orchestration, micro-prompting, context caching, thinking budgets. 7 Trust and controls (a human gate, a "
       "check tile and an audit ledger): 21 CFR Part 11 / GxP; patterns: deterministic validation, "
       "human-in-the-loop, audit trails, provenance. Two measurement rails run alongside: observability (metrics, "
       "structured logs, tracing, token cost and latency) taps every layer, and evals (gold-set harness, "
       "LLM-as-judge) tap retrieval, agents, and trust and controls.")
# The README <img> carries ALT (printed by main); the SVG <desc> stays short to save bytes.
DESC = ("Isometric tower of seven glass layers, infrastructure at the base to trust and controls at the top, each "
        "with its tools and patterns, beside observability and evals rails.")
DESC_NARROW = ("Seven stacked layer plates, trust and controls on top and infrastructure at the base, each with its "
               "tools and patterns, above observability and evals bars.")

CYCLE, LOOP0 = 8, 3.8          # request-pulse loop: 8 s cycle starting after the build
RISE_END = 40                  # the pulse reaches the top at 40% of the cycle, gone by 46%


def motion_css():
    """Build once base to top, then rails, taps; transients (pulse, rim flashes) hidden at rest."""
    return "".join([K.css_drop("s"), K.css_fade("k", .6, 0, dx=6), K.css_fade("so", .5, 2.6),
                    K.css_draw("rail", 1.1, 2.75), K.css_fade("rl", .5, 2.9), K.css_fade("tap", .4, 3.4),
                    K.css_flash("fl", CYCLE)])


def rim_flash(points, hue, t_cross, w=1.6):
    """Rim polyline that glows in the layer's rim tint as the pulse crosses it (peak at t_cross)."""
    p = K.pts(points)
    rim = K.rim_tint(hue)
    return (f'<g class="fl"{K.delay(t_cross - CYCLE * .03)}>'
            f'<polyline points="{p}" fill="none" stroke="{rim}" stroke-width="4" stroke-opacity=".7" '
            f'filter="url(#k-glow)"/><polyline points="{p}" fill="none" stroke="{rim}" stroke-width="{w}"/></g>')


def hue_windows(y_start, y_end, centres):
    """Halo hue schedule: each layer's hue from midway below its centre to midway above it."""
    pct = lambda y: (y_start - y) / (y_start - y_end) * RISE_END
    out = [(0, K.HUE[LAYERS[0][0]])]
    for i in range(1, 7):
        out.append((pct((centres[i - 1] + centres[i]) / 2), K.HUE[LAYERS[i][0]]))
    return out, pct


# ---------------------------------------------------------------- wide
def build_wide():
    """850-wide isometric tower with callouts, two measurement rails and the hue-tracking request pulse."""
    W, A, B, T, P, CX, YC7 = 850, 100, 50, 14, 76, 142, 148
    yc = {k: YC7 + (7 - k) * P for k in range(1, 8)}
    base_bot = yc[1] + B + T
    H = base_bot + 60
    X0, XR = 272, 738                       # callout column; chip rows must end by XR
    OBS_X, EVAL_X = 766, 806
    K.assert_within(XR + 24, OBS_X - 2.5, "slack before the OBS rail")

    body = [K.card(W, H, "ONE SYSTEM · BASE → TOP"),
            K.glow(CX, yc[6], 330, 250, K.VIOLET, .20),
            K.glow(CX, yc[1] + 40, 300, 200, K.WARM, .16),
            K.floor_shadow(CX, yc[1] + 28, A + 14, B + 2)]

    y_start = base_bot + 22
    hues, pct = hue_windows(y_start, yc[7], [yc[k] for k in range(1, 8)])
    rights, flashes = {}, []
    for i, (key, tools, techs, _) in enumerate(LAYERS):
        k, hue = i + 1, K.HUE[key]
        iso = K.Iso(CX, yc[k], A, B)
        d = .15 + .33 * i
        body.append(f'<g class="s"{K.delay(d)}>{K.slab(iso, T, hue)}{K.layer_scene(key, iso)}</g>')
        lines = K.chips_layout(tools, techs, XR - X0)
        if len(lines) > 2:
            raise OverflowError(f"{key}: {len(lines)} chip lines, the row pitch holds 2")
        chips, right = K.chips_svg(lines, X0, yc[k] + 32, 24, hue)
        K.assert_within(right, XR, f"{key} chips")
        name = K.LAYER_NAMES[key]
        nw = K.fit(name, "nm", XR - X0 - 22, what=f"{key} name")
        rights[k] = max(right, X0 + 22 + nw)
        ly = yc[k] + 7
        body.append(f'<g class="k"{K.delay(d + .25)}>' + K.leader(CX + A + 7, ly, X0 - 8, ly, hue) +
                    K.txt(X0, yc[k] + 11, f"0{k}", "ix", hue) +
                    K.txt(X0 + 22, yc[k] + 11, name, "nm", K.name_tint(hue)) + chips + "</g>")
        t_cross = LOOP0 + pct(yc[k]) / 100 * CYCLE
        flashes.append(rim_flash([iso.p(0, 1), iso.p(0, 0), iso.p(1, 0)], hue, t_cross))

    so = "".join(K.hairline(x, yc[k] + T + 2, x, yc[k - 1] - 2) for k in range(2, 8) for x in (CX - A, CX + A))
    body.append(f'<g class="so">{so}</g>')
    body.extend(flashes)
    pcss, psvg = K.pulse("dot", [(0, CX, y_start), (RISE_END, CX, yc[7])], hues, CYCLE, LOOP0, core=3, halo=14)
    body.append(psvg)

    # axis: base -> top, with the card's only two annotations
    body.append(f'<line x1="22" y1="{yc[1]}" x2="22" y2="{yc[7]}" stroke="{K.MUTED}"/>' +
                K.chevron(22, yc[7], -math.pi / 2, K.MUTED, 1, 5, 1.2) +
                K.note(22, yc[7] - 10, "top", anchor="middle") + K.note(22, yc[1] + 22, "base", anchor="middle"))

    # measurement rails: observability taps every layer, evals tap retrieval, agents, trust
    ytop = yc[7] - 4
    yt = ytop - 40
    titles, taps = [], []
    for j, (x, hue, lo, title, items) in enumerate(((OBS_X, K.OBS, 1, "OBSERVABILITY", OBS_ITEMS),
                                                    (EVAL_X, K.EVAL, 5, "EVALS", EVAL_ITEMS))):
        ybot = yc[lo] + 62
        body.append(K.conduit(x, ybot, x, ytop, hue, "rail"))
        ty = yt + 16 * j
        tw = K.fit(title, "rt", 826 - (OBS_X - 60), what="rail title")
        K.assert_within(x, 826, "rail under its title")
        K.assert_within(826 - tw, x - 6, "title spans its rail")
        K.fit(items, "ri", ybot - ytop - 12, what="rail items")
        titles.append(K.txt(826, ty, title, "rt", hue, anchor="end") +
                      f'<line x1="{x}" y1="{ty + 4}" x2="{x}" y2="{ytop - 7}" stroke="{hue}" stroke-opacity=".6"/>' +
                      f'<text transform="translate({x + 15},{ybot}) rotate(-90)" class="ri">{K.esc(items)}</text>')
    for k in range(1, 8):
        y = yc[k] + 7
        taps.append(K.feeder(rights[k] + 10, y, OBS_X - 4, y, K.OBS) + K.ring_tap(OBS_X, y, K.OBS))
        if k >= 5:
            taps.append(K.feeder(OBS_X + 4, y, EVAL_X - 4, y, K.EVAL) + K.ring_tap(EVAL_X, y, K.EVAL))
    body.append(f'<g class="rl">{"".join(titles)}</g><g class="tap">{"".join(taps)}</g>')
    body.append(K.legend(826, H - 24))
    return K.svg_doc(W, H, TITLE, DESC, "", motion_css() + pcss, "".join(body))


# ---------------------------------------------------------------- narrow
def build_narrow():
    """400-wide re-layout: cabinet-oblique plates (trust on top) with chips, iso glyphs, and two horizontal rails."""
    W, PX, PR, DX, DY = 400, 18, 382, 14, 9
    fx0, fx1 = PX + 12, PR - DX - 12          # chip box inside the plate front face
    GLYPH_L = PR - DX - 50 - 38 - 8           # first chip line stops before the glyph
    LH = 28
    plates, y = [], 74
    for k in range(7, 0, -1):
        key, _, _, (tools, techs) = LAYERS[k - 1]
        lines = K.chips_layout(tools, techs, fx1 - fx0, narrow=True, first=GLYPH_L - fx0)
        h = 41 + LH * len(lines)
        plates.append((k, key, y, h, lines))
        y += DY + h + 14
    stack_bot = plates[-1][2] + DY + plates[-1][3]
    rails_y = stack_bot + 50
    H = rails_y + 66 + 44

    body = [K.card(W, H, "BASE → TOP"),
            K.glow(150, plates[1][2] + 60, 230, 180, K.VIOLET, .20),
            K.glow(150, plates[-1][2] + 40, 230, 170, K.WARM, .16),
            K.note(PX, 62, "top", narrow=True)]
    y_start = stack_bot + 16
    y_end = plates[0][2] + 4
    centres = [p[2] + DY + p[3] / 2 for p in reversed(plates)]
    hues, pct = hue_windows(y_start, y_end, centres)
    flashes = []
    for k, key, py, h, lines in plates:
        hue = K.HUE[key]
        name = K.LAYER_NAMES[key]
        K.fit(name, "nm", GLYPH_L - (PX + 38), narrow=True, what=f"{key} narrow name")
        chips, right = K.chips_svg(lines, fx0, py + DY + 46, LH, hue, narrow=True)
        K.assert_within(right, fx1, f"{key} narrow chips")
        g = K.Iso(PR - DX - 50, py + DY + 30, 38)
        body.append(f'<g class="s"{K.delay(.15 + .33 * (k - 1))}>' + K.plate(PX, py, PR - PX, h, hue, DX, DY) +
                    K.txt(PX + 12, py + DY + 22, f"0{k}", "ix", hue) +
                    K.txt(PX + 38, py + DY + 22, name, "nm", K.name_tint(hue)) + chips +
                    K.slab(g, 14, hue) + K.layer_scene(key, g) + "</g>")
        flashes.append(rim_flash(K.plate_top(PX, py, PR - PX, DX, DY), hue,
                                 LOOP0 + pct(py + DY / 2) / 100 * CYCLE, 1.4))
    so = "".join(K.hairline(x, plates[i][2] + DY + plates[i][3] + 2, x, plates[i + 1][2] + DY - 2)
                 for i in range(6) for x in (PX + 10, PR - DX - 10))
    body.append(f'<g class="so">{so}</g>')
    body.extend(flashes)
    pcss, psvg = K.pulse("dot", [(0, PR - DX / 2, y_start), (RISE_END, PR - DX / 2, y_end)], hues, CYCLE, LOOP0,
                         halo=12, core=2.6)
    body.append(psvg)
    body.append(K.note(PX, stack_bot + 24, "base", narrow=True))

    # rails as two horizontal conduits with evenly spaced taps (7 on observability, 3 on evals)
    titles, taps = [], []
    for j, (hue, title, sub, n) in enumerate(((K.OBS, "OBSERVABILITY", "every layer", 7),
                                              (K.EVAL, "EVALS", "retrieval → trust", 3))):
        ty, by = rails_y + 50 * j, rails_y + 50 * j + 16
        x0, x1 = PX + 6, PR - 6
        tw = K.measure(title, "rt", True)
        K.assert_within(PX + tw + 6 + K.measure("· " + sub, "ri", True), PR, "narrow rail label")
        body.append(K.conduit(x0, by, x1, by, hue, "rail"))
        titles.append(f'<text x="{PX}" y="{ty}"><tspan class="rt" fill="{hue}">{title}</tspan>'
                      f'<tspan class="ri" dx="6">· {K.esc(sub)}</tspan></text>')
        taps.extend(K.ring_tap(x0 + (x1 - x0) * i / (n - 1), by, hue) for i in range(n))
    body.append(f'<g class="rl">{"".join(titles)}</g><g class="tap">{"".join(taps)}</g>')
    body.append(K.legend(PR, H - 20, narrow=True))
    return K.svg_doc(W, H, TITLE, DESC_NARROW, "", motion_css() + pcss, "".join(body))


if __name__ == "__main__":
    K.write(os.path.join(ASSETS, "stack.svg"), build_wide())
    K.write(os.path.join(ASSETS, "stack-narrow.svg"), build_narrow())
    print(K.picture("stack", ALT))
