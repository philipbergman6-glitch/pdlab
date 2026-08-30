"""Backward induction in the finitely repeated PD."""

from __future__ import annotations

import numpy as np
import pytest

from pdlab.finite import backward_induction, stage_nash_pure
from pdlab.game import PayoffMatrix

PM = PayoffMatrix.axelrod()


def test_stage_nash_of_the_one_shot_pd_is_unique_defection():
    A = np.array(PM.as_matrix())
    assert stage_nash_pure(A, A.T) == [(1, 1)]


def test_stage_nash_of_a_coordination_game_has_two_equilibria():
    A = np.array([[2.0, 0.0], [0.0, 1.0]])
    assert stage_nash_pure(A, A.T) == [(0, 0), (1, 1)]


def test_stage_nash_validation():
    with pytest.raises(ValueError, match="equally shaped"):
        stage_nash_pure(np.ones((2, 2)), np.ones((2, 3)))
    with pytest.raises(ValueError, match="equally shaped"):
        stage_nash_pure(np.ones(2), np.ones(2))


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_backward_induction_defects_in_every_round(n):
    path, total = backward_induction(PM, n)
    assert path == [(1, 1)] * n
    assert total == pytest.approx(n * PM.P)


def test_backward_induction_on_the_donation_game():
    pm = PayoffMatrix.donation(b=4, c=1)
    path, total = backward_induction(pm, 3)
    assert path == [(1, 1)] * 3
    assert total == pytest.approx(3 * pm.P)


def test_backward_induction_rejects_non_positive_n():
    with pytest.raises(ValueError, match="n must be"):
        backward_induction(PM, 0)


class _CoordinationGame:
    """Duck-typed stand-in exposing a coordination stage game."""

    def as_matrix(self) -> list[list[float]]:
        return [[2.0, 0.0], [0.0, 1.0]]


def test_backward_induction_raises_when_the_stage_game_has_two_equilibria():
    with pytest.raises(ValueError, match="pure NE; SPE not unique"):
        backward_induction(_CoordinationGame(), 3)  # type: ignore[arg-type]
