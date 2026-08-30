# ASSUMPTIONS.md

Unfilled placeholders in the mission brief were resolved as follows:

1. **Course level**: undergraduate intro game theory (from the course brief: pairs, 7-min talk, rubric theory/numerics/beyond 30/30/30/10). Report written at advanced-undergrad / early-grad rigor.
2. **Hard requirements**: the course brief supplied in chat (introduce → theory → numerics → go beyond). No written hand-in required by the course; the report is portfolio-motivated.
3. **Target roles**: quant / data science / software engineering — hence typed Python, tests, CI, reproducibility.
4. **Original contribution**: noise-robustness of memory-1 strategies under implementation error ε (exact Markov-chain stationary payoffs vs. simulation, evolutionary consequences) plus ZD-extortion vs. adaptive Q-learner.
5. **Payoffs**: Axelrod canonical (T,R,P,S)=(5,3,1,0) unless stated. Nowak–May spatial model uses the weak PD (R=1, T=b, P=S=0) exactly as in the 1992 paper, with self-interaction included and synchronous best-neighbour imitation, so cooperation fractions are comparable with published values.
6. **Noise model**: implementation (trembling-hand) error — each intended move is flipped independently with probability ε. Perception error is not modelled.
7. **Tooling**: Python 3.11 via `uv`; PDF via pandoc + tectonic (installed via Homebrew). No MacTeX.
8. **Axelrod reproduction**: the original 1980 tournament entries are not all publicly available as code; we reproduce the *qualitative* result (TFT wins/near-top among nice strategies) with a representative set of 15+ strategies, and compare against published rankings from the `axelrod` Python library documentation where possible.

9. **Report length**: the brief asked for 15–25 pages. With every proof written out (four one-shot-deviation classes for TFT, complete replicator phase portrait, Nowak–May thresholds) the report is ~48 pages at 11 pt. Rigor was prioritised over the page budget; Remarks 4.17, 5.20, 5.21 and the phase-diagram data table are the natural cuts if a shorter version is wanted.
10. **Moran "dominant strategy" tables** come from single long runs (500k events); which *nice* strategy is most frequent at a given (μ, ε) is partly drift, and the report says so where it matters.
11. **Safari**: the app was verified in headless Chrome only (no console-capturing Safari automation available); it uses ES5 JavaScript and guarded feature detection, so Safari is expected to work but was not machine-verified.
12. **App design brief was self-authored.** The scrollcraft skill requires an interview before building; the standing instruction for this project is to work without questions, so `scrollcraft/builds/pdlab-surface/BRIEF.md` was written in the project's voice and marked as such. The grammar (live surface), the signature move (scroll is the lattice generation counter) and the feeling curve are my choices, not the owner's.
13. **App verification.** The scroll page was walked by the scrollcraft harness in headless Chrome at 1440 × 900 (light and dark), 390 × 844 and under reduced motion: no dead scroll, no console errors, all cued copy ≥ 4.5:1 at its worst frame. A real phone (iOS decoder, Low Power Mode, touch scrolling) and Safari were not tested. `ffmpeg` is absent on this machine, so the harness's own contact sheet was replaced by one tiled with Pillow from the same frames.
