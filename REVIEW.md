# REVIEW.md — independent review passes and their resolution

Two adversarial reviews were run on the finished project (2026-08-30) by
separate agents that had not seen the code or report before: a **hostile
game-theory professor** on the report, and a **senior software engineer**
on the code, tests, CI and app. Every finding is listed with what was done.
Verdicts quoted verbatim where useful.

## A. Hostile professor — report

> "The mathematics that the report actually proves is, with one exception,
> sound: I re-derived every threshold, spectrum, lattice count and Markov
> expansion independently … What fails is the report's discipline about
> its own claims."

Sections the reviewer re-derived and confirmed correct: all of Chapter 2
(dominance, mixed-strategy uniqueness, Pareto classification, weak-dilemma
equilibrium set), all of Chapter 3 (backward induction, unique Nash path),
Grim threshold and both phases, the two-state dynamic program behind
Axelrod's Proposition 2, all four one-shot-deviation classes of the TFT
knife-edge theorem, the folk-theorem statements and attributions, the
replicator payoff matrix, edge fixed point and all four Jacobian spectra,
ESS classification, the Moran fixation formula and 1/3 law, the Nowak–May
thresholds 9/8, 7/5, 8/5, 9/5 (recomputed two ways), Proposition 7.1(1)'s
doubly-stochastic proof, the ZD sign conventions and the Stewart–Plotkin
vectors, and the bibliography details checked.

| # | severity | finding | resolution |
|---|---|---|---|
| B1 | BLOCKER | ALLC noise expansion stated as $R-(R-S)\varepsilon$; correct is $R-(2R-T-S)\varepsilon$ (contradicted the table beside it) | **Fixed** (07_original.md), with the one-line derivation added |
| B2 | BLOCKER | Hard-coded "exactly 1.0397" for Grim self-play at $\varepsilon=0.01$; true long-run value is $1+3\varepsilon-\varepsilon^2=1.0299$ | **Fixed**: replaced by the closed form and its value (04_infinite.md) |
| B3 | BLOCKER | Template slip rendered "TFT-th" in the PDF | **Fixed**: render script now supports `{{stat:rank_TFT_0.0\|ordinal}}` |
| B4 | BLOCKER | Three citation keys missing (`beaufils1996`, `axelrodlib`, `nowakbonhoeffermay1994`) rendered "(?)" | **Fixed**: key corrected; Knight et al. 2016 (JORS) and Nowak–Bonhoeffer–May 1994 (PNAS) added to references.bib |
| M1 | MAJOR | Huberman–Glance stated backwards in the built PDF (source already corrected, PDF stale) | **Fixed**: PDF rebuilt from source; PDF now committed |
| M2 | MAJOR | "Extort-2 is last at every noise level" — false at $\varepsilon=0.05, 0.1$ | **Fixed**: sentence now computed from the leaderboard (`stat:extort2_best_rank`) |
| M3 | MAJOR | ZD table computed at $\varepsilon=0.01$ on *both* sides, which destroys the ZD property it claimed to confirm (ratios 1.2–1.9 instead of 2) | **Fixed and turned into a result**: table now shows exact noise-free payoffs (ratio exactly 2 wherever $s_Y>P$) *and* the noisy ratio, with text explaining that extortion is exact only for a player who never misplays |
| M4 | MAJOR | "Extortion wins every pairwise contest" — false vs ALLD and itself | **Fixed**: precise statement $s_X-P=2(s_Y-P)\ge s_Y-P$ |
| M5 | MAJOR | "Every simulated value within 2 s.e." — 2 of 21 were not | **Fixed**: counts outside 2 and 3 s.e. are computed and quoted (`stat:threshold_outside_2se`) |
| M6 | MAJOR | Staircase steps claimed to occur only at the derived rationals; five further steps visible | **Fixed**: text now says the derived values are among the steps and names the unexplained ones |
| M7 | MAJOR | Selten–Stoecker design misdescribed | **Fixed**: 25 supergames of ten rounds |
| M8 | MAJOR | Every theorem reference in Chapters 6 and 8 pointed at the wrong object | **Fixed**: all eight references corrected to the numbering of Chapters 2–5 |
| M9 | MAJOR | $\delta^*_{\mathrm{TFT}}$ restated as the single branch $(T-R)/(R-S)$ instead of the max | **Fixed** |
| m1 | MINOR | $\sigma$ vs $\delta(P-S)$ slip in the interior-rest-point proof | **Fixed** |
| m2 | MINOR | One corner-neighbourhood score listed as 7 instead of 6 | **Fixed** |
| m3 | MINOR | Incumbent-defector conditions should be $\ge$, not $>$ (tie rule) | **Fixed** |
| m4 | MINOR | 9/8 marks the *disappearance* of the frozen monad; blinker regime unmentioned | **Fixed** |
| m5 | MINOR | Strictness in Theorem 5.10(2) asserted without reason | **Fixed**: reason added |
| m6 | MINOR | The equivalence (4.6) $\iff T-R=P-S$ used in Chapter 8 but not proved | **Fixed**: three-line proof added to Theorem 4.9 |
| m7 | MINOR | "three-dimensional projective space" imprecise | **Fixed**: replaced by the linear equation $T+S=R+P$ |
| m8 | MINOR | Fudenberg–Maskin stated with pure minmax | **Fixed**: mixed minmax stated, with the remark that they coincide in the PD |
| m9 | MINOR | Weak dilemma wrongly called a limit of the donation game | **Fixed** |
| m10–11 | MINOR | "exceeds" → "is at least"; profiles vs payoff vectors | **Fixed** |
| m12 | MINOR | "seven best are nice" — actually eight | **Fixed**: computed from the data (`stat:top_nice_run`) |
| m13 | MINOR | s.e. conventions inconsistent between two tables | **Fixed**: both tables now show 2 s.e. |
| m14 | MINOR | "$N=50$" stated for all Moran runs; fixation uses 4–32 | **Fixed** |
| m15 | MINOR | 1/3 law invoked outside its weak-selection regime | **Fixed**: caveat added |
| m16 | MINOR | "near one third" at $\mu=0.2$ overstated | **Fixed**: now $\mu=0.5$ |
| m17 | MINOR | ALLC called "generous"; slope ranking over-interpreted | **Fixed** |
| m18 | MINOR | Q-learner parameters reused $\alpha,\gamma,\varepsilon$ | **Fixed**: named in words |
| m19 | MINOR | $\varepsilon=0.02$ Grim row unexplained | **Fixed**: drift explanation added |
| m20 | MINOR | "344 tests" stale | **Fixed**: "about 350" |
| m21 | MINOR | "destroys" → "erodes" | **Fixed** |
| m22 | MINOR | Abstract over-claims cross-checking and extinction | **Fixed** |
| m23 | MINOR | seventy-five → seventy-six years | **Fixed** |

Not changed: the reviewer's remark that Proposition 7.1(1) holds for all
$\varepsilon\in(0,1)$ (we keep the statement for $(0,\tfrac12]$ to match the
code's guard; the proof is unchanged).

## B. Senior engineer — code, tests, CI, app

> "The engineering floor is genuinely high … What stops approval is small
> and entirely fixable in a day."

| # | severity | finding | resolution |
|---|---|---|---|
| 1 | BLOCKER | README links a non-existent REVIEW.md | **Fixed**: this file |
| 2 | BLOCKER | JS port of Contrite TFT still had the one-round-apology bug (Python had been fixed) | **Fixed**: JS now tracks both standings exactly as `pdlab.strategies.ContriteTitForTat` |
| 3 | MAJOR | `clone()` silently dropped a custom `payoffs` argument for GTFT / Extort / ZDGTFT | **Fixed**: the matrix is stored and passed through `clone()` |
| 4 | MAJOR | `SpatialPD` aliased and mutated the caller's grid | **Fixed**: copies on construction |
| 5 | MAJOR | `include_self=False` fabricated the diagonal of `mean_payoff` | **Fixed**: diagonal stays NaN; `scores()` uses `nanmean`; test updated to assert NaN |
| 6 | MAJOR | README numbers hand-typed and unchecked | **Fixed**: `tests/test_readme_numbers.py` asserts every headline number against `canonical.json` (the "1.97 vs 2.98" the reviewer flagged is the 5-seed mean, now tested as such) |
| 7 | MAJOR | Wall-clock time inside `canonical.json` breaks byte-reproducibility | **Fixed**: timings go to `results/timing.json`; test asserts no timing in canonical |
| 8 | MAJOR | CI never compared regenerated numbers | **Fixed**: CI runs the quick reproduce twice and `cmp`s the two canonical files |
| 9 | MAJOR | `make all` skipped tests and the app; `make clean` deleted tracked results | **Fixed**: `all: sync test reproduce app report`; clean leaves `results/` |
| 10 | MAJOR | mypy did not cover tests/scripts; results structure is `Any` | **Partly fixed**: mypy now checks `src`, `scripts` and `tests` (tests with relaxed untyped-def rules). The `dict[str, Any]` result structure is kept deliberately: it is JSON by design, and the report renderer hard-fails on any missing key |
| 11 | MAJOR | `np.std` with ddof=0 and a cancellation-prone SE formula | **Fixed**: sample s.d. (ddof=1) everywhere; SE from `np.std(..., ddof=1)/sqrt(n)`; single-seed s.d. is NaN, not 0 |
| 12 | MAJOR | Fixation runs allocated full histories; unresolved runs counted silently as losses | **Fixed**: `record=False` option; unresolved runs raise |
| 13 | MINOR | `fixation_probability` did not validate indices; product could overflow | **Fixed**: validation; log-space accumulation |
| 14 | MINOR | `stop_at_fixation` silently ignored with mutation | **Fixed**: raises |
| 15 | MINOR | `assert` used for validation in src | **Fixed**: all replaced with explicit raises |
| 16–18 | MINOR | `"np"` in `__all__`; dead `_rng_cache`; a `type: ignore` | **Fixed** |
| 19 | MINOR | coverage flags in `addopts` broke partial runs | **Fixed**: coverage only in `make test` and CI |
| 20 | MINOR | `Vec4` used for a 4×4 matrix; `MemoryOneT` defined after use | **Fixed**: `Mat4` alias; moved |
| 21 | MINOR | Test weaknesses (no determinism test; seed-only-equals-seed; tests that cannot fail; loose tolerances) | **Partly fixed**: CI determinism check added; `_pair` helper typed; tolerance and negative-control improvements left as future work |
| NIT | — | README PDF link into a gitignored directory | **Fixed**: the built PDF is now committed |
| NIT | — | `Gradual.queue.pop(0)`; `snapshots` naming; deprecated license form; CI permissions/concurrency/`--frozen`; `.PHONY render`; `asdict` in CLI | **Fixed** |
| NIT | — | `step_async` triple loop recomputes local scores | Not changed (correctness verified against the vectorised scorer; runtime is seconds) |
| NIT | — | `reproduce` exposes no `--seed` | Not changed (seeds are experiment-level constants in `experiments.py` by design; documented there) |

Both reviewers noted that a fresh clone of the earlier HEAD could not build the
report because chapters 6–8 were uncommitted at the time of review; all
chapters, the render script and the built PDF are now committed.
