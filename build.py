"""Regenerates assets/*.svg. Standard library only: python build.py

Every SVG is self-contained (inline CSS keyframes, no scripts, no fonts, no
external references) because GitHub serves README images as sandboxed <img>.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).parent / "assets"

EASE_OUT = "cubic-bezier(0.23,1,0.32,1)"
EASE_IN_OUT = "cubic-bezier(0.77,0,0.175,1)"

THEMES = {
    "dark": {
        "panel": "#161b22", "line": "#30363d", "mute": "#30363d", "rule": "#6e7681",
        "ink": ["#e6edf3", "#c9d1d9", "#adbac7"],
        "ember": ["#ffd166", "#ffbd4a", "#ffa23f", "#ff8736", "#fb6b2c", "#ef5022", "#dc3a1a"],
        "teal": "#2dd4bf", "violet": "#a78bfa", "gold": "#e3b341",
        "sand": ["#e9c46a", "#dcb35c", "#f1d38a"],
        "water": ["#58a6ff", "#4493f8", "#79c0ff"],
    },
    "light": {
        "panel": "#f6f8fa", "line": "#d0d7de", "mute": "#d0d7de", "rule": "#8c959f",
        "ink": ["#1f2328", "#32383f", "#454c54"],
        "ember": ["#f0920a", "#ec800c", "#e66d0e", "#df5a10", "#d54612", "#c63413", "#b02711"],
        "teal": "#0f9d8c", "violet": "#8250df", "gold": "#bf8700",
        "sand": ["#c69026", "#b5811c", "#d4a23a"],
        "water": ["#0969da", "#218bff", "#54aeff"],
    },
}

# Loops are decoration, so reduced motion gets the static frame.
STILL = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"

FONT = {
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "u": [".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"],
    "e": [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
    "l": [".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "d": ["....#", "....#", ".##.#", "#..##", "#...#", "#...#", ".####"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "y": [".....", ".....", "#...#", "#...#", ".####", "....#", ".###."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
}


def rect(x, y, w, h, fill=None, cls=None, style=None, rx=None, stroke=None):
    attrs = {"class": cls, "x": x, "y": y, "width": w, "height": h, "rx": rx, "fill": fill, "stroke": stroke, "style": style}
    return "<rect" + "".join(f' {k}="{v}"' for k, v in attrs.items() if v is not None) + "/>"


def svg(w, h, label, css, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{label}"><title>{label}</title><style>{css}</style>{body}</svg>\n'
    )


def hero(t):
    rnd = random.Random(7)
    word, hot_from = "FueledByRedBull", 8
    cell, size, w, h, y0 = 14, 12, 1280, 222, 88
    # proportional spacing: drop each glyph's empty side columns, one blank column between glyphs
    used = {ch: [cx for cx in range(5) if any(row[cx] == "#" for row in FONT[ch])] for ch in set(word)}
    starts = [sum(len(used[c]) + 1 for c in word[:i]) for i in range(len(word))]
    x0 = (w - ((starts[-1] + len(used[word[-1]])) * cell - (cell - size))) // 2
    grains, tops = [], {}
    for i, ch in enumerate(word):
        for n, cx in enumerate(used[ch]):
            col = starts[i] + n
            pour = col * 8 + rnd.randrange(140)  # sweep left to right, uneven like a real pour
            for r in range(7):
                if FONT[ch][r][cx] != "#":
                    continue
                if i >= hot_from:
                    fill = t["ember"][min(6, max(0, r + rnd.choice((-1, 0, 0, 1))))]
                    tops.setdefault(col, r)
                else:
                    fill = rnd.choice(t["ink"])
                # same speed and drop height for every grain; lower rows leave first so columns stack bottom-up
                delay = pour + (6 - r) * 45
                grains.append(rect(x0 + col * cell, y0 + r * cell, size, size, fill, "g", f"animation-delay:{delay}ms", 1.5))
    sparks = []
    for n, col in enumerate(rnd.sample(sorted(tops), 6)):
        style = f"animation-duration:{5.3 + n * 0.9:.1f}s;animation-delay:{2.2 + rnd.random() * 4:.1f}s"
        sparks.append(rect(x0 + col * cell + 3, y0 + tops[col] * cell - 8, 6, 6, t["ember"][n % 3], f"s s{n % 2}", style, 1))
    css = (
        ".g{animation:fall .46s linear backwards}"
        f".s{{opacity:0;animation:rise0 6s {EASE_OUT} infinite}}.s1{{animation-name:rise1}}"
        "@keyframes fall{from{transform:translateY(-240px)}}"
        "@keyframes rise0{0%{transform:translate(0,0);opacity:0}5%{opacity:.9}30%,100%{transform:translate(7px,-58px);opacity:0}}"
        "@keyframes rise1{0%{transform:translate(0,0);opacity:0}5%{opacity:.9}30%,100%{transform:translate(-6px,-70px);opacity:0}}"
        "@keyframes fade{from{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.g{animation:fade .2s ease backwards;animation-delay:0s!important}.s{animation:none}}"
    )
    return svg(w, h, "FueledByRedBull", css, "".join(sparks + grains))


def tile(t, label, css, body, over="", grid=True):
    """640x240 panel. With grid=True a panel-coloured mesh sits on top, so solid
    shapes snapped to the 10px grid read as rows of grains while they animate."""
    mesh = ""
    if grid:
        mesh = (
            f'<pattern id="m" width="10" height="10" patternUnits="userSpaceOnUse">'
            f'<path d="M0 9h10M9 0v10" stroke="{t["panel"]}" stroke-width="2"/></pattern>'
            '<rect x="40" y="20" width="560" height="200" fill="url(#m)"/>'
        )
    frame = rect(0.5, 0.5, 639, 239, t["panel"], rx=14, stroke=t["line"])
    return svg(640, 240, label, css + STILL, frame + body + mesh + over)


def audio(t):
    rnd = random.Random(3)
    floor, gate = 200, 149
    bars = ""
    for i in range(17):
        voice = 0.35 + 0.65 * math.exp(-(((i - 6) / 3.6) ** 2)) + 0.25 * math.exp(-(((i - 12.5) / 2.2) ** 2))
        h = 10 * max(3, min(15, round(15 * voice * (0.8 + 0.4 * rnd.random()))))
        style = f"animation-duration:{1.5 + rnd.random() * 1.2:.2f}s;animation-delay:-{rnd.random() * 3:.2f}s"
        bars += rect(70 + i * 30, floor - h, 20, h, cls=f"b b{rnd.randrange(3)}", style=style)
    css = (
        f".b{{transform-box:fill-box;transform-origin:50% 100%;animation:m0 2s {EASE_IN_OUT} infinite alternate}}"
        ".b1{animation-name:m1}.b2{animation-name:m2}"
        "@keyframes m0{from{transform:scaleY(.38)}}"
        "@keyframes m1{from{transform:scaleY(.55)}}"
        "@keyframes m2{from{transform:scaleY(.22)}to{transform:scaleY(.9)}}"
    )
    # same bars twice: muted below the gate, coloured only where they clear it
    body = (
        f'<g fill="{t["mute"]}">{bars}</g>'
        f'<clipPath id="c"><rect x="40" y="20" width="560" height="{gate - 20}"/></clipPath>'
        f'<g fill="{t["teal"]}" clip-path="url(#c)">{bars}</g>'
    )
    over = f'<path d="M50 {gate}H590" stroke="{t["rule"]}" stroke-width="2" stroke-dasharray="6 6"/>'
    return tile(t, "audio-forge: level meters crossing a noise gate", css, body, over)


def powder(t):
    rnd = random.Random(11)
    floor, peak, peak_col, level = 21, 8, 22, 3  # grid rows/cols, 10px each
    heap = {c: max(0, round(peak - 0.5 * abs(c - peak_col) + rnd.uniform(-0.45, 0.45))) for c in range(4, 60)}
    heap[peak_col] = peak
    still, surface = [], []
    for c, h in heap.items():
        for k in range(h):
            still.append(rect(c * 10, (floor - k) * 10, 8, 8, rnd.choice(t["sand"]), rx=1.5))
        if c >= 34:
            for k in range(h, level):
                top = k == level - 1
                g = rect(c * 10, (floor - k) * 10, 8, 8, rnd.choice(t["water"]), "f" if top and rnd.random() < 0.4 else None,
                         f"animation-delay:-{rnd.random() * 3:.1f}s" if top else None, 1.5)
                (surface if top else still).append(g)
    sand_drop = (floor - peak + 1) * 10 - 30
    water_drop = (floor - level + 1) * 10 - 30
    falling = [rect(peak_col * 10, 30, 8, 8, t["sand"][n % 3], "d", f"animation-delay:-{n * 0.2:.1f}s", 1.5) for n in range(5)]
    falling += [rect(500, 30, 8, 8, t["water"][n % 3], "w", f"animation-delay:-{n * 0.55:.2f}s", 1.5) for n in range(3)]
    spouts = rect(peak_col * 10 - 10, 20, 28, 8, t["rule"], rx=1.5) + rect(490, 20, 28, 8, t["rule"], rx=1.5)
    css = (
        ".d{animation:d 1s linear infinite}.w{animation:w 1.65s linear infinite}"
        ".f{animation:f 3s ease infinite alternate}"
        f"@keyframes d{{to{{transform:translateY({sand_drop}px)}}}}"
        f"@keyframes w{{to{{transform:translateY({water_drop}px)}}}}"
        "@keyframes f{to{opacity:.5}}"
    )
    return tile(t, "Powder-Game: sand and water falling into a heap", css, "".join(falling + still + surface) + spouts, grid=False)


def twitch(t):
    gem = "".join(rect(280 + 10 * off, 60 + 10 * r, 10 * (8 - 2 * off), 10) for r, off in enumerate((3, 2, 1, 0, 0, 1, 2, 3)))
    plus = rect(380, 80, 30, 10) + rect(390, 70, 10, 30)
    body = (
        rect(100, 170, 440, 20, t["mute"])
        + rect(100, 170, 440, 20, t["violet"], "p")
        + f'<g class="q" fill="{t["violet"]}">{gem}</g><g class="u" fill="{t["ink"][0]}">{plus}</g>'
    )
    css = (
        ".p{transform-box:fill-box;transform-origin:0 50%;animation:p 7s steps(22,end) infinite}"
        f".q{{transform-box:fill-box;transform-origin:50% 50%;animation:q 7s {EASE_OUT} infinite}}"
        f".u{{opacity:0;animation:u 7s {EASE_OUT} infinite}}"
        "@keyframes p{0%{transform:scaleX(0)}72%,100%{transform:scaleX(1)}}"
        "@keyframes q{0%,71%{opacity:.4;transform:scale(1)}74%{opacity:1;transform:scale(1.1)}80%,96%{opacity:1;transform:scale(1)}100%{opacity:.4;transform:scale(1)}}"
        "@keyframes u{0%,73%{opacity:0;transform:translateY(0)}77%{opacity:1}92%,100%{opacity:0;transform:translateY(-30px)}}"
    )
    return tile(t, "Twitch-Miner-Rust: points filling up until a bonus is claimed", css, body)


def arsenal(t):
    blade = "".join(
        rect(120 if k == 0 else 110, 50 + 10 * k, 10 if k == 0 else 30, 10, cls="h", style=f"animation-delay:{(8 - k) * 60}ms")
        for k in range(9)
    )
    sword = (
        f'<g fill="{t["ink"][0]}">{blade}</g>'
        + rect(90, 140, 70, 10, t["gold"]) + rect(120, 150, 10, 30, t["rule"]) + rect(110, 180, 30, 10, t["gold"])
    )
    stats = [(0.45, 0.8), (0.85, 0.4), (0.3, 0.65), (0.6, 0.35), (0.55, 0.95)]  # before -> after; last row is the result
    bars = css = ""
    for i, (a, b) in enumerate(stats):
        y = 50 + 30 * i + (10 if i == 4 else 0)
        bars += rect(220, y, 340, 20, t["mute"]) + rect(220, y, 340, 20, t["gold"] if i == 4 else t["ink"][1], f"r r{i}")
        css += f".r{i}{{transform:scaleX({b});animation-name:r{i}}}@keyframes r{i}{{0%,30%{{transform:scaleX({a})}}70%,100%{{transform:scaleX({b})}}}}"
    css = (
        f".r{{transform-box:fill-box;transform-origin:0 50%;animation:4s {EASE_IN_OUT} infinite alternate}}" + css
        + ".h{animation:h 5s ease infinite}@keyframes h{0%,12%,100%{opacity:.7}5%{opacity:1}}"
    )
    return tile(t, "tarnisheds-arsenal: stats rebalancing while the attack rating climbs", css, sword + bars)


ASSETS = {"hero": hero, "audio-forge": audio, "powder-game": powder, "twitch-miner": twitch, "tarnisheds-arsenal": arsenal}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, draw in ASSETS.items():
        for theme, palette in THEMES.items():
            text = draw(palette)
            # nothing here may reach outside the file, or GitHub shows a broken image
            assert "<script" not in text and "href" not in text and "@import" not in text, name
            assert len(text) < 60_000, (name, len(text))
            (OUT / f"{name}-{theme}.svg").write_text(text, encoding="utf-8", newline="\n")
            print(f"{name}-{theme}.svg  {len(text) / 1024:.1f} KB")
