"""Download the OpenMoji color SVGs listed in symbols.json into assets/emojis/.

Idempotent: files already present are skipped. Symbols with source 'custom'
are expected to already exist locally (e.g. the hand-drawn cone) and are only
checked for presence. Exits non-zero if any asset is missing.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets" / "emojis"   # shared cache across all decks
OPENMOJI_URL = "https://openmoji.org/data/color/svg/{hex}.svg"


def asset_path(symbol: dict) -> Path:
    return ASSETS_DIR / f"{symbol['hexcode']}.svg"


def load_symbols(deck_dir: Path) -> list[dict]:
    with open(deck_dir / "symbols.json", encoding="utf-8") as fh:
        return json.load(fh)["symbols"]


def fetch_one(symbol: dict) -> bool:
    """Ensure the SVG for one symbol exists locally. Return True on success."""
    dest = asset_path(symbol)
    label = f"{symbol['english']} ({symbol['hexcode']})"

    if symbol["source"] == "custom":
        if dest.exists():
            print(f"  custom  {label}: present")
            return True
        print(f"  custom  {label}: MISSING at {dest}")
        return False

    if dest.exists():
        print(f"  cached  {label}")
        return True

    url = OPENMOJI_URL.format(hex=symbol["hexcode"])
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
    except Exception as exc:  # noqa: BLE001 - report and continue
        print(f"  FAILED  {label}: {exc}")
        return False
    dest.write_bytes(data)
    print(f"  fetched {label}: {len(data)} bytes")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch OpenMoji SVGs for a deck.")
    parser.add_argument("--deck-dir", type=Path, default=ROOT,
                        help="folder containing symbols.json (default: project root)")
    args = parser.parse_args()

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    symbols = load_symbols(args.deck_dir.resolve())
    print(f"Resolving {len(symbols)} symbol assets into {ASSETS_DIR}")
    ok = all(fetch_one(s) for s in symbols)
    if not ok:
        print("\nSome assets are missing. Fix symbols.json or add the file.")
        return 1
    print("\nAll symbol assets present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
