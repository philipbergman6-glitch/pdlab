# Original contribution: noise, exact Markov analysis, and extortion against learners

The theory of Chapter 4 assumes that intended moves are executed
perfectly. Real players tremble: a soldier fails to hold fire, a firm's
price cut is a clerical error, a bacterium's toxin gene misfires. This
chapter treats implementation error exactly, then turns to a second
departure from the classical setting, opponents who *learn*, and asks
whether Press and Dyson's extortionate strategies really do "enslave"
adaptive players.

## Memory-one strategies as a Markov chain

Let $p = (p_{CC}, p_{CD}, p_{DC}, p_{DD})$ and $q$ be the cooperation
probabilities of players $X$ and $Y$ conditional on the previous outcome
(each written from the player's own perspective, so $Y$'s vector must be
read in the order $CC, DC, CD, DD$ when $X$'s state labels are used). An
implementation error that flips each intended move independently with
probability $\varepsilon$ replaces every probability $p$ by
$$\tilde p = (1-\varepsilon)\,p + \varepsilon\,(1-p) = (1-2\varepsilon)\,p + \varepsilon .$$
The outcome sequence is a Markov chain on $\{CC, CD, DC, DD\}$ with
transition matrix $M_{s s'} = \tilde p_s^{\,x'} \tilde q_s^{\,y'}$ (with the
obvious complements for $D$). For $\varepsilon>0$ every entry of $M$ is
strictly positive, so the chain is irreducible and aperiodic and has a
unique stationary distribution $v$; the long-run payoffs are
$s_X = v \cdot S_X$ and $s_Y = v \cdot S_Y$ with $S_X = (R,S,T,P)$ and
$S_Y = (R,T,S,P)$. `pdlab.markov` computes $v$ numerically;
`pdlab.analytic.stationary_payoffs_symbolic` computes it *symbolically* in
$(T,R,P,S,\varepsilon)$ with `sympy`.

**Proposition 7.1 (Exact self-play payoffs under noise).** Let
$(T,R,P,S)$ be a strict PD and $\varepsilon \in (0, \tfrac12]$. The self-play
payoff per round of

1. TFT is $\dfrac{T+R+P+S}{4}$, *independent of* $\varepsilon$;
2. WSLS is $R - (4R - 2P - T - S)\,\varepsilon + O(\varepsilon^2)$;
3. ALLC is $R - (R-S)\,\varepsilon + O(\varepsilon^2)$ and ALLD is $P + (T+S-2P)\,\varepsilon + O(\varepsilon^2)$;
4. GTFT with forgiveness $g = 1/3$ is, for $(5,3,1,0)$,
   $\dfrac{3 + 21\varepsilon + 27\varepsilon^2}{(1+4\varepsilon)^2}
   = \dfrac{3(1 + 7\varepsilon + 9\varepsilon^2)}{(1+4\varepsilon)^2} = 3 - 3\varepsilon + 3\varepsilon^2 + O(\varepsilon^3)$.

*Proof.* (1) Write $a = 1-\varepsilon$. In $X$'s state order $(CC, CD, DC, DD)$ the
noisy TFT rule gives $X$ the cooperation probabilities
$\tilde p = (a, \varepsilon, a, \varepsilon)$ (cooperate iff the opponent
cooperated) and gives $Y$ the probabilities $\tilde q = (a, a, \varepsilon, \varepsilon)$
(cooperate iff $X$ cooperated). As $s$ runs over the four states the pair
$(\tilde p_s, \tilde q_s)$ runs over all four elements of $\{a, \varepsilon\}^2$ exactly
once. Hence for every target state $s'$ the column sum
$\sum_s M_{ss'} = \sum_s \tilde p_s^{\,x'}(1-\tilde p_s)^{1-x'} \tilde q_s^{\,y'}(1-\tilde q_s)^{1-y'}$
factorises as $(a + \varepsilon)(a + \varepsilon) = 1$: the chain is doubly
stochastic, so the uniform vector is stationary, and since the chain is
irreducible for $\varepsilon > 0$ it is the unique stationary distribution.
Therefore $s_X = \tfrac14 (R + S + T + P)$. Items (2)–(4) are direct symbolic
computation (`self_play_noise_symbolic` in `pdlab.analytic` solves $vM = v$
with `sympy`; the exact rational functions are stored in
`results/canonical.json` and checked by the test-suite), followed by a
Taylor expansion at $\varepsilon = 0$. $\square$

Item (1) is the sharpest possible statement of TFT's fragility: the limit
$\varepsilon \to 0$ of the noisy payoff, $9/4$, is *not* the noiseless
payoff $R = 3$. TFT self-play is discontinuous in the noise level. The
generous strategies, by contrast, degrade linearly, with slopes that rank
them: ALLC ($-1$), GTFT ($-3$), WSLS ($-5$), ZDGTFT-2 ($-8$) for
Axelrod's payoffs. Table @tbl:noise lists the expansions and the exact
values at two noise levels; Figure @fig:noise compares the exact curves
with simulated matches of {{scale.noise_sim_rounds}} rounds.

{{table:noise_selfplay}}

Table: Exact self-play payoffs under implementation error. {#tbl:noise}

![Self-play payoff versus error rate: lines are exact stationary payoffs, dots are simulations.](../figures/noise_selfplay.pdf){#fig:noise width=80%}

### Which strategy survives selection under noise?

Self-play payoffs decide who wins once a strategy has taken over, but not
who takes over. To answer that we ran the full {{tournament.payoff_matrix.names|len}}-strategy
tournament at seven noise levels, used each resulting payoff matrix as
the fitness landscape of a Moran process ($N = {{scale.moran_n}}$,
$\mu = 0.01$, {{scale.moran_steps}} events) and recorded the
time-averaged frequencies:

{{table:evolution_noise}}

Table: Strategies favoured by selection as implementation error rises. {#tbl:evonoise}

Without noise the strict reciprocators (TFT, Grim) hold the population.
For small positive error rates the leader is decided by drift among the
forgiving strategies (generous ZD, GTFT, Gradual), a consequence of their
near-equal payoffs against one another. From $\varepsilon = 0.05$ upwards
the picture is unambiguous: *contrite* TFT dominates at every noise level,
with the history-averaging majority rule SOFTMAJ second. CTFT's advantage
is exactly the mechanism of Chapter 4: it accepts one round of punishment
for its own error instead of echoing it, so its self-play payoff stays near
$R$ while TFT's collapses to $(T+R+P+S)/4$. (An earlier version of the code
cleared contrition one round too early, which delayed rather than broke
the echo; with that bug CTFT fell to mid-table under noise and the generous
strategies led. The test-suite now pins the correct standing dynamics.)
This is the evolutionary counterpart of Proposition 7.1: selection under
noise rewards error-correction first and generosity second
(Figure @fig:evonoise).

![Time-averaged strategy frequencies in the Moran process at increasing noise.](../figures/evolution_noise.pdf){#fig:evonoise width=85%}

## Zero-determinant strategies

Press and Dyson [-@pressdyson2012] discovered that a memory-one player
can *unilaterally* enforce a linear relation between the two long-run
payoffs. Writing $\tilde p = (p_{CC}-1, p_{CD}-1, p_{DC}, p_{DD})$, if
$$\tilde p = \alpha S_X + \beta S_Y + \gamma \mathbf 1$$
then $\alpha s_X + \beta s_Y + \gamma = 0$ for *every* opponent $q$ (the
proof uses the determinant formula $s = D(p,q,S)/D(p,q,\mathbf 1)$, in
which the column $\tilde p$ appears; `pdlab.markov.press_dyson_payoffs`
implements it and the test-suite verifies it against the stationary
distribution to $10^{-9}$). Two families matter here.

*Extortion.* Choosing $\alpha = \phi$, $\beta = -\phi\chi$,
$\gamma = \phi(\chi-1)P$ with $\chi > 1$ enforces
$s_X - P = \chi\,(s_Y - P)$: the extortioner's surplus over mutual
defection is always $\chi$ times the opponent's. For $(5,3,1,0)$,
$\chi = 2$ and $\phi = 1/18$ this is Extort-2 $= ({{zd.extort2[0]|.4f}}, {{zd.extort2[1]|.4g}}, {{zd.extort2[2]|.4f}}, {{zd.extort2[3]|.4g}})$,
the vector published by Stewart and Plotkin [-@stewartplotkin2012] and
identical to the one in the `axelrod` library. The exact payoffs against every
memory-one strategy of the tournament field confirm the relation:

{{table:zd_named}}

Table: Extort-2 against named strategies (exact stationary payoffs, $\varepsilon = 0.01$ to make every chain irreducible). {#tbl:zdnamed}

![Extort-2 confines every opponent to the line $s_X - 1 = 2(s_Y - 1)$.](../figures/zd_scatter.pdf){#fig:zdscatter width=65%}

*Generosity.* The same construction with baseline $R$ instead of $P$
enforces $s_X - R = \chi\,(s_Y - R)$: the generous player's *shortfall*
from $R$ is $\chi$ times the opponent's, so it always earns *less* than
its opponent but pulls both towards $R$. With $\chi = 2$ and the largest
feasible $\phi$ this is ZDGTFT-2 $= ({{zd.zdgtft2[0]|.4g}}, {{zd.zdgtft2[1]|.4g}}, {{zd.zdgtft2[2]|.4g}}, {{zd.zdgtft2[3]|.4g}})$ [@stewartplotkin2012].

### Extortion against an adaptive opponent

Press and Dyson's most provocative claim is that against an
*evolutionary* opponent, one that adjusts its own strategy to increase
its own payoff, the extortioner obtains the maximum of its enforced line,
because the opponent's best response is to cooperate fully. We test this
with a tabular Q-learner whose state is the last joint outcome
($\alpha = 0.05$, $\gamma = 0.9$, $\varepsilon$-greedy exploration decaying
from $0.2$ by a factor $0.9997$ per round), playing {{scale.learner_rounds}}
rounds against Extort-2, ZDGTFT-2 and TFT for {{scale.learner_seeds}} seeds
each. Table @tbl:learner reports the mean payoffs over the final fifth of
each match.

{{table:learner}}

Table: A Q-learner against zero-determinant and reciprocal opponents (final 20% of {{scale.learner_rounds}} rounds). {#tbl:learner}

![Payoffs per round of the learner and its opponent (moving averages), {{scale.learner_seeds}} seeds per panel.](../figures/zd_learner.pdf){#fig:learner width=100%}

Three conclusions. First, the learner is indeed exploited: against
Extort-2 it ends near $2$ per round while the extortioner collects about
$3$, and every terminal pair lies on the extortion line to within
simulation error. Second, the learner does *not* reach the full
cooperation that would maximise its own payoff ($s_Y = 2.25$ against
Extort-2), because a memory-one Q-learner with a discount factor of $0.9$
sees the immediate temptation payoff clearly and the delayed cost only
dimly; Press and Dyson's argument assumes an opponent that optimises
its *long-run* score, and the gap between that idealisation and an actual
learning rule is worth about $0.25$ per round. Third, generosity is
rewarded: against ZDGTFT-2 and TFT the learner discovers mutual
cooperation in most runs (payoff $3$ for both), and where it does not it
falls into a suboptimal alternating pattern rather than into exploitation.

### Extortion in a population

Extortion wins every pairwise contest but, as the tournament of Chapter 6
already showed, loses the field. Its evolutionary fate among memory-one
strategies is decided by self-play: Extort-2 against itself earns only
$P + 18\varepsilon + O(\varepsilon^2)$ (Table @tbl:noise), essentially
mutual defection, so it cannot hold a population it has conquered.
Replicator dynamics among seven memory-one strategies with exact payoffs
at $\varepsilon = 0.01$, and a Moran process with mutation on the same
matrix, give:

{{table:zd_evolution}}

Table: Evolution among memory-one strategies at $\varepsilon = 0.01$. {#tbl:zdevo}

![Replicator trajectories among memory-one strategies at $\varepsilon = 0.01$.](../figures/zd_evolution.pdf){#fig:zdevo width=75%}

The deterministic dynamics converge to WSLS, the error-correcting strategy
of Nowak and Sigmund [-@nowaksigmund1993]; the stochastic process with
mutation spends most of its time in ZDGTFT-2 and WSLS. Extort-2 goes
extinct in both, in agreement with Hilbe, Nowak and Sigmund
[-@hilbenowaksigmund2013] and Adami and Hintze [-@adamihintze2013]: extortion can
act as a catalyst for cooperation but is never its end state.

## Summary of the contribution

The exact Markov-chain treatment turns "TFT is fragile under noise" into a
theorem with a striking form (a payoff discontinuous at $\varepsilon = 0$)
and ranks the classical repairs by the slope of their payoff in
$\varepsilon$; the evolutionary experiment shows selection acting on
exactly that ranking. The learning experiment confirms Press and Dyson's
extortion result qualitatively while quantifying the gap between an
idealised adaptive opponent and a real learning rule. All of it is
reproducible from `make reproduce`.
