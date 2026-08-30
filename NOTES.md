# NOTES.md — running state (update after each milestone)

## Current state (2026-08-30, final)
- All deliverables built, both reviews applied (REVIEW.md), PDF committed. Remaining ideas: 7-min slide deck; tighten test tolerances; Safari manual check.

## Earlier state
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

## App rebuilt as a scroll-driven live surface (2026-08-30)
- Grammar: live surface. Eight acts: flow > pin > flow > pan > pin (peak, 3.6vh) > flow > pin > flow; 14.0 viewport-heights on desktop, 15.9 on a 390px phone.
- Signature move: the fixed ground canvas is the real 99×99 synchronous Nowak–May lattice (130 generations precomputed in ~50 ms); scroll before the peak advances it 0→6, the peak act's `--sc-p` advances it 6→130, then it holds and recedes toward the canvas colour. `data-sc-verify-state` publishes `gen|f_C|b|dim` for the harness.
- Bench logic (strategies, Markov chain, replicator RK4, lattice) reused from the previous app and unchanged in semantics; new: exact stationary-distribution solver in JS (Gaussian elimination, hard-fails at ε = 0 when the chain is not unique), FLIP re-ranking of the tournament cards, `pdlab>` prompt.
- Harness fixes: hero never revealed (`data-sc-stagger` without `data-sc-in`); lattice too loud after the peak (added dimming); keyboard focus inside pinned acts parks the act at the control's cue window.
- Feel check (cold): curiosity / pressure / control / breadth / awe / clarity / sober / ready. Intended act 4 was 'recognition'; it reads as breadth first; the read-out card carries the recognition (Gradual > TFT, first non-nice at rank k). Left as is.
