"""Independent cross-check of pdlab strategies against the `axelrod` library.

Run with an environment that has `axelrod` installed (it is *not* a project
dependency):  ``python scripts/crosscheck_axelrod.py > results/crosscheck_axelrod.md``

For every deterministic strategy pair we compare the exact 200-round payoff of
pdlab's implementation with axelrod's.  Differences are either bugs or
documented definitional differences; the report discusses each.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import axelrod as axl  # type: ignore[import-not-found]  # noqa: E402
import numpy as np  # noqa: E402

from pdlab.game import PayoffMatrix  # noqa: E402
from pdlab.match import play_match  # noqa: E402
from pdlab.strategies import REGISTRY  # noqa: E402

MAP = {
    "ALLC": axl.Cooperator,
    "ALLD": axl.Defector,
    "TFT": axl.TitForTat,
    "STFT": axl.SuspiciousTitForTat,
    "TF2T": axl.TitFor2Tats,
    "GRIM": axl.Grudger,
    "WSLS": axl.WinStayLoseShift,
    "CTFT": axl.ContriteTitForTat,
    "ALT": axl.Alternator,
    "SOFTMAJ": axl.GoByMajority,
    "HARDMAJ": axl.HardGoByMajority,
    "PROBER": axl.Prober,
    "GRADUAL": axl.OriginalGradual,
}
STOCHASTIC = {"GTFT": lambda: axl.GTFT(p=1 / 3), "EXTORT2": axl.ZDExtort2, "ZDGTFT2": axl.ZDGTFT2}
ROUNDS = 200


def main() -> None:
    pm = PayoffMatrix.axelrod()
    game = axl.Game(r=3, s=0, t=5, p=1)
    names = list(MAP)
    print("# Cross-check: pdlab vs axelrod %s (deterministic strategies, %d rounds)\n" % (axl.__version__, ROUNDS))
    print("| pdlab A | pdlab B | pdlab (A,B) | axelrod (A,B) | match |")
    print("|---|---|---|---|---|")
    n_match = n_total = 0
    mismatches = []
    for i, a in enumerate(names):
        for b in names[i:]:
            r = play_match(REGISTRY.make(a), REGISTRY.make(b), ROUNDS, pm, np.random.default_rng(0))
            m = axl.Match((MAP[a](), MAP[b]()), turns=ROUNDS, game=game)
            m.play()
            sa, sb = m.final_score()
            ok = abs(sa - r.score1) < 1e-9 and abs(sb - r.score2) < 1e-9
            n_total += 1
            n_match += ok
            if not ok:
                mismatches.append((a, b, r.score1, r.score2, sa, sb))
            print(f"| {a} | {b} | ({r.score1:g}, {r.score2:g}) | ({sa:g}, {sb:g}) | {'yes' if ok else 'NO'} |")
    print(f"\n**{n_match}/{n_total} deterministic pairings agree exactly.**\n")
    if mismatches:
        print("Mismatches:\n")
        for a, b, p1, p2, q1, q2 in mismatches:
            print(f"- {a} vs {b}: pdlab ({p1:g},{p2:g}) axelrod ({q1:g},{q2:g})")
    print("\n# Memory-one vectors\n")
    for nm, fac in STOCHASTIC.items():
        s = REGISTRY.make(nm)
        ax = fac()
        vec = getattr(ax, "_four_vector", None)
        print(f"- {nm}: pdlab {tuple(round(v, 6) for v in s.memory_one)}; axelrod {ax.name}: {vec}")


if __name__ == "__main__":
    main()
