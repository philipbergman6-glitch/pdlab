"""Axelrod-style round-robin tournament engine."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd

from pdlab.game import PayoffMatrix
from pdlab.match import play_match
from pdlab.strategies import Strategy


@dataclass(frozen=True)
class TournamentResult:
    names: tuple[str, ...]
    #: shape (reps, n, n): mean per-round payoff of row strategy vs column strategy
    payoff: np.ndarray
    #: shape (reps, n, n): cooperation rate of row strategy vs column
    coop: np.ndarray
    rounds: int
    noise: float

    @property
    def mean_payoff(self) -> np.ndarray:
        """(n, n) payoff matrix averaged over repetitions.

        The diagonal is NaN when the tournament was run with ``include_self=False``:
        those matches were never played.
        """
        return np.asarray(self.payoff.mean(axis=0))

    def scores(self) -> pd.DataFrame:
        """Mean score per round (averaged over the opponents actually played) per rep."""
        per_rep = np.nanmean(self.payoff, axis=2)  # (reps, n)
        df = pd.DataFrame(
            {
                "strategy": self.names,
                "score": per_rep.mean(axis=0),
                "score_sd": per_rep.std(axis=0, ddof=1) if per_rep.shape[0] > 1 else 0.0,
                "coop_rate": np.nanmean(self.coop, axis=(0, 2)),
            }
        )
        df = df.sort_values("score", ascending=False, ignore_index=True)
        df.insert(0, "rank", np.arange(1, len(df) + 1))
        return df

    def payoff_table(self) -> pd.DataFrame:
        return pd.DataFrame(self.mean_payoff, index=list(self.names), columns=list(self.names))


def round_robin(
    strategies: Sequence[Strategy],
    rounds: int = 200,
    pm: PayoffMatrix | None = None,
    noise: float = 0.0,
    reps: int = 1,
    seed: int = 0,
    include_self: bool = True,
) -> TournamentResult:
    """Every strategy plays every other (and itself if ``include_self``).

    Each pairing is played once per repetition with fresh clones, so strategy
    objects never leak state between matches.  Results are fully determined by
    ``seed``.
    """
    pm = pm or PayoffMatrix.axelrod()
    if reps < 1:
        raise ValueError("reps must be >= 1")
    n = len(strategies)
    if n < 2:
        raise ValueError("need at least two strategies")
    names = tuple(s.name for s in strategies)
    if len(set(names)) != n:
        raise ValueError(f"strategy names must be unique, got {names}")
    rng = np.random.default_rng(seed)
    payoff = np.full((reps, n, n), np.nan)
    coop = np.full((reps, n, n), np.nan)
    for r in range(reps):
        for i in range(n):
            for j in range(i, n):
                if i == j and not include_self:
                    continue
                a, b = strategies[i].clone(), strategies[j].clone()
                res = play_match(a, b, rounds, pm, rng, noise)
                payoff[r, i, j] = res.mean1
                payoff[r, j, i] = res.mean2
                coop[r, i, j] = res.cooperation_rate(1)
                coop[r, j, i] = res.cooperation_rate(2)
    return TournamentResult(names, payoff, coop, rounds, noise)
