"""Exact analysis of memory-one strategies as a 4-state Markov chain.

State order (from player X's point of view): CC, CD, DC, DD, where the first
letter is X's last move and the second is Y's.  A memory-one strategy is a
vector ``p = (p_CC, p_CD, p_DC, p_DD)`` of cooperation probabilities.

Implementation noise ``eps`` flips each intended move independently, which
turns a cooperation probability ``p`` into ``(1 - eps) p + eps (1 - p)``.

Also implements the zero-determinant (ZD) algebra of Press & Dyson (2012):
``p_tilde = alpha S_X + beta S_Y + gamma 1`` enforces
``alpha s_X + beta s_Y + gamma = 0`` on the long-run scores.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from pdlab.game import PayoffMatrix

Vec4 = NDArray[np.float64]


def _vec(p: Sequence[float], name: str = "p") -> Vec4:
    arr = np.asarray(p, dtype=float)
    if arr.shape != (4,):
        raise ValueError(f"{name} must have shape (4,), got {arr.shape}")
    if np.any(arr < 0) or np.any(arr > 1) or not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} entries must lie in [0, 1], got {arr}")
    return arr


def _check_eps(eps: float) -> float:
    if not 0.0 <= eps <= 0.5:
        raise ValueError(f"eps must be in [0, 0.5], got {eps}")
    return float(eps)


def noisy(p: Sequence[float], eps: float) -> Vec4:
    """Effective cooperation probabilities after implementation error ``eps``."""
    arr = _vec(p)
    e = _check_eps(eps)
    return (1 - 2 * e) * arr + e


def swap_perspective(q: Sequence[float]) -> Vec4:
    """Express Y's memory-one vector in X's state order (CD <-> DC)."""
    arr = _vec(q, "q")
    return arr[[0, 2, 1, 3]]


def transition_matrix(p: Sequence[float], q: Sequence[float], eps: float = 0.0) -> Vec4:
    """Row-stochastic 4x4 transition matrix over (CC, CD, DC, DD)."""
    px = noisy(p, eps)
    qy = noisy(swap_perspective(q), eps)
    M = np.empty((4, 4))
    for s in range(4):
        a, b = px[s], qy[s]
        M[s] = [a * b, a * (1 - b), (1 - a) * b, (1 - a) * (1 - b)]
    return M


def payoff_vectors(pm: PayoffMatrix) -> tuple[Vec4, Vec4]:
    """(S_X, S_Y) payoffs in state order CC, CD, DC, DD."""
    sx = np.array([pm.R, pm.S, pm.T, pm.P], dtype=float)
    sy = np.array([pm.R, pm.T, pm.S, pm.P], dtype=float)
    return sx, sy


def stationary_distribution(M: NDArray[np.float64], tol: float = 1e-10) -> Vec4:
    """Unique stationary distribution of a row-stochastic matrix.

    Raises ``ValueError`` if the chain does not have a unique stationary
    distribution (e.g. two deterministic strategies with ``eps = 0``); use
    :func:`expected_payoffs` or :func:`discounted_payoffs` in that case.
    """
    M = np.asarray(M, dtype=float)
    if M.shape != (4, 4):
        raise ValueError("M must be 4x4")
    if not np.allclose(M.sum(axis=1), 1.0, atol=1e-12):
        raise ValueError("M must be row-stochastic")
    A = M.T - np.eye(4)
    # nullity check: number of singular values ~ 0
    sv = np.linalg.svd(A, compute_uv=False)
    nullity = int(np.sum(sv < 1e-9))
    if nullity != 1:
        raise ValueError(
            f"chain has {nullity} stationary directions; stationary distribution not unique"
        )
    # solve A v = 0 with sum(v) = 1 via least squares on the augmented system
    Aug = np.vstack([A, np.ones((1, 4))])
    b = np.zeros(5)
    b[-1] = 1.0
    v, *_ = np.linalg.lstsq(Aug, b, rcond=None)
    v = np.clip(v, 0.0, None)
    v /= v.sum()
    if not np.allclose(v @ M, v, atol=tol):
        raise ValueError("failed to converge to a stationary distribution")
    return v


def stationary_payoffs(
    p: Sequence[float], q: Sequence[float], pm: PayoffMatrix, eps: float = 0.0
) -> tuple[float, float]:
    """Long-run per-round payoffs (s_X, s_Y) for memory-one X vs Y."""
    v = stationary_distribution(transition_matrix(p, q, eps))
    sx, sy = payoff_vectors(pm)
    return float(v @ sx), float(v @ sy)


def initial_distribution(p0: float, q0: float, eps: float = 0.0) -> Vec4:
    """Round-1 state distribution from initial cooperation probabilities."""
    for v in (p0, q0):
        if not 0 <= v <= 1:
            raise ValueError("initial probabilities must lie in [0, 1]")
    e = _check_eps(eps)
    a = (1 - 2 * e) * p0 + e
    b = (1 - 2 * e) * q0 + e
    return np.array([a * b, a * (1 - b), (1 - a) * b, (1 - a) * (1 - b)])


def expected_payoffs(
    p: Sequence[float],
    q: Sequence[float],
    p0: float,
    q0: float,
    pm: PayoffMatrix,
    rounds: int,
    eps: float = 0.0,
) -> tuple[float, float]:
    """Exact expected *average* per-round payoffs over ``rounds`` rounds."""
    if rounds < 1:
        raise ValueError("rounds must be >= 1")
    M = transition_matrix(p, q, eps)
    v = initial_distribution(p0, q0, eps)
    sx, sy = payoff_vectors(pm)
    acc = np.zeros(4)
    for _ in range(rounds):
        acc += v
        v = v @ M
    acc /= rounds
    return float(acc @ sx), float(acc @ sy)


def discounted_payoffs(
    p: Sequence[float],
    q: Sequence[float],
    p0: float,
    q0: float,
    pm: PayoffMatrix,
    delta: float,
    eps: float = 0.0,
) -> tuple[float, float]:
    """Exact normalised discounted payoffs ``(1-delta) sum_t delta^t pi_t``.

    Uses ``(1 - delta) v0 (I - delta M)^{-1}`` which is always well defined for
    ``0 <= delta < 1`` (reducible chains included).
    """
    if not 0 <= delta < 1:
        raise ValueError(f"delta must be in [0, 1), got {delta}")
    M = transition_matrix(p, q, eps)
    v0 = initial_distribution(p0, q0, eps)
    occ = (1 - delta) * np.linalg.solve((np.eye(4) - delta * M).T, v0)
    sx, sy = payoff_vectors(pm)
    return float(occ @ sx), float(occ @ sy)


# --------------------------------------------------------------------------
# Press & Dyson determinant formalism
# --------------------------------------------------------------------------
def press_dyson_determinant(
    p: Sequence[float], q: Sequence[float], f: Sequence[float]
) -> float:
    """D(p, q, f) of Press & Dyson (2012), eq. (4)."""
    px = _vec(p)
    qy = swap_perspective(q)
    fv = np.asarray(f, dtype=float)
    if fv.shape != (4,):
        raise ValueError("f must have shape (4,)")
    col1 = np.array([-1 + px[0] * qy[0], px[1] * qy[1], px[2] * qy[2], px[3] * qy[3]])
    col2 = np.array([-1 + px[0], -1 + px[1], px[2], px[3]])
    col3 = np.array([-1 + qy[0], qy[1], -1 + qy[2], qy[3]])
    return float(np.linalg.det(np.column_stack([col1, col2, col3, fv])))


def press_dyson_payoffs(
    p: Sequence[float], q: Sequence[float], pm: PayoffMatrix
) -> tuple[float, float]:
    """Stationary payoffs via the determinant formula s = D(p,q,S)/D(p,q,1)."""
    sx, sy = payoff_vectors(pm)
    den = press_dyson_determinant(p, q, np.ones(4))
    if abs(den) < 1e-12:
        raise ValueError("D(p, q, 1) = 0: stationary distribution not unique")
    return (
        press_dyson_determinant(p, q, sx) / den,
        press_dyson_determinant(p, q, sy) / den,
    )


def zd_vector(pm: PayoffMatrix, alpha: float, beta: float, gamma: float) -> Vec4:
    """Memory-one vector enforcing ``alpha s_X + beta s_Y + gamma = 0``.

    Raises ``ValueError`` if the resulting probabilities leave [0, 1].
    """
    sx, sy = payoff_vectors(pm)
    p_tilde = alpha * sx + beta * sy + gamma
    p = p_tilde + np.array([1.0, 1.0, 0.0, 0.0])
    if np.any(p < -1e-12) or np.any(p > 1 + 1e-12):
        raise ValueError(f"infeasible ZD strategy: p={p}")
    return np.clip(p, 0.0, 1.0)


def _max_phi(pm: PayoffMatrix, chi: float, baseline: float) -> float:
    """Largest phi with all four probabilities in [0, 1] for the ZD family
    enforcing ``s_X - baseline = chi (s_Y - baseline)``."""
    sx, sy = payoff_vectors(pm)
    # p_tilde = phi * (sx - baseline) - phi*chi*(sy - baseline)
    slope = (sx - baseline) - chi * (sy - baseline)
    offset = np.array([1.0, 1.0, 0.0, 0.0])
    bound = np.inf
    for k in range(4):
        m = slope[k]
        if m > 0:  # p_k = offset + m*phi <= 1
            bound = min(bound, (1 - offset[k]) / m)
        elif m < 0:  # p_k = offset + m*phi >= 0
            bound = min(bound, -offset[k] / m)
    if not np.isfinite(bound) or bound <= 0:
        raise ValueError("no feasible phi > 0 for this ZD family")
    return float(bound)


def extort_vector(pm: PayoffMatrix, chi: float = 2.0, phi_frac: float = 0.5) -> MemoryOneT:
    """Extortionate ZD strategy: ``s_X - P = chi (s_Y - P)`` with ``chi > 1``.

    ``phi_frac`` scales phi relative to its maximal feasible value.  The published
    Extort-2 of Stewart & Plotkin (2012), (8/9, 1/2, 1/3, 0), corresponds to
    ``phi_frac = 0.5`` under (5, 3, 1, 0).
    """
    if chi <= 1:
        raise ValueError("extortion requires chi > 1")
    if not 0 < phi_frac <= 1:
        raise ValueError("phi_frac must be in (0, 1]")
    phi = phi_frac * _max_phi(pm, chi, pm.P)
    p = zd_vector(pm, alpha=phi, beta=-phi * chi, gamma=phi * (chi - 1) * pm.P)
    return (float(p[0]), float(p[1]), float(p[2]), float(p[3]))


def generous_vector(pm: PayoffMatrix, chi: float = 2.0, phi_frac: float = 1.0) -> MemoryOneT:
    """Generous ZD strategy: ``s_X - R = chi (s_Y - R)`` with ``chi > 1``.

    ZDGTFT-2 of Stewart & Plotkin (2012), (1, 1/8, 1, 1/4), corresponds to
    ``phi_frac = 1`` under (5, 3, 1, 0).
    """
    if chi <= 1:
        raise ValueError("generous ZD requires chi > 1")
    if not 0 < phi_frac <= 1:
        raise ValueError("phi_frac must be in (0, 1]")
    phi = phi_frac * _max_phi(pm, chi, pm.R)
    p = zd_vector(pm, alpha=phi, beta=-phi * chi, gamma=phi * (chi - 1) * pm.R)
    return (float(p[0]), float(p[1]), float(p[2]), float(p[3]))


MemoryOneT = tuple[float, float, float, float]
