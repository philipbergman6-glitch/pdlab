"""Nowak & May (1992) spatial PD on a lattice."""

from __future__ import annotations

import numpy as np
import pytest

from pdlab.spatial import _OFFSETS, SpatialPD, _shift


# --------------------------------------------------------------------------
# _shift
# --------------------------------------------------------------------------
@pytest.mark.parametrize(("di", "dj"), _OFFSETS)
def test_shift_periodic_matches_modular_indexing(di, dj):
    a = np.arange(20.0).reshape(4, 5)
    out = _shift(a, di, dj, periodic=True)
    n, m = a.shape
    for i in range(n):
        for j in range(m):
            assert out[i, j] == a[(i + di) % n, (j + dj) % m]


@pytest.mark.parametrize(("di", "dj"), _OFFSETS)
def test_shift_fixed_boundary_pads_with_zeros(di, dj):
    a = np.arange(20.0).reshape(4, 5) + 1.0  # strictly positive: 0 marks padding
    out = _shift(a, di, dj, periodic=False)
    n, m = a.shape
    for i in range(n):
        for j in range(m):
            ii, jj = i + di, j + dj
            expected = a[ii, jj] if (0 <= ii < n and 0 <= jj < m) else 0.0
            assert out[i, j] == expected


def test_offsets_are_the_eight_moore_neighbours():
    assert len(_OFFSETS) == 8
    assert (0, 0) not in _OFFSETS


# --------------------------------------------------------------------------
# scores
# --------------------------------------------------------------------------
def test_scores_by_hand_on_a_3x3_grid_with_a_central_defector():
    b = 1.85
    grid = np.ones((3, 3), dtype=bool)
    grid[1, 1] = False
    s = SpatialPD(b, grid, periodic=False, self_interaction=True)
    sc = s.scores()
    # centre defector: 8 cooperating neighbours, self does not count (it defects)
    assert sc[1, 1] == pytest.approx(8 * b)
    # corner: 3 in-grid neighbours of which the centre defects -> 2 C + itself
    assert sc[0, 0] == pytest.approx(3.0)
    # edge: 5 in-grid neighbours of which the centre defects -> 4 C + itself
    assert sc[0, 1] == pytest.approx(5.0)


def test_scores_without_self_interaction_drop_by_one_for_cooperators():
    grid = np.ones((5, 5), dtype=bool)
    a = SpatialPD(1.5, grid.copy(), self_interaction=True)
    b_ = SpatialPD(1.5, grid.copy(), self_interaction=False)
    assert a.scores() == pytest.approx(b_.scores() + 1.0)
    assert np.all(b_.scores() == 8.0)


def test_defector_in_a_sea_of_cooperators_earns_the_most():
    s = SpatialPD.single_defector(9, 1.85)
    sc = s.scores()
    assert sc.argmax() == 4 * 9 + 4  # centre site


# --------------------------------------------------------------------------
# dynamics
# --------------------------------------------------------------------------
@pytest.mark.parametrize("periodic", [True, False])
def test_all_cooperators_is_absorbing(periodic):
    s = SpatialPD(1.85, np.ones((7, 7), dtype=bool), periodic=periodic)
    series, _ = s.run(5)
    assert series == pytest.approx(np.ones(6))


@pytest.mark.parametrize("periodic", [True, False])
def test_all_defectors_is_absorbing(periodic):
    s = SpatialPD(1.85, np.zeros((7, 7), dtype=bool), periodic=periodic)
    series, _ = s.run(5)
    assert series == pytest.approx(np.zeros(6))
    assert s.cooperation == 0.0


@pytest.mark.parametrize("periodic", [True, False])
def test_single_defector_spreads_at_b_1_85(periodic):
    s = SpatialPD.single_defector(21, 1.85, periodic=periodic)
    series, _ = s.run(10)
    assert series[0] == pytest.approx(1 - 1 / 441)
    assert series[3] < series[1] < series[0]  # the defector cluster grows
    assert series[-1] < 0.6


def test_single_defector_does_not_spread_when_b_is_barely_above_one():
    s = SpatialPD.single_defector(11, 1.05)
    series, _ = s.run(5)
    # b < 9/8: the defector scores 8b < 9 = a cooperator surrounded by cooperators
    assert series[-1] == pytest.approx(series[0])


def test_cooperation_series_stays_in_the_unit_interval():
    rng = np.random.default_rng(0)
    s = SpatialPD.random(15, 1.85, 0.6, rng)
    series, _ = s.run(8)
    assert series.shape == (9,)
    assert np.all((series >= 0.0) & (series <= 1.0))


def test_random_constructor_respects_coop_frac_bounds():
    rng = np.random.default_rng(0)
    assert SpatialPD.random(30, 1.5, 0.0, rng).cooperation == 0.0
    assert SpatialPD.random(30, 1.5, 1.0, rng).cooperation == 1.0
    s = SpatialPD.random(60, 1.5, 0.5, rng)
    assert 0.4 < s.cooperation < 0.6
    with pytest.raises(ValueError, match="coop_frac"):
        SpatialPD.random(10, 1.5, 1.5, rng)


def test_run_with_snapshots_returns_the_expected_count():
    s = SpatialPD.single_defector(11, 1.85)
    series, snaps = s.run(12, snapshots=4)
    assert series.shape == (13,)
    assert len(snaps) == 4 + 1  # initial grid plus one every 3 steps
    assert all(g.shape == (11, 11) for g in snaps)
    assert snaps[0][5, 5] is np.False_ or not snaps[0][5, 5]
    assert not np.array_equal(snaps[0], snaps[-1])


def test_run_without_snapshots_returns_no_grids():
    s = SpatialPD.single_defector(9, 1.85)
    _, snaps = s.run(3)
    assert snaps == []


def test_async_update_needs_an_rng_and_changes_the_grid():
    s = SpatialPD.single_defector(9, 1.85)
    with pytest.raises(ValueError, match="asynchronous update needs an rng"):
        s.run(3, asynchronous=True)
    rng = np.random.default_rng(0)
    series, _ = s.run(3, rng=rng, asynchronous=True)
    assert series[-1] < series[0]


@pytest.mark.parametrize("periodic", [True, False])
def test_async_update_is_seed_reproducible(periodic):
    a = SpatialPD.single_defector(9, 1.85, periodic=periodic)
    b_ = SpatialPD.single_defector(9, 1.85, periodic=periodic)
    sa, _ = a.run(2, rng=np.random.default_rng(4), asynchronous=True)
    sb, _ = b_.run(2, rng=np.random.default_rng(4), asynchronous=True)
    assert sa == pytest.approx(sb)


# --------------------------------------------------------------------------
# validation
# --------------------------------------------------------------------------
@pytest.mark.parametrize("b", [1.0, 2.0, 0.5, 3.0])
def test_invalid_b_raises(b):
    with pytest.raises(ValueError, match="Nowak-May"):
        SpatialPD(b, np.ones((5, 5), dtype=bool))


@pytest.mark.parametrize("grid", [np.ones(5, dtype=bool), np.ones((2, 5), dtype=bool)])
def test_invalid_grid_raises(grid):
    with pytest.raises(ValueError, match="grid must be 2-D"):
        SpatialPD(1.5, grid)


def test_steps_must_be_positive():
    s = SpatialPD.single_defector(5, 1.5)
    with pytest.raises(ValueError, match="steps must be"):
        s.run(0)
