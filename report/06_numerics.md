# Numerical analysis: testing the theory

Every result in this chapter is produced by `pdlab`, the Python package
written for this project, from a single command (`make reproduce`) with fixed
random seeds. The numbers quoted in the text are substituted into the
manuscript at build time directly from `results/canonical.json`, so a number
in this report cannot disagree with the code that produced it. All
experiments use Axelrod's payoffs $(T,R,P,S)=(5,3,1,0)$ unless stated
otherwise. Simulation parameters: {{tournament.rounds}} rounds per match and
{{tournament.reps}} repetitions for tournaments; lattices of
${{scale.lattice}}\times{{scale.lattice}}$ sites for {{scale.lattice_steps}} generations;
Moran populations of $N={{scale.moran_n}}$ run for {{scale.moran_steps}} birth–death events in the mutation and noise experiments (the fixation experiment uses $N = {{stat:fixation_N_min}}$ to ${{stat:fixation_N_max}}$).

## The one-shot game and backward induction

`pdlab.finite.backward_induction` solves the $n$-fold repeated game by the
constructive argument of Theorem 3.4: at each stage it enumerates the pure
Nash equilibria of the stage game shifted by the (history-independent)
continuation values. For every $n$ it finds exactly one, $(D,D)$, and the
resulting path is all-$D$ with row total $nP$:

{{table:finite}}

The solver refuses to proceed if a stage game has several pure equilibria
(a coordination game in the test-suite triggers this), which is precisely the
case in which the Benoit–Krishna [-@benoitkrishna1985] cooperative equilibria
of finitely repeated games become possible.

## Discount thresholds by geometric stopping

Theorems 4.5 and 4.8 predict $\delta^*_{\mathrm{Grim}}=(T-R)/(T-P)={{thresholds.thresholds.grim_spe|.4g}}$
and $\delta^*_{\mathrm{TFT}}=\max\{(T-R)/(T-P),\,(T-R)/(R-S)\}={{thresholds.thresholds.tft_nash|.4g}}$, the second branch being the binding one for Axelrod's payoffs.
`pdlab.analytic` derives both symbolically with `sympy` (the code solves
$R/(1-\delta)=T+\delta P/(1-\delta)$ and $R/(1-\delta)=(T+\delta S)/(1-\delta^2)$
and simplifies), and the test-suite checks that the symbolic expressions
reduce to the closed forms above.

To test the *interpretation* of $\delta$ as a continuation probability, we
simulate matches whose length is geometric: after every round the match
continues with probability $\delta$, so the expected unnormalised total is
exactly $\sum_t \delta^t \pi_t$. We play Grim against Grim (cooperation),
ALLD against Grim (permanent defection) and Suspicious TFT against TFT
(which produces the alternating path $D,C,D,C,\dots$ against a TFT opponent)
for {{scale.discount_matches}} matches per value of $\delta$ and compare the
normalised mean totals $(1-\delta)\,\bar V$ with the exact values:

{{table:thresholds_sim}}

Of the {{stat:threshold_comparisons}} comparisons, {{stat:threshold_outside_2se}} fall outside two standard errors and {{stat:threshold_outside_3se}} outside three, as expected for that many independent comparisons; the crossing points of the curves in @fig:thresholds fall at the
predicted thresholds. Note the qualitative content: the alternating deviation
is the *binding* one for TFT, which is why TFT needs a more patient player
($\delta\ge 2/3$) than Grim Trigger ($\delta \ge 1/2$).

![Cooperation and deviation values as a function of the discount factor: lines are the closed forms, markers are geometric-stopping simulations ($\pm 2$ s.e.). The dotted lines mark $\delta^*_{\mathrm{Grim}}=1/2$ and $\delta^*_{\mathrm{TFT}}=2/3$.](../figures/thresholds.pdf){#fig:thresholds width=85%}

## Exact Markov-chain payoffs versus simulation

For two memory-one strategies the match is a four-state Markov chain
(Chapter 7 gives the details). `pdlab.markov` computes the stationary
distribution exactly, and also implements the Press–Dyson determinant
formula $s_X = D(p,q,S_X)/D(p,q,\mathbf 1)$ independently; the test-suite
verifies that the two agree to $10^{-9}$ on random strategy pairs and that
the exact expected $n$-round averages agree with simulated matches for
deterministic strategies. This machinery underlies every "exact" curve in
the remainder of the report.

## An Axelrod-style tournament

We ran a round-robin among {{tournament.payoff_matrix.names|len}} strategies
(the fifteen classical strategies of @tbl:strategies plus the two zero-determinant
strategies and a Q-learning agent), every strategy also playing a copy of
itself, exactly as in Axelrod's tournaments. The same tournament was then
repeated with implementation noise $\varepsilon \in \{0, 0.01, 0.05, 0.1\}$:
each intended move is replaced by its opposite with probability
$\varepsilon$, independently for both players, and both players observe the
move that was actually played.

| strategy | rule | nice | memory-one $p$ |
|---|---|---|---|
| ALLC | always cooperate | yes | $(1,1,1,1)$ |
| ALLD | always defect | no | $(0,0,0,0)$ |
| TFT | cooperate first, then copy the opponent's last move | yes | $(1,0,1,0)$ |
| STFT | TFT starting with $D$ | no | $(1,0,1,0)$, starts $D$ |
| GTFT | TFT that forgives a defection with probability $1/3$ | yes | $(1,\tfrac13,1,\tfrac13)$ |
| TF2T | defect only after two consecutive defections | yes | — |
| GRIM | cooperate until the first defection, then defect forever | yes | — |
| WSLS | repeat the last move after $R$ or $T$, switch after $S$ or $P$ | yes | $(1,0,0,1)$ |
| CTFT | TFT with standing (contrite) | yes | — |
| RANDOM | cooperate with probability $1/2$ | no | $(\tfrac12,\tfrac12,\tfrac12,\tfrac12)$ |
| ALT | $C, D, C, D, \dots$ | no | — |
| SOFTMAJ | cooperate iff the opponent has cooperated at least as often as defected | yes | — |
| HARDMAJ | cooperate iff the opponent has cooperated strictly more often | no | — |
| PROBER | $D,C,C$; exploit if not punished, else TFT | no | — |
| GRADUAL | punish the $k$-th defection with $k$ defections, then $C,C$ | yes | — |
| EXTORT2 | zero-determinant extortioner, $\chi = 2$ | no | $(\tfrac89,\tfrac12,\tfrac13,0)$ |
| ZDGTFT2 | generous zero-determinant, $\chi = 2$ | yes | $(1,\tfrac18,1,\tfrac14)$ |
| QLEARN | tabular $\varepsilon$-greedy Q-learner on the last outcome | — | learned |

Table: The tournament field. "Nice" means never the first to defect. {#tbl:strategies}

{{table:leaderboard}}

Table: Mean payoff per round (rank in parentheses) for four noise levels. Strategies are ordered by their noiseless score. {#tbl:leaderboard}

Three features deserve comment.

1. **Nice strategies fill the top of the table**, exactly as Axelrod found:
   the {{stat:top_nice_run}} best strategies at $\varepsilon = 0$ are all nice (never the
   first to defect); {{stat:first_non_nice}} is the first that is not. Tit-for-Tat itself is {{stat:rank_TFT_0.0|ordinal}}; the winner is
   {{tournament.leaderboards["0.0"][0].strategy}} with
   {{tournament.leaderboards["0.0"][0].score|.3f}} per round, in line with
   Beaufils, Delahaye and Mathieu [-@beaufilsdelahayemathieu1996], who introduced Gradual
   precisely because it beats TFT in tournaments of this kind. TFT's
   success in 1980 depended on the particular field of entrants, not on
   dominance over all comers (indeed no strategy can be best against every
   field; Axelrod [-@axelrod1984, ch. 2]).
2. **Generous strategies gain as noise rises.** GTFT and ZDGTFT-2 overtake
   the stricter reciprocators once $\varepsilon>0$, while Grim collapses:
   a single accidental defection triggers permanent punishment. @fig:ranks shows the full rank changes.
3. **Extortion loses tournaments.** Extort-2 is last without noise and never
   better than {{stat:extort2_best_rank|ordinal}} of {{stat:n_strategies}} at any noise level (only ALLD and,
   under heavy noise, ALLC keep it company at the bottom). It can only "win"
   *relative* to its current opponent, at the cost of a low absolute score.
   We return to this in Chapter 7.

![Tournament rank as implementation noise increases.](../figures/tournament_noise_ranks.pdf){#fig:ranks width=80%}

![Pairwise per-round payoff matrix (row versus column) without noise.](../figures/tournament_matrix.pdf){#fig:matrix width=85%}

### Cross-check against an independent implementation

To guard against implementation errors we compared `pdlab` with the
independently developed `axelrod` library [@knight2016axelrod]. For all
91 pairings of the thirteen deterministic strategies
the two libraries produce *identical* 200-round scores, and the memory-one
vectors of GTFT, Extort-2 and ZDGTFT-2 agree with the library's to machine
precision (`results/crosscheck_axelrod.md`).

## Replicator dynamics for ALLC, ALLD and TFT

With $\delta=0.9$ the normalised payoff matrix of Chapter 5 is

$$A=\begin{pmatrix} {{replicator.A[0][0]|.2f}} & {{replicator.A[0][1]|.2f}} & {{replicator.A[0][2]|.2f}}\\ {{replicator.A[1][0]|.2f}} & {{replicator.A[1][1]|.2f}} & {{replicator.A[1][2]|.2f}}\\ {{replicator.A[2][0]|.2f}} & {{replicator.A[2][1]|.2f}} & {{replicator.A[2][2]|.2f}}\end{pmatrix},$$

and Theorem 5.8 predicts the unstable fixed point on the ALLD–TFT edge at
$x^*_{\mathrm{TFT}} = {{replicator.x_star|.4f}} = 1/17$. Integrating the replicator
equation (`scipy.integrate.solve_ivp`, relative tolerance $10^{-9}$) from 27
initial conditions confirms the bistable picture of @fig:simplex:
populations that start with fewer than $x^*$ reciprocators converge to
all-ALLD; populations above the threshold eliminate ALLD and drift to a
point on the ALLC–TFT edge that depends on the initial condition (the edge
is a continuum of neutral fixed points). The finite-difference Jacobian
eigenvalues agree with the symbolic ones of Theorem 5.9:

{{table:eigenvalues}}

![Replicator trajectories on the simplex for $\delta=0.9$. Black dots: vertex fixed points; gold: the saddle at $x^*_{\mathrm{TFT}}=1/17$; every point on the ALLC–TFT edge is a fixed point.](../figures/replicator_simplex.pdf){#fig:simplex width=70%}

### Beyond the fixed points: how fast is convergence?

Linearisation predicts that near the ALLD vertex the TFT frequency decays as
$e^{\lambda t}$ with $\lambda = A_{\mathrm{TFT},\mathrm{ALLD}}-A_{\mathrm{ALLD},\mathrm{ALLD}} = (1-\delta)(S-P) = {{replicator.convergence.predicted_rate|.3f}}$.
A least-squares fit of $\log x_{\mathrm{TFT}}(t)$ on the numerical trajectory
started at $x_{\mathrm{TFT}}=x^*/2$ gives a slope of
{{replicator.convergence.fitted_rate|.4f}} (@fig:conv): convergence is
exponential, and the rate is set by the *discounted* gap between the
sucker's and the punishment payoff. Because $(1-\delta)$ multiplies the
rate, a more patient population (larger $\delta$) loses its reciprocators
*more slowly*: patience protects cooperation even where it fails to sustain
it.

![Extinction of TFT below the threshold is exponential at the Jacobian rate.](../figures/replicator_convergence.pdf){#fig:conv width=65%}

## Finite populations: the Moran process

In a finite population selection is stochastic. We simulate the
frequency-dependent Moran process with fitness equal to payoff ($w=1$) and
compare the fixation probability of a single TFT mutant in an ALLD
population with the exact formula of Theorem 5.13, for
{{moran_fixation.rows[0].runs}} independent runs per population size:

{{table:moran_fixation}}

{{stat:fixation_outside_2se}} of the seven simulated values fall outside two standard errors of the exact ones.
The fixation probability exceeds the neutral value $1/N$ for every $N$:
a lone reciprocator is *favoured* by selection even though TFT is not an ESS
in the infinite-population sense, because with $N$ finite it meets itself
sufficiently often once it has a few copies. (The $1/3$ law of Theorem 5.14 is a weak-selection, large-$N$ statement; here $w = 1$ and $N \le 32$, so the agreement in sign is a bonus rather than a test of that theorem.)

### Mutation: how much is needed to break the cooperative equilibrium?

The syllabus asks how large the mutation rate must be to destroy the
equilibrium. The answer depends sharply on the strategy space.

*Three strategies.* Starting from an all-TFT population of size $N$ with
mutation to a uniformly random strategy at rate $\mu$ per birth:

{{table:moran_three}}

Without mutation TFT is absorbing. With mutation the population is pushed
along the neutral ALLC–TFT edge by drift; once enough ALLC has accumulated
an ALLD mutant invades (the TFT share has fallen below the threshold), the
population crashes towards ALLD, and it is rescued only when a TFT lineage
reaches the threshold $x^*$ by drift. The result is the
ALLC$\to$ALLD$\to$TFT cycle of Nowak and Sigmund [-@nowaksigmund1992; @nowak2006book, ch. 5]
(@fig:three). Already at $\mu = 0.001$ (one birth in a thousand) the
population spends {{moran_mutation.three.rows[1].frac_time_alld_majority|.0%}}
of its time with an ALLD majority and the cooperation rate has fallen from 1
to {{moran_mutation.three.rows[1].coop_rate|.2f}}; at $\mu = 0.01$ it is
{{moran_mutation.three.rows[3].coop_rate|.2f}}, and by $\mu = 0.5$ the
population is mutation-dominated, with all three strategies near one third
and cooperation at {{moran_mutation.three.rows[9].coop_rate|.2f}}. There is
therefore no sharp critical mutation rate: the cooperative equilibrium
erodes continuously, and the *first* order-of-magnitude of mutation is the
one that matters, because it opens the neutral drift along the ALLC–TFT
edge that ALLD then exploits.

![Mutation-driven cycling in the three-strategy Moran process.](../figures/moran_three.pdf){#fig:three width=95%}

*Eighteen strategies.* With the full tournament field and the same
protocol the answer is strikingly different:

{{table:moran_mutation}}

Cooperation *never* collapses, even at $\mu=0.3$ where nearly a third of all
births are random. The reason is that most of the strategy space is
reciprocating: a random mutant is far more likely to be a conditional
cooperator than an exploiter, and conditional cooperators earn $R$ against
one another. Mutation therefore spreads the population across the "nice"
cluster (which strategy happens to be most frequent is a matter of drift,
hence the changing leader) rather than out of it. The lesson is that the
robustness of cooperation to mutation is a property of the *distribution of
mutants*, not of the equilibrium itself.

## Spatial structure: Nowak and May's lattice

`pdlab.spatial` implements the weak dilemma on a square lattice with eight
neighbours, self-interaction, synchronous updating and periodic boundaries.
Sweeping $b$ from 1.05 to 1.99 from random 90% cooperator initial
conditions gives the phase diagram of @fig:phase (raw values in
@tbl:phase). The cooperator fraction is a staircase in $b$, because the
outcome of every local contest depends only on the comparison of integer
multiples of $b$ against integers. The four thresholds derived in Chapter 5
($9/8$, $7/5$, $8/5$, $9/5$) are among the step locations; the remaining
steps (near $1.2$, $1.32$, $1.52$, $1.68$ and $1.76$) come from other local
configurations, larger clusters and irregular boundaries, that Chapter 5
does not enumerate.

![Asymptotic cooperator fraction versus $b$.](../figures/spatial_phase.pdf){#fig:phase width=75%}

For $1.8 < b < 2$ our lattices settle into the "spatial chaos" regime with
$f_C = {{spatial.coop_1p8_2|.3f}}$ averaged over all $b$ in that interval and over seeds,
against the published value of $0.318$ [@nowakmay1992]. The
1% discrepancy is within the run-to-run fluctuation of $f_C$ (compare the
time series of @fig:series), and the value is independent of the
initial cooperator fraction, as the authors reported:

{{table:spatial_init}}

![Cooperator fraction over time for $b=1.9$; the dashed line is 0.318.](../figures/spatial_series.pdf){#fig:series width=65%}

Starting from a single defector in a sea of cooperators with fixed
boundaries reproduces Nowak and May's kaleidoscope (@fig:kal): the
defector cluster grows, cooperators re-invade along the diagonals where
they touch enough cooperators to out-score the defectors, and the
symmetric initial condition is preserved forever by the deterministic rule.

![Deterministic "evolutionary kaleidoscope" from a single defector, $b=1.9$, fixed boundary.](../figures/spatial_kaleidoscope.pdf){#fig:kal width=100%}

### Beyond: the update rule matters

Huberman and Glance [-@hubermanglance1993] objected that synchronous
updating is an artefact. Replacing it with random sequential updating
(one site at a time, scores recomputed from the current lattice) at
$b = 1.9$ destroys cooperation almost completely: after
{{scale.async_steps}} sweeps the cooperator fraction is
{{spatial.sync_vs_async.async[-1]|.3f}} under asynchronous updating against
{{spatial.sync_vs_async.sync[-1]|.3f}} under synchronous updating from the
same initial lattice (@fig:async). Spatial cooperation in the weak
dilemma at large $b$ is therefore a property of the *joint* choice of
payoffs and update rule; the smaller-$b$ steps of the phase diagram
survive asynchrony (Nowak, Bonhoeffer and May [-@nowakbonhoeffermay1994] give the fuller picture).

![Synchronous versus asynchronous updating from the same initial condition, $b=1.9$.](../figures/spatial_sync_async.pdf){#fig:async width=65%}

{{table:spatial_phase}}

Table: Phase-diagram data behind @fig:phase. {#tbl:phase}
