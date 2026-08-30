"""Tabular Q-learning agent for the iterated PD (the 'adaptive' opponent)."""

from __future__ import annotations

import numpy as np

from pdlab.game import C, D, Move
from pdlab.strategies import Strategy

_STATE_START = 4


class QLearner(Strategy):
    """epsilon-greedy tabular Q-learning over the last joint outcome.

    State = index of (own, opp) last outcome in (CC, CD, DC, DD) or 4 at the
    start.  ``persist=True`` keeps the Q-table across ``reset()`` calls so the
    agent can keep learning over many matches.
    """

    name = "QLEARN"

    def __init__(
        self,
        alpha: float = 0.1,
        gamma: float = 0.95,
        explore: float = 0.1,
        explore_decay: float = 1.0,
        persist: bool = False,
        optimistic: float = 0.0,
    ) -> None:
        super().__init__()
        for v, nm in ((alpha, "alpha"), (gamma, "gamma"), (explore, "explore")):
            if not 0 <= v <= 1:
                raise ValueError(f"{nm} must be in [0, 1], got {v}")
        if not 0 < explore_decay <= 1:
            raise ValueError("explore_decay must be in (0, 1]")
        self.alpha, self.gamma = alpha, gamma
        self.explore0, self.explore_decay = explore, explore_decay
        self.explore = explore
        self.persist = persist
        self.optimistic = optimistic
        self.Q = np.full((5, 2), optimistic, dtype=float)
        self.state = _STATE_START
        self.last_action = 0
        self._rng_cache: np.random.Generator | None = None

    def _reset_state(self) -> None:
        self.state = _STATE_START
        self.explore = self.explore0
        if not self.persist:
            self.Q[:] = self.optimistic

    def _decide(self, rng: np.random.Generator) -> Move:
        self._rng_cache = rng
        q = self.Q[self.state]
        if rng.random() < self.explore:
            a = int(rng.integers(0, 2))
        elif q[0] == q[1]:
            a = int(rng.integers(0, 2))
        else:
            a = int(np.argmax(q))
        self.last_action = a
        return C if a == 0 else D

    def observe(self, own: Move, opp: Move, payoff: float) -> None:
        super().observe(own, opp, payoff)
        # learn on the *actual* action taken (implementation error included)
        a = 0 if own is C else 1
        s_next = (0 if own is C else 2) + (0 if opp is C else 1)
        target = payoff + self.gamma * float(np.max(self.Q[s_next]))
        self.Q[self.state, a] += self.alpha * (target - self.Q[self.state, a])
        self.state = s_next
        self.explore *= self.explore_decay

    def greedy_policy(self) -> tuple[float, float, float, float]:
        """Deterministic memory-one vector implied by the current Q-table."""
        return tuple(1.0 if self.Q[s, 0] >= self.Q[s, 1] else 0.0 for s in range(4))  # type: ignore[return-value]

    def clone(self) -> Strategy:
        return QLearner(
            self.alpha, self.gamma, self.explore0, self.explore_decay, self.persist, self.optimistic
        )
