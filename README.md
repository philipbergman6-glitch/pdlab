<p align="center">
  <img src="figures/hero_kaleidoscope.gif" width="360" alt="Nowak–May evolutionary kaleidoscope: one defector (red) in a lattice of cooperators (blue), b = 1.9">
</p>

<h1 align="center">pdlab — a laboratory for the Prisoner's Dilemma</h1>

<p align="center">
  <a href="report/build/prisoners_dilemma_report.pdf"><b>Report (PDF)</b></a> ·
  <a href="https://philipbergman6-glitch.github.io/pdlab/app/"><b>Interactive app</b></a> ·
  <a href="results/canonical.json">canonical results</a> ·
  <a href="REVIEW.md">independent reviews</a>
</p>

Defecting is better for you whatever the other player does, so two rational players defect and both end up worse off. **pdlab** takes that one game through rationality (backward induction, discount thresholds, folk theorems), selection (replicator, Moran, lattice) and imperfection (implementation noise, learning opponents, zero-determinant extortion), proving each result and then testing it numerically. Every number in the report, the figures and the app is produced by one command and cross-checked against an independent library.

## Key findings

| claim | derived | measured |
|---|---|---|
| Grim Trigger sustains cooperation iff $\delta \ge (T-R)/(T-P)$ | $\delta^* = 1/2$ | geometric-stopping simulation crosses at $0.50$ |
| Tit-for-Tat is a Nash equilibrium iff $\delta \ge \max\{(T-R)/(T-P),(T-R)/(R-S)\}$; subgame perfect **only if** $T-R = P-S$ | $\delta^* = 2/3$; never SPE for $(5,3,1,0)$ | four one-shot-deviation checks, symbolic + numeric |
| TFT needs a critical mass to invade ALLD (replicator, $\delta=0.9$) | $x^* = 1/17 = 0.0588$ | trajectories split at $0.0588$; extinction rate $-0.098$ vs Jacobian $-0.100$ |
| One TFT mutant in $N$ ALLD players fixes with probability $> 1/N$ | Nowak's exact formula | 2000-run simulations within 2 s.e. for $N = 4 \dots 32$ |
| Spatial cooperation without memory (Nowak & May 1992) | published $f_C = 0.318$ for $1.8 < b < 2$ | **0.314**, independent of initial conditions; collapses to $0.006$ under asynchronous updating |
| TFT's self-play payoff under implementation error $\varepsilon$ | $(T+R+P+S)/4 = 2.25$ for **every** $\varepsilon > 0$ (discontinuous at 0) | exact Markov chain = simulation; WSLS $3-5\varepsilon$, GTFT $3-3\varepsilon$ |
| Extort-2 pins any opponent to $s_X - 1 = 2(s_Y - 1)$ | Press & Dyson 2012 | Q-learner ends at $1.97$ vs extortioner $2.98$; but Extort-2 is **last** in the 18-strategy tournament and extinct in populations |
| Who wins Axelrod's tournament? | — | Gradual $2.74$ > ZDGTFT-2 > GTFT > CTFT > TFT (5th); contrite TFT dominates selection once $\varepsilon \ge 0.05$ |

## Run it in three commands

```bash
uv sync --extra dev          # Python ≥ 3.11; installs pdlab and dev tools
uv run pdlab reproduce       # ~2 min: results/canonical.json, 20 figures, README GIF
make report                  # pandoc + tectonic → report/build/prisoners_dilemma_report.pdf
```

`make all` does all three. `make test` runs the ~350-test suite (99 % branch coverage, property-based tests with Hypothesis; a test asserts that every number in this README matches `results/canonical.json`); `make lint` runs ruff and strict mypy. The app is rebuilt from the canonical results with `uv run python scripts/build_app.py`; open `app/index.html` by double-clicking. It is a scroll-driven live surface: the page ground is the 99 × 99 Nowak–May lattice computed in the page, and scrolling advances its generation (quiet for the first half, then 6 → 130 across the lattice bench); the finite-horizon bench unravels 200 rounds under the wheel, the noise bench sweeps ε through the exact 4 × 4 Markov chain, and the page ends in a `pdlab>` prompt that computes thresholds, matches, stationary payoffs and lattices on demand. Four benches show the theory rather than only its numbers: the discount slider assembles the Grim and TFT threshold derivations from the live payoffs, the noise bench prints the 4 × 4 transition matrix of any memory-one strategy with its column sums (TFT's are all 1, which is the whole proof), the lattice has a synchronous/asynchronous switch (Huberman–Glance), and the replicator simplex has a mutation-rate slider with the basin of cooperation drawn from 28 starts. The scroll engine is the scrollcraft runtime (inlined verbatim, unmodified); the build brief and verification shots live under `scrollcraft/builds/pdlab-surface/`. Hosted copy: <https://philipbergman6-glitch.github.io/pdlab/app/>.

Other entry points: `uv run pdlab tournament --noise 0.05`, `uv run pdlab thresholds --T 5 --R 3 --P 1 --S 0`, `uv run pdlab play --me WSLS --opponent EXTORT2 --rounds 30`.

## Architecture

```
                 ┌──────────────┐
                 │  game.py     │  PayoffMatrix (validated T>R>P>S, 2R>T+S), Move
                 └──────┬───────┘
        ┌───────────────┼───────────────────────────┐
 ┌──────▼──────┐ ┌──────▼──────┐             ┌──────▼──────┐
 │strategies.py│ │ markov.py   │             │ analytic.py │  sympy: δ* thresholds,
 │ 18 strats + │ │ exact 4-    │             │ replicator  │  Jacobian spectra, ESS,
 │ registry    │ │ state chain,│             │ fixed points│  noisy stationary payoffs
 └──────┬──────┘ │ ZD algebra  │             └──────┬──────┘
        │        └──────┬──────┘                    │
 ┌──────▼──────┐        │        ┌─────────────┐    │   ┌─────────────┐
 │ match.py    │        │        │ evolution.py│◄───┘   │ spatial.py  │
 │ tournament  │        │        │ replicator  │        │ Nowak–May   │
 │ learning.py │        │        │ Moran, ρ    │        │ sync/async  │
 └──────┬──────┘        │        └──────┬──────┘        └──────┬──────┘
        └───────────────┴───────────────┴──────────────────────┘
                                        │
                              ┌─────────▼──────────┐
                              │ experiments.py     │  every experiment, Scale.quick()/full()
                              │ figures.py         │  matplotlib, PDF + PNG
                              │ reproduce.py / cli │  results/canonical.json, app payload
                              └─────────┬──────────┘
                    ┌───────────────────┼───────────────────┐
             report/*.md          app/template.html     tests/ (~350)
       (numbers templated from    (payload inlined by    property tests,
        canonical.json at build)   scripts/build_app.py)  closed-form checks
```

Design rules: invalid input raises immediately (no silent failures); every stochastic routine takes an explicit `numpy.random.Generator`; strategies are cloned per match so no state leaks; the report cannot quote a number that the code did not produce (`scripts/render_report.py` fails on a missing key).

## Verification

* **Closed forms vs. simulation**: thresholds, stationary payoffs, fixation probabilities, Jacobian rates — all in `tests/`.
* **Independent implementation**: all 91 deterministic strategy pairings give identical 200-round scores in the [`axelrod`](https://github.com/Axelrod-Python/Axelrod) library; the Extort-2 and ZDGTFT-2 vectors match Stewart & Plotkin (2012) exactly (`results/crosscheck_axelrod.md`).
* **Published values**: Nowak–May $0.318$ (ours $0.314$), Beaufils et al. 1996 (Gradual beats TFT), Press–Dyson extortion line.
* **Reviews**: a hostile game-theory professor pass and a senior-engineer pass, with every finding and its resolution, in [`REVIEW.md`](REVIEW.md).

## Layout

```
src/pdlab/     package            report/     pandoc sources + Makefile     figures/   PDF+PNG+GIF
tests/         pytest suite       results/    canonical.json, CSV tables    app/       single-file web app
scripts/       render_report.py, build_app.py, crosscheck_axelrod.py        .github/   CI (ruff, mypy, pytest, quick reproduce)
```

Course: undergraduate game theory, final project. Author: Philip Bergman. MIT license.
