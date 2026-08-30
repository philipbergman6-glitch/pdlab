# The Infinitely Repeated Game

## Discounting and strategies

**Definition 4.1 (The discounted supergame).** Fix a stage Prisoner's Dilemma $G$ and a *discount factor* $\delta \in [0,1)$. The supergame $G^\infty(\delta)$ is played in rounds $t = 0,1,2,\dots$ with perfect monitoring. Histories, subgames and (behaviour) strategies are defined as in Definitions 3.1--3.2, with $H = \bigcup_{t \ge 0} A^t$ now infinite. Given a strategy profile $s = (s_1,s_2)$ inducing the (random) action path $(a^t)_{t \ge 0}$, define the *unnormalised* and *normalised* discounted payoffs
$$
\widetilde U_i(s) \;=\; \mathbb{E}\Bigl[\sum_{t=0}^{\infty} \delta^{t}\, u_i(a^t)\Bigr],
\qquad
U_i(s) \;=\; (1-\delta)\,\widetilde U_i(s). \tag{4.1}
$$
Both series converge absolutely because stage payoffs are bounded by $\max\{|T|,|S|\}$ and $\delta < 1$.

The two conventions differ by the positive constant $1-\delta$ and therefore induce identical preferences, best responses and equilibria. The normalised version has the advantage that a constant stream $\pi$ is worth exactly $\pi$, which makes payoffs comparable across $\delta$ and puts them in the same units as the stage game; we use it whenever payoffs of different strategy pairs are compared (Chapter 5 and all payoff matrices), and the unnormalised version inside deviation calculations, where expressions such as $R/(1-\delta)$ are cleaner. Every threshold in this chapter is invariant to the choice.

**Remark 4.2 (Two readings of $\delta$).** Algebraically, $\delta$ is a discount factor: a payoff received one round later is worth $\delta$ times as much. Behaviourally, it is a *continuation probability*: if after each round the interaction ends with probability $1-\delta$ and continues with probability $\delta$, then the expected number of rounds in which round $t$'s payoff is actually collected is $\delta^t$, and expected total payoff is exactly $\widetilde U_i$. The expected length of the interaction is $\sum_{t \ge 0}\delta^t = 1/(1-\delta)$. Under this reading, $\delta$ measures "the shadow of the future'' [@axelrod1984] --- how likely the players are to meet again --- and thresholds of the form $\delta \ge \delta^*$ read as *cooperation requires a sufficiently long expected relationship*.

**Theorem 4.3 (One-shot deviation principle, infinite horizon).** Let $\delta \in [0,1)$. A strategy profile $s^*$ of $G^\infty(\delta)$ is a subgame-perfect equilibrium if and only if no player has a profitable one-shot deviation at any history $h \in H$.

*Proof (sketch; [@fudenbergtirole1991, Thm. 4.2], [@osbornerubinstein1994, Lemma 98.2]).* Necessity is trivial. For sufficiency the finite-horizon argument of Theorem 3.3 is supplemented by *continuity at infinity*: the payoff function (4.1) satisfies
$$
\sup_{s,\,s' :\, s \text{ and } s' \text{ agree in rounds } 0,\dots,\tau-1} \bigl|\widetilde U_i(s) - \widetilde U_i(s')\bigr| \;\le\; \frac{\delta^{\tau}}{1-\delta}\,\bigl(\max_a u_i(a) - \min_a u_i(a)\bigr) \;\xrightarrow[\tau \to \infty]{}\; 0,
$$
because stage payoffs are bounded and $\delta < 1$. Suppose $\hat s_i$ improves on $s_i^*$ in the subgame after $h$ by $\eta > 0$. Choose $\tau$ with the bound above smaller than $\eta$, and let $\hat s_i^\tau$ agree with $\hat s_i$ for the first $\tau$ rounds after $h$ and with $s_i^*$ thereafter; then $\hat s_i^\tau$ still improves on $s_i^*$ by at least $\eta$ minus that bound, hence strictly. But $\hat s_i^\tau$ differs from $s_i^*$ at finitely many rounds, so the backward-unwinding argument of Theorem 3.3 applies verbatim and produces a profitable one-shot deviation, a contradiction. $\square$

Without continuity at infinity the principle is false; it is the discounting, not the repetition, that makes local checking sufficient.

## Grim Trigger

**Definition 4.4 (Grim Trigger).** The strategy $\mathrm{GRIM}$ plays $C$ at the empty history and at every history in which the realised profile was $(C,C)$ in every past round; it plays $D$ at every other history. Equivalently: cooperate until someone defects, then defect forever.

$\mathrm{GRIM}$ partitions histories into two *phases*: the *cooperative phase*, consisting of histories in which $(C,C)$ occurred in all past rounds, and the *punishment phase*, all other histories. The phase is common knowledge under perfect monitoring, and once entered the punishment phase is absorbing.

**Theorem 4.5 (Grim Trigger).** $(\mathrm{GRIM}, \mathrm{GRIM})$ is a subgame-perfect equilibrium of $G^\infty(\delta)$ if and only if
$$
\delta \;\ge\; \delta^{\mathrm{G}} \;:=\; \frac{T-R}{T-P}. \tag{4.2}
$$
For Axelrod's $(T,R,P,S)=(5,3,1,0)$, $\delta^{\mathrm{G}} = 2/4 = 1/2$.

*Proof.* By Theorem 4.3 it suffices to check one-shot deviations at every history; by symmetry we check them for player 1, and by the phase structure there are exactly two cases.

*Cooperative phase.* Let $h$ be a history in the cooperative phase. Conforming, both players cooperate forever, giving
$$
\widetilde U_1(\text{conform}) \;=\; \sum_{t \ge 0}\delta^t R \;=\; \frac{R}{1-\delta}.
$$
The one-shot deviation is to play $D$ now and revert to $\mathrm{GRIM}$ afterwards. This yields $T$ this round; the resulting history lies in the punishment phase for both players, so from the next round both play $D$ forever, giving $P$ per round:
$$
\widetilde U_1(\text{deviate}) \;=\; T + \sum_{t \ge 1}\delta^t P \;=\; T + \frac{\delta P}{1-\delta}.
$$
No profitable deviation therefore requires
$$
\frac{R}{1-\delta} \;\ge\; T + \frac{\delta P}{1-\delta}
\iff R \;\ge\; (1-\delta)T + \delta P
\iff \delta\,(T-P) \;\ge\; T-R
\iff \delta \ge \frac{T-R}{T-P},
$$
using $T > P$ so that the division preserves the inequality. Deviating to $C$ is not a deviation at all, since $\mathrm{GRIM}$ prescribes $C$ here.

*Punishment phase.* Let $h$ be a history in the punishment phase. Both continuation strategies prescribe $D$ unconditionally --- the punishment phase is absorbing, so no future history leaves it --- and the continuation payoff is $P/(1-\delta)$. The one-shot deviation to $C$ yields $S$ this round, after which both again play $D$ forever:
$$
S + \frac{\delta P}{1-\delta} \;<\; P + \frac{\delta P}{1-\delta} \;=\; \frac{P}{1-\delta},
$$
strictly, because $S < P$. So the deviation is strictly unprofitable, for every $\delta \in [0,1)$; no condition arises. (This is the substantive content of subgame perfection here: the threat is credible because carrying it out is itself an equilibrium, $\mathrm{ALLD}$ being a stage best reply to $\mathrm{ALLD}$.)

Both cases are covered, so by Theorem 4.3 the profile is an SPE precisely when (4.2) holds; and if (4.2) fails the cooperative-phase deviation is strictly profitable, so the profile is not even a Nash equilibrium. $\square$

The threshold is computed symbolically by `analytic.grim_threshold_symbolic()`, which returns $(T-R)/(T-P)$.

## Tit for Tat

**Definition 4.6 (Tit for Tat).** The strategy $\mathrm{TFT}$ plays $C$ at the empty history, and at a history $h^t = (a^0,\dots,a^{t-1})$ plays the opponent's previous action $a^{t-1}_{-i}$.

$\mathrm{TFT}$ is *nice* (never the first to defect), *retaliatory*, *forgiving* (a single cooperation restores cooperation) and *clear*. It won both of Axelrod's tournaments [@axelrod1984]. The following is Axelrod's Proposition 2 (his "collective stability'' of $\mathrm{TFT}$), stated as a Nash-equilibrium condition. The difficulty in proving it honestly is the phrase *all deviations*: the deviating player has a continuum of behaviour strategies. The resolution is that against $\mathrm{TFT}$ the problem is a two-state Markov decision process.

**Lemma 4.7 (The best reply to TFT).** Fix $\delta \in [0,1)$ and suppose player 2 plays $\mathrm{TFT}$. Then player 1's optimisation problem is a discounted Markov decision process with state space $\Theta = \{\theta_C, \theta_D\}$ --- $\theta_x$ meaning "the opponent plays $x$ this round'' --- action space $\{C,D\}$, deterministic transition $\theta \mapsto \theta_{a}$ upon choosing $a$, reward $u_1(a,x)$ in state $\theta_x$, and initial state $\theta_C$. Its optimal values $V_C, V_D$ (unnormalised) satisfy the Bellman equations
$$
V_C = \max\{\,R + \delta V_C,\; T + \delta V_D\,\}, \qquad
V_D = \max\{\,S + \delta V_C,\; P + \delta V_D\,\}, \tag{4.3}
$$
and
$$
V_C \;=\; \max\Bigl\{\;\underbrace{\tfrac{R}{1-\delta}}_{\text{always } C},\;\;
\underbrace{T + \tfrac{\delta P}{1-\delta}}_{\text{always } D},\;\;
\underbrace{\tfrac{T + \delta S}{1-\delta^{2}}}_{\text{alternate } D,C,D,C,\dots}\;\Bigr\}. \tag{4.4}
$$

*Proof.* $\mathrm{TFT}$'s action in round $t \ge 1$ is player 1's action in round $t-1$, and its action in round $0$ is $C$. Hence the opponent's current action is a deterministic function of player 1's own previous action; taking that action as the state makes player 1's stage reward and transition depend on the current state and current action only, which is precisely a stationary MDP with the stated data. It has two states, two actions, bounded rewards and $\delta < 1$, so by standard discounted dynamic programming the Bellman operator is a $\delta$-contraction on $\mathbb{R}^\Theta$, $(V_C,V_D)$ is its unique fixed point, it equals the supremum of $\widetilde U_1$ over *all* strategies of player 1 (history-dependent and randomised included), and the supremum is attained by a deterministic stationary policy.

There are exactly four deterministic stationary policies $\pi : \Theta \to \{C,D\}$, and since transitions are deterministic each generates an eventually periodic payoff stream from $\theta_C$:

* $\pi(\theta_C)=C,\ \pi(\theta_D)=C$ (unconditional $C$): the state never leaves $\theta_C$; stream $R,R,R,\dots$; value $R/(1-\delta)$.
* $\pi(\theta_C)=C,\ \pi(\theta_D)=D$ ($\mathrm{TFT}$ itself): starting at $\theta_C$ the state never leaves $\theta_C$; stream $R,R,R,\dots$; value $R/(1-\delta)$.
* $\pi(\theta_C)=D,\ \pi(\theta_D)=D$ (unconditional $D$): stream $T,P,P,\dots$; value $T+\delta P/(1-\delta)$.
* $\pi(\theta_C)=D,\ \pi(\theta_D)=C$ ($\mathrm{ALT}$, "defect, then cooperate, then defect, ...''): the state alternates $\theta_C,\theta_D,\theta_C,\dots$; stream $T,S,T,S,\dots$; value $\sum_{k\ge 0}\delta^{2k}(T + \delta S) = (T+\delta S)/(1-\delta^{2})$.

Taking the maximum over the four values --- two of which coincide --- yields (4.4). $\square$

Lemma 4.7 is the precise sense in which "only two deviations matter'': the *only* candidate improvements on permanent cooperation are permanent defection and the alternating exploitation cycle.

**Theorem 4.8 (Axelrod's Proposition 2).** $(\mathrm{TFT},\mathrm{TFT})$ is a Nash equilibrium of $G^\infty(\delta)$ if and only if
$$
\delta \;\ge\; \delta^{\mathrm{TFT}} \;:=\; \max\Bigl\{\, \frac{T-R}{T-P},\; \frac{T-R}{R-S} \,\Bigr\}. \tag{4.5}
$$
For $(5,3,1,0)$: $\max\{2/4,\,2/3\} = 2/3$.

*Proof.* $(\mathrm{TFT},\mathrm{TFT})$ produces mutual cooperation in every round, so each player's equilibrium payoff is $R/(1-\delta)$. By symmetry, the profile is a Nash equilibrium iff no strategy of player 1 earns more than $R/(1-\delta)$ against $\mathrm{TFT}$, i.e. iff $V_C = R/(1-\delta)$ in Lemma 4.7. By (4.4) this holds iff $R/(1-\delta)$ dominates the other two candidates.

Against unconditional $D$:
$$
\frac{R}{1-\delta} \ge T + \frac{\delta P}{1-\delta}
\iff R \ge (1-\delta)T + \delta P
\iff \delta \ge \frac{T-R}{T-P}.
$$

Against $\mathrm{ALT}$: multiplying by $(1-\delta^{2}) = (1-\delta)(1+\delta) > 0$,
$$
\frac{R}{1-\delta} \ge \frac{T+\delta S}{1-\delta^{2}}
\iff R(1+\delta) \ge T + \delta S
\iff \delta\,(R-S) \ge T-R
\iff \delta \ge \frac{T-R}{R-S},
$$
using $R > S$. The conjunction of the two conditions is (4.5). $\square$

`analytic.tft_nash_threshold_symbolic()` returns exactly $\max\{(T-R)/(T-P),\,(T-R)/(R-S)\}$. Note that neither term dominates the other in general: the second exceeds the first iff $R - S < T - P$, i.e. iff $R + P < T + S$, which holds for $(5,3,1,0)$ ($4 < 5$) but fails for, say, $(5,4,3,0)$.

## Tit for Tat is not subgame perfect

Nash equilibrium tolerates incredible threats. $\mathrm{TFT}$ contains one.

Under $(\mathrm{TFT},\mathrm{TFT})$ the continuation play after a history depends only on the last realised profile, so there are four continuation regimes. Write them from player 1's point of view, with $\widetilde V(h)$ her unnormalised continuation payoff and $\widetilde V^{\mathrm{dev}}(h)$ her payoff from a one-shot deviation followed by a return to $\mathrm{TFT}$.

* **After $(C,C)$** (and at the empty history). Both play $C$: stream $R,R,\dots$, so $\widetilde V = R/(1-\delta)$. Deviating to $D$ gives $T$, then the players are in the "$(D,C)$'' regime below, which yields the alternating stream: $\widetilde V^{\mathrm{dev}} = T + \delta\,\frac{S+\delta T}{1-\delta^{2}} = \frac{T+\delta S}{1-\delta^{2}}$.
* **After $(C,D)$** (player 1 was cheated). $\mathrm{TFT}$ makes player 1 play $D$ and player 2 play $C$; thereafter the roles alternate: stream $T,S,T,S,\dots$, so $\widetilde V = (T+\delta S)/(1-\delta^{2})$. Deviating to $C$ produces $(C,C)$ and thus permanent mutual cooperation: $\widetilde V^{\mathrm{dev}} = R/(1-\delta)$.
* **After $(D,C)$** (player 1 cheated). Player 1 plays $C$, player 2 plays $D$: stream $S,T,S,T,\dots$, so $\widetilde V = (S+\delta T)/(1-\delta^{2})$. Deviating to $D$ produces $(D,D)$ and thus permanent mutual defection: $\widetilde V^{\mathrm{dev}} = P/(1-\delta)$.
* **After $(D,D)$**. Both play $D$ forever: $\widetilde V = P/(1-\delta)$. Deviating to $C$ produces $(C,D)$, then $(D,C)$, then $(C,D)$, ...: $\widetilde V^{\mathrm{dev}} = (S+\delta T)/(1-\delta^{2})$.

**Theorem 4.9 (Knife-edge subgame perfection).** $(\mathrm{TFT},\mathrm{TFT})$ is a subgame-perfect equilibrium of $G^\infty(\delta)$ if and only if
$$
\delta \;=\; \frac{T-R}{R-S} \;=\; \frac{P-S}{T-P}. \tag{4.6}
$$
In particular, for generic payoffs satisfying (2.1)--(2.2) there is *no* $\delta \in [0,1)$ for which $(\mathrm{TFT},\mathrm{TFT})$ is subgame perfect; for Axelrod's $(5,3,1,0)$ the two required values are $2/3$ and $1/4$, so $(\mathrm{TFT},\mathrm{TFT})$ is never subgame perfect.

*Proof.* By Theorem 4.3 we require $\widetilde V(h) \ge \widetilde V^{\mathrm{dev}}(h)$ in each of the four regimes above; by the symmetry of the profile these four conditions, applied to player 1, exhaust all histories and both players. Throughout, $(1-\delta) > 0$ and $(1-\delta^{2}) > 0$, so multiplying through is legitimate.

*After $(C,C)$:* $\dfrac{R}{1-\delta} \ge \dfrac{T+\delta S}{1-\delta^{2}} \iff R(1+\delta) \ge T + \delta S \iff \delta \ge \dfrac{T-R}{R-S}$.

*After $(C,D)$:* $\dfrac{T+\delta S}{1-\delta^{2}} \ge \dfrac{R}{1-\delta} \iff T + \delta S \ge R(1+\delta) \iff \delta \le \dfrac{T-R}{R-S}$.

*After $(D,C)$:* $\dfrac{S+\delta T}{1-\delta^{2}} \ge \dfrac{P}{1-\delta} \iff S + \delta T \ge P(1+\delta) \iff \delta\,(T-P) \ge P-S \iff \delta \ge \dfrac{P-S}{T-P}$.

*After $(D,D)$:* $\dfrac{P}{1-\delta} \ge \dfrac{S+\delta T}{1-\delta^{2}} \iff P(1+\delta) \ge S + \delta T \iff \delta \le \dfrac{P-S}{T-P}$.

The first two conditions hold simultaneously iff $\delta = (T-R)/(R-S)$; the last two iff $\delta = (P-S)/(T-P)$. Both pairs must hold, giving (4.6). Conversely, if (4.6) holds then all four inequalities hold with equality, no one-shot deviation is strictly profitable, and Theorem 4.3 gives subgame perfection. Since (4.6) imposes one equation on the three-dimensional projective space of payoff parameters, it fails on an open dense set of admissible $(T,R,P,S)$. For $(5,3,1,0)$: $(T-R)/(R-S) = 2/3$ and $(P-S)/(T-P) = 1/4$, which are unequal. $\square$

The two obstructions have distinct interpretations. The pair "after $(C,C)$ / after $(C,D)$'' says that $\mathrm{TFT}$'s retaliation must be *exactly* worth it: if $\delta > (T-R)/(R-S)$, punishing a defection by defecting locks the pair into the costly alternating cycle when immediate forgiveness would restore $R$ forever, so the threat is not credible. The pair "after $(D,C)$ / after $(D,D)$'' says the same about $\mathrm{TFT}$'s behaviour in mutual defection: with $\delta > (P-S)/(T-P)$ a player should offer an olive branch, absorbing $S$ once to escape the $P$-forever trap, so unconditional continuation of the feud is not credible either.

The numbers for $(5,3,1,0)$ are collected in Table 4.1; the conditions are generated by `analytic.tft_spe_conditions_symbolic()` and evaluated by `analytic.thresholds()`.

| Last profile | $\widetilde V$ (follow TFT) | $\widetilde V^{\mathrm{dev}}$ (one-shot deviation) | TFT optimal iff | at $\delta=2/3$ |
|:--|:--|:--|:--|:--|
| $(C,C)$ | $\frac{R}{1-\delta}=9$ | $\frac{T+\delta S}{1-\delta^{2}}=9$ | $\delta \ge \frac{T-R}{R-S} = \frac23$ | holds (tie) |
| $(C,D)$ | $\frac{T+\delta S}{1-\delta^{2}}=9$ | $\frac{R}{1-\delta}=9$ | $\delta \le \frac{T-R}{R-S} = \frac23$ | holds (tie) |
| $(D,C)$ | $\frac{S+\delta T}{1-\delta^{2}}=6$ | $\frac{P}{1-\delta}=3$ | $\delta \ge \frac{P-S}{T-P} = \frac14$ | holds |
| $(D,D)$ | $\frac{P}{1-\delta}=3$ | $\frac{S+\delta T}{1-\delta^{2}}=6$ | $\delta \le \frac{P-S}{T-P} = \frac14$ | **fails** |

Table: **Table 4.1.** One-shot-deviation checks for $(\mathrm{TFT},\mathrm{TFT})$ under $(T,R,P,S)=(5,3,1,0)$. Numerical values are unnormalised continuation payoffs at $\delta = 2/3$, the smallest $\delta$ satisfying the on-path condition.

**Remark 4.10 (Grim is perfect but brittle).** Theorems 4.5 and 4.9 pull in opposite directions. $\mathrm{GRIM}$ is subgame perfect for all $\delta \ge 1/2$, because its punishment is a stage equilibrium and hence self-enforcing; but the same absorbing punishment makes it catastrophic under noise: a single implementation error $\varepsilon$ (Chapter 6) sends a $\mathrm{GRIM}$ pair into permanent mutual defection, so its long-run payoff per round is close to $P$ for every $\varepsilon > 0$ (exactly $1.0397$ at $\varepsilon = 0.01$ under $(5,3,1,0)$). $\mathrm{TFT}$ is forgiving but, as Theorem 4.9 shows, its threat is not credible --- and under noise a $\mathrm{TFT}$ pair falls into an echo of alternating recriminations. As a memory-one vector $\mathrm{TFT}$ is $(p_{CC},p_{CD},p_{DC},p_{DD}) = (1,0,1,0)$, and the induced chain on $(CC,CD,DC,DD)$ has, for *every* $\varepsilon \in (0,\tfrac12]$, the uniform stationary distribution $(\tfrac14,\tfrac14,\tfrac14,\tfrac14)$; the long-run payoff is therefore $(R+S+T+P)/4$, which is $2.25$ for $(5,3,1,0)$ rather than $R = 3$, no matter how small the error rate [@molander1985].

Two classical repairs, used later in the numerical chapters, address exactly this. *Contrite TIT FOR TAT* [@boerlijstnowaksigmund1997] augments $\mathrm{TFT}$ with a standing label: a player who defects while the opponent is in good standing loses her own good standing, and a player in bad standing accepts one round of punishment without retaliating. A defection caused by error is thus atoned for in a single round instead of echoing, which makes the pair error-correcting while retaining $\mathrm{TFT}$'s resistance to deliberate exploitation. *Win-Stay, Lose-Shift* (Pavlov) [@nowaksigmund1993] repeats its previous action after the two high payoffs $T$ and $R$ and switches after $S$ and $P$; as a memory-one vector it is $(p_{CC},p_{CD},p_{DC},p_{DD}) = (1,0,0,1)$, and a single error in a WSLS pair is corrected within two rounds. We state these without proof here; their stationary payoffs under noise are computed exactly in Chapter 6 via the four-state Markov chain of `pdlab.markov`.

## The folk theorems

**Definition 4.11 (Feasible set).** The *feasible payoff set* of the repeated game is
$$
V \;=\; \operatorname{conv}\bigl\{(R,R),\,(S,T),\,(T,S),\,(P,P)\bigr\} \subset \mathbb{R}^{2},
$$
as in (2.3). Every normalised discounted payoff pair $(U_1(s),U_2(s))$ lies in $V$, being a convex combination (with weights $(1-\delta)\delta^t$) of stage payoff vectors; conversely, with a public randomisation device every point of $V$ is attainable, and without one every point of $V$ is attainable in the limit $\delta \to 1$.

**Lemma 4.12 (Full dimensionality).** $V$ has non-empty interior in $\mathbb{R}^2$.

*Proof.* The three points $(R,R)$, $(T,S)$, $(S,T)$ are affinely independent: the determinant of the matrix with rows $(T,S)-(R,R) = (T-R,\,S-R)$ and $(S,T)-(R,R) = (S-R,\,T-R)$ equals $(T-R)^2 - (S-R)^2 = (T-S)\,(T+S-2R)$, which is non-zero because $T > S$ and, by (2.2), $T+S-2R < 0$. Hence $V$ contains a non-degenerate triangle. $\square$

Thus the additivity condition (2.2), introduced in Remark 2.3 to make $(C,C)$ efficient, is exactly what guarantees the full-dimensionality hypothesis of the subgame-perfect folk theorem.

**Definition 4.13 (Minmax and individual rationality).** Player $i$'s *(pure-action) minmax payoff* in the stage game is
$$
\underline{v}_i \;=\; \min_{a_{-i} \in A_{-i}} \; \max_{a_i \in A_i} \; u_i(a_i, a_{-i}).
$$
A payoff vector $v$ is *individually rational* if $v_i \ge \underline{v}_i$ for both $i$, and *strictly individually rational* if $v_i > \underline{v}_i$ for both. Write $V^{*} = \{v \in V : v_i > \underline{v}_i,\ i=1,2\}$.

**Proposition 4.14 (Minmax of the Prisoner's Dilemma).** $\underline{v}_1 = \underline{v}_2 = P$, and the minmaxing action is $D$. The same value obtains if the minimum is taken over mixed strategies of the opponent.

*Proof.* $\max_{a_1} u_1(a_1,C) = \max\{R,T\} = T$ and $\max_{a_1} u_1(a_1,D) = \max\{S,P\} = P$; the minimum of $\{T,P\}$ is $P$ since $T > P$. For mixed $\sigma_2$ with $\sigma_2(C) = r$, $\max_{a_1}u_1(a_1,\sigma_2) \ge u_1(D,\sigma_2) = rT + (1-r)P \ge P$, with equality at $r=0$; so the mixed minmax is also $P$. $\square$

Consequently $V^{*}$ is the set of feasible payoff pairs giving both players strictly more than mutual defection --- the shaded region of Figure @fig:folk. It is non-empty (it contains $(R,R)$) and, by Lemma 4.12, two-dimensional.

![Feasible and individually rational payoff set for (5,3,1,0).](../figures/folk_theorem.pdf){#fig:folk width=70%}

**Theorem 4.15 (Nash-threats folk theorem; Friedman 1971).** Let $e = (P,P)$ be the payoff of the unique stage Nash equilibrium, and let $v \in V$ satisfy $v_i > P$ for $i=1,2$. Then there exists $\bar\delta \in [0,1)$ such that for every $\delta \in (\bar\delta, 1)$ the supergame $G^\infty(\delta)$ --- extended by a public randomisation device if $v$ is not a stage payoff vector --- has a subgame-perfect equilibrium with normalised payoff vector $v$ [@friedman1971].

*Proof sketch (the Friedman construction).* Let $\alpha$ be a (possibly randomised) sequence or public lottery over action profiles whose normalised discounted payoff is $v$. Consider the trigger profile: play $\alpha$ as long as no player has deviated from $\alpha$; after any deviation, play $D$ forever. Since $(D,D)$ is a stage Nash equilibrium, the punishment phase is absorbing and prescribes a stage equilibrium at every history, so no one-shot deviation is profitable there (as in the punishment case of Theorem 4.5). Set $M := \max_{i,a} u_i(a) - \min_{i,a} u_i(a) < \infty$. In unnormalised terms a one-shot deviation in the cooperative phase gains at most $M$ in the current round and forfeits, from the next round on, a continuation stream worth $v_i$ per round in favour of one worth $P$ per round, a loss of at least $\frac{\delta}{1-\delta}\,\min_i (v_i - P) > 0$. Since $\min_i(v_i - P) > 0$ is fixed and $\delta/(1-\delta) \to \infty$ as $\delta \to 1$, there is $\bar\delta < 1$ beyond which the loss exceeds the gain at every history in the cooperative phase. Theorem 4.3 then yields subgame perfection. $\square$

Friedman's theorem delivers everything strictly above the *stage-equilibrium* payoff. For the Prisoner's Dilemma this happens to coincide with everything strictly above the minmax, because $\underline{v}_i = P$ is itself a stage equilibrium payoff --- a coincidence special to this game. In general the two differ, and closing the gap requires punishments harsher than a stage equilibrium, together with rewards for punishers who would otherwise refuse to punish.

**Theorem 4.16 (Subgame-perfect folk theorem; Fudenberg and Maskin 1986).** Let $G$ be a finite $n$-player stage game whose feasible set $V \subset \mathbb{R}^n$ has full dimension $n$. Then for every $v \in V$ with $v_i > \underline{v}_i$ for all $i$ there exists $\bar\delta \in [0,1)$ such that for all $\delta \in (\bar\delta,1)$ the discounted supergame has a subgame-perfect equilibrium with normalised payoff vector $v$ [@fudenbergmaskin1986].

Full dimensionality is used to construct, for each player $i$, a continuation payoff vector that rewards the other players $j \ne i$ for carrying out $i$'s punishment while still leaving $i$ punished --- impossible if the feasible set is degenerate, for instance in a zero-sum game. Fudenberg and Maskin also show that for $n = 2$ the dimensionality hypothesis can be dispensed with. For the Prisoner's Dilemma, Lemma 4.12 shows the hypothesis holds anyway, and Proposition 4.14 identifies $V^{*}$ concretely: for $(5,3,1,0)$, every payoff pair in the quadrilateral with vertices $(3,3),(0,5),(5,0),(1,1)$ that gives both players strictly more than $1$ is a subgame-perfect equilibrium payoff for $\delta$ close enough to $1$.

**Remark 4.17 (What the folk theorems do and do not say).** They say that patience makes cooperation *possible*, not that it makes cooperation *predicted*: for $\delta$ near $1$ the equilibrium set is enormous, containing mutual defection, mutual cooperation, and every asymmetric split in between. Equilibrium selection is therefore left entirely open, which is the intellectual justification for the rest of this report. Axelrod's tournaments (Chapter 6) select among strategies by ecological success rather than by refinement; evolutionary game theory (Chapter 5) selects by dynamic stability; and reinforcement learning (Chapter 8) selects by what adaptive agents actually converge to. None of these is a refinement of subgame perfection, and they need not agree --- which is precisely what makes the comparison worth making.
