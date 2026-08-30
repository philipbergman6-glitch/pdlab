"""Closed-form theory, derived symbolically with sympy and verified numerically.

* one-shot dominance / Nash / Pareto facts
* discount-factor thresholds for Grim Trigger and Tit-for-Tat (one-shot deviation checks)
* replicator dynamics for {ALLC, ALLD, TFT} in the discounted repeated game:
  payoff matrix, fixed points, Jacobian eigenvalues, ESS test
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import sympy as sp
from numpy.typing import NDArray

from pdlab.game import PayoffMatrix

T, R, P, S, delta = sp.symbols("T R P S delta", real=True)
"""Symbolic payoffs and discount factor shared by all derivations."""


def _subs(pm: PayoffMatrix) -> dict[sp.Symbol, float]:
    return {T: pm.T, R: pm.R, P: pm.P, S: pm.S}


# --------------------------------------------------------------------------
# one-shot game
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class OneShotFacts:
    d_dominant: bool
    dd_unique_nash: bool
    cc_pareto_dominates_dd: bool
    cc_beats_alternation: bool  # 2R > T + S

    @property
    def is_dilemma(self) -> bool:
        return all(
            (self.d_dominant, self.dd_unique_nash, self.cc_pareto_dominates_dd, self.cc_beats_alternation)
        )


def one_shot_facts(pm: PayoffMatrix) -> OneShotFacts:
    d_dom = pm.T > pm.R and pm.P > pm.S
    # In a symmetric 2x2 game with a strictly dominant strategy the unique NE is that profile.
    return OneShotFacts(
        d_dominant=d_dom,
        dd_unique_nash=d_dom,
        cc_pareto_dominates_dd=pm.R > pm.P,
        cc_beats_alternation=2 * pm.R > pm.T + pm.S,
    )


def best_responses(pm: PayoffMatrix) -> dict[str, str]:
    """Best response of the row player to each column move (C or D)."""
    return {
        "C": "D" if pm.T > pm.R else "C",
        "D": "D" if pm.P > pm.S else "C",
    }


# --------------------------------------------------------------------------
# repeated game thresholds
# --------------------------------------------------------------------------
V_coop = R / (1 - delta)
"""Normalised-free discounted value of perpetual mutual cooperation."""

V_dev_alld = T + delta * P / (1 - delta)
"""Value of deviating to D forever against Grim Trigger (or of ALLD vs TFT)."""

V_dev_alt = (T + delta * S) / (1 - delta**2)
"""Value of a one-shot deviation against TFT followed by TFT play: T, S, T, S, ..."""


def grim_threshold_symbolic() -> sp.Expr:
    """delta* such that Grim Trigger vs Grim Trigger is a SPE: (T-R)/(T-P)."""
    sol = sp.solve(sp.Eq(V_coop, V_dev_alld), delta)
    assert len(sol) == 1
    return sp.simplify(sol[0])


def tft_alld_threshold_symbolic() -> sp.Expr:
    """delta such that deviating to ALLD against TFT is not profitable: (T-R)/(T-P)."""
    return grim_threshold_symbolic()


def tft_alt_threshold_symbolic() -> sp.Expr:
    """delta such that alternating deviation against TFT is not profitable: (T-R)/(R-S)."""
    sol = sp.solve(sp.Eq(V_coop, V_dev_alt), delta)
    sol = [s for s in sol if s != -1]
    assert len(sol) == 1
    return sp.simplify(sol[0])


def tft_nash_threshold_symbolic() -> sp.Expr:
    """Axelrod (1984) Prop. 2: TFT is collectively stable iff delta >= max(...)."""
    return sp.Max(tft_alld_threshold_symbolic(), tft_alt_threshold_symbolic())


def tft_spe_conditions_symbolic() -> dict[str, sp.Rel]:
    """One-shot-deviation conditions for (TFT, TFT) to be subgame perfect.

    Three classes of histories must be checked:

    * on path (both cooperated last round): delta >= (T-R)/(R-S) and delta >= (T-R)/(T-P)
    * after being cheated (I played C, opponent D): TFT prescribes D, yielding T, S, T, S...;
      forgiving instead yields R forever, so punishing is optimal iff delta <= (T-R)/(R-S)
    * after mutual defection: TFT prescribes D forever (P each round); a one-shot C yields
      S, T, S, T... so defecting is optimal iff delta <= (P-S)/(T-P)

    Generic payoffs cannot satisfy both delta >= (T-R)/(R-S) and delta <= (T-R)/(R-S) except
    at a single value, hence TFT is (generically) *not* subgame perfect.
    """
    punish_value = (T + delta * S) / (1 - delta**2)
    forgive_value = R / (1 - delta)
    dd_value = P / (1 - delta)
    dd_dev_value = (S + delta * T) / (1 - delta**2)
    return {
        "on_path_vs_alld": delta >= (T - R) / (T - P),
        "on_path_vs_alternate": delta >= (T - R) / (R - S),
        "after_cheated_prefers_punish": sp.simplify(punish_value - forgive_value) >= 0,
        "after_cheated_threshold": delta <= (T - R) / (R - S),
        "after_dd_prefers_defect": sp.simplify(dd_value - dd_dev_value) >= 0,
        "after_dd_threshold": delta <= (P - S) / (T - P),
    }


@dataclass(frozen=True)
class Thresholds:
    grim_spe: float
    tft_vs_alld: float
    tft_vs_alternate: float
    tft_nash: float
    tft_after_dd_max: float

    @property
    def tft_is_spe_possible(self) -> bool:
        """True iff some delta in [0,1) satisfies every TFT one-shot-deviation condition."""
        d = self.tft_vs_alternate
        return (
            0 <= d < 1
            and d >= self.tft_vs_alld
            and d <= self.tft_after_dd_max
        )


def thresholds(pm: PayoffMatrix) -> Thresholds:
    sub = _subs(pm)
    g = float(grim_threshold_symbolic().subs(sub))
    a = float(tft_alt_threshold_symbolic().subs(sub))
    dd = (pm.P - pm.S) / (pm.T - pm.P)
    return Thresholds(
        grim_spe=g, tft_vs_alld=g, tft_vs_alternate=a, tft_nash=max(g, a), tft_after_dd_max=dd
    )


def cooperation_value(pm: PayoffMatrix, d: float) -> float:
    return float(V_coop.subs({**_subs(pm), delta: d}))


def deviation_values(pm: PayoffMatrix, d: float) -> dict[str, float]:
    sub = {**_subs(pm), delta: d}
    return {"alld": float(V_dev_alld.subs(sub)), "alternate": float(V_dev_alt.subs(sub))}


# --------------------------------------------------------------------------
# replicator dynamics for ALLC / ALLD / TFT
# --------------------------------------------------------------------------
STRATS3 = ("ALLC", "ALLD", "TFT")


def payoff_matrix_3_symbolic() -> sp.Matrix:
    """Normalised discounted payoff (1-delta) * sum delta^t pi_t of row vs column.

    ALLD vs TFT: T in round 1 then P forever  -> (1-delta) T + delta P
    TFT vs ALLD: S in round 1 then P forever  -> (1-delta) S + delta P
    """
    return sp.Matrix(
        [
            [R, S, R],
            [T, P, (1 - delta) * T + delta * P],
            [R, (1 - delta) * S + delta * P, R],
        ]
    )


def payoff_matrix_3(pm: PayoffMatrix, d: float) -> NDArray[np.float64]:
    if not 0 <= d < 1:
        raise ValueError("delta must be in [0, 1)")
    A = payoff_matrix_3_symbolic().subs({**_subs(pm), delta: d})
    return np.array(A.tolist(), dtype=float)


def replicator_rhs(x: NDArray[np.float64], A: NDArray[np.float64]) -> NDArray[np.float64]:
    x = np.asarray(x, dtype=float)
    f = A @ x
    return x * (f - x @ f)


def replicator_fixed_points_symbolic() -> dict[str, sp.Matrix]:
    """Fixed points of the 3-strategy replicator dynamics (symbolic)."""
    x1, x3 = sp.symbols("x1 x3", nonnegative=True)
    x = sp.Matrix([x1, 1 - x1 - x3, x3])
    A = payoff_matrix_3_symbolic()
    f = A * x
    phi = (x.T * f)[0]
    rhs = sp.Matrix([x[i] * (f[i] - phi) for i in range(3)])
    # interior point on the TFT-ALLD edge: x1 = 0, TFT and ALLD earn equal payoff
    edge = sp.solve(sp.Eq(f[1].subs(x1, 0), f[2].subs(x1, 0)), x3)
    assert len(edge) == 1
    x3_star = sp.simplify(edge[0])
    return {
        "ALLC": sp.Matrix([1, 0, 0]),
        "ALLD": sp.Matrix([0, 1, 0]),
        "TFT": sp.Matrix([0, 0, 1]),
        "TFT_ALLD_edge": sp.Matrix([0, 1 - x3_star, x3_star]),
        "_rhs": rhs,
    }


def tft_invasion_threshold_symbolic() -> sp.Expr:
    """Minimal TFT share x* to invade ALLD: TFT and ALLD payoffs equal on the edge."""
    return sp.simplify(replicator_fixed_points_symbolic()["TFT_ALLD_edge"][2])


def tft_invasion_threshold(pm: PayoffMatrix, d: float) -> float:
    return float(tft_invasion_threshold_symbolic().subs({**_subs(pm), delta: d}))


def jacobian_eigenvalues(x: NDArray[np.float64], A: NDArray[np.float64]) -> NDArray[np.complex128]:
    """Eigenvalues of the replicator Jacobian at ``x`` restricted to the simplex.

    Uses coordinates (x1, x3) with x2 = 1 - x1 - x3 so exactly two eigenvalues
    are returned; both are transverse to the simplex-normal direction.
    """
    x = np.asarray(x, dtype=float)
    if x.shape != (3,) or not np.isclose(x.sum(), 1.0):
        raise ValueError("x must be a point on the 3-simplex")

    def g(y: NDArray[np.float64]) -> NDArray[np.float64]:
        full = np.array([y[0], 1 - y[0] - y[1], y[1]])
        r = replicator_rhs(full, A)
        return np.array([r[0], r[2]])

    y0 = np.array([x[0], x[2]])
    h = 1e-6
    J = np.zeros((2, 2))
    for k in range(2):
        e = np.zeros(2)
        e[k] = h
        J[:, k] = (g(y0 + e) - g(y0 - e)) / (2 * h)
    return np.linalg.eigvals(J)


def jacobian_eigenvalues_symbolic(point: str) -> list[sp.Expr]:
    """Symbolic eigenvalues at a named fixed point (vertices and edge point)."""
    fps = replicator_fixed_points_symbolic()
    if point not in fps or point.startswith("_"):
        raise KeyError(point)
    x1, x3 = sp.symbols("x1 x3", nonnegative=True)
    rhs = fps["_rhs"]
    g = sp.Matrix([rhs[0], rhs[2]])
    J = g.jacobian([x1, x3])
    pt = fps[point]
    Jp = J.subs({x1: pt[0], x3: pt[2]})
    return [sp.simplify(e) for e in Jp.eigenvals(multiple=True)]


def is_ess(A: NDArray[np.float64], i: int, tol: float = 1e-12) -> bool:
    """Maynard Smith ESS conditions for pure strategy ``i`` in payoff matrix ``A``."""
    n = A.shape[0]
    for j in range(n):
        if j == i:
            continue
        if A[i, i] > A[j, i] + tol:
            continue
        if abs(A[i, i] - A[j, i]) <= tol and A[i, j] > A[j, j] + tol:
            continue
        return False
    return True


def is_neutrally_stable(A: NDArray[np.float64], i: int, tol: float = 1e-12) -> bool:
    """Weaker condition: A_ii >= A_ji and, if equal, A_ij >= A_jj."""
    n = A.shape[0]
    for j in range(n):
        if j == i:
            continue
        if A[i, i] > A[j, i] + tol:
            continue
        if abs(A[i, i] - A[j, i]) <= tol and A[i, j] >= A[j, j] - tol:
            continue
        return False
    return True
