"""Replicator dynamics and the Moran process."""

from __future__ import annotations

import numpy as np
import pytest

from pdlab.analytic import payoff_matrix_3, tft_invasion_threshold
from pdlab.evolution import (
    fixation_probability,
    moran_process,
    replicator_discrete,
    replicator_trajectory,
)
from pdlab.game import PayoffMatrix

PM = PayoffMatrix.axelrod()
A3 = payoff_matrix_3(PM, 0.9)  # [[3,0,3],[5,1,1.4],[3,0.9,3]]
X_STAR = tft_invasion_threshold(PM, 0.9)  # 1/17


# --------------------------------------------------------------------------
# replicator ODE
# --------------------------------------------------------------------------
def test_trajectory_stays_on_the_simplex():
    traj = replicator_trajectory(A3, [0.3, 0.4, 0.3], t_max=20.0)
    assert traj.x.shape == (400, 3)
    assert np.all(traj.x >= -1e-12)
    assert traj.x.sum(axis=1) == pytest.approx(np.ones(400))
    assert traj.t[0] == 0.0 and traj.t[-1] == pytest.approx(20.0)


def test_below_the_invasion_threshold_the_population_converges_to_alld():
    x0 = [0.1, 0.9 - X_STAR / 2, X_STAR / 2]
    traj = replicator_trajectory(A3, x0, t_max=200.0)
    end = traj.x[-1]
    assert end[1] == pytest.approx(1.0, abs=1e-3)
    assert end[2] < 1e-3


def test_above_the_invasion_threshold_the_population_reaches_the_allc_tft_edge():
    x0 = [0.1, 0.9 - 5 * X_STAR, 5 * X_STAR]
    traj = replicator_trajectory(A3, x0, t_max=200.0)
    end = traj.x[-1]
    assert end[1] < 1e-3  # ALLD wiped out
    assert end[0] + end[2] == pytest.approx(1.0, abs=1e-3)
    assert end[0] > 0 and end[2] > 0  # the whole ALLC-TFT edge is neutral


def test_replicator_trajectory_validation():
    with pytest.raises(ValueError, match="square"):
        replicator_trajectory(np.ones((2, 3)), [0.5, 0.5], 1.0)
    with pytest.raises(ValueError, match="finite"):
        replicator_trajectory(np.array([[np.nan, 1.0], [1.0, 1.0]]), [0.5, 0.5], 1.0)
    with pytest.raises(ValueError, match="probability vector"):
        replicator_trajectory(A3, [0.5, 0.5, 0.5], 1.0)
    with pytest.raises(ValueError, match="probability vector"):
        replicator_trajectory(A3, [-0.5, 1.0, 0.5], 1.0)
    with pytest.raises(ValueError, match="t_max"):
        replicator_trajectory(A3, [1 / 3, 1 / 3, 1 / 3], 0.0)


# --------------------------------------------------------------------------
# discrete replicator
# --------------------------------------------------------------------------
def test_discrete_replicator_requires_strictly_positive_payoffs():
    with pytest.raises(ValueError, match="strictly positive"):
        replicator_discrete(A3, [1 / 3, 1 / 3, 1 / 3], 10)


def test_discrete_replicator_drives_out_the_dominated_strategy():
    A = np.array([[3.0, 1.0], [4.0, 2.0]])  # row 1 dominates row 0
    out = replicator_discrete(A, [0.5, 0.5], 100)
    assert out.shape == (101, 2)
    assert out.sum(axis=1) == pytest.approx(np.ones(101))
    assert out[-1, 1] > 0.99


def test_discrete_replicator_mutation_keeps_both_types_alive():
    A = np.array([[3.0, 1.0], [4.0, 2.0]])
    out = replicator_discrete(A, [0.5, 0.5], 200, mutation=0.1)
    assert out[-1].min() > 0.04


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"generations": 0}, "generations"),
        ({"generations": 5, "mutation": 1.5}, "mutation"),
        ({"generations": 5, "mutation": -0.1}, "mutation"),
    ],
)
def test_discrete_replicator_validation(kwargs, match):
    A = np.array([[3.0, 1.0], [4.0, 2.0]])
    with pytest.raises(ValueError, match=match):
        replicator_discrete(A, [0.5, 0.5], **kwargs)


# --------------------------------------------------------------------------
# Moran process: exact fixation probabilities
# --------------------------------------------------------------------------
@pytest.mark.parametrize("N", [2, 5, 10, 50])
def test_neutral_fixation_probability_is_one_over_n(N):
    A = np.ones((2, 2))
    assert fixation_probability(A, 0, 1, N) == pytest.approx(1 / N)
    # w = 0 (no selection) is neutral for any payoff matrix
    assert fixation_probability(A3, 2, 1, N, w=0.0) == pytest.approx(1 / N)


def test_advantageous_mutant_beats_neutral_and_dominated_loses():
    A = np.array([[2.0, 2.0], [1.0, 1.0]])
    N = 20
    assert fixation_probability(A, 0, 1, N) > 1 / N
    assert fixation_probability(A, 1, 0, N) < 1 / N


def test_fixation_probability_validation():
    with pytest.raises(ValueError, match="N must be"):
        fixation_probability(A3, 2, 1, 1)
    with pytest.raises(ValueError, match="square"):
        fixation_probability(np.ones((2, 3)), 0, 1, 5)
    with pytest.raises(ValueError, match="non-positive fitness"):
        fixation_probability(np.array([[-5.0, -5.0], [-5.0, -5.0]]), 0, 1, 10)


def test_simulated_fixation_matches_the_formula_for_a_tft_mutant_in_alld():
    """1 TFT among 19 ALLD, N=20, w=1, delta=0.9 payoffs."""
    N, runs = 20, 2000
    rho = fixation_probability(A3, mutant=2, resident=1, N=N, w=1.0)
    rng = np.random.default_rng(1)
    hits = 0
    for _ in range(runs):
        res = moran_process(A3, [0, N - 1, 1], steps=20_000, rng=rng, w=1.0)
        assert res.fixated is not None  # absorbed within the step budget
        hits += res.fixated == 2
    freq = hits / runs
    se = np.sqrt(rho * (1 - rho) / runs)
    assert abs(freq - rho) < 3 * se


def test_moran_result_records_history_and_frequencies():
    rng = np.random.default_rng(0)
    res = moran_process(A3, [0, 19, 1], steps=50, rng=rng, w=0.5)
    assert res.counts.shape[1] == 3
    assert np.all(res.counts.sum(axis=1) == 20)
    assert res.frequencies.sum(axis=1) == pytest.approx(np.ones(res.counts.shape[0]))
    if res.fixated is not None:
        assert res.counts[-1].max() == 20


def test_moran_absorbs_and_stops_at_fixation():
    rng = np.random.default_rng(5)
    res = moran_process(A3, [0, 19, 1], steps=100_000, rng=rng)
    assert res.fixated in (1, 2)
    assert res.counts[-1][res.fixated] == 20
    assert res.counts.shape[0] < 100_001  # stopped early


def test_moran_without_stopping_runs_the_full_budget():
    rng = np.random.default_rng(5)
    res = moran_process(A3, [0, 19, 1], steps=200, rng=rng, stop_at_fixation=False)
    assert res.counts.shape == (201, 3)
    assert res.fixated is None


def test_moran_mutation_keeps_the_process_running():
    rng = np.random.default_rng(2)
    res = moran_process(
        A3, [0, 19, 1], steps=2000, rng=rng, w=0.5, mutation=0.05, stop_at_fixation=False
    )
    assert res.fixated is None
    assert res.counts.shape == (2001, 3)
    assert res.counts[:, 0].max() > 0  # ALLC introduced by mutation


def test_moran_stop_at_fixation_with_mutation_is_rejected():
    with pytest.raises(ValueError, match="stop_at_fixation"):
        moran_process(A3, [0, 19, 1], steps=10, rng=np.random.default_rng(0), mutation=0.1)


def test_moran_record_false_keeps_only_endpoints():
    rng = np.random.default_rng(3)
    res = moran_process(A3, [0, 19, 1], steps=500, rng=rng, w=0.5, record=False)
    assert res.counts.shape == (2, 3)
    assert res.counts.sum(axis=1).tolist() == [20, 20]


def test_moran_negative_fitness_raises():
    A = np.array([[-10.0, -10.0], [-10.0, -10.0]])
    rng = np.random.default_rng(0)
    with pytest.raises(ValueError, match="negative fitness"):
        moran_process(A, [1, 9], steps=5, rng=rng, w=1.0)


def test_moran_zero_total_fitness_raises():
    A = np.zeros((2, 2))
    rng = np.random.default_rng(0)
    with pytest.raises(ValueError, match="zero total fitness"):
        moran_process(A, [1, 9], steps=5, rng=rng, w=1.0)


@pytest.mark.parametrize(
    ("counts0", "kwargs", "match"),
    [
        ([1], {}, "counts0"),
        ([1, 0, 0], {}, "counts0"),
        ([-1, 3, 0], {}, "counts0"),
        ([0, 19, 1], {"w": 1.5}, "bad Moran"),
        ([0, 19, 1], {"mutation": -0.1}, "bad Moran"),
        ([0, 19, 1], {"steps": 0}, "bad Moran"),
    ],
)
def test_moran_parameter_validation(counts0, kwargs, match):
    rng = np.random.default_rng(0)
    kwargs.setdefault("steps", 5)
    with pytest.raises(ValueError, match=match):
        moran_process(A3, counts0, rng=rng, **kwargs)
