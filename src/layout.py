"""Compose a single Dobble CAT card as a self-contained SVG.

Cards are 5.5 cm x 9 cm, vertical. Coordinates use millimetres (viewBox
"0 0 55 90"). Each of the 4 symbols on a card is the inlined content of an
OpenMoji (or custom) SVG, placed with a jittered 2x2 layout and randomised
rotation + size so cards look varied while staying non-overlapping.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

# --- card geometry (millimetres) ---------------------------------------------
CARD_W = 55.0
CARD_H = 90.0
CORNER_R = 4.0
MARGIN = 5.0           # blank border inside the card edge
GLYPH_VB = 72.0        # OpenMoji / custom glyphs are all 72x72

# placement: symbols are laid out on a jittered grid sized to the symbol count
DIAM_FACTOR_MIN, DIAM_FACTOR_MAX = 0.74, 0.96  # symbol diameter as fraction of cell
JITTER = 0.35                                   # fraction of free cell space used for jitter


def _grid_dims(count: int) -> tuple[int, int]:
    """Choose (cols, rows) for ``count`` symbols on the tall 55x90 card.

    Biases toward more rows than columns to suit the portrait aspect ratio.
    """
    usable_w = CARD_W - 2 * MARGIN
    usable_h = CARD_H - 2 * MARGIN
    cols = max(1, round(math.sqrt(count * usable_w / usable_h)))
    rows = math.ceil(count / cols)
    # shrink an over-wide grid if the last row would be sparse
    while cols > 1 and (cols - 1) * rows >= count:
        cols -= 1
        rows = math.ceil(count / cols)
    return cols, rows

_SVG_OPEN_RE = re.compile(r"<svg\b[^>]*>", re.IGNORECASE | re.DOTALL)
_SVG_CLOSE_RE = re.compile(r"</svg\s*>", re.IGNORECASE)
_VIEWBOX_RE = re.compile(r'viewBox\s*=\s*"([^"]+)"', re.IGNORECASE)


def load_glyph(path: Path) -> tuple[str, float, float]:
    """Return (inner_svg_markup, vb_width, vb_height) for a glyph SVG file."""
    text = path.read_text(encoding="utf-8")
    vb_match = _VIEWBOX_RE.search(text)
    if vb_match:
        _, _, vw, vh = (float(v) for v in vb_match.group(1).split())
    else:
        vw = vh = GLYPH_VB
    open_match = _SVG_OPEN_RE.search(text)
    start = open_match.end() if open_match else 0
    close_match = _SVG_CLOSE_RE.search(text)
    end = close_match.start() if close_match else len(text)
    return text[start:end].strip(), vw, vh


def _place(inner: str, vw: float, vh: float, cx: float, cy: float,
           diameter: float, rotation: float) -> str:
    """Wrap glyph markup in a group centred at (cx, cy), sized & rotated."""
    scale = diameter / max(vw, vh)
    # translate to target centre, rotate, scale, then recentre the glyph box
    transform = (
        f"translate({cx:.3f},{cy:.3f}) "
        f"rotate({rotation:.2f}) "
        f"scale({scale:.4f}) "
        f"translate({-vw / 2:.3f},{-vh / 2:.3f})"
    )
    return f'  <g transform="{transform}">\n{inner}\n  </g>'


def render_card(symbols, glyph_cache, rng) -> str:
    """Render one card.

    symbols: list of 4 dicts (each with a 'hexcode' used as the cache key)
    glyph_cache: {hexcode: (inner, vw, vh)}
    rng: random.Random instance (seeded by the caller for reproducibility)
    """
    cols, rows = _grid_dims(len(symbols))
    cells = [(c, r) for r in range(rows) for c in range(cols)]
    rng.shuffle(cells)

    usable_w = CARD_W - 2 * MARGIN
    usable_h = CARD_H - 2 * MARGIN
    cell_w = usable_w / cols
    cell_h = usable_h / rows
    cell_min = min(cell_w, cell_h)

    pieces: list[str] = []
    for symbol, (col, row) in zip(symbols, cells):
        inner, vw, vh = glyph_cache[symbol["hexcode"]]
        diameter = rng.uniform(DIAM_FACTOR_MIN, DIAM_FACTOR_MAX) * cell_min

        cell_cx = MARGIN + (col + 0.5) * cell_w
        cell_cy = MARGIN + (row + 0.5) * cell_h
        free_x = max(0.0, (cell_w - diameter) / 2) * JITTER
        free_y = max(0.0, (cell_h - diameter) / 2) * JITTER
        cx = cell_cx + rng.uniform(-free_x, free_x)
        cy = cell_cy + rng.uniform(-free_y, free_y)
        rotation = rng.uniform(0, 360)

        pieces.append(_place(inner, vw, vh, cx, cy, diameter, rotation))

    body = "\n".join(pieces)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" \
width="{CARD_W / 10:g}cm" height="{CARD_H / 10:g}cm" \
viewBox="0 0 {CARD_W:g} {CARD_H:g}">
  <rect x="0.5" y="0.5" width="{CARD_W - 1:g}" height="{CARD_H - 1:g}" \
rx="{CORNER_R:g}" ry="{CORNER_R:g}" fill="#FFFFFF" stroke="#222222" \
stroke-width="0.6"/>
{body}
</svg>
'''


# convenience for ad-hoc testing
if __name__ == "__main__":
    import json
    import random

    root = Path(__file__).resolve().parent.parent
    syms = json.loads((root / "symbols.json").read_text(encoding="utf-8"))["symbols"]
    cache = {
        s["hexcode"]: load_glyph(root / "assets" / "emojis" / f"{s['hexcode']}.svg")
        for s in syms
    }
    out = render_card(syms[:4], cache, random.Random(1))
    print(out[:600])
