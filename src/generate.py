"""Build the full Dobble CAT deck: 13 card SVGs in cards/.

Usage:
    python src/generate.py [--seed N]

Loads symbols.json, builds the order-3 projective-plane deck, renders each
card via layout.render_card, and writes cards/card_01.svg .. card_13.svg.
Verifies the Dobble invariants before writing. A fixed seed keeps runs
reproducible.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

from deck import generate_deck
from layout import load_glyph, render_card
from verify import verify_deck

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets" / "emojis"   # shared across decks


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Dobble CAT deck.")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--order", type=int, default=5,
                        help="projective-plane order (5 -> 31 cards, 4 -> 21 cards)")
    parser.add_argument("--deck-dir", type=Path, default=ROOT,
                        help="folder with symbols.json; cards/ written here")
    args = parser.parse_args()

    order = args.order
    deck_dir = args.deck_dir.resolve()
    cards_dir = deck_dir / "cards"

    symbols = json.loads((deck_dir / "symbols.json").read_text(encoding="utf-8"))["symbols"]
    expected = order * order + order + 1
    if len(symbols) != expected:
        print(f"symbols.json has {len(symbols)} symbols, need {expected} for order {order}.")
        return 1

    deck = generate_deck(order)
    problems = verify_deck(deck, order)
    if problems:
        print("Refusing to render an invalid deck:")
        for p in problems:
            print(f"  - {p}")
        return 1

    glyph_cache = {}
    for s in symbols:
        path = ASSETS_DIR / f"{s['hexcode']}.svg"
        if not path.exists():
            print(f"Missing asset {path}. Run src/fetch_emojis.py first.")
            return 1
        glyph_cache[s["hexcode"]] = load_glyph(path)

    cards_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    for idx, card in enumerate(deck, 1):
        card_symbols = [symbols[i] for i in card]
        svg = render_card(card_symbols, glyph_cache, rng)
        out = cards_dir / f"card_{idx:02d}.svg"
        out.write_text(svg, encoding="utf-8")
        names = ", ".join(s["english"] for s in card_symbols)
        print(f"  card_{idx:02d}.svg  [{names}]")

    print(f"\nWrote {len(deck)} cards to {cards_dir} "
          f"(order={order}, seed={args.seed}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
