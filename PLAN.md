# PLAN.md — Prisoner's Dilemma Final Project

Status legend: [ ] todo  [~] in progress  [x] done

## M0 Scaffold
- [x] git init, uv project, dirs, PLAN/NOTES/ASSUMPTIONS
- [x] toolchain: pandoc + tectonic

## M1 Core package `pdlab`
- [x] core modules all written (game, strategies, match, tournament, markov, analytic, evolution, spatial, finite, learning, experiments, figures, reproduce, cli)
- [x] strategies.py — 18 strategies via Strategy protocol + registry
- [x] match.py — play_match(s1,s2,rounds,noise,rng)
- [x] tournament.py — round robin, noise, seeds → DataFrame
- [x] markov.py — memory-1 stationary payoffs (exact, noise ε), ZD algebra
- [x] analytic.py — sympy δ* for Grim/TFT, one-shot deviation check, replicator fixed pts + Jacobian
- [x] evolution.py — replicator ODE (ALLC/ALLD/TFT), Moran process
- [x] spatial.py — Nowak–May lattice
- [x] learning.py — Q-learning agent
- [x] cli.py — `python -m pdlab reproduce`
- [x] reproduce.py — results/canonical.json + app payload (planned as export.py)

## M2 Tests
- [x] pytest + hypothesis (346 tests, 99% cov), ruff, mypy clean, GH Actions

## M3 Figures + results
- [x] all figures PDF+PNG, tables, canonical.json, hero GIF

## M4 Report (pandoc → PDF)
- [x] chapters 1–8 + bib; pandoc-crossref + tectonic build (48 pp.)

## M5 App (single HTML)
- [x] frontend-design skill → build → verified headless Chrome (Safari not machine-verified)

## M6 README, REVIEW (hostile prof + senior eng), cross-checks
- [x] README.md w/ hero GIF
- [x] REVIEW.md (prof + engineer findings, all resolved or noted)
- [x] 3 published cross-checks (Nowak–May 0.318, Stewart–Plotkin ZD vectors, Beaufils Gradual>TFT) + axelrod lib 91/91

## Original contribution decision
Noise-robustness of memory-1 strategies under implementation error ε:
exact Markov stationary payoffs vs simulation; evolutionary consequences;
plus ZD-extortion vs Q-learner.
