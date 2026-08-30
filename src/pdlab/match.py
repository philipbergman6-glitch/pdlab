"""Play one iterated match between two strategies (with optional noise)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pdlab.game import Move, PayoffMatrix
from pdlab.strategies import Strategy


@dataclass(frozen=True, slots=True)
class MatchResult:
    moves1: tuple[Move, ...]
    moves2: tuple[Move, ...]
    score1: float
    score2: float
    rounds: int

    @property
    def mean1(self) -> float:
        return self.score1 / self.rounds

    @property
    def mean2(self) -> float:
        return self.score2 / self.rounds

    def cooperation_rate(self, player: int) -> float:
        moves = self.moves1 if player == 1 else self.moves2
        return sum(m is Move.C for m in moves) / self.rounds


def play_match(
    s1: Strategy,
    s2: Strategy,
    rounds: int,
    pm: PayoffMatrix,
    rng: np.random.Generator,
    noise: float = 0.0,
) -> MatchResult:
    """Play ``rounds`` rounds; each intended move flips with probability ``noise``."""
    if rounds < 1:
        raise ValueError(f"rounds must be >= 1, got {rounds}")
    if not 0.0 <= noise <= 0.5:
        raise ValueError(f"noise must be in [0, 0.5], got {noise}")
    if s1 is s2:
        raise ValueError("a strategy object cannot play itself; use clone()")
    s1.reset()
    s2.reset()
    m1: list[Move] = []
    m2: list[Move] = []
    total1 = total2 = 0.0
    for _ in range(rounds):
        a = s1.play(rng)
        b = s2.play(rng)
        if noise > 0.0:
            u = rng.random(2)
            if u[0] < noise:
                a = a.flip()
            if u[1] < noise:
                b = b.flip()
        pa, pb = pm.payoffs(a, b)
        s1.observe(a, b, pa)
        s2.observe(b, a, pb)
        m1.append(a)
        m2.append(b)
        total1 += pa
        total2 += pb
    return MatchResult(tuple(m1), tuple(m2), total1, total2, rounds)
