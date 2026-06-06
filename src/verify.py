"""Verify that a generated deck obeys the Dobble invariants.

Run directly to check the order-3 deck, or import ``verify_deck`` for use
elsewhere. Exits non-zero on any violation so it can gate a build.
"""

from __future__ import annotations

import sys
from itertools import combinations

from deck import generate_deck


def verify_deck(deck: list[list[int]], n: int = 3) -> list[str]:
    """Return a list of human-readable problems (empty == valid)."""
    problems: list[str] = []
    expected_count = n * n + n + 1
    symbols_per_card = n + 1

    if len(deck) != expected_count:
        problems.append(f"expected {expected_count} cards, got {len(deck)}")

    for idx, card in enumerate(deck, 1):
        if len(set(card)) != symbols_per_card:
            problems.append(
                f"card {idx} has {len(set(card))} distinct symbols, "
                f"expected {symbols_per_card}: {sorted(card)}"
            )

    # The core invariant: every pair of cards shares exactly one symbol.
    for (i, a), (j, b) in combinations(enumerate(deck, 1), 2):
        shared = set(a) & set(b)
        if len(shared) != 1:
            problems.append(
                f"cards {i} and {j} share {len(shared)} symbols "
                f"(expected 1): {sorted(shared)}"
            )

    # Balance: each symbol used on exactly n + 1 cards.
    usage: dict[int, int] = {}
    for card in deck:
        for symbol in card:
            usage[symbol] = usage.get(symbol, 0) + 1
    if len(usage) != expected_count:
        problems.append(
            f"expected {expected_count} distinct symbols, got {len(usage)}"
        )
    for symbol, count in sorted(usage.items()):
        if count != symbols_per_card:
            problems.append(
                f"symbol {symbol} used on {count} cards, "
                f"expected {symbols_per_card}"
            )

    return problems


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Verify a Dobble deck's invariants.")
    parser.add_argument("--order", type=int, default=5, help="projective-plane order")
    n = parser.parse_args().order
    deck = generate_deck(n)
    problems = verify_deck(deck, n)
    if problems:
        print("DECK INVALID:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(
        f"Deck OK: {len(deck)} cards, {n + 1} symbols/card, "
        "every pair shares exactly one symbol, balanced."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
