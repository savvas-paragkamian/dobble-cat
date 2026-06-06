"""Generate a Dobble / Spot-It deck as a projective plane of order n.

A projective plane of order ``n`` (n a prime power) yields a deck with:
  * n**2 + n + 1 symbols
  * n**2 + n + 1 cards
  * n + 1 symbols per card
  * each symbol appearing on exactly n + 1 cards
  * every pair of cards sharing exactly one common symbol

Two construction paths:
  * **prime n** (3, 5, 7, ...): a fast modular construction over Z/nZ.
  * **prime-power n** (4 = 2**2, 8, 9, ...): the projective plane PG(2, q)
    built from the finite field GF(q). Needed because Z/4Z is not a field,
    so the modular construction does NOT work for n = 4.

Orders used here: 5 -> 31 symbols (6/card) and 4 -> 21 symbols (5/card).
"""

from __future__ import annotations

# Monic irreducible polynomials for the prime powers we support, as coefficient
# lists low -> high (degree k, leading coeff 1 implied at index k).
_IRRED: dict[int, list[int]] = {
    4: [1, 1, 1],      # GF(2^2): x^2 + x + 1
    8: [1, 1, 0, 1],   # GF(2^3): x^3 + x + 1
    9: [1, 0, 1],      # GF(3^2): x^2 + 1
    16: [1, 1, 0, 0, 1],  # GF(2^4): x^4 + x + 1
    25: [2, 0, 1],     # GF(5^2): x^2 + 2
}


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def _prime_power(q: int) -> tuple[int, int] | None:
    """Return (p, k) if q == p**k with p prime, else None."""
    if q < 2:
        return None
    p = 2
    while p * p <= q:
        if q % p == 0:
            break
        p += 1
    else:
        p = q  # q is prime
    k, t = 0, q
    while t % p == 0:
        t //= p
        k += 1
    return (p, k) if t == 1 else None


class GF:
    """Finite field GF(q) for q a prime power. Elements are ints 0..q-1."""

    def __init__(self, q: int):
        pp = _prime_power(q)
        if pp is None:
            raise ValueError(f"{q} is not a prime power")
        self.q = q
        self.p, self.k = pp
        if self.k > 1 and q not in _IRRED:
            raise ValueError(f"no irreducible polynomial registered for GF({q})")
        self.mod = _IRRED.get(q)

    def _coeffs(self, a: int) -> list[int]:
        c = []
        for _ in range(self.k):
            c.append(a % self.p)
            a //= self.p
        return c

    def _from(self, c: list[int]) -> int:
        v = 0
        for d in reversed(range(self.k)):
            v = v * self.p + (c[d] % self.p)
        return v

    def add(self, a: int, b: int) -> int:
        if self.k == 1:
            return (a + b) % self.p
        A, B = self._coeffs(a), self._coeffs(b)
        return self._from([(A[i] + B[i]) % self.p for i in range(self.k)])

    def mul(self, a: int, b: int) -> int:
        if self.k == 1:
            return (a * b) % self.p
        A, B = self._coeffs(a), self._coeffs(b)
        prod = [0] * (2 * self.k)
        for i in range(self.k):
            if A[i]:
                for j in range(self.k):
                    prod[i + j] = (prod[i + j] + A[i] * B[j]) % self.p
        mod = self.mod
        for d in range(2 * self.k - 2, self.k - 1, -1):
            c = prod[d]
            if c:
                prod[d] = 0
                for i in range(self.k + 1):
                    prod[d - self.k + i] = (prod[d - self.k + i] - c * mod[i]) % self.p
        return self._from(prod[:self.k])


def _generate_deck_prime(n: int) -> list[list[int]]:
    """Fast modular construction. Valid only when n is prime."""
    cards: list[list[int]] = []
    for i in range(n + 1):
        cards.append([0] + [1 + n * i + j for j in range(n)])
    for i in range(n):
        for j in range(n):
            card = [i + 1]
            for k in range(n):
                card.append(n + 1 + n * k + (i * k + j) % n)
            cards.append(card)
    return cards


def _generate_deck_prime_power(q: int) -> list[list[int]]:
    """Build PG(2, q): symbols are points, cards are lines.

    Points (and lines) are the q**2 + q + 1 normalised non-zero triples over
    GF(q). A point P lies on a line L iff their GF(q) dot product is zero, and
    any two distinct lines meet in exactly one point -> the Dobble property.
    """
    gf = GF(q)
    f = range(q)
    points: list[tuple[int, int, int]] = []
    points += [(1, a, b) for a in f for b in f]
    points += [(0, 1, a) for a in f]
    points.append((0, 0, 1))

    index = {p: i for i, p in enumerate(points)}
    deck: list[list[int]] = []
    for line in points:  # lines share the same normalised representatives
        card = [
            index[p] for p in points
            if gf.add(gf.add(gf.mul(p[0], line[0]), gf.mul(p[1], line[1])),
                      gf.mul(p[2], line[2])) == 0
        ]
        deck.append(card)
    return deck


def generate_deck(n: int = 5) -> list[list[int]]:
    """Return the card/symbol incidence as a list of cards (lists of symbol ids).

    Works for any prime-power order n. Primes use the fast modular path;
    other prime powers (e.g. 4) use the finite-field construction.
    """
    if _is_prime(n):
        return _generate_deck_prime(n)
    if _prime_power(n) is None:
        raise ValueError(
            f"order {n} is not a prime power; no projective plane of that order exists"
        )
    return _generate_deck_prime_power(n)


if __name__ == "__main__":
    import sys

    order = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    deck = generate_deck(order)
    print(f"order {order}: {len(deck)} cards, {len(deck[0])} symbols/card")
    for idx, card in enumerate(deck, 1):
        print(f"card {idx:2d}: {sorted(card)}")
