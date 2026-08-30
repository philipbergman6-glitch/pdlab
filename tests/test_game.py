"""PayoffMatrix validation, payoffs and state indexing."""

from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pdlab.game import STATES, C, D, Move, PayoffMatrix, state_index

FINITE = st.floats(min_value=-50, max_value=50, allow_nan=False, allow_infinity=False, width=32)


def _is_strict_pd(T: float, R: float, P: float, S: float) -> bool:
    return T > R > P > S and 2 * R > T + S


def _is_weak_pd(T: float, R: float, P: float, S: float) -> bool:
    return T > R >= P >= S and 2 * R > T + S


@settings(max_examples=400, deadline=None)
@given(T=FINITE, R=FINITE, P=FINITE, S=FINITE)
def test_strict_constructor_succeeds_exactly_on_strict_pds(T, R, P, S):
    try:
        PayoffMatrix(T=T, R=R, P=P, S=S)
        ok = True
    except ValueError:
        ok = False
    assert ok is _is_strict_pd(T, R, P, S)


@settings(max_examples=400, deadline=None)
@given(T=FINITE, R=FINITE, P=FINITE, S=FINITE)
def test_weak_constructor_succeeds_exactly_on_weak_pds(T, R, P, S):
    try:
        PayoffMatrix(T=T, R=R, P=P, S=S, strict=False)
        ok = True
    except ValueError:
        ok = False
    assert ok is _is_weak_pd(T, R, P, S)


def test_weak_allows_ties_strict_does_not():
    PayoffMatrix(T=1.5, R=1, P=0, S=0, strict=False)
    with pytest.raises(ValueError, match="strict PD"):
        PayoffMatrix(T=1.5, R=1, P=0, S=0)


def test_2r_gt_t_plus_s_enforced_even_in_weak_mode():
    with pytest.raises(ValueError, match=r"2R > T \+ S"):
        PayoffMatrix(T=2.5, R=1, P=0, S=0, strict=False)


@pytest.mark.parametrize("bad", ["5", None, complex(1, 0), [1]])
def test_non_real_payoffs_raise_type_error(bad):
    with pytest.raises(TypeError, match="must be a real number"):
        PayoffMatrix(T=bad, R=3, P=1, S=0)


@pytest.mark.parametrize("bad", [True, False])
def test_bool_payoffs_rejected(bad):
    with pytest.raises(TypeError):
        PayoffMatrix(T=5, R=3, P=1, S=bad)


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_nan_and_inf_rejected(bad):
    with pytest.raises(ValueError, match="must be finite"):
        PayoffMatrix(T=5, R=3, P=bad, S=0)


def test_axelrod_payoff_table(axelrod):
    assert axelrod.as_tuple() == (5, 3, 1, 0)
    assert axelrod.payoff(C, C) == 3
    assert axelrod.payoff(C, D) == 0
    assert axelrod.payoff(D, C) == 5
    assert axelrod.payoff(D, D) == 1
    assert axelrod.payoffs(C, D) == (0, 5)
    assert axelrod.payoffs(D, D) == (1, 1)
    assert axelrod.as_matrix() == [[3, 0], [5, 1]]
    assert axelrod.dominance_gap() == (2, 1)
    assert axelrod.is_strict()


@pytest.mark.parametrize("b", [1.01, 1.5, 1.85, 1.99])
def test_nowak_may_in_bounds(b):
    pm = PayoffMatrix.nowak_may(b)
    assert pm.as_tuple() == (b, 1, 0, 0)
    assert not pm.is_strict()  # P == S, so not a strict PD
    assert 2 * pm.R > pm.T + pm.S


@pytest.mark.parametrize("b", [1.0, 2.0, 0.5, 3.0])
def test_nowak_may_out_of_bounds_raises(b):
    with pytest.raises(ValueError, match="Nowak-May"):
        PayoffMatrix.nowak_may(b)


def test_donation_game():
    pm = PayoffMatrix.donation(b=4, c=1)
    assert pm.as_tuple() == (4, 3, 0, -1)
    assert pm.is_strict()


@pytest.mark.parametrize(("b", "c"), [(1, 2), (1, 1), (2, 0), (2, -1)])
def test_donation_invalid_raises(b, c):
    with pytest.raises(ValueError, match="donation game"):
        PayoffMatrix.donation(b=b, c=c)


@settings(max_examples=100, deadline=None)
@given(
    c=st.floats(min_value=0.01, max_value=10, allow_nan=False),
    extra=st.floats(min_value=0.01, max_value=10, allow_nan=False),
)
def test_donation_is_always_a_strict_pd(c, extra):
    """b > c > 0 implies 2R - (T + S) = b - c > 0, so validation never fires."""
    pm = PayoffMatrix.donation(b=c + extra, c=c)
    assert pm.is_strict()
    assert pytest.approx(extra) == 2 * pm.R - (pm.T + pm.S)


def test_move_flip_and_str():
    assert C.flip() is D
    assert D.flip() is C
    assert Move("C") is C


def test_state_index_matches_states_tuple():
    for k, (own, other) in enumerate(STATES):
        assert state_index(own, other) == k
    assert state_index(C, C) == 0
    assert state_index(C, D) == 1
    assert state_index(D, C) == 2
    assert state_index(D, D) == 3
