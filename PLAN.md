# PLAN.md — Prisoner's Dilemma Final Project

Status legend: [ ] todo  [~] in progress  [x] done

## M0 Scaffold
- [x] git init, uv project, dirs, PLAN/NOTES/ASSUMPTIONS
- [x] toolchain: pandoc + tectonic

## M1 Core package `pdlab`
- [x] core modules all written (game, strategies, match, tournament, markov, analytic, evolution, spatial, finite, learning, experiments, figures, reproduce, cli)
- [ ] strategies.py — ≥15 strategies via Strategy protocol + registry
- [ ] match.py — play_match(s1,s2,rounds,noise,rng)
- [ ] tournament.py — round robin, noise, seeds → DataFrame
- [ ] markov.py — memory-1 stationary payoffs (exact, noise ε), ZD algebra
- [ ] analytic.py — sympy δ* for Grim/TFT, one-shot deviation check, replicator fixed pts + Jacobian
- [ ] evolution.py — replicator ODE (ALLC/ALLD/TFT), Moran process
- [ ] spatial.py — Nowak–May lattice
- [ ] learning.py — Q-learning agent
- [ ] cli.py — `python -m pdlab reproduce`
- [ ] export.py — results/canonical.json for app

## M2 Tests
- [ ] pytest + hypothesis, ≥90% cov, ruff, mypy clean, GH Actions

## M3 Figures + results
- [ ] all figures PDF+PNG, tables, canonical.json

## M4 Report (pandoc → PDF)
- [ ] sections 1–9 + bib; compile clean

## M5 App (single HTML)
- [ ] frontend-design skill → build → verify in Safari/Chrome

## M6 README, REVIEW (hostile prof + senior eng), cross-checks
- [ ] README.md w/ hero GIF
- [ ] REVIEW.md
- [ ] 3 published cross-checks

## Original contribution decision
Noise-robustness of memory-1 strategies under implementation error ε:
exact Markov stationary payoffs vs simulation; evolutionary consequences;
plus ZD-extortion vs Q-learner.
