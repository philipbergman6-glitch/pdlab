"""Every headline number in README.md must be the one in results/canonical.json.

The README is hand-written prose, so this is the only thing stopping it from
drifting away from the code.  Skipped when the full-scale results are absent
(a fresh clone before `make reproduce`).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "results" / "canonical.json"
README = ROOT / "README.md"


@pytest.fixture(scope="module")
def canon() -> dict:  # type: ignore[type-arg]
    if not CANON.exists():
        pytest.skip("results/canonical.json not present")
    d = json.loads(CANON.read_text())
    if d["scale"]["rounds"] < 200:
        pytest.skip("canonical.json is not full scale")
    return d


def _expected_strings(d: dict) -> list[str]:  # type: ignore[type-arg]
    rep = d["replicator"]
    board = d["tournament"]["leaderboards"]["0.0"]
    tft_rank = next(r["rank"] for r in board if r["strategy"] == "TFT")
    learner = [r for r in d["zd"]["learner"] if r["opponent"] == "EXTORT2"]
    lm = sum(r["final_learner"] for r in learner) / len(learner)
    om = sum(r["final_opponent"] for r in learner) / len(learner)
    return [
        f"$x^* = 1/17 = {rep['x_star']:.4f}$",
        f"extinction rate ${rep['convergence']['fitted_rate']:.3f}$",
        f"**{d['spatial']['coop_1p8_2']:.3f}**",
        f"collapses to ${d['spatial']['sync_vs_async']['async'][-1]:.3f}$",
        f"Gradual ${board[0]['score']:.2f}$",
        f"TFT ({tft_rank}th)",
        f"Q-learner ends at ${lm:.2f}$ vs extortioner ${om:.2f}$",
    ]


def test_readme_quotes_canonical_numbers(canon: dict) -> None:  # type: ignore[type-arg]
    text = README.read_text()
    missing = [s for s in _expected_strings(canon) if s not in text]
    assert not missing, f"README numbers out of date: {missing}"
