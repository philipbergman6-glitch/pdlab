"""Deterministic behavioural tests for every strategy in the registry."""

from __future__ import annotations

import numpy as np
import pytest

from pdlab.game import C, D, Move, PayoffMatrix
from pdlab.match import play_match
from pdlab.strategies import (
    REGISTRY,
    ContriteTitForTat,
    GenerousTitForTat,
    MemoryOneStrategy,
    Random,
    Registry,
    Strategy,
    TitForTat,
)

PM = PayoffMatrix.axelrod()
STOCHASTIC = {"GTFT", "RANDOM", "EXTORT2", "ZDGTFT2", "QLEARN"}


def _s(moves: tuple[Move, ...]) -> str:
    return "".join(m.value for m in moves)


def duel(name1: str, name2: str, rounds: int, seed: int = 0) -> tuple[str, str]:
    """Play a match between two registry strategies and return move strings."""
    res = play_match(
        REGISTRY.make(name1), REGISTRY.make(name2), rounds, PM, np.random.default_rng(seed)
    )
    return _s(res.moves1), _s(res.moves2)


def against_script(strategy: Strategy, opp_moves: str, seed: int = 0) -> str:
    """Feed a fixed opponent move sequence to ``strategy`` and return its moves."""
    rng = np.random.default_rng(seed)
    strategy.reset()
    out: list[Move] = []
    for ch in opp_moves:
        b = C if ch == "C" else D
        a = strategy.play(rng)
        pa, _ = PM.payoffs(a, b)
        strategy.observe(a, b, pa)
        out.append(a)
    return _s(out)


# --------------------------------------------------------------------------
# known deterministic duels
# --------------------------------------------------------------------------
DUELS = [
    ("ALLC", "ALLD", "CCCCCCCC", "DDDDDDDD"),
    ("ALLC", "ALT", "CCCCCCCC", "CDCDCDCD"),
    ("ALLD", "TFT", "DDDDDDDD", "CDDDDDDD"),
    ("ALLD", "ALLC", "DDDDDDDD", "CCCCCCCC"),
    ("TFT", "ALLD", "CDDDDDDD", "DDDDDDDD"),
    ("TFT", "TFT", "CCCCCCCC", "CCCCCCCC"),
    ("TFT", "ALT", "CCDCDCDC", "CDCDCDCD"),
    ("STFT", "TFT", "DCDCDCDC", "CDCDCDCD"),
    ("STFT", "ALLC", "DCCCCCCC", "CCCCCCCC"),
    ("STFT", "ALLD", "DDDDDDDD", "DDDDDDDD"),
    ("TF2T", "ALLD", "CCDDDDDD", "DDDDDDDD"),
    ("TF2T", "ALT", "CCCCCCCC", "CDCDCDCD"),
    ("GRIM", "ALLD", "CDDDDDDD", "DDDDDDDD"),
    ("GRIM", "ALT", "CCDDDDDD", "CDCDCDCD"),
    ("GRIM", "TFT", "CCCCCCCC", "CCCCCCCC"),
    ("WSLS", "ALLD", "CDCDCDCD", "DDDDDDDD"),
    ("WSLS", "ALT", "CCDDCCDD", "CDCDCDCD"),
    ("WSLS", "TFT", "CCCCCCCC", "CCCCCCCC"),
    ("CTFT", "ALLD", "CDDDDDDD", "DDDDDDDD"),
    ("CTFT", "TFT", "CCCCCCCC", "CCCCCCCC"),
    ("ALT", "ALLC", "CDCDCDCD", "CCCCCCCC"),
    ("SOFTMAJ", "ALT", "CCCCCCCC", "CDCDCDCD"),
    ("SOFTMAJ", "ALLD", "CDDDDDDD", "DDDDDDDD"),
    ("HARDMAJ", "ALT", "DCDCDCDC", "CDCDCDCD"),
    ("HARDMAJ", "ALLC", "DCCCCCCC", "CCCCCCCC"),
    ("HARDMAJ", "ALLD", "DDDDDDDD", "DDDDDDDD"),
    ("PROBER", "ALLC", "DCCDDDDD", "CCCCCCCC"),
    ("PROBER", "TFT", "DCCCCCCC", "CDCCCCCC"),
    ("PROBER", "ALLD", "DCCDDDDD", "DDDDDDDD"),
    ("GRADUAL", "ALLC", "CCCCCCCC", "CCCCCCCC"),
]


@pytest.mark.parametrize(("a", "b", "want_a", "want_b"), DUELS)
def test_known_duels(a, b, want_a, want_b):
    got_a, got_b = duel(a, b, len(want_a))
    assert (got_a, got_b) == (want_a, want_b)


def test_registry_covers_every_strategy_against_the_four_probes():
    """Every registry entry produces legal moves against ALLC/ALLD/TFT/ALT."""
    for name in REGISTRY.names():
        for opp in ("ALLC", "ALLD", "TFT", "ALT"):
            ma, mb = duel(name, opp, 12, seed=3)
            assert len(ma) == len(mb) == 12
            assert set(ma) <= {"C", "D"}


def test_tft_vs_alld_scores_s_then_p_forever(axelrod):
    res = play_match(
        REGISTRY.make("TFT"), REGISTRY.make("ALLD"), 20, axelrod, np.random.default_rng(0)
    )
    assert res.score1 == axelrod.S + 19 * axelrod.P
    assert res.score2 == axelrod.T + 19 * axelrod.P
    assert res.mean1 == pytest.approx((axelrod.S + 19 * axelrod.P) / 20)


def test_grim_trigger_is_permanent():
    grim = REGISTRY.make("GRIM")
    # a single defection in round 3, cooperation afterwards, never forgiven
    assert against_script(grim, "CCDCCCCCCC") == "CCCDDDDDDD"


def test_tf2t_tolerates_isolated_defections_but_not_two_in_a_row():
    tf2t = REGISTRY.make("TF2T")
    assert against_script(tf2t, "DCDCDDCC") == "CCCCCCDC"


def test_gradual_punishment_lengths_grow_1_2_3():
    got = duel("GRADUAL", "ALLD", 13)[0]
    assert got == "CDCCDDCCDDDCC"
    runs = [len(r) for r in got.split("C") if r]
    assert runs == [1, 2, 3]


def test_softmajority_ties_cooperate_hardmajority_ties_defect():
    # opponent history C, D -> equal counts: SOFTMAJ cooperates, HARDMAJ defects
    assert against_script(REGISTRY.make("SOFTMAJ"), "CD")[-1] == "C"
    assert against_script(REGISTRY.make("HARDMAJ"), "CD")[-1] == "C"  # 1 C beats 0 D
    # after C, D, D the defections lead: both defect
    assert against_script(REGISTRY.make("SOFTMAJ"), "CDDC") == "CCCD"
    assert against_script(REGISTRY.make("HARDMAJ"), "CDDC") == "DCDD"


def test_prober_exploits_allc_and_reverts_to_tft_against_tft():
    exploit, _ = duel("PROBER", "ALLC", 10)
    assert exploit == "DCCDDDDDDD"
    tft_like, opp = duel("PROBER", "TFT", 10)
    assert tft_like == "DCCCCCCCCC"
    assert opp == "CDCCCCCCCC"


def test_ctft_becomes_contrite_after_a_forced_error_and_cooperates_once_more():
    ctft = ContriteTitForTat()
    tft = TitForTat()
    rng = np.random.default_rng(0)
    seen = []
    for t in range(5):
        a = ctft.play(rng)
        b = tft.play(rng)
        if t == 2:  # implementation error: intended C came out as D
            a = a.flip()
        pa, pb = PM.payoffs(a, b)
        ctft.observe(a, b, pa)
        tft.observe(b, a, pb)
        seen.append((a.value, b.value, ctft.contrite))
    assert [s[:2] for s in seen[:3]] == [("C", "C"), ("C", "C"), ("D", "C")]
    assert seen[2][2] is True  # contrite after defecting on a cooperator
    # while contrite it cooperates despite the retaliation, then contrition clears
    assert seen[3][:2] == ("C", "D")
    assert seen[3][2] is False


def test_ctft_contrition_does_not_arise_from_a_deliberate_defection():
    ctft = ContriteTitForTat()
    assert against_script(ctft, "CDCC") == "CCDC"
    assert ctft.contrite is False


# --------------------------------------------------------------------------
# registry mechanics
# --------------------------------------------------------------------------
def test_registry_make_unknown_name_raises_keyerror():
    with pytest.raises(KeyError, match="unknown strategy"):
        REGISTRY.make("NOPE")


def test_registry_names_and_make_all():
    names = REGISTRY.names()
    assert "TFT" in names and "QLEARN" in names
    made = REGISTRY.make_all()
    assert len(made) == len(names)
    assert [s.name for s in made] == names


def test_empty_registry_error_lists_known_names():
    reg = Registry({"ALLC": REGISTRY.factories["ALLC"]})
    assert reg.names() == ["ALLC"]
    with pytest.raises(KeyError):
        reg.make("TFT")


# --------------------------------------------------------------------------
# memory-one machinery
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("probs", "initial"),
    [((1.2, 0, 0, 0), 1.0), ((-0.1, 0, 0, 0), 1.0), ((1, 0, 0, 0), 1.5), ((1, 0, 0, 0), -1e-9)],
)
def test_memory_one_rejects_probabilities_outside_unit_interval(probs, initial):
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        MemoryOneStrategy(probs, initial, "BAD")


def test_memory_one_wrong_length_raises():
    with pytest.raises(ValueError):
        MemoryOneStrategy((1, 0, 0), 1.0, "BAD")


def test_random_p_validation_and_clone_keeps_p():
    with pytest.raises(ValueError, match=r"p must be in"):
        Random(1.5)
    r = Random(0.25)
    c = r.clone()
    assert isinstance(c, Random)
    assert c.p == 0.25
    assert c.memory_one == (0.25,) * 4


def test_memory_one_interior_probability_uses_rng():
    s = MemoryOneStrategy((0.5, 0.5, 0.5, 0.5), 0.5, "HALF")
    rng = np.random.default_rng(0)
    draws = [s.play(rng) for _ in range(200)]
    assert {m for m in draws} == {C, D}
    clone = s.clone()
    assert isinstance(clone, MemoryOneStrategy)
    assert clone.memory_one == s.memory_one and clone.initial == s.initial


@pytest.mark.parametrize("name", sorted(REGISTRY.factories))
def test_clone_returns_fresh_independent_object(name):
    s = REGISTRY.make(name)
    play_match(s, REGISTRY.make("ALLD"), 6, PM, np.random.default_rng(1))
    assert s.own  # history recorded
    c = s.clone()
    assert c is not s
    assert type(c) is type(s)
    assert c.name == s.name
    assert c.own == [] and c.opp == [] and c.score == 0.0
    # mutating the clone leaves the original alone
    c.observe(C, D, 0.0)
    assert len(s.own) == 6
    assert len(c.own) == 1


def test_reset_clears_history_and_state():
    grim = REGISTRY.make("GRIM")
    against_script(grim, "DDDD")
    assert grim.triggered
    grim.reset()
    assert not grim.triggered
    assert grim.own == [] and grim.score == 0.0
    assert against_script(grim, "CCC") == "CCC"


def test_repr_shows_name():
    assert repr(REGISTRY.make("TFT")) == "<TFT>"


def test_gtft_generosity_is_one_third_for_axelrod_payoffs():
    g = GenerousTitForTat()
    assert g.generosity == pytest.approx(1 / 3)
    assert g.memory_one == pytest.approx((1.0, 1 / 3, 1.0, 1 / 3))
    assert g.initial == 1.0
    assert isinstance(g.clone(), GenerousTitForTat)


def test_gtft_generosity_takes_the_binding_constraint():
    pm = PayoffMatrix(T=4, R=3, P=1, S=0)
    g = GenerousTitForTat(pm)
    assert g.generosity == pytest.approx(min(1 - (4 - 3) / 3, (3 - 1) / (4 - 1)))


def test_gtft_never_defects_against_a_cooperator():
    moves, _ = duel("GTFT", "ALLC", 50, seed=11)
    assert set(moves) == {"C"}


def test_zd_strategies_expose_published_vectors():
    ex = REGISTRY.make("EXTORT2")
    gen = REGISTRY.make("ZDGTFT2")
    assert ex.memory_one == pytest.approx((8 / 9, 1 / 2, 1 / 3, 0.0))
    assert ex.initial == 0.0
    assert ex.name == "EXTORT2"
    assert gen.memory_one == pytest.approx((1.0, 1 / 8, 1.0, 1 / 4))
    assert gen.initial == 1.0
    assert ex.clone().memory_one == ex.memory_one
    assert gen.clone().memory_one == gen.memory_one


@pytest.mark.parametrize("name", sorted(set(REGISTRY.factories) - STOCHASTIC))
def test_deterministic_strategies_ignore_the_rng(name):
    a = duel(name, "ALT", 15, seed=0)
    b = duel(name, "ALT", 15, seed=999)
    assert a == b


@pytest.mark.parametrize("name", sorted(STOCHASTIC - {"QLEARN"}))
def test_stochastic_strategies_are_seed_reproducible(name):
    assert duel(name, "ALT", 40, seed=7) == duel(name, "ALT", 40, seed=7)
