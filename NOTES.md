# NOTES.md — running state (update after each milestone)

## Current state
- M0 scaffold in progress. Nothing built yet.

## Decisions
- Python 3.11 via uv (`uv run`), package `pdlab` in src/ layout.
- Canonical payoffs: T=5,R=3,P=1,S=0 (Axelrod). Nowak–May uses b-parametrised weak PD (R=1,P=S=0,T=b).
- Original contribution: noise ε robustness + ZD vs Q-learning.

## Next steps
- Build core package.
