"""Nowak & May (1992) spatial Prisoner's Dilemma on a square lattice.

Each site plays the one-shot weak PD (R=1, T=b, P=S=0) with its 8 Moore
neighbours (and itself if ``self_interaction``), then adopts the strategy of
the highest-scoring site in its 3x3 neighbourhood (itself included).  Updates
are synchronous by default; ``asynchronous=True`` reproduces the
Huberman & Glance (1993) random-sequential variant.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

BoolGrid = NDArray[np.bool_]
FGrid = NDArray[np.float64]

_OFFSETS = [(di, dj) for di in (-1, 0, 1) for dj in (-1, 0, 1) if (di, dj) != (0, 0)]


def _shift(a: NDArray[np.float64], di: int, dj: int, periodic: bool) -> NDArray[np.float64]:
    """Array whose (i, j) entry is a[i+di, j+dj] (zero outside if not periodic)."""
    if periodic:
        return np.roll(np.roll(a, -di, axis=0), -dj, axis=1)
    out = np.zeros_like(a)
    n, m = a.shape
    src_i = slice(max(di, 0), n + min(di, 0))
    dst_i = slice(max(-di, 0), n + min(-di, 0))
    src_j = slice(max(dj, 0), m + min(dj, 0))
    dst_j = slice(max(-dj, 0), m + min(-dj, 0))
    out[dst_i, dst_j] = a[src_i, src_j]
    return out


@dataclass
class SpatialPD:
    b: float
    grid: BoolGrid  # True = cooperator
    periodic: bool = True
    self_interaction: bool = True

    def __post_init__(self) -> None:
        if not 1 < self.b < 2:
            raise ValueError("Nowak-May requires 1 < b < 2")
        self.grid = np.asarray(self.grid, dtype=bool)
        if self.grid.ndim != 2 or min(self.grid.shape) < 3:
            raise ValueError("grid must be 2-D with at least 3x3 sites")

    # --- constructors -----------------------------------------------------
    @classmethod
    def random(
        cls, L: int, b: float, coop_frac: float, rng: np.random.Generator, **kw: bool
    ) -> SpatialPD:
        if not 0 <= coop_frac <= 1:
            raise ValueError("coop_frac must be in [0, 1]")
        return cls(b, rng.random((L, L)) < coop_frac, **kw)

    @classmethod
    def single_defector(cls, L: int, b: float, **kw: bool) -> SpatialPD:
        g = np.ones((L, L), dtype=bool)
        g[L // 2, L // 2] = False
        return cls(b, g, **kw)

    # --- dynamics -------------------------------------------------------
    @property
    def cooperation(self) -> float:
        return float(self.grid.mean())

    def scores(self) -> FGrid:
        c = self.grid.astype(float)
        n_coop_neighbours = np.zeros_like(c)
        for di, dj in _OFFSETS:
            n_coop_neighbours += _shift(c, di, dj, self.periodic)
        if self.self_interaction:
            n_coop_neighbours += c
        # cooperator earns 1 per cooperating partner; defector earns b per cooperating partner
        return np.where(self.grid, n_coop_neighbours, self.b * n_coop_neighbours)

    def step(self) -> None:
        sc = self.scores()
        best_score = sc.copy()
        best_strat = self.grid.copy()
        for di, dj in _OFFSETS:
            s = _shift(sc, di, dj, self.periodic)
            g = _shift(self.grid.astype(float), di, dj, self.periodic) > 0.5
            better = s > best_score  # strict: ties keep the current best (own first)
            best_score = np.where(better, s, best_score)
            best_strat = np.where(better, g, best_strat)
        self.grid = best_strat

    def step_async(self, rng: np.random.Generator) -> None:
        """One sweep of L*L random single-site updates (Huberman & Glance 1993)."""
        n, m = self.grid.shape
        for _ in range(n * m):
            i, j = int(rng.integers(n)), int(rng.integers(m))
            sc = self.scores()
            best, strat = sc[i, j], self.grid[i, j]
            for di, dj in _OFFSETS:
                ii, jj = i + di, j + dj
                if self.periodic:
                    ii, jj = ii % n, jj % m
                elif not (0 <= ii < n and 0 <= jj < m):
                    continue
                if sc[ii, jj] > best:
                    best, strat = sc[ii, jj], self.grid[ii, jj]
            self.grid[i, j] = strat

    def run(
        self,
        steps: int,
        rng: np.random.Generator | None = None,
        asynchronous: bool = False,
        snapshots: int = 0,
    ) -> tuple[FGrid, list[BoolGrid]]:
        """Advance ``steps`` generations; return cooperation series and snapshots."""
        if steps < 1:
            raise ValueError("steps must be >= 1")
        if asynchronous and rng is None:
            raise ValueError("asynchronous update needs an rng")
        series = np.empty(steps + 1)
        series[0] = self.cooperation
        snaps: list[BoolGrid] = [self.grid.copy()] if snapshots else []
        every = max(1, steps // snapshots) if snapshots else 0
        for k in range(1, steps + 1):
            if asynchronous:
                assert rng is not None
                self.step_async(rng)
            else:
                self.step()
            series[k] = self.cooperation
            if snapshots and k % every == 0:
                snaps.append(self.grid.copy())
        return series, snaps
