"""Every number on the talk slides must be the one in results/canonical.json.

Same guard as test_readme_numbers.py: slides/index.html is hand-written, so
this is what stops it drifting from the code.  Skipped when the full-scale
results are absent.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "results" / "canonical.json"
SLIDES = ROOT / "slides" / "index.html"


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
    score = {r["strategy"]: r["score"] for r in board}
    learner = [r for r in d["zd"]["learner"] if r["opponent"] == "EXTORT2"]
    lm = sum(r["final_learner"] for r in learner) / len(learner)
    om = sum(r["final_opponent"] for r in learner) / len(learner)
    return [
        f"x* = 1/17</td><td>trajectories split at {rep['x_star']:.4f}",
        # the slides typeset rates with U+2212
        f"<td>\u2212{-rep['convergence']['predicted_rate']:.3f}</td>"
        f"<td>\u2212{-rep['convergence']['fitted_rate']:.3f}</td>",
        f"<mark>{d['spatial']['coop_1p8_2']:.3f}</mark>",
        f"<mark>{d['spatial']['sync_vs_async']['async'][-1]:.3f}</mark>",
        f"Gradual <mark>{score['GRADUAL']:.3f}</mark>",
        f"ZDGTFT-2 {score['ZDGTFT2']:.3f}",
        f"GTFT {score['GTFT']:.3f}",
        f"Contrite TFT {score['CTFT']:.3f}",
        f"TFT {score['TFT']:.3f}",
        f'ends at <span class="math">{lm:.2f}</span>',
        f"<mark>{om:.2f}</mark>",
        f'scores <span class="math">{score["EXTORT2"]:.3f}</span>, last of {len(board)}',
    ]


def test_slides_quote_canonical_numbers(canon: dict) -> None:  # type: ignore[type-arg]
    text = SLIDES.read_text()
    missing = [s for s in _expected_strings(canon) if s not in text]
    assert not missing, f"slide numbers out of date: {missing}"


def test_slide_rankings_match_leaderboard(canon: dict) -> None:  # type: ignore[type-arg]
    board = canon["tournament"]["leaderboards"]["0.0"]
    assert [r["strategy"] for r in board[:5]] == ["GRADUAL", "ZDGTFT2", "GTFT", "CTFT", "TFT"]
    assert board[-1]["strategy"] == "EXTORT2"
