"""Exact memory-one Markov analysis and the Press-Dyson ZD algebra."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from pdlab.game import PayoffMatrix
from pdlab.markov import (
    discounted_payoffs,
    expected_payoffs,
    extort_vector,
    generous_vector,
    initial_distribution,
    noisy,
    payoff_vectors,
    press_dyson_determinant,
    press_dyson_payoffs,
    stationary_distribution,
    stationary_payoffs,
    swap_perspective,
    transition_matrix,
    zd_vector,
)
from pdlab.match import play_match
from pdlab.strategies import REGISTRY

PM = PayoffMatrix.axelrod()
TFT = (1.0, 0.0, 1.0, 0.0)
ALLD = (0.0, 0.0, 0.0, 0.0)
ALLC = (1.0, 1.0, 1.0, 1.0)
WSLS = (1.0, 0.0, 0.0, 1.0)

PROB = st.floats(min_value=0.05, max_value=0.95, allow_nan=False, allow_infinity=False)
VEC = st.tuples(PROB, PROB, PROB, PROB)
SLOW = settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])


# --------------------------------------------------------------------------
# basic algebra
# --------------------------------------------------------------------------
@SLOW
@given(p=VEC, q=VEC, eps=st.floats(min_value=0, max_value=0.5))
def test_transition_matrix_rows_sum_to_one(p, q, eps):
    M = transition_matrix(p, q, eps)
    assert M.shape == (4, 4)
    assert np.all(M >= 0)
    assert np.allclose(M.sum(axis=1), 1.0)


def test_noisy_interpolates_towards_one_half():
    assert noisy((1, 0, 1, 0), 0.0) == pytest.approx([1, 0, 1, 0])
    assert noisy((1, 0, 1, 0), 0.1) == pytest.approx([0.9, 0.1, 0.9, 0.1])
    assert noisy((1, 0, 0.25, 0), 0.5) == pytest.approx([0.5] * 4)


@pytest.mark.parametrize("eps", [-1e-9, 0.5000001, 1.0])
def test_noisy_rejects_eps_outside_range(eps):
    with pytest.raises(ValueError, match="eps must be in"):
        noisy(ALLC, eps)


@pytest.mark.parametrize("bad", [(1, 0, 1), (1, 0, 1, 0, 1)])
def test_vector_shape_validation(bad):
    with pytest.raises(ValueError, match=r"shape \(4,\)"):
        noisy(bad, 0.0)


@pytest.mark.parametrize("bad", [(1.1, 0, 0, 0), (-0.1, 0, 0, 0), (np.nan, 0, 0, 0)])
def test_vector_range_validation(bad):
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        noisy(bad, 0.0)


def test_swap_perspective_exchanges_cd_and_dc():
    assert swap_perspective((0.1, 0.2, 0.3, 0.4)) == pytest.approx([0.1, 0.3, 0.2, 0.4])
    # involution
    v = (0.1, 0.2, 0.3, 0.4)
    assert swap_perspective(swap_perspective(v)) == pytest.approx(v)


def test_payoff_vectors_are_transposes_of_each_other():
    sx, sy = payoff_vectors(PM)
    assert sx == pytest.approx([3, 0, 5, 1])
    assert sy == pytest.approx([3, 5, 0, 1])
    assert list(sy) == [sx[0], sx[2], sx[1], sx[3]]


def test_transition_matrix_of_tft_vs_tft_is_a_permutation():
    M = transition_matrix(TFT, TFT, 0.0)
    assert np.allclose(M, np.eye(4)[[0, 2, 1, 3]])


# --------------------------------------------------------------------------
# stationary distribution
# --------------------------------------------------------------------------
def test_stationary_distribution_raises_on_reducible_chain():
    M = transition_matrix(TFT, TFT, 0.0)
    with pytest.raises(ValueError, match="stationary directions"):
        stationary_distribution(M)


def test_stationary_distribution_rejects_bad_matrices():
    with pytest.raises(ValueError, match="4x4"):
        stationary_distribution(np.eye(3))
    with pytest.raises(ValueError, match="row-stochastic"):
        stationary_distribution(np.full((4, 4), 0.1))


@SLOW
@given(eps=st.floats(min_value=1e-6, max_value=0.5))
def test_tft_vs_tft_under_noise_earns_the_average_of_all_four_payoffs(eps):
    """Any eps > 0 makes the chain doubly stochastic: v = (1/4, 1/4, 1/4, 1/4)."""
    v = stationary_distribution(transition_matrix(TFT, TFT, eps))
    assert v == pytest.approx([0.25] * 4, abs=1e-9)
    sx, sy = stationary_payoffs(TFT, TFT, PM, eps)
    assert sx == pytest.approx((PM.T + PM.R + PM.P + PM.S) / 4)
    assert sx == pytest.approx(2.25)
    assert sy == pytest.approx(2.25)


@pytest.mark.parametrize(("eps", "tol"), [(1e-2, 5e-2), (1e-3, 5e-3), (1e-4, 5e-4)])
def test_wsls_vs_wsls_payoff_tends_to_r_as_noise_vanishes(eps, tol):
    sx, sy = stationary_payoffs(WSLS, WSLS, PM, eps)
    assert sx == pytest.approx(sy)
    assert sx == pytest.approx(PM.R, abs=tol)
    assert sx < PM.R


def test_alld_vs_anything_stationary_is_mutual_defection():
    sx, sy = stationary_payoffs(ALLD, ALLC, PM)
    assert (sx, sy) == pytest.approx((PM.T, PM.S))
    sx, sy = stationary_payoffs(ALLD, TFT, PM)
    assert (sx, sy) == pytest.approx((PM.P, PM.P))


# --------------------------------------------------------------------------
# finite-horizon and discounted payoffs
# --------------------------------------------------------------------------
def test_initial_distribution_and_validation():
    v = initial_distribution(1.0, 0.0)
    assert v == pytest.approx([0, 1, 0, 0])
    assert initial_distribution(0.5, 0.5) == pytest.approx([0.25] * 4)
    with pytest.raises(ValueError, match="initial probabilities"):
        initial_distribution(1.5, 0.0)
    assert initial_distribution(1.0, 1.0, eps=0.1) == pytest.approx([0.81, 0.09, 0.09, 0.01])


@pytest.mark.parametrize("rounds", [1, 2, 5, 25, 100])
def test_expected_payoffs_match_the_closed_form_for_alld_vs_tft(rounds):
    n = rounds
    sx, sy = expected_payoffs(ALLD, TFT, 0.0, 1.0, PM, n)
    assert sx == pytest.approx((PM.T + (n - 1) * PM.P) / n)
    assert sy == pytest.approx((PM.S + (n - 1) * PM.P) / n)


@pytest.mark.parametrize("rounds", [1, 3, 10, 50])
def test_expected_payoffs_match_a_simulated_match(rounds):
    res = play_match(
        REGISTRY.make("ALLD"), REGISTRY.make("TFT"), rounds, PM, np.random.default_rng(0)
    )
    sx, sy = expected_payoffs(ALLD, TFT, 0.0, 1.0, PM, rounds)
    assert sx == pytest.approx(res.mean1)
    assert sy == pytest.approx(res.mean2)


def test_expected_payoffs_rejects_zero_rounds():
    with pytest.raises(ValueError, match="rounds must be"):
        expected_payoffs(ALLD, TFT, 0.0, 1.0, PM, 0)


@pytest.mark.parametrize("d", [0.0, 0.5, 0.9, 0.99])
def test_discounted_payoffs_match_closed_form_for_alld_vs_tft(d):
    sx, sy = discounted_payoffs(ALLD, TFT, 0.0, 1.0, PM, d)
    assert sx == pytest.approx((1 - d) * PM.T + d * PM.P)
    assert sy == pytest.approx((1 - d) * PM.S + d * PM.P)


def test_discounted_payoffs_work_on_a_reducible_chain():
    sx, sy = discounted_payoffs(TFT, TFT, 1.0, 1.0, PM, 0.9)
    assert (sx, sy) == pytest.approx((PM.R, PM.R))


@pytest.mark.parametrize("d", [-0.1, 1.0, 1.5])
def test_discounted_payoffs_reject_bad_delta(d):
    with pytest.raises(ValueError, match="delta must be"):
        discounted_payoffs(ALLD, TFT, 0.0, 1.0, PM, d)


# --------------------------------------------------------------------------
# Press & Dyson determinant formalism
# --------------------------------------------------------------------------
@SLOW
@given(p=VEC, q=VEC)
def test_press_dyson_payoffs_equal_stationary_payoffs(p, q):
    a = press_dyson_payoffs(p, q, PM)
    b = stationary_payoffs(p, q, PM)
    assert a == pytest.approx(b, abs=1e-9)


def test_press_dyson_determinant_validates_f():
    with pytest.raises(ValueError, match=r"f must have shape"):
        press_dyson_determinant(TFT, TFT, np.ones(3))


def test_press_dyson_payoffs_raise_when_the_chain_is_degenerate():
    with pytest.raises(ValueError, match=r"D\(p, q, 1\) = 0"):
        press_dyson_payoffs(TFT, TFT, PM)


# --------------------------------------------------------------------------
# zero-determinant strategies
# --------------------------------------------------------------------------
def test_extort2_is_the_published_vector():
    assert extort_vector(PM, chi=2, phi_frac=0.5) == pytest.approx((8 / 9, 1 / 2, 1 / 3, 0.0))


def test_zdgtft2_is_the_published_vector():
    assert generous_vector(PM, chi=2, phi_frac=1.0) == pytest.approx((1.0, 1 / 8, 1.0, 1 / 4))


@SLOW
@given(q=VEC)
def test_extortion_enforces_the_linear_relation_about_p(q):
    chi = 2.0
    p = extort_vector(PM, chi=chi, phi_frac=0.5)
    sx, sy = stationary_payoffs(p, q, PM)
    assert sx - PM.P == pytest.approx(chi * (sy - PM.P), abs=1e-9)
    assert sx >= sy - 1e-9  # extortion never loses


@SLOW
@given(q=VEC)
def test_generous_zd_enforces_the_linear_relation_about_r(q):
    chi = 2.0
    p = generous_vector(PM, chi=chi, phi_frac=1.0)
    sx, sy = stationary_payoffs(p, q, PM)
    assert sx - PM.R == pytest.approx(chi * (sy - PM.R), abs=1e-9)
    assert sx <= sy + 1e-9  # generosity never wins


@pytest.mark.parametrize("chi", [1.0, 0.5, -2.0])
def test_infeasible_chi_raises(chi):
    with pytest.raises(ValueError, match="chi > 1"):
        extort_vector(PM, chi=chi)
    with pytest.raises(ValueError, match="chi > 1"):
        generous_vector(PM, chi=chi)


@pytest.mark.parametrize("phi_frac", [0.0, -0.5, 1.5])
def test_bad_phi_frac_raises(phi_frac):
    with pytest.raises(ValueError, match="phi_frac"):
        extort_vector(PM, chi=2, phi_frac=phi_frac)
    with pytest.raises(ValueError, match="phi_frac"):
        generous_vector(PM, chi=2, phi_frac=phi_frac)


def test_zd_vector_infeasible_raises():
    with pytest.raises(ValueError, match="infeasible ZD strategy"):
        zd_vector(PM, alpha=1.0, beta=-1.0, gamma=0.0)


def test_zd_vector_feasible_returns_probabilities():
    p = zd_vector(PM, alpha=0.1, beta=-0.2, gamma=0.1)
    assert np.all((p >= 0) & (p <= 1))
