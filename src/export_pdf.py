"""Export the generated SVG cards to PDF.

Produces a single multi-page PDF (one card per page, at the true 5.5 x 9 cm
size) and, with --per-card, one PDF per card. Uses rsvg-convert if available,
otherwise inkscape.

Usage:
    python3 src/export_pdf.py [--per-card]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def card_svgs(cards_dir: Path) -> list[Path]:
    return sorted(cards_dir.glob("card_*.svg"))


def to_pdf(svgs: list[Path], out: Path) -> None:
    """Render one or more SVGs into a (multi-page) PDF."""
    rsvg = shutil.which("rsvg-convert")
    inkscape = shutil.which("inkscape")
    out.parent.mkdir(parents=True, exist_ok=True)

    if rsvg:
        cmd = [rsvg, "-f", "pdf", "-o", str(out), *[str(s) for s in svgs]]
        subprocess.run(cmd, check=True)
    elif inkscape and len(svgs) == 1:
        subprocess.run(
            [inkscape, str(svgs[0]), "--export-type=pdf", f"--export-filename={out}"],
            check=True,
        )
    elif inkscape:
        # inkscape has no native multi-page merge; render singles then merge
        raise SystemExit(
            "Multi-page PDF needs rsvg-convert. Install librsvg, or use --per-card."
        )
    else:
        raise SystemExit("Need rsvg-convert (librsvg) or inkscape on PATH.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export cards to PDF.")
    parser.add_argument("--deck-dir", type=Path, default=ROOT,
                        help="deck folder containing cards/ (default: project root)")
    parser.add_argument("--per-card", action="store_true",
                        help="also write pdf/card_NN.pdf for each card")
    args = parser.parse_args()

    deck_dir = args.deck_dir.resolve()
    cards_dir = deck_dir / "cards"
    pdf_dir = deck_dir / "pdf"
    deck_pdf = pdf_dir / "dobble-cat.pdf"

    svgs = card_svgs(cards_dir)
    if not svgs:
        print(f"No card SVGs in {cards_dir}. Run src/generate.py first.")
        return 1

    to_pdf(svgs, deck_pdf)
    print(f"  {deck_pdf}  ({len(svgs)} pages, 5.5 x 9 cm each)")

    if args.per_card:
        for svg in svgs:
            to_pdf([svg], pdf_dir / f"{svg.stem}.pdf")
        print(f"  {len(svgs)} per-card PDFs in {pdf_dir}/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
