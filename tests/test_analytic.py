"""Symbolic thresholds, replicator payoff matrix, fixed points and stability."""

from __future__ import annotations

import numpy as np
import pytest
import sympy as sp
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from pdlab.analytic import (
    STRATS3,
    P,
    R,
    S,
    T,
    best_responses,
    cooperation_value,
    delta,
    deviation_values,
    eps,
    grim_threshold_symbolic,
    is_ess,
    is_neutrally_stable,
    jacobian_eigenvalues,
    jacobian_eigenvalues_symbolic,
    one_shot_facts,
    payoff_matrix_3,
    payoff_matrix_3_symbolic,
    replicator_fixed_points_symbolic,
    replicator_rhs,
    self_play_noise_symbolic,
    stationary_payoffs_symbolic,
    tft_alld_threshold_symbolic,
    tft_alt_threshold_symbolic,
    tft_invasion_threshold,
    tft_invasion_threshold_symbolic,
    tft_nash_threshold_symbolic,
    tft_spe_conditions_symbolic,
    thresholds,
)
from pdlab.game import PayoffMatrix

PM = PayoffMatrix.axelrod()
SUB = {T: 5, R: 3, P: 1, S: 0}


# --------------------------------------------------------------------------
# one-shot facts
# --------------------------------------------------------------------------
def test_one_shot_facts_for_a_strict_pd():
    f = one_shot_facts(PM)
    assert f.d_dominant and f.dd_unique_nash
    assert f.cc_pareto_dominates_dd and f.cc_beats_alternation
    assert f.is_dilemma


def test_one_shot_facts_for_a_weak_dilemma():
    f = one_shot_facts(PayoffMatrix.nowak_may(1.5))
    assert f.d_dominant is False  # P == S, so D only weakly dominates
    assert f.cc_pareto_dominates_dd
    assert f.is_dilemma is False


def test_best_responses_are_always_defect_in_a_pd():
    assert best_responses(PM) == {"C": "D", "D": "D"}
    assert best_responses(PayoffMatrix.nowak_may(1.5)) == {"C": "D", "D": "C"}


# --------------------------------------------------------------------------
# symbolic thresholds
# --------------------------------------------------------------------------
def test_grim_threshold_simplifies_to_t_minus_r_over_t_minus_p():
    assert sp.simplify(grim_threshold_symbolic() - (T - R) / (T - P)) == 0
    assert sp.simplify(tft_alld_threshold_symbolic() - (T - R) / (T - P)) == 0


def test_tft_alternation_threshold_simplifies_to_t_minus_r_over_r_minus_s():
    assert sp.simplify(tft_alt_threshold_symbolic() - (T - R) / (R - S)) == 0


def test_tft_nash_threshold_is_the_max_of_both():
    expr = tft_nash_threshold_symbolic()
    assert float(expr.subs(SUB)) == pytest.approx(2 / 3)


def test_thresholds_for_axelrod_payoffs():
    th = thresholds(PM)
    assert (th.grim_spe, th.tft_vs_alld) == pytest.approx((0.5, 0.5))
    assert th.tft_vs_alternate == pytest.approx(2 / 3)
    assert th.tft_nash == pytest.approx(2 / 3)
    assert th.tft_after_dd_max == pytest.approx(0.25)
    assert th.tft_is_spe_possible is False


def test_tft_is_spe_possible_exactly_when_t_minus_r_equals_p_minus_s():
    """Algebra: SPE needs R-S <= T-P and (T-R)(T-P) <= (P-S)(R-S), which force T-R = P-S."""
    pm = PayoffMatrix(T=4, R=3, P=1, S=0)  # T-R = P-S = 1
    th = thresholds(pm)
    assert th.tft_is_spe_possible is True
    assert th.tft_vs_alld == pytest.approx(1 / 3)
    assert th.tft_vs_alternate == pytest.approx(1 / 3)
    assert th.tft_after_dd_max == pytest.approx(1 / 3)


@settings(max_examples=200, deadline=None, suppress_health_check=[HealthCheck.filter_too_much])
@given(
    x=st.floats(min_value=0.1, max_value=5),
    y=st.floats(min_value=0.1, max_value=5),
    z=st.floats(min_value=0.1, max_value=5),
)
def test_tft_is_generically_not_spe(x, y, z):
    """With T-R = x, R-P = y, P-S = z, SPE requires z >= x and x(x+y) <= z(y+z),
    which together force x == z; strict inequalities make it impossible."""
    T_, R_, P_, S_ = x + y + z, y + z, z, 0.0
    if not (2 * R_ > T_ + S_):
        return
    pm = PayoffMatrix(T=T_, R=R_, P=P_, S=S_)
    th = thresholds(pm)
    if abs(x - z) > 1e-9:
        assert th.tft_is_spe_possible is False
    # the knife-edge x == z is exactly the case in test_tft_is_spe_possible_...


def test_tft_spe_conditions_are_mutually_exclusive_for_axelrod():
    cond = tft_spe_conditions_symbolic()
    assert set(cond) == {
        "on_path_vs_alld",
        "on_path_vs_alternate",
        "after_cheated_prefers_punish",
        "after_cheated_threshold",
        "after_dd_prefers_defect",
        "after_dd_threshold",
    }
    on_path = cond["on_path_vs_alternate"].subs(SUB)
    after_dd = cond["after_dd_threshold"].subs(SUB)
    d = sp.Symbol("d", positive=True)
    # no delta in [0, 1) satisfies delta >= 2/3 and delta <= 1/4 simultaneously
    both = sp.And(on_path.subs(delta, d), after_dd.subs(delta, d))
    assert sp.simplify(both) is sp.false


def test_cooperation_and_deviation_values():
    d = 0.9
    assert cooperation_value(PM, d) == pytest.approx(3 / 0.1)
    dv = deviation_values(PM, d)
    assert dv["alld"] == pytest.approx(5 + 0.9 * 1 / 0.1)
    assert dv["alternate"] == pytest.approx((5 + 0.9 * 0) / (1 - 0.81))
    # at the threshold delta = 1/2 the ALLD deviation is exactly break-even
    assert cooperation_value(PM, 0.5) == pytest.approx(deviation_values(PM, 0.5)["alld"])
    assert cooperation_value(PM, 2 / 3) == pytest.approx(deviation_values(PM, 2 / 3)["alternate"])


# --------------------------------------------------------------------------
# 3-strategy replicator system
# --------------------------------------------------------------------------
def test_payoff_matrix_3_numbers_at_delta_0_9():
    A = payoff_matrix_3(PM, 0.9)
    assert pytest.approx(np.array([[3, 0, 3], [5, 1, 1.4], [3, 0.9, 3]])) == A
    assert STRATS3 == ("ALLC", "ALLD", "TFT")


def test_payoff_matrix_3_symbolic_agrees_with_numeric():
    A = payoff_matrix_3_symbolic().subs({**SUB, delta: 0.5})
    assert np.array(A.tolist(), dtype=float) == pytest.approx(payoff_matrix_3(PM, 0.5))


@pytest.mark.parametrize("d", [-0.1, 1.0, 1.5])
def test_payoff_matrix_3_rejects_bad_delta(d):
    with pytest.raises(ValueError, match="delta must be"):
        payoff_matrix_3(PM, d)


def test_replicator_rhs_vanishes_at_vertices_and_on_the_edge_fixed_point():
    A = payoff_matrix_3(PM, 0.9)
    for k in range(3):
        x = np.zeros(3)
        x[k] = 1.0
        assert replicator_rhs(x, A) == pytest.approx(np.zeros(3), abs=1e-12)
    xs = tft_invasion_threshold(PM, 0.9)
    edge = np.array([0.0, 1 - xs, xs])
    assert replicator_rhs(edge, A) == pytest.approx(np.zeros(3), abs=1e-12)


def test_replicator_rhs_sums_to_zero_on_the_simplex():
    A = payoff_matrix_3(PM, 0.9)
    x = np.array([0.2, 0.3, 0.5])
    assert replicator_rhs(x, A).sum() == pytest.approx(0.0, abs=1e-12)


def test_tft_invasion_threshold_is_one_seventeenth():
    assert tft_invasion_threshold(PM, 0.9) == pytest.approx(1 / 17)
    expr = tft_invasion_threshold_symbolic()
    assert float(expr.subs({**SUB, delta: 0.9})) == pytest.approx(1 / 17)


def test_symbolic_fixed_points_are_the_three_vertices_plus_the_edge_point():
    fps = replicator_fixed_points_symbolic()
    assert list(fps["ALLC"]) == [1, 0, 0]
    assert list(fps["ALLD"]) == [0, 1, 0]
    assert list(fps["TFT"]) == [0, 0, 1]
    edge = fps["TFT_ALLD_edge"]
    assert float(edge[2].subs({**SUB, delta: 0.9})) == pytest.approx(1 / 17)
    assert float(edge[1].subs({**SUB, delta: 0.9})) == pytest.approx(16 / 17)


# --------------------------------------------------------------------------
# stability
# --------------------------------------------------------------------------
NAMED_POINTS = {
    "ALLC": np.array([1.0, 0.0, 0.0]),
    "ALLD": np.array([0.0, 1.0, 0.0]),
    "TFT": np.array([0.0, 0.0, 1.0]),
    "TFT_ALLD_edge": np.array([0.0, 16 / 17, 1 / 17]),
}


def test_jacobian_at_alld_has_eigenvalues_minus_one_and_minus_one_tenth():
    A = payoff_matrix_3(PM, 0.9)
    ev = np.sort(np.real(jacobian_eigenvalues(NAMED_POINTS["ALLD"], A)))
    assert ev == pytest.approx([-1.0, -0.1], abs=1e-5)
    assert np.all(ev < 0)  # ALLD is locally asymptotically stable


@pytest.mark.parametrize("name", list(NAMED_POINTS))
def test_symbolic_and_numeric_jacobian_eigenvalues_agree(name):
    A = payoff_matrix_3(PM, 0.9)
    num = np.sort(np.real(jacobian_eigenvalues(NAMED_POINTS[name], A)))
    sym_exprs = jacobian_eigenvalues_symbolic(name)
    sym = np.sort([float(sp.re(e.subs({**SUB, delta: 0.9}))) for e in sym_exprs])
    assert num == pytest.approx(sym, abs=1e-5)


def test_edge_fixed_point_is_a_saddle():
    A = payoff_matrix_3(PM, 0.9)
    ev = np.real(jacobian_eigenvalues(NAMED_POINTS["TFT_ALLD_edge"], A))
    assert ev.min() < 0 < ev.max()


def test_jacobian_eigenvalues_validate_the_point():
    A = payoff_matrix_3(PM, 0.9)
    with pytest.raises(ValueError, match="3-simplex"):
        jacobian_eigenvalues(np.array([0.5, 0.2, 0.1]), A)
    with pytest.raises(ValueError, match="3-simplex"):
        jacobian_eigenvalues(np.array([0.5, 0.5]), A)


def test_symbolic_jacobian_rejects_unknown_points():
    with pytest.raises(KeyError):
        jacobian_eigenvalues_symbolic("_rhs")
    with pytest.raises(KeyError):
        jacobian_eigenvalues_symbolic("NOPE")


def test_ess_classification_of_the_three_strategies():
    A = payoff_matrix_3(PM, 0.9)
    assert is_ess(A, 1) is True  # ALLD
    assert is_ess(A, 2) is False  # TFT: A_TT == A_CT and A_TC == A_CC
    assert is_ess(A, 0) is False  # ALLC is invaded by ALLD
    assert is_neutrally_stable(A, 2) is True
    assert is_neutrally_stable(A, 0) is False
    assert is_neutrally_stable(A, 1) is True


def test_ess_of_a_dominant_pure_strategy():
    A = np.array([[2.0, 0.0], [3.0, 1.0]])
    assert is_ess(A, 1) and not is_ess(A, 0)


# --------------------------------------------------------------------------
# symbolic noise analysis
# --------------------------------------------------------------------------
def test_tft_self_play_under_noise_is_the_average_of_all_four_payoffs():
    sx, sy = stationary_payoffs_symbolic((1, 0, 1, 0), (1, 0, 1, 0))
    assert sp.simplify(sx - (T + R + P + S) / 4) == 0
    assert sp.simplify(sx - sy) == 0
    assert float(sx.subs(SUB)) == pytest.approx(2.25)


def test_wsls_self_play_under_noise_tends_to_r():
    w = self_play_noise_symbolic((1, 0, 0, 1))
    assert sp.limit(w, eps, 0) == R
    assert float(w.subs({**SUB, eps: sp.Rational(1, 100)})) == pytest.approx(2.9510919999, abs=1e-9)


def test_stationary_payoffs_symbolic_validates_lengths():
    with pytest.raises(ValueError, match="four entries"):
        stationary_payoffs_symbolic((1, 0, 1), (1, 0, 1, 0))
    with pytest.raises(ValueError, match="four entries"):
        stationary_payoffs_symbolic((1, 0, 1, 0), (1, 0, 1, 0, 0))
