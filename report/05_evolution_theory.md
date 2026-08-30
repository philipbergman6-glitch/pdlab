# Evolutionary Game Theory

Chapters 3 and 4 asked which strategy profiles a rational player would choose. This chapter asks a different question: which strategies *survive*. Payoffs become reproductive fitness, deliberation is replaced by differential reproduction or imitation, and equilibrium is replaced by dynamic stability.

## The replicator equation and evolutionary stability

**Definition 5.1 (Population game).** Let $\mathcal{S} = \{1,\dots,n\}$ be a finite set of pure strategies and $A = (a_{ij}) \in \mathbb{R}^{n\times n}$ a payoff matrix, $a_{ij}$ being the payoff to an $i$-player matched with a $j$-player. A *population state* is a point of the simplex
$$
\Delta^{n-1} = \Bigl\{ x \in \mathbb{R}^n_{\ge 0} : \textstyle\sum_i x_i = 1 \Bigr\},
$$
$x_i$ being the frequency of strategy $i$. In a randomly matched infinite population, the expected payoff to strategy $i$ is $f_i(x) = (Ax)_i$ and the mean population payoff is $\bar f(x) = x^{\!\top} A x$.

**Definition 5.2 (Replicator equation; Taylor and Jonker 1978).** The *replicator dynamics* on $\Delta^{n-1}$ is
$$
\dot x_i \;=\; x_i\bigl[(Ax)_i - x^{\!\top}Ax\bigr], \qquad i = 1,\dots,n. \tag{5.1}
$$
[@taylorjonker1978] A strategy grows exactly when it earns more than the population average.

The simplex and each of its faces are invariant: $\sum_i \dot x_i = \bar f - \bar f = 0$, and $x_i = 0 \Rightarrow \dot x_i = 0$. Adding a constant to any *column* of $A$ leaves (5.1) unchanged, a fact used below to simplify computations. Equation (5.1) is implemented as `analytic.replicator_rhs`.

**Definition 5.3 (Evolutionarily stable strategy; Maynard Smith and Price 1973).** A state $x^* \in \Delta^{n-1}$ is an *evolutionarily stable strategy* (ESS) if for every $y \ne x^*$ there is $\bar\epsilon \in (0,1)$ such that
$$
(x^*)^{\!\top} A\,\bigl(\epsilon y + (1-\epsilon)x^*\bigr) \;>\; y^{\!\top} A\,\bigl(\epsilon y + (1-\epsilon) x^*\bigr) \quad \text{for all } \epsilon \in (0,\bar\epsilon).
$$
[@maynardsmithprice1973] Equivalently (expanding in $\epsilon$), $x^*$ is an ESS iff for every $y \ne x^*$:
$$
\textbf{(E1)}\quad (x^*)^{\!\top} A x^* \ge y^{\!\top} A x^*, \qquad\text{and}\qquad
\textbf{(E2)}\quad \text{if } (x^*)^{\!\top} A x^* = y^{\!\top} A x^* \text{ then } (x^*)^{\!\top} A y > y^{\!\top} A y. \tag{5.2}
$$
If the strict inequality in (E2) is weakened to "$\ge$'', $x^*$ is called *neutrally stable* (an NSS).

For a pure strategy $i$, (5.2) reads: for every $j \ne i$, either $a_{ii} > a_{ji}$, or $a_{ii} = a_{ji}$ and $a_{ij} > a_{jj}$. These are the conditions tested by `analytic.is_ess` and, in the weakened form, `analytic.is_neutrally_stable`.

**Theorem 5.4 (ESS, Nash, and stability).** Let $x^*$ be an ESS of the population game $A$. Then (i) $(x^*,x^*)$ is a symmetric Nash equilibrium of the underlying two-player symmetric game, and (ii) $x^*$ is an asymptotically stable rest point of the replicator dynamics (5.1). Neither converse holds in general: a symmetric Nash equilibrium need not be an ESS (e.g. $\mathrm{TFT}$ in Theorem 5.10), and for $n \ge 3$ strategies there are asymptotically stable rest points that are not evolutionarily stable; for $n = 2$ the two notions coincide.

*Proof.* (i) is condition (E1), which is precisely the statement that no $y$ is a strictly better reply to $x^*$ than $x^*$ itself. For (ii) see Hofbauer and Sigmund [@hofbauersigmund1998, Thm. 7.2.4]: the relative entropy $H(x) = -\sum_{i \in \operatorname{supp} x^*} x_i^* \log(x_i/x_i^*)$ is a strict local Lyapunov function for (5.1) at an ESS, since $\dot H = -\bigl[(x^*)^{\!\top}Ax - x^{\!\top}Ax\bigr] < 0$ in a punctured neighbourhood of $x^*$ by (5.2). $\square$

We shall also need the eigenvalues of (5.1) at the vertices.

**Lemma 5.5 (Vertex spectrum).** In the coordinates $(x_j)_{j \ne i}$ on $\Delta^{n-1}$ (with $x_i = 1 - \sum_{j \ne i} x_j$), the Jacobian of (5.1) at the vertex $e_i$ is diagonal with entries
$$
\lambda_j \;=\; a_{ji} - a_{ii}, \qquad j \ne i.
$$

*Proof.* For $j \ne i$ write $\dot x_j = x_j\,G_j(x)$ with $G_j(x) = (Ax)_j - x^\top A x$. Then $\partial \dot x_j/\partial x_k = \delta_{jk}G_j(x) + x_j\,\partial G_j/\partial x_k$. At $x = e_i$ we have $x_j = 0$ for all $j \ne i$, killing the second term, and $G_j(e_i) = a_{ji} - a_{ii}$. $\square$

Thus $e_i$ is asymptotically stable iff $a_{ji} < a_{ii}$ for all $j\ne i$ (a *strict* symmetric Nash equilibrium), which for pure strategies is also exactly the ESS condition without the tie-breaking clause.

## The one-shot dilemma: ALLD is the unique ESS

Take $\mathcal{S} = \{C,D\}$ with $A = \begin{pmatrix} R & S \\ T & P\end{pmatrix}$ and write $x$ for the frequency of $C$.

**Theorem 5.6.** In the one-shot Prisoner's Dilemma the replicator dynamics on $\Delta^1$ is
$$
\dot x \;=\; x(1-x)\bigl[\,x\,(R-T) + (1-x)(S-P)\,\bigr],
$$
which is strictly negative for all $x \in (0,1)$. Hence $x(t) \to 0$ for every initial $x(0) < 1$, the vertex $D$ is globally asymptotically stable on $[0,1)$, and $D$ is the unique ESS; $C$ is not even neutrally stable.

*Proof.* Substituting into (5.1) with $n=2$ gives $\dot x = x\bigl[(Ax)_C - \bar f\bigr] = x(1-x)\bigl[(Ax)_C - (Ax)_D\bigr]$, and $(Ax)_C - (Ax)_D = x(R-T) + (1-x)(S-P)$. Both $R-T$ and $S-P$ are strictly negative by (2.1), so the bracket is a convex combination of two negative numbers, hence negative on $[0,1]$; $\dot x < 0$ on $(0,1)$ gives monotone convergence to $0$. By Lemma 5.5 the eigenvalue at $e_D$ is $a_{CD}-a_{DD} = S - P < 0$ and at $e_C$ it is $a_{DC}-a_{CC} = T-R > 0$. ESS: $a_{DD} = P > S = a_{CD}$ verifies (E1) strictly for $D$, whereas for $C$ we have $a_{CC} = R < T = a_{DC}$, violating (E1) even weakly. $\square$

This is the evolutionary restatement of Theorem 2.7: selection on individual fitness in a well-mixed population destroys cooperation. Everything that follows is an account of what must be added to the model to prevent this.

## Repeated play: the system $\{\mathrm{ALLC}, \mathrm{ALLD}, \mathrm{TFT}\}$

Suppose now that each encounter is not a single round but a discounted supergame $G^\infty(\delta)$, and that the heritable unit is a repeated-game strategy. Restrict attention to the three strategies $\mathcal{S}_3 = (\mathrm{ALLC}, \mathrm{ALLD}, \mathrm{TFT})$, indexed $1,2,3$ in that order, with payoffs given by the *normalised* discounted value (4.1) so that entries are directly comparable to stage payoffs.

**Proposition 5.7 (The $3\times 3$ payoff matrix).** With normalised discounted payoffs,
$$
A(\delta) \;=\;
\begin{pmatrix}
R & S & R \\[2pt]
T & P & (1-\delta)T + \delta P \\[2pt]
R & (1-\delta)S + \delta P & R
\end{pmatrix}. \tag{5.3}
$$

*Proof.* Each entry is $(1-\delta)\sum_{t\ge 0}\delta^t \pi_t$ for the realised path.

*Row $\mathrm{ALLC}$.* Against $\mathrm{ALLC}$ the path is $(C,C)$ forever: $R$. Against $\mathrm{ALLD}$ it is $(C,D)$ forever: $S$. Against $\mathrm{TFT}$: $\mathrm{TFT}$ opens with $C$ and thereafter copies $C$, so the path is $(C,C)$ forever: $R$.

*Row $\mathrm{ALLD}$.* Against $\mathrm{ALLC}$: $T$ forever. Against $\mathrm{ALLD}$: $P$ forever. Against $\mathrm{TFT}$: round $0$ is $(D,C)$ giving $T$; from round $1$ onward $\mathrm{TFT}$ plays $D$ and the path is $(D,D)$. Hence $(1-\delta)T + (1-\delta)\sum_{t \ge 1}\delta^t P = (1-\delta)T + \delta P$.

*Row $\mathrm{TFT}$.* Against $\mathrm{ALLC}$: $(C,C)$ forever, $R$. Against $\mathrm{ALLD}$: round $0$ is $(C,D)$ giving $S$, then $(D,D)$ forever; hence $(1-\delta)S + \delta P$. Against $\mathrm{TFT}$: mutual cooperation, $R$. $\square$

This is `analytic.payoff_matrix_3_symbolic()`. For $(5,3,1,0)$ and $\delta = 0.9$ it evaluates to
$$
A(0.9) = \begin{pmatrix} 3 & 0 & 3 \\ 5 & 1 & 1.4 \\ 3 & 0.9 & 3 \end{pmatrix}.
$$

Two structural features of (5.3) drive everything below. First, $\mathrm{ALLC}$ and $\mathrm{TFT}$ are *payoff-indistinguishable* against each other and against themselves: rows 1 and 3 agree in columns 1 and 3, and columns 1 and 3 agree in every row. In a population containing no $\mathrm{ALLD}$, the two strategies are behaviourally identical --- $\mathrm{TFT}$ never gets to retaliate --- and selection cannot separate them. Second, $\mathrm{TFT}$ differs from $\mathrm{ALLC}$ only in column 2: $(1-\delta)S+\delta P > S$ for $\delta > 0$. $\mathrm{TFT}$'s entire evolutionary advantage is that it loses to $\mathrm{ALLD}$ only once.

### Rest points

**Theorem 5.8 (Rest points).** Assume (2.1)--(2.2) and $\delta \in (0,1)$. Set
$$
\sigma \;:=\; (1-\delta)(P-S) \;>\; 0, \qquad
\Delta \;:=\; (R-P) - (1-\delta)(T-P). \tag{5.4}
$$
The rest points of (5.1) with $A = A(\delta)$ are: the three vertices; every point of the $\mathrm{ALLC}$--$\mathrm{TFT}$ edge $\{(x_1,0,x_3) : x_1+x_3=1\}$; and, when $\Delta > 0$, the single point
$$
x^{\dagger} \;=\; \bigl(0,\;1-x^{*},\;x^{*}\bigr), \qquad
\boxed{\;x^{*} \;=\; \frac{\sigma}{\sigma + \Delta} \;=\; \frac{(1-\delta)(P-S)}{(1-\delta)(P-S) + (R-P) - (1-\delta)(T-P)}\;} \tag{5.5}
$$
on the $\mathrm{ALLD}$--$\mathrm{TFT}$ edge. Moreover $x^{*} \in (0,1)$ if and only if $\Delta > 0$, i.e. if and only if
$$
\delta \;>\; \frac{T-R}{T-P} \;=\; \delta^{\mathrm{G}},
$$
the Grim/Nash threshold (4.2). There are no rest points in the interior of the simplex.

*Proof.* *Edge $\mathrm{ALLC}$--$\mathrm{TFT}$.* On $x_2 = 0$, $(Ax)_1 = R x_1 + R x_3 = R$ and $(Ax)_3 = R$, so $\bar f = R$ and $\dot x_1 = \dot x_3 = 0$: the entire edge consists of rest points. This is the payoff-indistinguishability noted above.

*Edge $\mathrm{ALLD}$--$\mathrm{TFT}$.* Put $x = (0, 1-x_3, x_3)$. Then
$$
(Ax)_2 = x_3\bigl[(1-\delta)T + \delta P\bigr] + (1-x_3)P, \qquad
(Ax)_3 = x_3 R + (1-x_3)\bigl[(1-\delta)S + \delta P\bigr],
$$
and a rest point with $x_3 \in (0,1)$ requires $(Ax)_2 = (Ax)_3$. Rearranging,
$$
x_3\Bigl[\,R - (1-\delta)T - \delta P\,\Bigr] \;=\; (1-x_3)\Bigl[\,P - (1-\delta)S - \delta P\,\Bigr],
$$
i.e. $x_3\,\Delta = (1-x_3)\,\sigma$, since $R - (1-\delta)T - \delta P = (R-P) - (1-\delta)(T-P) = \Delta$ and $P - (1-\delta)S - \delta P = (1-\delta)(P-S) = \sigma$. Solving gives $x_3 = \sigma/(\sigma+\Delta) = x^*$. As $\sigma > 0$, $x^* \in (0,1)$ iff $\Delta > 0$; and $\Delta > 0 \iff (R - P) > (1-\delta)(T-P) \iff \delta > (T-R)/(T-P)$ (divide by $T-P>0$).

*Edge $\mathrm{ALLC}$--$\mathrm{ALLD}$.* Here $(Ax)_1 = Rx_1 + Sx_2$ and $(Ax)_2 = Tx_1 + Px_2$, and $(Ax)_2 - (Ax)_1 = x_1(T-R) + x_2(P-S) > 0$ whenever $x \neq e_{\mathrm{ALLC}}$; there is no interior rest point on this edge (this is Theorem 5.6 again).

*Interior.* An interior rest point requires $(Ax)_1 = (Ax)_2 = (Ax)_3$. But $(Ax)_3 - (Ax)_1 = x_2\bigl[(1-\delta)S + \delta P - S\bigr] = x_2\,\sigma > 0$ for $x_2 > 0$, so $\mathrm{TFT}$ strictly outperforms $\mathrm{ALLC}$ at every state with $x_2 > 0$: no interior rest point exists. $\square$

For $(5,3,1,0)$ and $\delta = 0.9$: $\sigma = 0.1$, $\Delta = 2 - 0.1\cdot 4 = 1.6$, hence $x^{*} = 0.1/1.7 = 1/17 \approx 0.0588$, reproduced by `analytic.tft_invasion_threshold_symbolic()`.

### Stability

**Theorem 5.9 (Spectra and classification).** Let $\delta \in (0,1)$, $\sigma, \Delta$ as in (5.4), and use the simplex coordinates $(x_1, x_3) = (x_{\mathrm{ALLC}}, x_{\mathrm{TFT}})$. Then the Jacobian eigenvalues of (5.1) are:

| Rest point | eigenvalues | classification |
|:--|:--|:--|
| $\mathrm{ALLC}$ | $\;T-R\;(>0),\qquad 0$ | unstable |
| $\mathrm{ALLD}$ | $\;-(P-S)\;(<0),\qquad -\sigma\;(<0)$ | asymptotically stable |
| $\mathrm{TFT}$  | $\;-\Delta,\qquad 0$ | stable (non-hyperbolic) iff $\Delta>0$ |
| $x^{\dagger}$ (when $\Delta>0$) | $\;-\delta\,(P-S)(1-x^{*})\;(<0),\qquad x^{*}\Delta\;(>0)$ | saddle |

*Proof.* The three vertex rows follow from Lemma 5.5 applied to (5.3):

* At $e_{\mathrm{ALLC}}$: $a_{21}-a_{11} = T-R$ and $a_{31}-a_{11} = R-R = 0$.
* At $e_{\mathrm{ALLD}}$: $a_{12}-a_{22} = S-P = -(P-S)$ and $a_{32}-a_{22} = (1-\delta)S + \delta P - P = -(1-\delta)(P-S) = -\sigma$.
* At $e_{\mathrm{TFT}}$: $a_{13}-a_{33} = R-R = 0$ and $a_{23}-a_{33} = (1-\delta)T + \delta P - R = -\Delta$.

For $x^{\dagger}$, write $g(x_1,x_3) = (\dot x_1, \dot x_3)$ with $x_2 = 1-x_1-x_3$ and differentiate; the computation is carried out symbolically by `analytic.jacobian_eigenvalues_symbolic("TFT_ALLD_edge")`, which returns
$$
\lambda_1 = \frac{\delta\,(P-S)\,\bigl[(T-R)-\delta(T-P)\bigr]}{\sigma+\Delta},
\qquad
\lambda_2 = \frac{-(1-\delta)(P-S)\,\bigl[(T-R)-\delta(T-P)\bigr]}{\sigma+\Delta}.
$$
Since $(T-R) - \delta(T-P) = -\bigl[(R-P)-(1-\delta)(T-P)\bigr] = -\Delta$, $(1-\delta)(P-S) = \sigma$, and $\sigma/(\sigma+\Delta) = x^{*}$, these simplify to
$$
\lambda_1 = -\,\delta\,(P-S)\,\frac{\Delta}{\sigma+\Delta} = -\,\delta\,(P-S)\,(1-x^{*}), \qquad
\lambda_2 = \frac{\sigma\,\Delta}{\sigma+\Delta} = x^{*}\,\Delta .
$$
When $\Delta > 0$ we have $\lambda_1 < 0 < \lambda_2$, a hyperbolic saddle. The eigenvector for $\lambda_2$ lies along the $\mathrm{ALLD}$--$\mathrm{TFT}$ edge and the one for $\lambda_1$ points into the simplex; the latter sign is intuitive, since at $x^{\dagger}$ strategy $\mathrm{ALLC}$ earns $x^{*}R + (1-x^{*})S$, which is strictly less than $\mathrm{TFT}$'s $x^{*}R + (1-x^{*})[(1-\delta)S+\delta P]$, so the $\mathrm{ALLC}$ direction is contracting.

For the classification of $e_{\mathrm{TFT}}$, note that the zero eigenvalue is not an artefact: the whole $\mathrm{ALLC}$--$\mathrm{TFT}$ edge consists of rest points (Theorem 5.8), so $e_{\mathrm{TFT}}$ can be Lyapunov stable but never asymptotically stable. It *is* Lyapunov stable when $\Delta > 0$, since the transverse eigenvalue $-\Delta$ is negative and the centre direction is a line of rest points. $\square$

For $(5,3,1,0)$, $\delta = 0.9$ the four spectra are $\{2, 0\}$, $\{-1, -0.1\}$, $\{-1.6, 0\}$ and $\{-0.847,\, +0.0941\}$, matching the numerical Jacobian of `analytic.jacobian_eigenvalues` to eight digits.

**Theorem 5.10 (ESS classification).** Let $\delta \in (0,1)$.

1. $\mathrm{ALLD}$ is an ESS, for every $\delta \in (0,1)$.
2. $\mathrm{TFT}$ is *not* an ESS, for any $\delta$; it is neutrally stable if and only if $\delta > (T-R)/(T-P)$.
3. $\mathrm{ALLC}$ is neither an ESS nor neutrally stable.

*Proof.* (1) Compare column $\mathrm{ALLD}$: $a_{22} = P$, $a_{12} = S < P$, and $a_{32} = (1-\delta)S+\delta P = P - \sigma < P$. Both inequalities are strict, so (E1) holds strictly for both $y = e_{\mathrm{ALLC}}$ and $y = e_{\mathrm{TFT}}$, and by linearity for every mixture $y \ne e_{\mathrm{ALLD}}$. Hence $\mathrm{ALLD}$ is a strict Nash equilibrium and therefore an ESS.

(2) Take $y = e_{\mathrm{ALLC}}$. Then $a_{33} = R = a_{13}$, so (E1) holds with equality and (E2) is required: it demands $a_{31} > a_{11}$, i.e. $R > R$, which is false. So $\mathrm{TFT}$ fails (E2) and is not an ESS. For neutral stability (E2) is weakened to $a_{31}\ge a_{11}$, i.e. $R \ge R$: true. The remaining comparison is $y = e_{\mathrm{ALLD}}$, requiring $a_{33} \ge a_{23}$, i.e. $R \ge (1-\delta)T+\delta P$, i.e. $\Delta \ge 0$, i.e. $\delta \ge (T-R)/(T-P)$; strict neutral stability against $\mathrm{ALLD}$ invasions needs the strict inequality, and mixtures $y$ with $y_2 > 0$ then also fail to invade by linearity.

(3) $a_{11} = R < T = a_{21}$, so (E1) fails already for $y = e_{\mathrm{ALLD}}$. $\square$

**Remark 5.11 (Bistability and the invasion barrier).** Combining Theorems 5.9 and 5.10: for $\delta > \delta^{\mathrm{G}} = (T-R)/(T-P)$ the system is *bistable*. $\mathrm{ALLD}$ and the $\mathrm{TFT}$-end of the cooperative edge are both stable, and the saddle $x^{\dagger}$ is the barrier between their basins along the $\mathrm{ALLD}$--$\mathrm{TFT}$ edge: a $\mathrm{TFT}$ mutant arising singly in an $\mathrm{ALLD}$ population is selected against, because a lone $\mathrm{TFT}$ pays $S$ once against almost every opponent and never collects $R$; only if the $\mathrm{TFT}$ frequency exceeds $x^{*}$ do $\mathrm{TFT}$-$\mathrm{TFT}$ encounters become common enough for reciprocity to pay. Reciprocity therefore requires a *critical mass*, supplied in practice by clustering, kin structure or drift --- themes taken up in Sections 5.4 and 5.5. Note how small the barrier is for realistic patience: $x^{*} = 1/17 \approx 5.9\%$ at $\delta = 0.9$, and $x^* \to 0$ as $\delta \to 1$ since $\sigma \to 0$ while $\Delta \to R-P > 0$.

The second consequence is the fragility of the cooperative state. Because the $\mathrm{ALLC}$--$\mathrm{TFT}$ edge is a line of rest points, a $\mathrm{TFT}$ population is subject to *neutral drift* towards $\mathrm{ALLC}$: $\mathrm{ALLC}$ mutants pay no selective price while $\mathrm{ALLD}$ is absent. Once drift has raised $x_{\mathrm{ALLC}}$ far enough, a subsequent $\mathrm{ALLD}$ invasion succeeds, and the cycle repeats. This is the standard account of the observed oscillations between defection, reciprocity and unconditional cooperation in evolutionary simulations, and the reason more forgiving reciprocators such as Generous TIT FOR TAT [@nowaksigmund1992] and Win-Stay-Lose-Shift [@nowaksigmund1993] eventually displace $\mathrm{TFT}$ in longer-run models.

## Finite populations: the Moran process

The replicator equation describes an infinite population; in a finite one, selection competes with sampling noise, and the relevant quantity is a *fixation probability*.

**Definition 5.12 (Moran process with frequency-dependent fitness).** [@nowak2006book, ch. 6] Fix a population of constant size $N$ containing $i$ individuals of type $A$ and $N-i$ of type $B$. With payoff matrix $\begin{pmatrix} a & b \\ c & d\end{pmatrix}$ (rows $A,B$) and *no self-interaction*, the expected payoffs are
$$
\pi_A(i) = \frac{a(i-1) + b\,(N-i)}{N-1}, \qquad
\pi_B(i) = \frac{c\,i + d\,(N-i-1)}{N-1},
$$
and fitnesses are $f_i = 1 - w + w\,\pi_A(i)$ and $g_i = 1 - w + w\,\pi_B(i)$, where $w \in [0,1]$ is the *intensity of selection* ($w \to 0$ is *weak selection*, $w = 1$ *strong*). In each elementary step one individual is chosen to reproduce with probability proportional to its fitness, its offspring replaces a uniformly chosen individual, and $i$ changes by at most one. The resulting birth--death chain on $\{0,1,\dots,N\}$ has absorbing states $0$ and $N$ and transition probabilities
$$
p_{i,i+1} = \frac{i f_i}{i f_i + (N-i) g_i}\cdot\frac{N-i}{N},
\qquad
p_{i,i-1} = \frac{(N-i) g_i}{i f_i + (N-i) g_i}\cdot\frac{i}{N}.
$$

**Theorem 5.13 (Fixation probability).** The probability that a single $A$ mutant introduced into a resident $B$ population reaches fixation is
$$
\rho_A \;=\; \frac{1}{\,1 + \displaystyle\sum_{k=1}^{N-1}\ \prod_{j=1}^{k} \frac{g_j}{f_j}\,}. \tag{5.6}
$$
[@nowak2006book, eq. (6.20)] Under neutrality ($w = 0$, so $f_j = g_j = 1$) this reduces to the *neutral benchmark* $\rho_A = 1/N$. A mutant is said to be *favoured by selection* if $\rho_A > 1/N$.

*Proof.* For a birth--death chain with absorbing boundaries the ratio $\gamma_i := p_{i,i-1}/p_{i,i+1}$ equals $g_i/f_i$ (the $N$-dependent factors cancel), and the classical gambler's-ruin formula gives $\rho_A = \bigl(1 + \sum_{k=1}^{N-1}\prod_{j=1}^{k}\gamma_j\bigr)^{-1}$. $\square$

**Theorem 5.14 (The $1/3$ law; Nowak, Sasaki, Taylor and Fudenberg 2004).** Let the two-strategy game be a *coordination game*, i.e. $a > c$ and $d > b$, so that the replicator dynamics has an unstable interior equilibrium at
$$
x^{*} \;=\; \frac{d-b}{(a-c)+(d-b)}
$$
(the frequency of $A$ at which the two types earn equally). Then, for weak selection and large $N$,
$$
\rho_A \;>\; \frac1N \quad\Longleftrightarrow\quad x^{*} \;<\; \frac13 .
$$
[@nowaksasakitaylorfudenberg2004]

The result is initially surprising --- the naive guess would be $x^* < 1/2$ --- and its source is that a mutant lineage on its way to fixation spends its time at low frequencies, so it experiences the payoff environment weighted towards the resident. Applied to the $\mathrm{ALLD}$--$\mathrm{TFT}$ edge of Section 5.3, with $A = \mathrm{TFT}$ and $B = \mathrm{ALLD}$, the barrier is $x^{*} = \sigma/(\sigma+\Delta)$ from (5.5); at $\delta = 0.9$ and $(5,3,1,0)$ this is $1/17 \ll 1/3$, so a single $\mathrm{TFT}$ mutant in an $\mathrm{ALLD}$ population is favoured by selection in a finite population even though the replicator dynamics of Theorem 5.9 sends it to extinction. Finite-population stochasticity is thus a *mechanism for cooperation* in its own right --- the discrepancy between (5.6) and (5.1) is not an approximation error but a genuinely different prediction.

## Spatial structure: the Nowak--May lattice

Cooperation can also be rescued by giving the population geometry, so that cooperators interact disproportionately with cooperators. The canonical demonstration is due to Nowak and May [@nowakmay1992; @nowakmay1993].

**Definition 5.15 (Nowak--May spatial game).** Sites of an $L \times L$ square lattice (periodic or fixed boundary) are each occupied by one player of type $C$ or $D$. Payoffs are the *weak dilemma* of Definition 2.12: $R = 1$, $T = b$, $P = S = 0$, with $1 < b < 2$. In each generation:

1. **Scoring.** Every player plays one round against each of its eight nearest neighbours (Moore neighbourhood) *and against itself*, and accumulates the nine payoffs.
2. **Updating.** Synchronously, every site adopts the strategy of the highest-scoring player in its own $3\times 3$ neighbourhood (itself included); ties are resolved in favour of the incumbent.

Because $P = S = 0$, the scores take a particularly simple form. Write $\nu(z)$ for the number of cooperators among the nine cells of $z$'s $3\times3$ neighbourhood. Then
$$
\mathrm{score}(z) = \nu(z) \quad\text{if } z \text{ is } C, \qquad
\mathrm{score}(z) = b\,\nu(z) \quad\text{if } z \text{ is } D. \tag{5.7}
$$
(A cooperator's own self-interaction contributes $R = 1$ and is counted in $\nu$; a defector's contributes $P=0$ and is not.) All thresholds below follow from (5.7) by counting.

**Proposition 5.16 (A lone defector).** Let a single $D$ sit in an otherwise all-$C$ lattice.

1. The defector always survives: its score is $8b$, the largest score in its own neighbourhood, since its eight neighbours are cooperators with $\nu = 8$ and $8b > 8$.
2. Its eight neighbours convert to $D$ if and only if $b > 9/8$. Hence for $1 < b < 9/8$ the lone defector is frozen forever; for $b > 9/8$ it grows into a $3\times3$ block of defectors in a single generation.

*Proof.* Put the defector at the origin. A cooperator $z$ adjacent to it (orthogonally or diagonally) has $\nu(z) = 8$, hence score $8$. Its own $3\times3$ neighbourhood contains the defector, with score $8b$; it also contains at least one cooperator at Chebyshev distance $2$ from the origin, whose neighbourhood excludes the origin and which therefore has score $9$. (For an orthogonal neighbour at $(0,1)$ take the cell $(-1,2)$; for a diagonal neighbour at $(1,1)$ take $(2,2)$.) No cooperator can score more than $9$. So the maximum in $z$'s neighbourhood is $\max\{8b, 9\}$, and $z$ becomes $D$ exactly when $8b > 9$. $\square$

**Proposition 5.17 (A $3\times3$ block of defectors).** Let a $3\times3$ block of $D$ occupy rows and columns $0,1,2$ of an otherwise all-$C$ lattice. Using (5.7), the relevant scores are:

| site | $\nu$ | score |
|:--|:--:|:--|
| block corner, e.g. $(0,0)$ ($D$) | $5$ | $5b$ |
| block edge-centre, e.g. $(0,1)$ ($D$) | $3$ | $3b$ |
| block centre $(1,1)$ ($D$) | $0$ | $0$ |
| $C$ diagonally off a block corner, $(-1,-1)$ | $8$ | $8$ |
| $C$ orthogonally off a block corner, $(-1,0)$ | $7$ | $7$ |
| $C$ orthogonally off a block edge-centre, $(-1,1)$ | $6$ | $6$ |
| $C$ at Chebyshev distance $\ge 2$ from the block | $9$ | $9$ |

Consequently:

1. **The block expands if and only if $b > 9/5 = 1.8$.** Every cooperator adjacent to the block has a score-$9$ cooperator in its own neighbourhood, and the largest defector score available to it is $5b$ (contributed by a block corner). Hence such a cooperator flips iff $5b > 9$.
2. **The block's corners survive if and only if $b > 8/5 = 1.6$.** The corner $(0,0)$ sees a maximum cooperator score of $8$ (from the diagonal cooperator at $(-1,-1)$) and a maximum defector score of $5b$ (itself); it stays $D$ iff $5b > 8$.
3. **The block's edges survive if and only if $b > 7/5 = 1.4$.** The edge-centre $(0,1)$ sees a maximum cooperator score of $7$ (from $(-1,0)$ and $(-1,2)$) and a maximum defector score of $5b$; it stays $D$ iff $5b > 7$.

*Proof.* Each claim is the comparison of the largest $C$-score with the largest $D$-score in the relevant $3\times3$ neighbourhood, read off the table.

For (1): the cooperator at $(-1,1)$ has neighbourhood rows $-2..0$, columns $0..2$, containing the defectors $(0,0),(0,1),(0,2)$ with scores $5b,3b,5b$ and the cooperators $(-2,0),(-2,1),(-2,2)$ with score $9$. The cooperator at $(-1,-1)$ has neighbourhood rows $-2..0$, columns $-2..0$, containing the single defector $(0,0)$ with score $5b$ and cooperators of score up to $9$. In both cases the condition is $5b > 9$; by symmetry the same holds around the whole block.

For (2): $(0,0)$'s neighbourhood is rows $-1..1$, columns $-1..1$, containing cooperators $(-1,-1),(-1,0),(-1,1),(0,-1),(1,-1)$ of scores $8,7,6,7,7$ and defectors $(0,0),(0,1),(1,0),(1,1)$ of scores $5b,3b,3b,0$.

For (3): $(0,1)$'s neighbourhood is rows $-1..1$, columns $0..2$, containing cooperators $(-1,0),(-1,1),(-1,2)$ of scores $7,6,7$ and defectors $(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)$ of scores $5b,3b,5b,3b,0,3b$. $\square$

**Proposition 5.18 (A straight interface, and the role of $b = 2$).** Let the half-plane of rows $\le -1$ be all $D$ and rows $\ge 0$ all $C$. Then row-$0$ cooperators score $6$, cooperators in rows $\ge 1$ score $9$, row-$(-1)$ defectors score $3b$, and defectors in rows $\le -2$ score $0$. Consequently:

1. The cooperative front never retreats: a row-$0$ cooperator sees a maximum cooperator score of $9$ and a maximum defector score of $3b < 6 < 9$.
2. The cooperative front advances --- the row-$(-1)$ defectors convert --- if and only if $6 > 3b$, i.e. $b < 2$.

*Proof.* Direct from (5.7): a row-$0$ cooperator has three defectors among its nine cells so $\nu = 6$; a row-$(-1)$ defector has three cooperators so $\nu=3$. A row-$0$ cooperator's neighbourhood spans rows $-1..1$ and hence contains row-$1$ cooperators of score $9$; a row-$(-1)$ defector's neighbourhood spans rows $-2..0$ and hence contains row-$0$ cooperators of score $6$, while the best defector score in it is $3b$. $\square$

**Remark 5.19 (Why $1 < b < 2$ is the interesting window).** The upper limit has two independent meanings that happen to coincide. Algebraically, $b<2$ is condition (2.2), $2R > T+S$, without which mutual cooperation is not the efficient outcome. Dynamically, Proposition 5.18 shows $b<2$ is exactly the condition for a flat cooperative front to advance into a defector region. The lower limit $b>1$ is $T > R$, without which there is no dilemma at all. Inside the window, Propositions 5.16--5.18 give a coherent picture of the two elementary processes in competition: defector clusters grow at their *corners* (needing $b > 9/5$) while cooperator regions eat into them along their *flat edges* (needing $b < 2$). For $b < 9/5$ only the second process operates, defector clusters are static or shrinking, and cooperators come to occupy most of the lattice; for $9/5 < b < 2$ both operate simultaneously, and Nowak and May's simulations from random initial conditions reveal *spatial chaos* --- a persistently churning coexistence with an asymptotic cooperator frequency close to $0.3178$, largely independent of $b$ within this range and of the initial condition [@nowakmay1992; @nowakmay1993]. The intermediate thresholds $b = 9/8$, $7/5$ and $8/5$ mark the successive appearance of frozen defector monads, static defector crosses, and static defector squares, and they are exactly the values at which the observed cooperator frequency in `pdlab.spatial` changes character.

**Remark 5.20 (Robustness).** The Nowak--May result depends on modelling choices. Huberman and Glance [@hubermanglance1993] showed that replacing synchronous updating by asynchronous (continuous-time) updating destroys the chaotic coexistence and lets cooperators take over the lattice, arguing that the discrete-time lockstep is an artefact. The modern reading is that the *mechanism* --- assortment of cooperators through spatial clustering --- is robust, while the specific chaotic attractor and its $0.3178$ signature are not. Both update schemes are implemented in `pdlab.spatial` and compared in Chapter 6.

**Remark 5.21 (Nowak's five rules).** Nowak [@nowak2006fiverules] organises the mechanisms that permit cooperation in the donation game $\mathrm{Don}(b,c)$ into five conditions, each of the form "benefit-to-cost ratio exceeds something'':

* **Kin selection:** $r > c/b$, where $r$ is the coefficient of relatedness (Hamilton's rule).
* **Direct reciprocity:** $w > c/b$, where $w$ is the probability of another round --- our $\delta$; indeed for the donation game $(T-R)/(T-P) = c/b$, so Theorem 4.5 *is* this rule.
* **Indirect reciprocity:** $q > c/b$, where $q$ is the probability of knowing a co-player's reputation.
* **Network reciprocity:** $b/c > k$, where $k$ is the average number of neighbours, for evolutionary graph dynamics under weak selection [@ohtsukihauertliebermannowak2006]. On the Moore lattice $k = 8$; the Nowak--May regime, which uses strong (imitate-the-best) selection rather than weak, is a different limit of the same idea.
* **Group selection:** $b/c > 1 + n/m$, where $n$ is the group size and $m$ the number of groups.

The first four are all present in this report in one form or another: direct reciprocity in Chapter 4, network reciprocity in Section 5.5, and the finite-population analogue of assortment in Section 5.4.
