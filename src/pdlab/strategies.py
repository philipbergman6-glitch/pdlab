"""Strategy library for the iterated Prisoner's Dilemma.

Every strategy is a small stateful object with the interface

* ``reset()``                     -- forget history before a new match
* ``play(rng) -> Move``          -- choose the next *intended* move
* ``observe(own, opp, payoff)``  -- learn what actually happened this round

Memory-one strategies additionally expose ``memory_one`` (probability of
cooperating after CC, CD, DC, DD from the strategy's own perspective) and
``initial`` (probability of cooperating in round 1), which the exact Markov
analysis in :mod:`pdlab.markov` consumes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np

from pdlab.game import C, D, Move, PayoffMatrix

MemoryOne = tuple[float, float, float, float]


class Strategy(ABC):
    """Base class. Subclasses override :meth:`_decide`; history is managed here."""

    name: str = "Strategy"
    memory_one: MemoryOne | None = None
    initial: float | None = None

    def __init__(self) -> None:
        self.own: list[Move] = []
        self.opp: list[Move] = []
        self.score: float = 0.0

    def reset(self) -> None:
        self.own.clear()
        self.opp.clear()
        self.score = 0.0
        self._reset_state()

    def _reset_state(self) -> None:  # noqa: B027 - optional hook
        """Optional hook for strategies with extra internal state."""

    def play(self, rng: np.random.Generator) -> Move:
        return self._decide(rng)

    @abstractmethod
    def _decide(self, rng: np.random.Generator) -> Move: ...

    def observe(self, own: Move, opp: Move, payoff: float) -> None:
        self.own.append(own)
        self.opp.append(opp)
        self.score += payoff

    def clone(self) -> Strategy:
        return type(self)()

    def __repr__(self) -> str:
        return f"<{self.name}>"


# --------------------------------------------------------------------------
# helper for memory-one strategies
# --------------------------------------------------------------------------
class MemoryOneStrategy(Strategy):
    """Generic memory-one strategy defined by ``(p_CC, p_CD, p_DC, p_DD)``."""

    def __init__(self, probs: MemoryOne, initial: float, name: str) -> None:
        super().__init__()
        probs_t = tuple(float(p) for p in probs)
        if len(probs_t) != 4:
            raise ValueError("memory-one strategy needs exactly 4 probabilities")
        for p in (*probs_t, initial):
            if not 0.0 <= p <= 1.0:
                raise ValueError(f"probabilities must lie in [0, 1], got {p}")
        self.memory_one = (probs_t[0], probs_t[1], probs_t[2], probs_t[3])
        self.initial = float(initial)
        self.name = name

    def _decide(self, rng: np.random.Generator) -> Move:
        if self.memory_one is None or self.initial is None:
            raise RuntimeError("memory-one strategy not initialised")
        if not self.own:
            p = self.initial
        else:
            idx = (0 if self.own[-1] is C else 2) + (0 if self.opp[-1] is C else 1)
            p = self.memory_one[idx]
        if p == 1.0:
            return C
        if p == 0.0:
            return D
        return C if rng.random() < p else D

    def clone(self) -> Strategy:
        if self.memory_one is None or self.initial is None:
            raise RuntimeError("memory-one strategy not initialised")
        return MemoryOneStrategy(self.memory_one, self.initial, self.name)


# --------------------------------------------------------------------------
# classic strategies
# --------------------------------------------------------------------------
class AllC(MemoryOneStrategy):
    def __init__(self) -> None:
        super().__init__((1, 1, 1, 1), 1, "ALLC")

    def clone(self) -> Strategy:
        return AllC()


class AllD(MemoryOneStrategy):
    def __init__(self) -> None:
        super().__init__((0, 0, 0, 0), 0, "ALLD")

    def clone(self) -> Strategy:
        return AllD()


class TitForTat(MemoryOneStrategy):
    """Cooperate first, then copy the opponent's last move (Rapoport)."""

    def __init__(self) -> None:
        super().__init__((1, 0, 1, 0), 1, "TFT")

    def clone(self) -> Strategy:
        return TitForTat()


class SuspiciousTitForTat(MemoryOneStrategy):
    """TFT that defects on the first move."""

    def __init__(self) -> None:
        super().__init__((1, 0, 1, 0), 0, "STFT")

    def clone(self) -> Strategy:
        return SuspiciousTitForTat()


class GenerousTitForTat(MemoryOneStrategy):
    """TFT that forgives a defection with probability g (Nowak & Sigmund 1992).

    g = min(1 - (T-R)/(R-S), (R-P)/(T-P)); for (5,3,1,0) this is 1/3.
    """

    def __init__(self, payoffs: PayoffMatrix | None = None) -> None:
        pm = payoffs or PayoffMatrix.axelrod()
        g = min(1 - (pm.T - pm.R) / (pm.R - pm.S), (pm.R - pm.P) / (pm.T - pm.P))
        self.generosity = g
        self._pm = pm
        super().__init__((1, g, 1, g), 1, "GTFT")

    def clone(self) -> Strategy:
        return GenerousTitForTat(self._pm)


class WinStayLoseShift(MemoryOneStrategy):
    """Pavlov: repeat last move if payoff was R or T, otherwise switch."""

    def __init__(self) -> None:
        super().__init__((1, 0, 0, 1), 1, "WSLS")

    def clone(self) -> Strategy:
        return WinStayLoseShift()


class Random(MemoryOneStrategy):
    def __init__(self, p: float = 0.5) -> None:
        if not 0 <= p <= 1:
            raise ValueError("p must be in [0, 1]")
        self.p = p
        super().__init__((p, p, p, p), p, "RANDOM")

    def clone(self) -> Strategy:
        return Random(self.p)


class Alternator(Strategy):
    """C, D, C, D, ... regardless of the opponent."""

    name = "ALT"

    def _decide(self, rng: np.random.Generator) -> Move:
        return C if len(self.own) % 2 == 0 else D


class GrimTrigger(Strategy):
    """Cooperate until the opponent defects once, then defect forever."""

    name = "GRIM"

    def _reset_state(self) -> None:
        self.triggered = False

    def __init__(self) -> None:
        super().__init__()
        self.triggered = False

    def observe(self, own: Move, opp: Move, payoff: float) -> None:
        super().observe(own, opp, payoff)
        if opp is D:
            self.triggered = True

    def _decide(self, rng: np.random.Generator) -> Move:
        return D if self.triggered else C


class TitForTwoTats(Strategy):
    """Defect only after two consecutive opponent defections."""

    name = "TF2T"

    def _decide(self, rng: np.random.Generator) -> Move:
        if len(self.opp) >= 2 and self.opp[-1] is D and self.opp[-2] is D:
            return D
        return C


class ContriteTitForTat(Strategy):
    """TFT with *standing* (Boerlijst, Nowak & Sigmund 1997, "The logic of contrition").

    A player is in *bad standing* after defecting against an opponent who was in
    good standing; cooperating restores good standing.  CTFT defects only when it
    is itself in good standing and the opponent is in bad standing.  Hence after
    an accidental defection it accepts one retaliation without answering it,
    which breaks the echo of mutual recrimination that plain TFT falls into.
    Without errors it is indistinguishable from TFT.
    """

    name = "CTFT"

    def __init__(self) -> None:
        super().__init__()
        self.my_good = True
        self.opp_good = True

    def _reset_state(self) -> None:
        self.my_good = True
        self.opp_good = True

    @property
    def contrite(self) -> bool:
        return not self.my_good

    def _decide(self, rng: np.random.Generator) -> Move:
        return D if (self.my_good and not self.opp_good) else C

    def observe(self, own: Move, opp: Move, payoff: float) -> None:
        super().observe(own, opp, payoff)
        my_prev, opp_prev = self.my_good, self.opp_good
        self.my_good = not (own is D and opp_prev)
        self.opp_good = not (opp is D and my_prev)


class SoftMajority(Strategy):
    """Cooperate if the opponent has cooperated at least as often as defected."""

    name = "SOFTMAJ"

    def _decide(self, rng: np.random.Generator) -> Move:
        n_c = sum(m is C for m in self.opp)
        return C if n_c >= len(self.opp) - n_c else D


class HardMajority(Strategy):
    """Defect unless the opponent has cooperated strictly more than defected."""

    name = "HARDMAJ"

    def _decide(self, rng: np.random.Generator) -> Move:
        n_c = sum(m is C for m in self.opp)
        return C if n_c > len(self.opp) - n_c else D


class Prober(Strategy):
    """Play D, C, C; if the opponent cooperated in rounds 2 and 3, defect forever,
    otherwise play TFT (Axelrod 1984 second-tournament entry style)."""

    name = "PROBER"

    def __init__(self) -> None:
        super().__init__()
        self.exploit = False

    def _reset_state(self) -> None:
        self.exploit = False

    def _decide(self, rng: np.random.Generator) -> Move:
        n = len(self.own)
        if n == 0:
            return D
        if n in (1, 2):
            return C
        if n == 3:
            self.exploit = self.opp[1] is C and self.opp[2] is C
        if self.exploit:
            return D
        return self.opp[-1]


class Gradual(Strategy):
    """Beaufils et al. (1996): after the k-th opponent defection, punish with k
    defections, then offer two cooperations."""

    name = "GRADUAL"

    def __init__(self) -> None:
        super().__init__()
        self.n_defections = 0
        self.queue: deque[Move] = deque()

    def _reset_state(self) -> None:
        self.n_defections = 0
        self.queue = deque()

    def observe(self, own: Move, opp: Move, payoff: float) -> None:
        super().observe(own, opp, payoff)
        if opp is D and not self.queue:
            self.n_defections += 1
            self.queue = deque([D] * self.n_defections + [C, C])

    def _decide(self, rng: np.random.Generator) -> Move:
        if self.queue:
            return self.queue.popleft()
        return C


# --------------------------------------------------------------------------
# zero-determinant strategies (Press & Dyson 2012; Stewart & Plotkin 2012)
# --------------------------------------------------------------------------
class ZDExtort(MemoryOneStrategy):
    """Extortionate ZD strategy enforcing s_X - P = chi (s_Y - P).

    Uses the closed form of Press & Dyson (2012) with the largest feasible phi
    scaled by ``phi_frac``; for (5,3,1,0), chi=2, phi_frac=1 gives (8/9, 1/2, 1/3, 0).
    """

    def __init__(
        self, chi: float = 2.0, phi_frac: float = 0.5, payoffs: PayoffMatrix | None = None
    ) -> None:
        from pdlab.markov import extort_vector

        pm = payoffs or PayoffMatrix.axelrod()
        p = extort_vector(pm, chi=chi, phi_frac=phi_frac)
        self.chi, self.phi_frac, self._pm = chi, phi_frac, pm
        super().__init__(p, 0.0, f"EXTORT{chi:g}")

    def clone(self) -> Strategy:
        return ZDExtort(self.chi, self.phi_frac, self._pm)


class ZDGenerous(MemoryOneStrategy):
    """Generous ZD strategy enforcing s_X - R = chi (s_Y - R) (Stewart & Plotkin 2012).

    For (5,3,1,0), chi=2, phi_frac=1 this is ZDGTFT-2 = (1, 1/8, 1, 1/4).
    """

    def __init__(
        self, chi: float = 2.0, phi_frac: float = 1.0, payoffs: PayoffMatrix | None = None
    ) -> None:
        from pdlab.markov import generous_vector

        pm = payoffs or PayoffMatrix.axelrod()
        p = generous_vector(pm, chi=chi, phi_frac=phi_frac)
        self.chi, self.phi_frac, self._pm = chi, phi_frac, pm
        super().__init__(p, 1.0, f"ZDGTFT{chi:g}")

    def clone(self) -> Strategy:
        return ZDGenerous(self.chi, self.phi_frac, self._pm)


# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Registry:
    factories: dict[str, Callable[[], Strategy]] = field(default_factory=dict)

    def names(self) -> list[str]:
        return list(self.factories)

    def make(self, name: str) -> Strategy:
        if name not in self.factories:
            raise KeyError(f"unknown strategy {name!r}; known: {sorted(self.factories)}")
        return self.factories[name]()

    def make_all(self) -> list[Strategy]:
        return [f() for f in self.factories.values()]


def _qlearner() -> Strategy:
    from pdlab.learning import QLearner

    return QLearner()


REGISTRY = Registry(
    {
        "ALLC": AllC,
        "ALLD": AllD,
        "TFT": TitForTat,
        "STFT": SuspiciousTitForTat,
        "GTFT": GenerousTitForTat,
        "TF2T": TitForTwoTats,
        "GRIM": GrimTrigger,
        "WSLS": WinStayLoseShift,
        "CTFT": ContriteTitForTat,
        "RANDOM": Random,
        "ALT": Alternator,
        "SOFTMAJ": SoftMajority,
        "HARDMAJ": HardMajority,
        "PROBER": Prober,
        "GRADUAL": Gradual,
        "EXTORT2": ZDExtort,
        "ZDGTFT2": ZDGenerous,
        "QLEARN": _qlearner,
    }
)
"""All strategies available to the tournament, keyed by short name."""
