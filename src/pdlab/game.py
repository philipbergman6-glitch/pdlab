"""Normal-form Prisoner's Dilemma: moves, payoff matrix, validation.

The payoff matrix is the single source of truth for every other module.
Invalid parameters raise immediately (hard-fail policy).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Move(Enum):
    """A single action in the Prisoner's Dilemma."""

    C = "C"
    D = "D"

    def flip(self) -> Move:
        """Return the opposite move (used to model implementation noise)."""
        return Move.D if self is Move.C else Move.C

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


C = Move.C
D = Move.D


@dataclass(frozen=True, slots=True)
class PayoffMatrix:
    """Symmetric 2x2 PD payoffs for the *row* player.

    ``T`` temptation (D vs C), ``R`` reward (C vs C), ``P`` punishment (D vs D),
    ``S`` sucker (C vs D).

    A *strict* Prisoner's Dilemma requires ``T > R > P > S`` and ``2R > T + S``.
    Nowak & May (1992) use the *weak* dilemma ``T > R >= P >= S`` with ``P == S == 0``;
    set ``strict=False`` to allow it.  ``2R > T + S`` is always enforced so that
    mutual cooperation Pareto-dominates alternating exploitation.
    """

    T: float
    R: float
    P: float
    S: float
    strict: bool = True

    def __post_init__(self) -> None:
        vals = (self.T, self.R, self.P, self.S)
        for name, v in zip("TRPS", vals, strict=True):
            if not isinstance(v, int | float) or isinstance(v, bool):
                raise TypeError(f"{name} must be a real number, got {v!r}")
            if v != v or v in (float("inf"), float("-inf")):
                raise ValueError(f"{name} must be finite, got {v!r}")
        if self.strict:
            if not (self.T > self.R > self.P > self.S):
                raise ValueError(f"strict PD requires T > R > P > S, got {vals}")
        else:
            if not (self.T > self.R >= self.P >= self.S):
                raise ValueError(f"weak PD requires T > R >= P >= S, got {vals}")
        if not (2 * self.R > self.T + self.S):
            raise ValueError(f"PD requires 2R > T + S, got 2R={2 * self.R}, T+S={self.T + self.S}")

    # --- constructors -----------------------------------------------------
    @classmethod
    def axelrod(cls) -> PayoffMatrix:
        """Canonical Axelrod (1984) payoffs (5, 3, 1, 0)."""
        return cls(T=5, R=3, P=1, S=0)

    @classmethod
    def nowak_may(cls, b: float) -> PayoffMatrix:
        """Nowak & May (1992) weak dilemma: R=1, T=b, P=S=0, valid for 1 < b < 2."""
        if not 1 < b < 2:
            raise ValueError(f"Nowak-May requires 1 < b < 2 (so 2R > T + S), got b={b}")
        return cls(T=b, R=1, P=0, S=0, strict=False)

    @classmethod
    def donation(cls, b: float, c: float) -> PayoffMatrix:
        """Donation game: cooperator pays c to give b (b > c > 0)."""
        if not b > c > 0:
            raise ValueError(f"donation game requires b > c > 0, got b={b}, c={c}")
        return cls(T=b, R=b - c, P=0, S=-c)

    # --- payoffs ----------------------------------------------------------
    def payoff(self, own: Move, other: Move) -> float:
        """Row player's payoff when playing ``own`` against ``other``."""
        if own is C:
            return self.R if other is C else self.S
        return self.T if other is C else self.P

    def payoffs(self, m1: Move, m2: Move) -> tuple[float, float]:
        """Both players' payoffs."""
        return self.payoff(m1, m2), self.payoff(m2, m1)

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.T, self.R, self.P, self.S)

    def as_matrix(self) -> list[list[float]]:
        """Row-player matrix in the state order [C, D] x [C, D]."""
        return [[self.R, self.S], [self.T, self.P]]

    # --- one-shot theory --------------------------------------------------
    def dominance_gap(self) -> tuple[float, float]:
        """(T - R, P - S): how much D beats C against C and against D.

        Both strictly positive <=> D strictly dominates C.
        """
        return (self.T - self.R, self.P - self.S)

    def is_strict(self) -> bool:
        return self.T > self.R > self.P > self.S


STATES: tuple[tuple[Move, Move], ...] = ((C, C), (C, D), (D, C), (D, D))
"""Memory-one state order (own, opponent): CC, CD, DC, DD."""


def state_index(own: Move, other: Move) -> int:
    """Index of (own, other) in :data:`STATES`."""
    return (0 if own is C else 2) + (0 if other is C else 1)
