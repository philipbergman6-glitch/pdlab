# NOTES.md — running state (update after each milestone)

## Current state (2026-08-30)
- M1 core package DONE and committed. Full reproduce = ~60 s (Moran now 500k steps → ~4 min).
- Cross-check vs axelrod lib: 91/91 deterministic pairings exact; ZD vectors match. results/crosscheck_azelrod.md
- Subagents running: tests (tests/), report theory chapters (report/01–05 + bib), app (app/template.html + scripts/build_app.py).
- Report numerical chapters (06_numerics, 07_original, 08_conclusion) + abstract: TO WRITE by main agent after full run 2.
- Then: README, REVIEW (hostile prof + senior eng subagents), quality gates.

## Key numbers (full scale, seed-fixed)
- δ*_Grim = 1/2 (SPE); δ*_TFT Nash = 2/3; TFT never SPE for (5,3,1,0) (needs δ ≤ 1/4 after DD).
- Replicator δ=0.9: x*_TFT = 1/17 = 0.0588; eig(ALLD) = (−1, −0.1); fitted TFT extinction rate −0.098.
- Noise self-play closed forms: TFT = (T+R+P+S)/4 = 9/4 ∀ε>0; WSLS = 3−5ε+O(ε²); GTFT = 3−3ε; ZDGTFT2 = 3−8ε; ALLC 3−ε.
- Tournament (200 rounds, 10 reps, ε=0): GRADUAL > ZDGTFT2 > GTFT > CTFT > TFT > SOFTMAJ > TF2T ...
- Nowak–May 1.8<b<2: f_C = 0.314 (published 0.318); init-independent; async update → collapse to ~0.
- Moran fixation of 1 TFT in ALLD agrees with exact formula (within 2 SE) for N=4..32.
- Extort-2 vs Q-learner: learner ≈ 1.9–2.1, extortioner ≈ 2.8–3.1 on the line s_X−1 = 2(s_Y−1).
- Memory-one evolution ε=0.01: replicator → WSLS; Moran+mutation → ZDGTFT2 dominant.

## Decisions
- Python 3.11 via uv; package `pdlab`, src layout. pandoc+tectonic for PDF (brew).
- Payoffs (5,3,1,0); Nowak–May weak PD with self-interaction, periodic boundary, ties keep own strategy.
- Extort-2 default phi_frac=0.5 (matches Stewart–Plotkin vector), ZDGTFT-2 phi_frac=1.
