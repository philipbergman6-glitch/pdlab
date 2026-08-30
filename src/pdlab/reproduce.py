"""One-command reproduction of every result, table and figure in the report."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from pdlab import figures as F
from pdlab.experiments import Scale, run_all
from pdlab.game import PayoffMatrix
from pdlab.spatial import SpatialPD


def write_tables(res: dict[str, Any], results_dir: Path) -> list[Path]:
    results_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for eps, board in res["tournament"]["leaderboards"].items():
        p = results_dir / f"leaderboard_eps{eps}.csv"
        pd.DataFrame(board).to_csv(p, index=False)
        paths.append(p)
    pm = res["tournament"]["payoff_matrix"]
    p = results_dir / "payoff_matrix.csv"
    pd.DataFrame(pm["values"], index=pm["names"], columns=pm["names"]).to_csv(p)
    paths.append(p)
    p = results_dir / "thresholds.csv"
    pd.DataFrame([res["thresholds"]["thresholds"]]).to_csv(p, index=False)
    paths.append(p)
    p = results_dir / "spatial_phase.csv"
    pd.DataFrame(res["spatial"]["phase"]).to_csv(p, index=False)
    paths.append(p)
    p = results_dir / "moran_fixation.csv"
    pd.DataFrame(res["moran_fixation"]["rows"]).to_csv(p, index=False)
    paths.append(p)
    return paths


def make_figures(res: dict[str, Any], fig_dir: Path, pm: PayoffMatrix) -> list[Path]:
    F.setup_style()
    paths: list[Path] = []
    paths += F.fig_folk_theorem(pm, fig_dir)
    paths += F.fig_thresholds(res["thresholds"], fig_dir)
    paths += F.fig_tournament(res["tournament"], fig_dir)
    paths += F.fig_noise_selfplay(res["noise_selfplay"], fig_dir)
    paths += F.fig_replicator(res["replicator"], fig_dir)
    paths += F.fig_moran(res["moran_fixation"], res["moran_mutation"], res["evolution_noise"], fig_dir)
    paths += F.fig_spatial(res["spatial"], fig_dir)
    paths += F.fig_zd(res["zd"], pm, fig_dir)
    return paths


def make_hero_gif(fig_dir: Path, L: int = 99, steps: int = 80) -> Path:
    g = SpatialPD.single_defector(L, 1.9, periodic=False)
    frames = [g.grid.copy()]
    for _ in range(steps):
        g.step()
        frames.append(g.grid.copy())
    p = fig_dir / "hero_kaleidoscope.gif"
    F.make_gif(frames, p)
    return p


def _app_payload(res: dict[str, Any]) -> dict[str, Any]:
    """Slim subset of the canonical results embedded in the web app."""
    rep = res["replicator"]
    return {
        "payoffs": res["payoffs"],
        "thresholds": res["thresholds"]["thresholds"],
        "leaderboards": res["tournament"]["leaderboards"],
        "payoff_matrix": res["tournament"]["payoff_matrix"],
        "replicator": {
            "delta": rep["delta"],
            "A": rep["A"],
            "x_star": rep["x_star"],
            "eigenvalues": rep["eigenvalues"],
            "ess": rep["ess"],
        },
        "noise_selfplay": {
            "eps": res["noise_selfplay"]["eps"],
            "strategies": {k: {"p": v["p"], "exact": v["exact"], "series_axelrod": v["series_axelrod"]} for k, v in res["noise_selfplay"]["strategies"].items()},
        },
        "spatial_phase": res["spatial"]["phase"],
        "spatial_coop_1p8_2": res["spatial"]["coop_1p8_2"],
        "moran_fixation": res["moran_fixation"]["rows"],
        "moran_mutation": [{k: v for k, v in r.items() if k != "mean_freq"} for r in res["moran_mutation"]["rows"]],
        "evolution_noise": [{"eps": r["eps"], "dominant": r["dominant"]} for r in res["evolution_noise"]["rows"]],
        "zd": {
            "extort2": res["zd"]["extort2"],
            "zdgtft2": res["zd"]["zdgtft2"],
            "scatter": res["zd"]["scatter"],
            "learner_final": [{k: r[k] for k in ("opponent", "seed", "final_learner", "final_opponent", "final_policy")} for r in res["zd"]["learner"]],
            "evolution_final": dict(zip(res["zd"]["evolution"]["names"], res["zd"]["evolution"]["replicator_final"], strict=True)),
            "moran_dominant": res["zd"]["evolution"]["moran_dominant"],
        },
    }


def reproduce(root: Path, scale: Scale, hero: bool = True) -> dict[str, Any]:
    t0 = time.time()
    pm = PayoffMatrix.axelrod()
    res = run_all(scale, pm)
    res["elapsed_s"] = time.time() - t0
    results_dir, fig_dir = root / "results", root / "figures"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "canonical.json").write_text(json.dumps(res, indent=1))
    (results_dir / "app_payload.json").write_text(json.dumps(_app_payload(res)))
    write_tables(res, results_dir)
    make_figures(res, fig_dir, pm)
    if hero:
        make_hero_gif(fig_dir, L=min(99, max(21, scale.lattice - 1)), steps=min(80, scale.lattice_steps))
    res["elapsed_total_s"] = time.time() - t0
    return res


def load_canonical(root: Path) -> dict[str, Any]:
    p = root / "results" / "canonical.json"
    if not p.exists():
        raise FileNotFoundError(f"{p} missing; run `pdlab reproduce` first")
    data: dict[str, Any] = json.loads(p.read_text())
    return data


__all__ = ["load_canonical", "make_figures", "make_hero_gif", "reproduce", "write_tables", "np"]
