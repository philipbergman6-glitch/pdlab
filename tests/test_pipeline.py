"""End-to-end smoke tests for the experiment / figure / CLI pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from pdlab.experiments import Scale, run_all
from pdlab.game import PayoffMatrix
from pdlab.reproduce import load_canonical, reproduce

PM = PayoffMatrix.axelrod()


@pytest.fixture(scope="module")
def quick_run(tmp_path_factory) -> tuple[Path, dict]:
    root = tmp_path_factory.mktemp("pdlab_repro")
    res = reproduce(root, Scale.quick(), hero=True)
    return root, res


def test_scale_presets_are_ordered():
    q, f = Scale.quick(), Scale.full()
    assert q.rounds < f.rounds
    assert q.moran_runs < f.moran_runs
    assert q.lattice < f.lattice


def test_run_all_produces_every_experiment_block():
    res = run_all(Scale.quick(), PM)
    expected = {
        "payoffs",
        "one_shot",
        "finite",
        "thresholds",
        "tournament",
        "noise_selfplay",
        "replicator",
        "moran_fixation",
        "moran_mutation",
        "evolution_noise",
        "spatial",
        "zd",
        "scale",
    }
    assert expected <= set(res)
    # the canonical numbers must match the analytic ones
    th = res["thresholds"]["thresholds"]
    assert th["grim_spe"] == pytest.approx(0.5)
    assert th["tft_vs_alternate"] == pytest.approx(2 / 3)
    assert json.dumps(res)  # fully JSON-serialisable


def test_reproduce_writes_results_and_figures(quick_run):
    root, res = quick_run
    assert (root / "results" / "canonical.json").exists()
    assert (root / "results" / "app_payload.json").exists()
    csvs = sorted(p.name for p in (root / "results").glob("*.csv"))
    assert "payoff_matrix.csv" in csvs
    assert "thresholds.csv" in csvs
    assert any(n.startswith("leaderboard_eps") for n in csvs)
    figs = sorted(p.name for p in (root / "figures").glob("*"))
    assert len(figs) > 20
    assert "hero_kaleidoscope.gif" in figs
    assert all((root / "figures" / f).stat().st_size > 0 for f in figs)
    assert res["elapsed_total_s"] > 0
    timing = json.loads((root / "results" / "timing.json").read_text())
    assert timing["total_s"] >= timing["experiments_s"] > 0
    # canonical.json carries no timings, so it is byte-reproducible
    assert "elapsed" not in (root / "results" / "canonical.json").read_text()


def test_load_canonical_round_trips(quick_run):
    root, res = quick_run
    loaded = load_canonical(root)
    assert loaded["payoffs"] == res["payoffs"]
    assert loaded["scale"] == res["scale"]


def test_load_canonical_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="run `pdlab reproduce` first"):
        load_canonical(tmp_path)


def test_app_payload_is_a_slim_subset(quick_run):
    root, _ = quick_run
    payload = json.loads((root / "results" / "app_payload.json").read_text())
    assert set(payload) >= {"payoffs", "thresholds", "leaderboards", "replicator", "zd"}
    assert payload["replicator"]["delta"] == pytest.approx(0.9)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def _runner():
    from typer.testing import CliRunner

    return CliRunner()


def test_cli_thresholds_command():
    from pdlab.cli import app

    res = _runner().invoke(app, ["thresholds"])
    assert res.exit_code == 0
    assert "grim_spe" in res.stdout
    assert "0.5000" in res.stdout
    assert "TFT can be SPE: False" in res.stdout


def test_cli_thresholds_with_custom_payoffs():
    from pdlab.cli import app

    res = _runner().invoke(app, ["thresholds", "--T", "4", "--R", "3", "--P", "1", "--S", "0"])
    assert res.exit_code == 0
    # T-R = P-S = 1 makes all three thresholds coincide at 1/3
    assert res.stdout.count("0.3333") == 5


def test_cli_play_command():
    from pdlab.cli import app

    res = _runner().invoke(app, ["play", "--me", "TFT", "--opponent", "ALLD", "--rounds", "6"])
    assert res.exit_code == 0
    assert "CDDDDD" in res.stdout
    assert "DDDDDD" in res.stdout


def test_cli_tournament_command():
    from pdlab.cli import app

    res = _runner().invoke(app, ["tournament", "--rounds", "20", "--reps", "1"])
    assert res.exit_code == 0
    assert "strategy" in res.stdout
    assert "ALLD" in res.stdout


def test_cli_reproduce_quick(tmp_path):
    from pdlab.cli import app

    res = _runner().invoke(app, ["reproduce", "--root", str(tmp_path), "--quick", "--no-hero"])
    assert res.exit_code == 0, res.output
    assert "done in" in res.stdout
    assert (tmp_path / "results" / "canonical.json").exists()
    assert not (tmp_path / "figures" / "hero_kaleidoscope.gif").exists()


def test_cli_no_args_shows_help():
    from pdlab.cli import app

    res = _runner().invoke(app, [])
    assert res.exit_code != 0
    assert "Prisoner" in res.stdout


def test_spatial_phase_values_are_probabilities():
    res = run_all(Scale.quick(), PM)
    for row in res["spatial"]["phase"]:
        assert 0.0 <= row["coop_mean"] <= 1.0
        assert np.isnan(row["coop_sd"]) or row["coop_sd"] >= 0.0
        assert 1 < row["b"] < 2


def test_moran_fixation_rows_bracket_the_neutral_value():
    res = run_all(Scale.quick(), PM)
    rows = res["moran_fixation"]["rows"]
    assert rows
    for r in rows:
        assert 0.0 <= r["exact"] <= 1.0
        assert 0.0 <= r["sim"] <= 1.0
        assert r["neutral"] == pytest.approx(1 / r["N"])


def test_replicator_block_reports_alld_as_ess():
    res = run_all(Scale.quick(), PM)
    rep = res["replicator"]
    assert np.array(rep["A"]) == pytest.approx(np.array([[3, 0, 3], [5, 1, 1.4], [3, 0.9, 3]]))
    assert rep["x_star"] == pytest.approx(1 / 17)
    assert rep["ess"]["ALLD"] is True
    assert rep["ess"]["ALLC"] is False


def test_simulate_discounted_total_validates_delta():
    from pdlab.experiments import simulate_discounted_total
    from pdlab.strategies import REGISTRY

    with pytest.raises(ValueError, match=r"delta in \[0,1\)"):
        simulate_discounted_total(
            REGISTRY.make("TFT"),
            REGISTRY.make("ALLD"),
            1.0,
            10,
            PM,
            np.random.default_rng(0),
        )


def test_simulate_discounted_total_matches_the_closed_form_for_alld_vs_tft():
    from pdlab.experiments import simulate_discounted_total
    from pdlab.strategies import REGISTRY

    d = 0.9
    mean, se = simulate_discounted_total(
        REGISTRY.make("ALLD"),
        REGISTRY.make("TFT"),
        d,
        4000,
        PM,
        np.random.default_rng(0),
    )
    exact = ((1 - d) * PM.T + d * PM.P) / (1 - d)  # normalised value / (1 - delta)
    assert mean == pytest.approx(exact, abs=4 * se)
