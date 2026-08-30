"""Match engine and round-robin tournament."""

from __future__ import annotations

import numpy as np
import pytest

from pdlab.game import C, PayoffMatrix
from pdlab.match import play_match
from pdlab.strategies import REGISTRY, Strategy
from pdlab.tournament import round_robin

PM = PayoffMatrix.axelrod()


def _make(*names: str) -> list[Strategy]:
    return [REGISTRY.make(n) for n in names]


def _pair(a: str, b: str) -> tuple[Strategy, Strategy]:
    return REGISTRY.make(a), REGISTRY.make(b)


# --------------------------------------------------------------------------
# play_match
# --------------------------------------------------------------------------
def test_a_strategy_cannot_play_itself():
    s = REGISTRY.make("TFT")
    with pytest.raises(ValueError, match="cannot play itself"):
        play_match(s, s, 10, PM, np.random.default_rng(0))


@pytest.mark.parametrize("rounds", [0, -1])
def test_invalid_rounds_raise(rounds):
    with pytest.raises(ValueError, match="rounds must be"):
        play_match(*_pair("TFT", "ALLD"), rounds, PM, np.random.default_rng(0))


@pytest.mark.parametrize("noise", [-0.01, 0.51, 1.0])
def test_invalid_noise_raises(noise):
    with pytest.raises(ValueError, match="noise must be"):
        play_match(*_pair("TFT", "ALLD"), 10, PM, np.random.default_rng(0), noise=noise)


def test_noiseless_tft_vs_tft_cooperates_throughout():
    res = play_match(*_pair("TFT", "TFT"), 50, PM, np.random.default_rng(0))
    assert all(m is C for m in res.moves1)
    assert all(m is C for m in res.moves2)
    assert res.score1 == res.score2 == 50 * PM.R
    assert res.mean1 == res.mean2 == PM.R
    assert res.cooperation_rate(1) == 1.0
    assert res.cooperation_rate(2) == 1.0
    assert res.rounds == 50


def test_match_result_accounting_for_allc_vs_alld():
    res = play_match(*_pair("ALLC", "ALLD"), 10, PM, np.random.default_rng(0))
    assert res.score1 == 10 * PM.S
    assert res.score2 == 10 * PM.T
    assert res.cooperation_rate(1) == 1.0
    assert res.cooperation_rate(2) == 0.0


def test_noise_is_seed_reproducible_and_seed_dependent():
    a = play_match(*_pair("TFT", "TFT"), 100, PM, np.random.default_rng(7), noise=0.1)
    b = play_match(*_pair("TFT", "TFT"), 100, PM, np.random.default_rng(7), noise=0.1)
    c = play_match(*_pair("TFT", "TFT"), 100, PM, np.random.default_rng(8), noise=0.1)
    assert a.moves1 == b.moves1 and a.moves2 == b.moves2
    assert a.score1 == b.score1
    assert (a.moves1, a.moves2) != (c.moves1, c.moves2)


def test_noise_makes_tft_vs_tft_defect_sometimes():
    res = play_match(*_pair("TFT", "TFT"), 400, PM, np.random.default_rng(1), noise=0.05)
    assert 0.0 < res.cooperation_rate(1) < 1.0
    # noisy TFT vs TFT tends to the average of all four payoffs, 2.25
    assert res.mean1 == pytest.approx(2.25, abs=0.5)


def test_match_resets_strategies_before_playing():
    tft = REGISTRY.make("TFT")
    play_match(tft, REGISTRY.make("ALLD"), 5, PM, np.random.default_rng(0))
    res = play_match(tft, REGISTRY.make("ALLC"), 5, PM, np.random.default_rng(0))
    assert all(m is C for m in res.moves1)
    assert len(tft.own) == 5


# --------------------------------------------------------------------------
# round_robin
# --------------------------------------------------------------------------
def test_round_robin_requires_unique_names():
    with pytest.raises(ValueError, match="names must be unique"):
        round_robin(_make("TFT", "TFT"), rounds=10)


def test_round_robin_requires_two_strategies():
    with pytest.raises(ValueError, match="at least two"):
        round_robin(_make("TFT"), rounds=10)


@pytest.mark.parametrize("reps", [0, -3])
def test_round_robin_requires_positive_reps(reps):
    with pytest.raises(ValueError, match="reps must be"):
        round_robin(_make("TFT", "ALLD"), rounds=10, reps=reps)


def test_payoff_matrix_entries_for_allc_vs_alld():
    res = round_robin(_make("ALLC", "ALLD"), rounds=20)
    mp = res.mean_payoff
    i, j = res.names.index("ALLC"), res.names.index("ALLD")
    assert mp[i, j] == pytest.approx(PM.S)
    assert mp[j, i] == pytest.approx(PM.T)
    assert mp[i, i] == pytest.approx(PM.R)  # ALLC vs its own clone
    assert mp[j, j] == pytest.approx(PM.P)
    table = res.payoff_table()
    assert list(table.index) == list(res.names)
    assert table.loc["ALLC", "ALLD"] == pytest.approx(PM.S)


def test_scores_are_sorted_and_ranked():
    res = round_robin(_make("ALLC", "ALLD", "TFT", "GRIM"), rounds=50, reps=2)
    df = res.scores()
    assert list(df.columns) == ["rank", "strategy", "score", "score_sd", "coop_rate"]
    assert list(df["rank"]) == [1, 2, 3, 4]
    assert list(df["score"]) == sorted(df["score"], reverse=True)
    assert set(df["strategy"]) == {"ALLC", "ALLD", "TFT", "GRIM"}
    assert df.loc[df.strategy == "ALLC", "coop_rate"].item() == pytest.approx(1.0)
    assert df.loc[df.strategy == "ALLD", "coop_rate"].item() == pytest.approx(0.0)
    assert res.payoff.shape == (2, 4, 4)
    assert np.all(np.isfinite(res.payoff))


def test_single_rep_reports_zero_standard_deviation():
    res = round_robin(_make("TFT", "ALLD"), rounds=20, reps=1)
    assert list(res.scores()["score_sd"]) == [0.0, 0.0]


def test_include_self_false_excludes_the_diagonal_match():
    names = ("ALLC", "ALLD", "TFT")
    with_self = round_robin(_make(*names), rounds=40, include_self=True)
    without = round_robin(_make(*names), rounds=40, include_self=False)
    i = without.names.index("ALLC")
    off_diag = [without.mean_payoff[i, k] for k in range(3) if k != i]
    # the diagonal match was never played: it must be reported as NaN, not fabricated
    assert np.isnan(without.mean_payoff[i, i])
    assert with_self.mean_payoff[i, i] == pytest.approx(PM.R)
    # scores average over the opponents actually played
    row = without.scores().set_index("strategy").loc["ALLC", "score"]
    assert row == pytest.approx(np.mean(off_diag))


def test_round_robin_is_reproducible_under_noise():
    strats = ["TFT", "ALLD", "RANDOM", "WSLS"]
    a = round_robin(_make(*strats), rounds=60, noise=0.05, seed=1)
    b = round_robin(_make(*strats), rounds=60, noise=0.05, seed=1)
    c = round_robin(_make(*strats), rounds=60, noise=0.05, seed=2)
    assert a.mean_payoff == pytest.approx(b.mean_payoff)
    assert not np.allclose(a.mean_payoff, c.mean_payoff)
    assert a.noise == 0.05 and a.rounds == 60


def test_round_robin_accepts_a_custom_payoff_matrix():
    pm = PayoffMatrix.donation(b=4, c=1)
    res = round_robin(_make("ALLC", "ALLD"), rounds=10, pm=pm)
    i, j = res.names.index("ALLC"), res.names.index("ALLD")
    assert res.mean_payoff[i, j] == pytest.approx(pm.S)
    assert res.mean_payoff[j, i] == pytest.approx(pm.T)


def test_full_registry_tournament_runs():
    res = round_robin(REGISTRY.make_all(), rounds=30, seed=0)
    df = res.scores()
    assert len(df) == len(REGISTRY.names())
    assert np.all(np.isfinite(res.mean_payoff))
    assert df["score"].max() <= PM.T
    assert df["score"].min() >= PM.S
