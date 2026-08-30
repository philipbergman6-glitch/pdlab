# The Finitely Repeated Game

## Definitions

Fix a stage game $G = \langle \{1,2\}, \{C,D\}^2, (u_1,u_2)\rangle$ satisfying (2.1)--(2.2), and an integer horizon $n \ge 1$.

**Definition 3.1 (The $n$-fold repeated game).** The *$n$-fold repetition* $G^n$ is the extensive game with perfect recall in which $G$ is played in rounds $t = 1,\dots,n$, both players observing the realised action profile at the end of each round (*perfect monitoring*). A *history of length $t$* is a sequence $h^t = (a^1,\dots,a^t) \in A^t$ with $A = \{C,D\}^2$; $h^0 = \varnothing$ is the empty history and $H = \bigcup_{t=0}^{n-1} A^t$ is the set of histories at which play continues. A (behaviour) *strategy* for player $i$ is a map
$$
s_i : H \longrightarrow \Delta(\{C,D\}),
$$
assigning to each history a --- possibly randomised --- action; $s_i$ is *pure* if every $s_i(h)$ is degenerate. Payoffs in $G^n$ are the undiscounted sums
$$
U_i^n(s_1,s_2) \;=\; \mathbb{E}\Bigl[\sum_{t=1}^{n} u_i(a^t)\Bigr],
$$
the expectation taken over the play path induced by $(s_1,s_2)$.

**Definition 3.2 (Subgame; SPE).** For each $h \in H$ of length $t$, the *subgame* $G^n|_h$ is the $(n-t)$-fold repetition of $G$ played after $h$; the *continuation strategy* $s_i|_h$ is defined by $s_i|_h(h') = s_i(h h')$, and the continuation payoff is $U_i^{n-t}(s_1|_h, s_2|_h)$. A profile $(s_1^*,s_2^*)$ is a *subgame-perfect equilibrium* (SPE) of $G^n$ if for every $h \in H$ the profile $(s_1^*|_h, s_2^*|_h)$ is a Nash equilibrium of $G^n|_h$. Every SPE is a Nash equilibrium (take $h = \varnothing$); the converse fails.

Because $G^n$ has perfect recall and finitely many nodes, subgame perfection can be checked one round at a time.

**Theorem 3.3 (One-shot deviation principle, finite horizon).** A strategy profile $s^* = (s_1^*, s_2^*)$ of $G^n$ is a subgame-perfect equilibrium if and only if it admits no profitable *one-shot deviation*: there is no player $i$, no history $h \in H$, and no action $a_i \in \{C,D\}$ such that player $i$ strictly increases her continuation payoff in $G^n|_h$ by playing $a_i$ at $h$ and following $s_i^*$ at every other history.

*Proof (sketch; see [@fudenbergtirole1991, Thm. 4.1] or [@osbornerubinstein1994, Lemma 98.2]).* Necessity is immediate: a one-shot deviation is a deviation. For sufficiency, suppose $s^*$ admits no profitable one-shot deviation but some $\hat s_i$ strictly improves player $i$'s payoff in the subgame after some $h$, by an amount $\eta > 0$. Since $G^n|_h$ has finite depth, $\hat s_i$ differs from $s_i^*$ at only finitely many histories; let $\tau$ be the *last* round at which they differ. Replacing $\hat s_i$ by $s_i^*$ from round $\tau$ onwards cannot lower player $i$'s payoff, since at every round-$\tau$ history the modification is a one-shot deviation from $s_i^*$ in the continuation, and by hypothesis such deviations are not strictly profitable. Iterating backwards over the finitely many rounds at which they differ produces $s_i^*$ itself with payoff at least that of $\hat s_i$, contradicting $\eta > 0$. $\square$

Write $\mathrm{ALLD}$ for the strategy $s_i^{D}(h) = D$ for every $h \in H$: unconditional defection.

## Backward induction

**Theorem 3.4 (Unravelling; uniqueness of the SPE).** For every $n \ge 1$, the $n$-fold repeated Prisoner's Dilemma $G^n$ has exactly one subgame-perfect equilibrium, namely $(\mathrm{ALLD}, \mathrm{ALLD})$. Its payoff is $(nP, nP)$, and the same is true in every subgame.

*Proof.* We prove by induction on $k$ the statement $\mathcal{P}(k)$: *in every subgame of $G^n$ with $k$ rounds remaining, the unique SPE is unconditional defection by both players, with continuation payoff $(kP,kP)$.*

$\mathcal{P}(1)$: a one-round subgame is a copy of the stage game $G$, whose unique Nash equilibrium is $(D,D)$ with payoff $(P,P)$ by Theorem 2.8.

$\mathcal{P}(k-1) \Rightarrow \mathcal{P}(k)$ for $k \ge 2$: let $h$ be a history with $k$ rounds remaining and let $s^*$ be an SPE of $G^n$. Every history $h a$, $a \in A$, has $k-1$ rounds remaining, so by $\mathcal{P}(k-1)$ the continuation profile $s^*|_{ha}$ is unconditional defection and yields $((k-1)P, (k-1)P)$ --- *for every* $a \in A$, on path and off. Hence the continuation payoff after the current round is the constant $(k-1)P$ for each player, independent of the current round's actions. Player $i$'s payoff in $G^n|_h$ is therefore
$$
u_i(\sigma_1,\sigma_2) + (k-1)P,
$$
where $\sigma_j = s_j^*(h)$. Adding a constant does not change the best-response correspondence, so $(\sigma_1,\sigma_2)$ is a Nash equilibrium of $G^n|_h$ if and only if it is a Nash equilibrium of the stage game $G$; by Theorem 2.8 this forces $\sigma_1 = \sigma_2 = D$, and the continuation payoff is $P + (k-1)P = kP$. This establishes $\mathcal{P}(k)$.

Applying $\mathcal{P}(k)$ at every history --- including $h = \varnothing$ with $k = n$ --- shows that $s^*$ prescribes $D$ everywhere, i.e. $s^* = (\mathrm{ALLD},\mathrm{ALLD})$; and this profile is an SPE because at every history it induces the stage equilibrium with history-independent continuations, so Theorem 3.3 applies with all one-shot deviation gains equal to $u_i(a_i,D) - u_i(D,D) \le 0$. $\square$

The engine of the proof is the phrase *independent of the current round's actions*: because the continuation is pinned down uniquely and identically after every action profile, no threat and no promise can be attached to today's behaviour, and the game collapses to $n$ independent copies of $G$.

## Nash equilibria without perfection

Subgame perfection is a strong requirement, and one might hope that Nash equilibrium alone permits cooperation, sustained by threats that are incredible but never tested. It does not.

**Theorem 3.5 (Uniqueness of the equilibrium path).** Let $s^* = (s_1^*,s_2^*)$ be *any* Nash equilibrium of $G^n$. Then the play path induced by $s^*$ is $(D,D)$ in every round, with probability one, and $U_i^n(s^*) = nP$.

*Proof.* Note first that each player can *guarantee* $P$ per round: $\min_{a_j} u_i(D,a_j) = \min\{T,P\} = P$, so by playing $D$ in every remaining round a player secures at least $mP$ in any $m$-round continuation, whatever the opponent does. (This is the minmax bound of Definition 4.13.)

We show by downward induction on $t = n, n-1, \dots, 1$ that the on-path round-$t$ profile is $(D,D)$ almost surely. Consider the statement $\mathcal{Q}(t)$: *on every history reached with positive probability under $s^*$, rounds $t, t+1, \dots, n$ are played as $(D,D)$.*

$\mathcal{Q}(n+1)$ is vacuously true. Assume $\mathcal{Q}(t+1)$; let $h$ be a positive-probability history of length $t-1$, and let $\sigma_j = s_j^*(h)$. By $\mathcal{Q}(t+1)$, the continuation payoff from round $t+1$ onwards, *along the equilibrium path from $h$*, equals $(n-t)P$ for each player. Hence
$$
U_i^{n-t+1}(s^*|_h) \;=\; u_i(\sigma_1,\sigma_2) + (n-t)P .
$$
Now fix $i$ and let $b_i \in \{C,D\}$ be a best response in the stage game to $\sigma_{-i}$. Consider the deviation $\hat s_i$: follow $s_i^*$ until $h$; at $h$ play $b_i$; from round $t+1$ onwards play $D$ unconditionally. By the guarantee above,
$$
U_i^{n-t+1}(\hat s_i, s_{-i}^*|_h) \;\ge\; u_i(b_i, \sigma_{-i}) + (n-t)P .
$$
Since $h$ has positive probability and $s^*$ is a Nash equilibrium, deviating in this way cannot be strictly profitable in the whole game, hence not in the continuation from $h$:
$$
u_i(\sigma_1,\sigma_2) + (n-t)P \;\ge\; u_i(b_i,\sigma_{-i}) + (n-t)P
\quad\Longrightarrow\quad
u_i(\sigma_i,\sigma_{-i}) \ge \max_{b_i} u_i(b_i,\sigma_{-i}).
$$
So $\sigma_i$ is a stage-game best response to $\sigma_{-i}$ for each $i$; that is, $(\sigma_1,\sigma_2)$ is a Nash equilibrium of $G$, and Theorem 2.8 gives $\sigma_1 = \sigma_2 = D$. This proves $\mathcal{Q}(t)$, and the induction down to $t=1$ gives the claim. $\square$

Theorem 3.5 does not say that $(\mathrm{ALLD},\mathrm{ALLD})$ is the unique Nash equilibrium of $G^n$ --- it is not, for $n \ge 2$. Off-path behaviour is unconstrained: for $n=2$, the profile "play $D$ in round 1; in round 2 play $D$ if round 1 was $(D,D)$ and play $C$ otherwise'' is a Nash equilibrium (the round-2 prescription is never invoked on path), yet it is not subgame perfect. What Theorem 3.5 does say is that the *outcome* is invariant: no Nash equilibrium of the finitely repeated Prisoner's Dilemma produces a single cooperative round.

**Remark 3.6 (Contrast: multiple stage equilibria).** Both theorems lean on the *uniqueness* of the stage equilibrium. Benoit and Krishna [@benoitkrishna1985] show that when the stage game has multiple Nash equilibria with distinct payoffs for each player, the finitely repeated game admits a folk theorem: as $n \to \infty$, essentially every feasible and individually rational payoff can be supported in subgame-perfect equilibrium, the terminal rounds being used to reward or punish with different stage equilibria. The Prisoner's Dilemma is exactly the case where this device is unavailable, which is why finite repetition buys nothing and infinite repetition (Chapter 4) buys everything.

**Remark 3.7 (The end-game effect and bounded rationality).** Human subjects do not unravel. In finitely repeated Prisoner's Dilemmas and their relatives, cooperation is typically high in early rounds and collapses only in the last few; Selten and Stoecker [@seltenstoecker1986] documented, in an experiment of 25 successive ten-round supergames with changing anonymous partners, that subjects learn to defect progressively *earlier* across supergames, but that the learning stabilises well short of round one, exactly as a bounded-rationality model of backward induction with a limited number of steps predicts. The leading rational-choice explanation is reputational: Kreps, Milgrom, Roberts and Wilson [@krepsmilgromrobertswilson1982] show that if each player attaches even a small prior probability to the opponent being a behavioural type committed to TIT FOR TAT, then in the resulting game of incomplete information there are sequential equilibria in which both players cooperate in all but the last few rounds, with the number of defecting rounds bounded independently of $n$. A vanishing amount of incomplete information thus overturns Theorem 3.4 completely --- a warning that the unravelling result is fragile in exactly the direction the data point.
