# Dobble CAT

This is the implementation of Dobble with 
objects from the classical athletics. 

Items (31 — Greek · english · OpenMoji hexcode):
    Ζάρι              dice          1F3B2
    Εμπόδιο           hurdle        E157
    Σχοινί            rope          1FAA2
    Στεφάνι           wreath        1F3F5
    Μπάλα ποδοσφαίρου soccer ball   26BD
    Μπάλα τέννις      tennis ball   1F3BE
    Σκάλα             ladder        1FA9C
    Κώνος             cone          (custom CC0)
    Χρονόμετρο        stopwatch     23F1
    Παπούτσι          shoe          1F45F
    Στάδιο            stadium       1F3DF
    Μπουκάλι          bottle        E0CB
    Αθλητής           athlete       1F3C3
    Στοπ              stop sign     1F6D1
    Μπανάνα           banana        1F34C
    Κύπελλο           trophy        1F3C6
    Μετάλλιο          gold medal    1F947
    Φανέλα            running shirt 1F3BD
    Μπάλα μπάσκετ     basketball    1F3C0
    Μπάλα βόλεϊ       volleyball    1F3D0
    Δίσκος            flying disc   1F94F
    Γάντι πυγμαχίας   boxing glove  1F94A
    Ποδηλάτης         cyclist       1F6B4
    Κολυμβητής        swimmer       1F3CA
    Στόχος            target        1F3AF
    Σταγόνα           droplet       1F4A7
    Κουδούνι          bell          1F514
    Τηλεβόας          megaphone     1F4E3
    Τέρμα             goal net      1F945
    Σημαία            flag in hole  26F3
    Γιο-γιο           yo-yo         1FA80

Create svg files, vertical orientation, 5.5 cm * 9 cm.

Follow the rules of DOBBLE, each card should have one and only one
common symbol with every other card. 

## How it works

31 symbols form a perfect order-5 Dobble deck (31 = 5² + 5 + 1): **31 cards,
6 symbols per card, every pair of cards shares exactly one symbol.** Symbol
artwork comes from [OpenMoji](https://openmoji.org) (CC BY-SA 4.0); the cone is
a custom CC0 SVG. See `ATTRIBUTION.md`.

## Build

```sh
python3 src/fetch_emojis.py   # download the OpenMoji SVGs into assets/emojis/ (cached)
python3 src/generate.py       # write cards/card_01.svg .. card_31.svg  (--seed N for variants)
python3 src/verify.py         # assert the Dobble property + balance
python3 src/export_pdf.py     # write pdf/dobble-cat.pdf (--per-card for one PDF each)
```

Output: `cards/card_01.svg` … `card_31.svg`, vertical, 5.5 cm × 9 cm, plus
`pdf/dobble-cat.pdf` (31 pages, one card per page at true size). PDF export
needs `rsvg-convert` (librsvg) or `inkscape` on PATH.

- `symbols.json` — the 31 items → emoji mapping (editable)
- `src/deck.py` — projective-plane deck generator (primes + prime powers)
- `src/layout.py` — SVG card composer (jittered grid, randomised rotation/size)

## Variants (`--order` / `--deck-dir`)

Each deck lives in its own folder with a `symbols.json`; the emoji cache in
`assets/emojis/` is shared. The number of symbols per card is `order + 1`, and
a deck needs exactly `order² + order + 1` symbols.

| Deck | Order | Symbols/card | Symbols / cards | Folder |
|------|-------|--------------|-----------------|--------|
| default | 5 | 6 | 31 / 31 | project root (`symbols.json`, `cards/`, `pdf/`) |
| fewer balls | 4 | 5 | 21 / 21 | `5-symbols/` |
| full size | 7 | 8 | 57 / 57 | `8-symbols/` |

`order` must be a prime power (3, 4, 5, 7, 8, 9 …). **Order 6 (7 symbols/card)
has no projective plane** (Bruck–Ryser) and is rejected — so there is no
7-per-card deck; 8 per card (order 7, the real Dobble size) is the next step up.
Build a variant by pointing the scripts at its folder, e.g. the 5-symbols deck:

```sh
python3 src/fetch_emojis.py --deck-dir 5-symbols
python3 src/generate.py    --deck-dir 5-symbols --order 4
python3 src/verify.py      --order 4
python3 src/export_pdf.py  --deck-dir 5-symbols
```

- `5-symbols/` trims the round/ball symbols down to soccer + tennis only.
- `8-symbols/` is the full 57-symbol deck; it adds a custom **racket** and
  **barbell** (CC0, like the cone) plus 22 more OpenMoji sports symbols. Build
  it the same way with `--deck-dir 8-symbols --order 7`.
