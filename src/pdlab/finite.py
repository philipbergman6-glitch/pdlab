"""Finitely repeated PD: backward induction.

For a stage game with a unique Nash equilibrium, the unique subgame-perfect
equilibrium of the n-fold repetition plays that equilibrium in every round
after every history (Selten; see Fudenberg & Tirole 1991, Prop. 4.1).  We
verify this constructively: continuation values are history-independent, so
each stage reduces to the one-shot game shifted by a constant.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pdlab.game import PayoffMatrix


def stage_nash_pure(A: NDArray[np.float64], B: NDArray[np.float64]) -> list[tuple[int, int]]:
    """All pure Nash equilibria of a 2-player bimatrix game (A row, B column)."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    if A.shape != B.shape or A.ndim != 2:
        raise ValueError("A and B must be equally shaped 2-D arrays")
    eqs = []
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            if A[i, j] >= A[:, j].max() and B[i, j] >= B[i, :].max():
                eqs.append((i, j))
    return eqs


def backward_induction(pm: PayoffMatrix, n: int) -> tuple[list[tuple[int, int]], float]:
    """SPE action profile per round (0=C, 1=D) and the row player's total payoff.

    Raises if any stage has multiple pure equilibria (then the SPE is not unique
    and this simple solver does not apply) -- never the case for a strict PD.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    A = np.array(pm.as_matrix())
    B = A.T.copy()
    cont_row = cont_col = 0.0
    path: list[tuple[int, int]] = []
    for _ in range(n):  # work backwards from the last round
        eqs = stage_nash_pure(A + cont_row, B + cont_col)
        if len(eqs) != 1:
            raise ValueError(f"stage game has {len(eqs)} pure NE; SPE not unique")
        i, j = eqs[0]
        cont_row += A[i, j]
        cont_col += B[i, j]
        path.append((i, j))
    return path[::-1], cont_row
