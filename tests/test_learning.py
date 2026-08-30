"""Tabular Q-learning opponent."""

from __future__ import annotations

import numpy as np
import pytest

from pdlab.game import C, D, PayoffMatrix
from pdlab.learning import QLearner
from pdlab.match import play_match
from pdlab.strategies import REGISTRY

PM = PayoffMatrix.axelrod()


def _defection_rate(moves, tail: int) -> float:
    return sum(m is D for m in moves[-tail:]) / tail


@pytest.mark.parametrize("opponent", ["ALLD", "ALLC"])
def test_qlearner_learns_to_defect_against_unconditional_opponents(opponent):
    q = QLearner(persist=True, explore=0.1)
    res = play_match(q, REGISTRY.make(opponent), 3000, PM, np.random.default_rng(3))
    assert _defection_rate(res.moves1, 500) > 0.9


def test_qlearner_q_table_prefers_defection_after_learning_against_alld():
    q = QLearner(persist=True, explore=0.1)
    play_match(q, REGISTRY.make("ALLD"), 3000, PM, np.random.default_rng(3))
    # in every state actually visited against ALLD (CD and DD) D is preferred
    assert q.Q[1, 1] > q.Q[1, 0]
    assert q.Q[3, 1] > q.Q[3, 0]
    pol = q.greedy_policy()
    assert len(pol) == 4
    assert set(pol) <= {0.0, 1.0}
    assert pol[1] == 0.0 and pol[3] == 0.0


def test_persist_false_wipes_the_q_table_on_reset():
    q = QLearner(persist=False, optimistic=0.0)
    play_match(q, REGISTRY.make("ALLD"), 200, PM, np.random.default_rng(0))
    assert np.any(q.Q != 0.0)
    q.reset()
    assert np.all(q.Q == 0.0)
    assert q.state == 4
    assert q.explore == q.explore0


def test_persist_true_keeps_the_q_table_across_resets():
    q = QLearner(persist=True)
    play_match(q, REGISTRY.make("ALLD"), 200, PM, np.random.default_rng(0))
    before = q.Q.copy()
    q.reset()
    assert np.array_equal(q.Q, before)
    assert q.state == 4


def test_optimistic_initialisation_and_reset():
    q = QLearner(optimistic=5.0)
    assert np.all(q.Q == 5.0)
    play_match(q, REGISTRY.make("ALLD"), 50, PM, np.random.default_rng(0))
    q.reset()
    assert np.all(q.Q == 5.0)


def test_explore_decays():
    q = QLearner(explore=1.0, explore_decay=0.9)
    play_match(q, REGISTRY.make("ALLD"), 10, PM, np.random.default_rng(0))
    assert q.explore == pytest.approx(0.9**10)
    q.reset()
    assert q.explore == 1.0


def test_greedy_policy_breaks_ties_towards_cooperation():
    q = QLearner()
    assert q.greedy_policy() == (1.0, 1.0, 1.0, 1.0)


def test_zero_exploration_is_greedy():
    q = QLearner(explore=0.0)
    q.Q[4] = [1.0, 0.0]
    assert q.play(np.random.default_rng(0)) is C
    q.Q[4] = [0.0, 1.0]
    assert q.play(np.random.default_rng(0)) is D


def test_clone_preserves_hyperparameters():
    q = QLearner(alpha=0.2, gamma=0.5, explore=0.3, explore_decay=0.99, persist=True)
    c = q.clone()
    assert isinstance(c, QLearner)
    assert (c.alpha, c.gamma, c.explore0, c.explore_decay, c.persist) == (
        0.2,
        0.5,
        0.3,
        0.99,
        True,
    )
    assert np.all(c.Q == 0.0)


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"alpha": 1.5}, "alpha"),
        ({"alpha": -0.1}, "alpha"),
        ({"gamma": 1.1}, "gamma"),
        ({"explore": 2.0}, "explore"),
        ({"explore_decay": 0.0}, "explore_decay"),
        ({"explore_decay": 1.5}, "explore_decay"),
    ],
)
def test_parameter_validation(kwargs, match):
    with pytest.raises(ValueError, match=match):
        QLearner(**kwargs)
