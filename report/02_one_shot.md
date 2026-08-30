# The One-Shot Prisoner's Dilemma

## The normal form

**Definition 2.1 (Finite normal-form game).** A *finite normal-form game* is a triple $G = \langle N, (A_i)_{i \in N}, (u_i)_{i \in N} \rangle$ in which $N$ is a finite set of *players*, $A_i$ is a finite set of *actions* available to player $i$, and $u_i : A \to \mathbb{R}$ is player $i$'s *payoff function*, defined on the set of *action profiles* $A = \prod_{j \in N} A_j$. We write $a = (a_i, a_{-i})$ to separate player $i$'s component from the others'.

Throughout this report $N = \{1,2\}$ and $A_1 = A_2 = \{C, D\}$, where $C$ stands for *cooperate* and $D$ for *defect*. The game is symmetric: $u_2(a_1, a_2) = u_1(a_2, a_1)$ for all $(a_1,a_2)$, so a single function determines both payoffs.

**Definition 2.2 (Prisoner's Dilemma).** Fix four real numbers $T, R, P, S$ (*temptation*, *reward*, *punishment*, *sucker*) and define the symmetric game $G(T,R,P,S)$ by
$$
u_1(C,C) = R,\quad u_1(C,D) = S,\quad u_1(D,C) = T,\quad u_1(D,D) = P,
$$
with $u_2(a_1,a_2) = u_1(a_2,a_1)$. The game is a *(strict) Prisoner's Dilemma* if
$$
T > R > P > S \tag{2.1}
$$
and
$$
2R > T + S. \tag{2.2}
$$

In bimatrix form, with player 1 choosing the row and player 2 the column:

|          |      $C$      |      $D$      |
|:--------:|:-------------:|:-------------:|
| **$C$**  | $R,\;R$       | $S,\;T$       |
| **$D$**  | $T,\;S$       | $P,\;P$       |

The canonical numerical instance used throughout this report is Axelrod's $(T,R,P,S) = (5,3,1,0)$ [@axelrod1984], implemented as `PayoffMatrix.axelrod()`:

|          |     $C$     |     $D$     |
|:--------:|:-----------:|:-----------:|
| **$C$**  | $3,\;3$     | $0,\;5$     |
| **$D$**  | $5,\;0$     | $1,\;1$     |

Condition (2.1) is what makes the game a dilemma: $T > R$ means unilateral defection beats mutual cooperation, $P > S$ means defection beats cooperation against a defector, and $R > P$ means mutual cooperation beats mutual defection. Condition (2.2) is a separate requirement, and it is worth being explicit about its role.

**Remark 2.3 (Why $2R > T+S$).** Consider two players who could coordinate on a public randomisation or on an alternating schedule: player 1 plays $D$ while player 2 plays $C$ in odd rounds, and the roles swap in even rounds. The long-run average payoff to each is $(T+S)/2$. Without (2.2) this exceeds $R$, and "cooperation'' in the sense of $(C,C)$ would no longer be the jointly best arrangement --- the efficient outcome would be *taking turns exploiting each other*, and the entire literature on sustaining $(C,C)$ by repetition would be pointed at the wrong target. Condition (2.2) says precisely that $(R,R)$ maximises the sum of payoffs over the feasible set; see Theorem 2.9 and, in the repeated game, Theorem 4.14. Note that (2.2) does not follow from (2.1): $(T,R,P,S) = (5, 2.4, 1, 0)$ satisfies (2.1) but has $2R = 4.8 < 5 = T+S$. The class `PayoffMatrix` enforces (2.2) unconditionally, and (2.1) unless `strict=False`.

## Dominance, equilibrium, efficiency

Let $\Delta(A_i)$ denote the set of probability distributions over $A_i$; an element $\sigma_i \in \Delta(A_i)$ is a *mixed strategy*, and payoffs are extended to mixed profiles by expectation,
$$
u_i(\sigma_1,\sigma_2) = \sum_{a \in A} \sigma_1(a_1)\,\sigma_2(a_2)\, u_i(a).
$$

**Definition 2.4 (Strict dominance).** Action $a_i \in A_i$ *strictly dominates* $a_i' \in A_i$ if $u_i(a_i, a_{-i}) > u_i(a_i', a_{-i})$ for every $a_{-i} \in A_{-i}$. It *weakly dominates* $a_i'$ if the inequality holds weakly for every $a_{-i}$ and strictly for at least one. An action is *strictly (weakly) dominant* if it strictly (weakly) dominates every other action.

**Definition 2.5 (Nash equilibrium).** A mixed profile $\sigma^* = (\sigma_1^*, \sigma_2^*)$ is a *Nash equilibrium* if for every player $i$ and every $\sigma_i \in \Delta(A_i)$, $u_i(\sigma_i^*, \sigma_{-i}^*) \ge u_i(\sigma_i, \sigma_{-i}^*)$. It is a *pure* equilibrium if each $\sigma_i^*$ is degenerate.

**Definition 2.6 (Pareto dominance and efficiency).** For payoff vectors $v, w \in \mathbb{R}^N$, $w$ *Pareto-dominates* $v$ if $w_i \ge v_i$ for all $i$ with strict inequality for some $i$. Given a set $V \subseteq \mathbb{R}^N$ of attainable payoff vectors, $v \in V$ is *Pareto-efficient in $V$* if no $w \in V$ Pareto-dominates it. We take $V$ to be the *feasible set*
$$
V \;=\; \operatorname{conv}\{(R,R),\,(S,T),\,(T,S),\,(P,P)\} \subset \mathbb{R}^2, \tag{2.3}
$$
the convex hull of the four pure payoff vectors --- the payoffs attainable with a public randomising device, and (Chapter 4) the set of long-run average payoffs attainable in the repeated game.

**Theorem 2.7 (Dominance).** In a strict Prisoner's Dilemma, $D$ strictly dominates $C$ for both players.

*Proof.* By symmetry it suffices to treat player 1. There are two possible actions of player 2. If $a_2 = C$, then $u_1(D,C) - u_1(C,C) = T - R > 0$ by (2.1). If $a_2 = D$, then $u_1(D,D) - u_1(C,D) = P - S > 0$ by (2.1). Both differences are strictly positive, so $D$ strictly dominates $C$. $\square$

The two gaps $(T-R, P-S)$ are returned by `PayoffMatrix.dominance_gap()`; both are strictly positive exactly when $D$ strictly dominates $C$.

**Theorem 2.8 (Uniqueness of equilibrium).** In a strict Prisoner's Dilemma, $(D,D)$ is the unique Nash equilibrium, in mixed as well as pure strategies.

*Proof.* First, $(D,D)$ is an equilibrium: by Theorem 2.7, $u_1(D,D) > u_1(C,D)$, so no unilateral deviation by player 1 to $C$ --- and hence, by linearity of $u_1$ in $\sigma_1$, no deviation to any mixture --- is profitable; symmetrically for player 2.

For uniqueness, let $\sigma = (\sigma_1,\sigma_2)$ be a Nash equilibrium and suppose $q := \sigma_1(C) > 0$. Define $\sigma_1'$ to be the degenerate strategy on $D$. Writing $r := \sigma_2(C)$, linearity gives
$$
u_1(\sigma_1', \sigma_2) - u_1(\sigma_1,\sigma_2) \;=\; q\bigl[\,u_1(D,\sigma_2) - u_1(C,\sigma_2)\,\bigr] \;=\; q\bigl[\, r\,(T-R) + (1-r)(P-S)\,\bigr].
$$
Since $r \in [0,1]$ and both $T-R$ and $P-S$ are strictly positive, the bracket is bounded below by $\min\{T-R,\,P-S\} > 0$; with $q > 0$ the whole expression is strictly positive. Hence $\sigma_1$ is not a best response to $\sigma_2$, contradicting the equilibrium property. Therefore $\sigma_1(C) = 0$, i.e. $\sigma_1 = D$, and symmetrically $\sigma_2 = D$. $\square$

Note that the argument uses only strict dominance: in *any* finite game, a strictly dominated action receives probability zero in every Nash equilibrium, and if each player has a strictly dominant action the profile of those actions is the unique equilibrium. This is `analytic.one_shot_facts`, which reports `dd_unique_nash` exactly when `d_dominant` holds.

**Theorem 2.9 (Efficiency classification).** In a strict Prisoner's Dilemma with feasible set $V$ as in (2.3), the profiles $(C,C)$, $(C,D)$ and $(D,C)$ are Pareto-efficient in $V$, and $(D,D)$ is not. In particular the unique Nash equilibrium is the unique Pareto-inefficient pure profile, and it is Pareto-dominated by $(C,C)$.

*Proof.* *(i) $(D,D)$ is inefficient.* Its payoff vector is $(P,P)$ and $(R,R) \in V$ with $R > P$ in both coordinates, so $(R,R)$ Pareto-dominates $(P,P)$.

*(ii) $(C,D)$ is efficient.* Its payoff vector is $(S,T)$. By (2.1), $T = \max\{T,R,P,S\}$, so every vertex of $V$ has second coordinate at most $T$; since the second coordinate is a linear functional, its maximum over the polytope $V$ equals its maximum over the vertices, namely $T$, and among the vertices it is attained only at $(S,T)$. Suppose $w \in V$ Pareto-dominates $(S,T)$; then $w_2 \ge T$, hence $w_2 = T$, hence $w$ lies on the face $\{v \in V : v_2 = T\}$. A face of a polytope is the convex hull of the vertices it contains, and the only such vertex is $(S,T)$; therefore $w = (S,T)$, which does not Pareto-dominate itself. Hence $(S,T)$ is efficient. The case of $(D,C)$ is symmetric.

*(iii) $(C,C)$ is efficient.* Consider the linear functional $\Sigma(v) = v_1 + v_2$. Its values at the four vertices are $2R$, $T+S$, $T+S$ and $2P$. By (2.2), $2R > T+S$, and by (2.1), $R > P$ so $2R > 2P$. Hence $\max_{v \in V}\Sigma(v) = 2R$, attained only at $(R,R)$. If $w \in V$ Pareto-dominated $(R,R)$ then $\Sigma(w) > \Sigma(R,R) = 2R$, a contradiction. $\square$

The classification is worth emphasising because it is frequently misstated. The Prisoner's Dilemma is *not* a game in which the two "exploitative'' outcomes are socially bad; they are Pareto-efficient, because the exploiter cannot be made better off at all. What is bad about them is that they are unfair and that they are not sustainable as equilibria. The genuinely defective outcome is $(D,D)$, and it is the one the players are driven to.

## Two reparametrisations

### The donation game

**Definition 2.10 (Donation game).** Fix $b > c > 0$. In the *donation game* $\mathrm{Don}(b,c)$, a cooperator pays a cost $c$ to confer a benefit $b$ on the co-player; a defector does nothing. The induced payoffs are
$$
T = b, \qquad R = b - c, \qquad P = 0, \qquad S = -c.
$$

**Proposition 2.11.** $\mathrm{Don}(b,c)$ is a strict Prisoner's Dilemma for every $b > c > 0$.

*Proof.* Order: $T - R = c > 0$, $R - P = b - c > 0$, $P - S = c > 0$, so $T > R > P > S$. Additivity: $2R - (T+S) = 2(b-c) - (b - c) = b - c > 0$. $\square$

The donation game is the standard vehicle for the biological literature, because it has one degree of freedom after normalisation: setting $c = 1$ leaves the *benefit-to-cost ratio* $b/c$ as the only parameter, and the classical conditions for the evolution of cooperation are all of the form $b/c > \text{something}$ (Chapter 5). It is implemented as `PayoffMatrix.donation(b, c)`.

### The weak dilemma of Nowak and May

**Definition 2.12 (Weak dilemma).** For $1 < b < 2$, the *Nowak--May* parametrisation [@nowakmay1992] is
$$
R = 1, \qquad T = b, \qquad P = S = 0,
$$
i.e. a donation game in the limit $c \to 0$ after rescaling. Its payoff bimatrix is

|          |     $C$     |     $D$     |
|:--------:|:-----------:|:-----------:|
| **$C$**  | $1,\;1$     | $0,\;b$     |
| **$D$**  | $b,\;0$     | $0,\;0$     |

Here $T > R \ge P \ge S$ holds with $P = S$, so (2.1) fails and only the weak ordering survives; (2.2) becomes $2 > b$, which is exactly the stated restriction $b < 2$. `PayoffMatrix.nowak_may(b)` enforces $1 < b < 2$ and is constructed with `strict=False`.

**Theorem 2.13 (Equilibrium structure of the weak dilemma).** Let $1 < b < 2$. Then:

1. $D$ weakly --- but not strictly --- dominates $C$ for both players.
2. $(D,D)$ is a Nash equilibrium, but it is *not* the unique one: the set of Nash equilibria is
$$
\mathcal{N} \;=\; \bigl\{ (\sigma_1, D) : \sigma_1 \in \Delta(\{C,D\}) \bigr\} \;\cup\; \bigl\{ (D, \sigma_2) : \sigma_2 \in \Delta(\{C,D\}) \bigr\}.
$$
3. $(D,D)$ is the unique Nash equilibrium surviving the elimination of weakly dominated strategies, and the unique trembling-hand perfect equilibrium.

*Proof.* (1) Against $C$: $u_1(D,C) - u_1(C,C) = b - 1 > 0$. Against $D$: $u_1(D,D) - u_1(C,D) = P - S = 0$. So the dominance is weak and not strict.

(2) Write $q = \sigma_1(C)$, $r = \sigma_2(C)$. Player 1's payoffs are $u_1(C,\sigma_2) = r$ and $u_1(D,\sigma_2) = rb$, so $D$ is a best response for every $r$, and $C$ is a best response iff $r = 0$, i.e. iff $\sigma_2 = D$. Symmetrically for player 2. Consequently $(\sigma_1,\sigma_2)$ is an equilibrium iff [$\sigma_1 = D$ or $\sigma_2 = D$] and [$\sigma_2 = D$ or $\sigma_1 = D$], i.e. iff at least one player plays $D$ with probability one. This is exactly $\mathcal{N}$.

(3) $C$ is weakly dominated for both players, so a single round of elimination leaves the profile $(D,D)$. For perfection, let $(\sigma_1^\eta, \sigma_2^\eta)$ be any sequence of completely mixed profiles converging to a candidate equilibrium, and suppose $\sigma_1(C) > 0$ in the limit. Along the sequence $r^\eta := \sigma_2^\eta(C) > 0$, so $u_1(D,\sigma_2^\eta) - u_1(C,\sigma_2^\eta) = r^\eta(b-1) > 0$ and $C$ is never a best response to $\sigma_2^\eta$; hence in the limit player 1 must put probability zero on $C$. The same holds for player 2, so $(D,D)$ is the only trembling-hand perfect equilibrium; and it is perfect, being a limit of best responses to any perturbation by the same computation. $\square$

**Remark 2.14.** Part (2) is a genuine difference from the strict game and a standard trap. Because $P = S$, a player facing a certain defector is *indifferent* between $C$ and $D$, so profiles such as $(C,D)$ --- one player is exploited and does not mind, because being exploited costs nothing in this parametrisation --- satisfy the equilibrium conditions. The weak dilemma is used in this report only in the spatial model of Section 5.5, where the dynamics is imitation-based rather than equilibrium-based and this multiplicity is immaterial; wherever equilibrium reasoning is done we use the strict game.
