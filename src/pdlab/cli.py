"""Command-line interface: ``pdlab reproduce`` regenerates everything."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import typer

from pdlab.experiments import Scale
from pdlab.game import PayoffMatrix

app = typer.Typer(help="Prisoner's Dilemma laboratory", no_args_is_help=True)


@app.command()
def reproduce(
    root: Path = typer.Option(Path("."), help="project root (results/ and figures/ go here)"),
    quick: bool = typer.Option(False, help="tiny scale for smoke tests"),
    no_hero: bool = typer.Option(False, help="skip the README GIF"),
) -> None:
    """Regenerate results/canonical.json, tables and every figure from scratch."""
    from pdlab.reproduce import reproduce as _run

    scale = Scale.quick() if quick else Scale.full()
    res = _run(root, scale, hero=not no_hero)
    typer.echo(f"done in {res['elapsed_total_s']:.1f}s -> {root / 'results'} and {root / 'figures'}")


@app.command()
def tournament(
    rounds: int = 200,
    reps: int = 5,
    noise: float = 0.0,
    seed: int = 0,
) -> None:
    """Run a round-robin among every registered strategy and print the leaderboard."""
    from pdlab.strategies import REGISTRY
    from pdlab.tournament import round_robin

    res = round_robin(REGISTRY.make_all(), rounds, PayoffMatrix.axelrod(), noise, reps, seed)
    typer.echo(res.scores().to_string(index=False, float_format=lambda v: f"{v:.3f}"))


@app.command()
def thresholds(T: float = 5, R: float = 3, P: float = 1, S: float = 0) -> None:
    """Print the discount-factor thresholds for Grim Trigger and Tit-for-Tat."""
    from pdlab.analytic import thresholds as _th

    th = _th(PayoffMatrix(T, R, P, S))
    for k, v in th.__dict__.items():
        typer.echo(f"{k:>20s}: {v:.4f}")
    typer.echo(f"TFT can be SPE: {th.tft_is_spe_possible}")


@app.command()
def play(
    opponent: str = "TFT",
    rounds: int = 20,
    noise: float = 0.0,
    seed: int = 0,
    me: str = "WSLS",
) -> None:
    """Play strategy ``me`` against ``opponent`` and print the move history."""
    from pdlab.match import play_match
    from pdlab.strategies import REGISTRY

    rng = np.random.default_rng(seed)
    res = play_match(REGISTRY.make(me), REGISTRY.make(opponent), rounds, PayoffMatrix.axelrod(), rng, noise)
    typer.echo(f"{me:>8s}: " + "".join(m.value for m in res.moves1) + f"  score {res.score1:g}")
    typer.echo(f"{opponent:>8s}: " + "".join(m.value for m in res.moves2) + f"  score {res.score2:g}")


if __name__ == "__main__":  # pragma: no cover
    app()
