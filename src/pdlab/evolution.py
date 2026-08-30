"""Population dynamics: replicator ODE, Moran process, fixation probabilities."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

from pdlab.analytic import replicator_rhs

FArr = NDArray[np.float64]


def _check_matrix(A: FArr) -> FArr:
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("payoff matrix must be square")
    if not np.all(np.isfinite(A)):
        raise ValueError("payoff matrix must be finite")
    return A


def _check_simplex(x: Sequence[float], n: int) -> FArr:
    x = np.asarray(x, dtype=float)
    if x.shape != (n,) or np.any(x < 0) or not np.isclose(x.sum(), 1.0, atol=1e-9):
        raise ValueError(f"x must be a probability vector of length {n}, got {x}")
    return x / x.sum()


@dataclass(frozen=True)
class Trajectory:
    t: FArr
    x: FArr  # shape (len(t), n)


def replicator_trajectory(
    A: FArr, x0: Sequence[float], t_max: float, n_points: int = 400, rtol: float = 1e-9
) -> Trajectory:
    """Integrate the replicator ODE dx_i/dt = x_i ((Ax)_i - x.Ax)."""
    A = _check_matrix(A)
    x0a = _check_simplex(x0, A.shape[0])
    if t_max <= 0:
        raise ValueError("t_max must be positive")
    t_eval = np.linspace(0, t_max, n_points)
    sol = solve_ivp(
        lambda _t, y: replicator_rhs(y, A), (0, t_max), x0a, t_eval=t_eval, rtol=rtol, atol=1e-12
    )
    if not sol.success:
        raise RuntimeError(f"replicator integration failed: {sol.message}")
    x = np.clip(sol.y.T, 0, 1)
    x /= x.sum(axis=1, keepdims=True)
    return Trajectory(sol.t, x)


def replicator_discrete(
    A: FArr, x0: Sequence[float], generations: int, mutation: float = 0.0
) -> FArr:
    """Discrete-time replicator map with uniform mutation (needs positive payoffs)."""
    A = _check_matrix(A)
    n = A.shape[0]
    x = _check_simplex(x0, n)
    if generations < 1:
        raise ValueError("generations must be >= 1")
    if not 0 <= mutation <= 1:
        raise ValueError("mutation must be in [0, 1]")
    if np.any(A <= 0):
        raise ValueError("discrete replicator needs strictly positive payoffs")
    out = np.empty((generations + 1, n))
    out[0] = x
    for g in range(1, generations + 1):
        f = A @ x
        x = x * f / (x @ f)
        x = (1 - mutation) * x + mutation / n
        out[g] = x
    return out


# --------------------------------------------------------------------------
# Moran process
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class MoranResult:
    counts: NDArray[np.int64]  # shape (steps+1, n)
    fixated: int | None  # index of fixated strategy, or None

    @property
    def frequencies(self) -> FArr:
        return np.asarray(self.counts / self.counts.sum(axis=1, keepdims=True))


def moran_process(
    A: FArr,
    counts0: Sequence[int],
    steps: int,
    rng: np.random.Generator,
    w: float = 1.0,
    mutation: float = 0.0,
    stop_at_fixation: bool = True,
) -> MoranResult:
    """Frequency-dependent Moran process (Nowak 2006, ch. 6).

    Fitness f_i = 1 - w + w * pi_i, where pi_i is i's mean payoff against the
    rest of the population (self-interaction excluded).  One birth-death event
    per step; offspring mutate to a uniformly random strategy with prob ``mutation``.
    """
    A = _check_matrix(A)
    n = A.shape[0]
    counts = np.asarray(counts0, dtype=np.int64)
    if counts.shape != (n,) or np.any(counts < 0) or counts.sum() < 2:
        raise ValueError("counts0 must be non-negative with population >= 2")
    if not 0 <= w <= 1 or not 0 <= mutation <= 1 or steps < 1:
        raise ValueError("bad Moran parameters")
    N = int(counts.sum())
    hist = np.empty((steps + 1, n), dtype=np.int64)
    hist[0] = counts
    fixated: int | None = None
    for s in range(1, steps + 1):
        # payoffs excluding self
        pi = (A @ counts - np.diag(A)) / (N - 1)
        fit = 1 - w + w * pi
        fit = np.where(counts > 0, fit, 0.0)
        if np.any(fit < 0):
            raise ValueError("negative fitness; reduce w or shift payoffs")
        weights = counts * fit
        tot = weights.sum()
        if tot <= 0:
            raise ValueError("zero total fitness")
        parent = int(rng.choice(n, p=weights / tot))
        if mutation > 0 and rng.random() < mutation:
            parent = int(rng.integers(0, n))
        victim = int(rng.choice(n, p=counts / N))
        counts = counts.copy()
        counts[victim] -= 1
        counts[parent] += 1
        hist[s] = counts
        if stop_at_fixation and mutation == 0 and np.max(counts) == N:
            fixated = int(np.argmax(counts))
            hist = hist[: s + 1]
            break
    return MoranResult(hist, fixated)


def fixation_probability(A: FArr, mutant: int, resident: int, N: int, w: float = 1.0) -> float:
    """Exact fixation probability of one ``mutant`` in N-1 ``resident`` players.

    rho = 1 / (1 + sum_{k=1}^{N-1} prod_{j=1}^{k} g_j / f_j)   (Nowak 2006, eq. 6.4)
    """
    A = _check_matrix(A)
    if N < 2:
        raise ValueError("N must be >= 2")
    a, b = A[mutant, mutant], A[mutant, resident]
    c, d = A[resident, mutant], A[resident, resident]
    total = 1.0
    prod = 1.0
    for j in range(1, N):
        f_j = 1 - w + w * (a * (j - 1) + b * (N - j)) / (N - 1)
        g_j = 1 - w + w * (c * j + d * (N - j - 1)) / (N - 1)
        if f_j <= 0 or g_j <= 0:
            raise ValueError("non-positive fitness in fixation formula")
        prod *= g_j / f_j
        total += prod
    return 1.0 / total
