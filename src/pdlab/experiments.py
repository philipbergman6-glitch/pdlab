"""Every numerical experiment in the report, parameterised by a :class:`Scale`.

Each function returns a plain JSON-serialisable ``dict`` so results can be
written to ``results/canonical.json`` and consumed by both the figures module
and the interactive app.  ``Scale.quick()`` runs everything in seconds (used
by the test-suite); ``Scale.full()`` reproduces the report.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import sympy as sp

from pdlab import analytic
from pdlab.evolution import (
    fixation_probability,
    moran_process,
    replicator_trajectory,
)
from pdlab.finite import backward_induction
from pdlab.game import PayoffMatrix
from pdlab.learning import QLearner
from pdlab.markov import stationary_payoffs
from pdlab.match import play_match
from pdlab.spatial import SpatialPD
from pdlab.strategies import REGISTRY, MemoryOneStrategy, Strategy
from pdlab.tournament import round_robin

Result = dict[str, Any]

NOISE_LEVELS = (0.0, 0.01, 0.05, 0.1)
MEMORY_ONE_FOR_NOISE = ("TFT", "GTFT", "WSLS", "STFT", "ALLC", "ALLD", "EXTORT2", "ZDGTFT2")
ZD_EVO_SET = ("ALLC", "ALLD", "TFT", "GTFT", "WSLS", "EXTORT2", "ZDGTFT2")


@dataclass(frozen=True)
class Scale:
    rounds: int = 200
    reps: int = 10
    discount_matches: int = 4000
    noise_sim_rounds: int = 20000
    lattice: int = 100
    lattice_steps: int = 300
    lattice_seeds: int = 3
    async_lattice: int = 50
    async_steps: int = 100
    moran_runs: int = 2000
    moran_N: int = 50
    moran_steps: int = 200_000
    learner_rounds: int = 30_000
    learner_seeds: int = 5
    b_grid: int = 25
    delta_grid: int = 41
    eps_grid: int = 26

    @classmethod
    def full(cls) -> Scale:
        return cls()

    @classmethod
    def quick(cls) -> Scale:
        return cls(
            rounds=30,
            reps=2,
            discount_matches=100,
            noise_sim_rounds=500,
            lattice=20,
            lattice_steps=15,
            lattice_seeds=1,
            async_lattice=10,
            async_steps=5,
            moran_runs=50,
            moran_N=10,
            moran_steps=2000,
            learner_rounds=600,
            learner_seeds=1,
            b_grid=4,
            delta_grid=6,
            eps_grid=4,
        )


def _f(x: Any) -> Any:
    """Recursively convert numpy types for JSON."""
    if isinstance(x, dict):
        return {str(k): _f(v) for k, v in x.items()}
    if isinstance(x, list | tuple):
        return [_f(v) for v in x]
    if isinstance(x, np.ndarray):
        return _f(x.tolist())
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, sp.Basic):
        return str(x)
    return x


# --------------------------------------------------------------------------
# 1. one-shot + thresholds
# --------------------------------------------------------------------------
def exp_one_shot(pm: PayoffMatrix) -> Result:
    facts = analytic.one_shot_facts(pm)
    return _f(
        {
            "payoffs": dict(zip("TRPS", pm.as_tuple(), strict=True)),
            "matrix_row_player": pm.as_matrix(),
            "facts": asdict(facts),
            "best_responses": analytic.best_responses(pm),
            "dominance_gap": pm.dominance_gap(),
        }
    )


def exp_finite(pm: PayoffMatrix, n_max: int = 10) -> Result:
    rows = []
    for n in range(1, n_max + 1):
        path, total = backward_induction(pm, n)
        rows.append({"n": n, "all_defect": all(p == (1, 1) for p in path), "row_total": total})
    return _f({"rows": rows})


def simulate_discounted_total(
    s1: Strategy, s2: Strategy, delta: float, n_matches: int, pm: PayoffMatrix, rng: np.random.Generator
) -> tuple[float, float]:
    """Mean *unnormalised* total payoff of player 1 with geometric stopping (continuation delta)."""
    if not 0 <= delta < 1:
        raise ValueError("delta in [0,1)")
    tot = 0.0
    tot_sq = 0.0
    for _ in range(n_matches):
        rounds = int(rng.geometric(1 - delta))  # >= 1, P(n) = (1-delta) delta^(n-1)
        res = play_match(s1.clone(), s2.clone(), rounds, pm, rng)
        tot += res.score1
        tot_sq += res.score1**2
    mean = tot / n_matches
    se = float(np.sqrt(max(tot_sq / n_matches - mean**2, 0.0) / n_matches))
    return mean, se


def exp_thresholds(pm: PayoffMatrix, scale: Scale, seed: int = 1) -> Result:
    th = analytic.thresholds(pm)
    deltas = np.linspace(0.0, 0.95, scale.delta_grid)
    curves = {
        "delta": deltas,
        "V_coop": [analytic.cooperation_value(pm, d) for d in deltas],
        "V_dev_alld": [analytic.deviation_values(pm, d)["alld"] for d in deltas],
        "V_dev_alt": [analytic.deviation_values(pm, d)["alternate"] for d in deltas],
    }
    rng = np.random.default_rng(seed)
    grim, alld, tft, alt = (REGISTRY.make(k) for k in ("GRIM", "ALLD", "TFT", "STFT"))
    sim_deltas = [d for d in (0.2, 0.4, 0.5, 0.6, 2 / 3, 0.8, 0.9) if d < 1]
    sims = []
    for d in sim_deltas:
        coop, coop_se = simulate_discounted_total(grim, grim, d, scale.discount_matches, pm, rng)
        dev, dev_se = simulate_discounted_total(alld, grim, d, scale.discount_matches, pm, rng)
        # alternating deviation vs TFT: STFT (D first, then TFT) against TFT gives D,C,D,C...
        altv, alt_se = simulate_discounted_total(alt, tft, d, scale.discount_matches, pm, rng)
        sims.append(
            {
                "delta": d,
                "coop_sim": coop,
                "coop_se": coop_se,
                "coop_exact": analytic.cooperation_value(pm, d),
                "alld_sim": dev,
                "alld_se": dev_se,
                "alld_exact": analytic.deviation_values(pm, d)["alld"],
                "alt_sim": altv,
                "alt_se": alt_se,
                "alt_exact": analytic.deviation_values(pm, d)["alternate"],
            }
        )
    spe = analytic.tft_spe_conditions_symbolic()
    return _f(
        {
            "thresholds": asdict(th),
            "tft_is_spe_possible": th.tft_is_spe_possible,
            "symbolic": {
                "grim": analytic.grim_threshold_symbolic(),
                "tft_alt": analytic.tft_alt_threshold_symbolic(),
                "tft_nash": analytic.tft_nash_threshold_symbolic(),
                "tft_spe_conditions": {k: str(v) for k, v in spe.items()},
            },
            "curves": curves,
            "simulation": sims,
        }
    )


# --------------------------------------------------------------------------
# 2. tournament
# --------------------------------------------------------------------------
def exp_tournament(pm: PayoffMatrix, scale: Scale, seed: int = 2) -> Result:
    strategies = REGISTRY.make_all()
    out: Result = {"noise_levels": list(NOISE_LEVELS), "rounds": scale.rounds, "reps": scale.reps}
    boards = {}
    for k, eps in enumerate(NOISE_LEVELS):
        res = round_robin(strategies, scale.rounds, pm, noise=eps, reps=scale.reps, seed=seed + k)
        df = res.scores()
        boards[str(eps)] = df.to_dict(orient="records")
        if eps == 0.0:
            out["payoff_matrix"] = {"names": list(res.names), "values": res.mean_payoff}
            out["coop_matrix"] = res.coop.mean(axis=0)
    out["leaderboards"] = boards
    return _f(out)


# --------------------------------------------------------------------------
# 3. noise: exact vs simulated self-play
# --------------------------------------------------------------------------
def exp_noise_selfplay(pm: PayoffMatrix, scale: Scale, seed: int = 3) -> Result:
    eps_grid = np.linspace(0.001, 0.25, scale.eps_grid)
    rng = np.random.default_rng(seed)
    out: Result = {"eps": eps_grid, "strategies": {}}
    sim_eps = [0.01, 0.05, 0.1, 0.2]
    for name in MEMORY_ONE_FOR_NOISE:
        s = REGISTRY.make(name)
        assert isinstance(s, MemoryOneStrategy) and s.memory_one is not None
        p = s.memory_one
        exact = [stationary_payoffs(p, p, pm, e)[0] for e in eps_grid]
        sims = []
        for e in sim_eps:
            r = play_match(s.clone(), s.clone(), scale.noise_sim_rounds, pm, rng, noise=e)
            sims.append({"eps": e, "sim": (r.mean1 + r.mean2) / 2})
        sym = analytic.self_play_noise_symbolic(tuple(sp.nsimplify(v) for v in p))
        series = sp.series(sym.subs({analytic.T: pm.T, analytic.R: pm.R, analytic.P: pm.P, analytic.S: pm.S}), analytic.eps, 0, 2).removeO()
        out["strategies"][name] = {
            "p": p,
            "exact": exact,
            "sim": sims,
            "symbolic": sp.factor(sym),
            "series_axelrod": series,
            "eps0_limit": float(sp.limit(sym.subs({analytic.T: pm.T, analytic.R: pm.R, analytic.P: pm.P, analytic.S: pm.S}), analytic.eps, 0)),
            "noiseless": float(stationary_payoffs(p, p, pm, 1e-9)[0]),
        }
    return _f(out)


# --------------------------------------------------------------------------
# 4. replicator dynamics ALLC / ALLD / TFT
# --------------------------------------------------------------------------
def exp_replicator(pm: PayoffMatrix, delta: float = 0.9, t_max: float = 60.0) -> Result:
    A = analytic.payoff_matrix_3(pm, delta)
    xstar = analytic.tft_invasion_threshold(pm, delta)
    fps = {
        "ALLC": [1, 0, 0],
        "ALLD": [0, 1, 0],
        "TFT": [0, 0, 1],
        "TFT_ALLD_edge": [0, 1 - xstar, xstar],
    }
    eig = {k: analytic.jacobian_eigenvalues(np.array(v, dtype=float), A) for k, v in fps.items()}
    eig_sym = {k: analytic.jacobian_eigenvalues_symbolic(k) for k in fps}
    # trajectories from a fan of initial conditions
    inits = []
    for a in np.linspace(0.05, 0.9, 6):
        for c in np.linspace(0.02, 0.9, 6):
            if a + c < 0.98:
                inits.append([a, 1 - a - c, c])
    trajs = []
    for x0 in inits:
        tr = replicator_trajectory(A, x0, t_max, n_points=300)
        trajs.append({"x0": x0, "t": tr.t, "x": tr.x, "final": tr.x[-1]})
    # convergence rate near ALLD: x_TFT(t) ~ exp(lambda t), lambda = A[2,1]-A[1,1]
    x0 = [0.0, 1 - xstar * 0.5, xstar * 0.5]
    tr = replicator_trajectory(A, x0, 80.0, n_points=400)
    mask = (tr.t > 20) & (tr.x[:, 2] > 1e-12)
    slope = float(np.polyfit(tr.t[mask], np.log(tr.x[mask, 2]), 1)[0])
    ess = {analytic.STRATS3[i]: analytic.is_ess(A, i) for i in range(3)}
    nss = {analytic.STRATS3[i]: analytic.is_neutrally_stable(A, i) for i in range(3)}
    return _f(
        {
            "delta": delta,
            "A": A,
            "x_star": xstar,
            "x_star_symbolic": analytic.tft_invasion_threshold_symbolic(),
            "fixed_points": fps,
            "eigenvalues": {k: [complex(e).real for e in v] for k, v in eig.items()},
            "eigenvalues_symbolic": eig_sym,
            "ess": ess,
            "neutrally_stable": nss,
            "trajectories": trajs,
            "convergence": {
                "x0": x0,
                "fitted_rate": slope,
                "predicted_rate": float(A[2, 1] - A[1, 1]),
                "t": tr.t,
                "x_tft": tr.x[:, 2],
            },
        }
    )


# --------------------------------------------------------------------------
# 5. Moran process
# --------------------------------------------------------------------------
def exp_moran_fixation(pm: PayoffMatrix, scale: Scale, delta: float = 0.9, seed: int = 5) -> Result:
    A = analytic.payoff_matrix_3(pm, delta)
    rng = np.random.default_rng(seed)
    Ns = [4, 6, 8, 12, 16, 24, 32]
    rows = []
    for N in Ns:
        exact = fixation_probability(A, mutant=2, resident=1, N=N, w=1.0)
        neutral = 1 / N
        wins = 0
        runs = scale.moran_runs
        for _ in range(runs):
            counts = np.zeros(3, dtype=int)
            counts[1], counts[2] = N - 1, 1
            r = moran_process(A, counts, steps=200 * N * N, rng=rng, w=1.0)
            if r.fixated == 2:
                wins += 1
        rows.append({"N": N, "exact": exact, "neutral": neutral, "sim": wins / runs, "runs": runs})
    return _f({"delta": delta, "rows": rows})


def _dominant(freqs: np.ndarray, names: list[str]) -> str:
    return names[int(np.argmax(freqs))]


def exp_moran_mutation(tournament: Result, scale: Scale, seed: int = 6) -> Result:
    """Long-run Moran process over the full strategy set with mutation."""
    names: list[str] = tournament["payoff_matrix"]["names"]
    A = np.array(tournament["payoff_matrix"]["values"])
    coopM = np.array(tournament["coop_matrix"])
    n = len(names)
    N = scale.moran_N
    mus = [0.0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3]
    rows = []
    for mu in mus:
        rng = np.random.default_rng(seed)
        counts = np.full(n, N // n)
        counts[0] += N - counts.sum()
        r = moran_process(A, counts, scale.moran_steps, rng, w=1.0, mutation=mu, stop_at_fixation=False)
        f = r.frequencies[len(r.frequencies) // 2 :]  # discard burn-in
        mean_f = f.mean(axis=0)
        mean_payoff = float(mean_f @ A @ mean_f)
        coop = float(mean_f @ coopM @ mean_f)
        rows.append(
            {
                "mu": mu,
                "mean_freq": mean_f,
                "dominant": _dominant(mean_f, names),
                "mean_payoff": mean_payoff,
                "coop_rate": coop,
            }
        )
    return _f({"names": names, "N": N, "rows": rows})


def exp_evolution_noise(pm: PayoffMatrix, scale: Scale, seed: int = 7) -> Result:
    """Which strategy dominates the Moran process as implementation noise rises?"""
    strategies = REGISTRY.make_all()
    names = [s.name for s in strategies]
    eps_levels = [0.0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.15]
    rows = []
    for k, e in enumerate(eps_levels):
        res = round_robin(strategies, scale.rounds, pm, noise=e, reps=max(1, scale.reps // 2), seed=seed + k)
        A = res.mean_payoff
        rng = np.random.default_rng(seed)
        n = len(names)
        counts = np.full(n, scale.moran_N // n)
        counts[0] += scale.moran_N - counts.sum()
        r = moran_process(A, counts, scale.moran_steps, rng, w=1.0, mutation=0.01, stop_at_fixation=False)
        f = r.frequencies[len(r.frequencies) // 2 :].mean(axis=0)
        rows.append({"eps": e, "mean_freq": f, "dominant": _dominant(f, names), "mean_payoff": float(f @ A @ f)})
    return _f({"names": names, "rows": rows})


# --------------------------------------------------------------------------
# 6. spatial
# --------------------------------------------------------------------------
def exp_spatial(scale: Scale, seed: int = 8) -> Result:
    bs = np.linspace(1.05, 1.99, scale.b_grid)
    phase = []
    tail = max(1, scale.lattice_steps // 3)
    for b in bs:
        vals = []
        for s in range(scale.lattice_seeds):
            rng = np.random.default_rng(seed + s)
            g = SpatialPD.random(scale.lattice, float(b), 0.9, rng)
            ser, _ = g.run(scale.lattice_steps)
            vals.append(ser[-tail:].mean())
        phase.append({"b": float(b), "coop_mean": float(np.mean(vals)), "coop_sd": float(np.std(vals))})
    # time series & snapshots at b = 1.9
    rng = np.random.default_rng(seed)
    g = SpatialPD.random(scale.lattice, 1.9, 0.9, rng)
    series, snaps = g.run(scale.lattice_steps, snapshots=6)
    # kaleidoscope: single defector, fixed boundary
    L = scale.lattice - 1 if scale.lattice % 2 == 0 else scale.lattice
    k = SpatialPD.single_defector(L, 1.9, periodic=False)
    kser, ksnaps = k.run(scale.lattice_steps, snapshots=6)
    # initial-condition independence at b = 1.9
    init_rows = []
    for f0 in (0.3, 0.5, 0.7, 0.9, 0.99):
        rng = np.random.default_rng(seed)
        gg = SpatialPD.random(scale.lattice, 1.9, f0, rng)
        ser, _ = gg.run(scale.lattice_steps)
        init_rows.append({"f0": f0, "coop_final": float(ser[-tail:].mean())})
    # synchronous vs asynchronous (Huberman & Glance)
    rng = np.random.default_rng(seed)
    a_sync = SpatialPD.random(scale.async_lattice, 1.9, 0.9, rng)
    sync_ser, _ = a_sync.run(scale.async_steps)
    rng = np.random.default_rng(seed)
    a_async = SpatialPD.random(scale.async_lattice, 1.9, 0.9, rng)
    async_ser, _ = a_async.run(scale.async_steps, rng=np.random.default_rng(seed + 1), asynchronous=True)
    return _f(
        {
            "phase": phase,
            "b_star_published": 0.318,
            "coop_1p8_2": float(np.mean([r["coop_mean"] for r in phase if 1.8 < r["b"] < 2.0])) if any(1.8 < r["b"] < 2 for r in phase) else None,
            "series_b1p9": series,
            "snapshots_b1p9": [s.astype(int) for s in snaps],
            "kaleidoscope_series": kser,
            "kaleidoscope_snapshots": [s.astype(int) for s in ksnaps],
            "init_independence": init_rows,
            "sync_vs_async": {"sync": sync_ser, "async": async_ser, "L": scale.async_lattice},
        }
    )


# --------------------------------------------------------------------------
# 7. zero-determinant strategies
# --------------------------------------------------------------------------
def exp_zd(pm: PayoffMatrix, scale: Scale, seed: int = 9) -> Result:
    ext = REGISTRY.make("EXTORT2")
    gen = REGISTRY.make("ZDGTFT2")
    assert isinstance(ext, MemoryOneStrategy) and isinstance(gen, MemoryOneStrategy)
    assert ext.memory_one is not None and gen.memory_one is not None
    # (a) exact payoffs of Extort-2 vs every memory-one strategy + random opponents
    rng = np.random.default_rng(seed)
    scatter = []
    for name in MEMORY_ONE_FOR_NOISE:
        s = REGISTRY.make(name)
        assert isinstance(s, MemoryOneStrategy) and s.memory_one is not None
        sx, sy = stationary_payoffs(ext.memory_one, s.memory_one, pm, 0.01)
        scatter.append({"opponent": name, "s_X": sx, "s_Y": sy})
    for _ in range(40):
        q = rng.random(4)
        sx, sy = stationary_payoffs(ext.memory_one, q, pm, 0.0)
        scatter.append({"opponent": "random", "s_X": sx, "s_Y": sy})
    # (b) Extort-2 vs Q-learner over time
    learner_runs = []
    for k in range(scale.learner_seeds):
        rng = np.random.default_rng(seed + 10 + k)
        for opp_name, opp in (("EXTORT2", ext), ("ZDGTFT2", gen), ("TFT", REGISTRY.make("TFT"))):
            q = QLearner(alpha=0.05, gamma=0.9, explore=0.2, explore_decay=0.9997, persist=True)
            res = play_match(q, opp.clone(), scale.learner_rounds, pm, rng)
            w = max(1, scale.learner_rounds // 100)
            m1 = np.array([pm.payoff(a, b) for a, b in zip(res.moves1, res.moves2, strict=True)])
            m2 = np.array([pm.payoff(b, a) for a, b in zip(res.moves1, res.moves2, strict=True)])
            coop = np.array([a.value == "C" for a in res.moves1], dtype=float)
            nb = len(m1) // w
            learner_runs.append(
                {
                    "seed": k,
                    "opponent": opp_name,
                    "t": (np.arange(nb) + 1) * w,
                    "learner_payoff": m1[: nb * w].reshape(nb, w).mean(axis=1),
                    "opponent_payoff": m2[: nb * w].reshape(nb, w).mean(axis=1),
                    "learner_coop": coop[: nb * w].reshape(nb, w).mean(axis=1),
                    "final_learner": float(m1[-len(m1) // 5 :].mean()),
                    "final_opponent": float(m2[-len(m2) // 5 :].mean()),
                    "final_policy": q.greedy_policy(),
                }
            )
    # (c) evolution among memory-one strategies incl. ZD (exact payoffs, small noise)
    names = list(ZD_EVO_SET)
    vecs = []
    for nm in names:
        s = REGISTRY.make(nm)
        assert isinstance(s, MemoryOneStrategy) and s.memory_one is not None
        vecs.append(s.memory_one)
    A = np.array([[stationary_payoffs(p, q, pm, 0.01)[0] for q in vecs] for p in vecs])
    n = len(names)
    x0 = np.full(n, 1 / n)
    tr = replicator_trajectory(A, x0, 300.0, n_points=300)
    rng = np.random.default_rng(seed)
    counts = np.full(n, scale.moran_N // n)
    counts[0] += scale.moran_N - counts.sum()
    mr = moran_process(A, counts, scale.moran_steps, rng, w=1.0, mutation=0.01, stop_at_fixation=False)
    mf = mr.frequencies[len(mr.frequencies) // 2 :].mean(axis=0)
    return _f(
        {
            "extort2": ext.memory_one,
            "zdgtft2": gen.memory_one,
            "chi": 2.0,
            "scatter": scatter,
            "learner": learner_runs,
            "evolution": {
                "names": names,
                "A": A,
                "replicator_t": tr.t,
                "replicator_x": tr.x,
                "replicator_final": tr.x[-1],
                "moran_mean_freq": mf,
                "moran_dominant": _dominant(mf, names),
            },
        }
    )


# --------------------------------------------------------------------------
def run_all(scale: Scale, pm: PayoffMatrix | None = None) -> Result:
    pm = pm or PayoffMatrix.axelrod()
    out: Result = {"scale": asdict(scale), "payoffs": dict(zip("TRPS", pm.as_tuple(), strict=True))}
    out["one_shot"] = exp_one_shot(pm)
    out["finite"] = exp_finite(pm)
    out["thresholds"] = exp_thresholds(pm, scale)
    out["tournament"] = exp_tournament(pm, scale)
    out["noise_selfplay"] = exp_noise_selfplay(pm, scale)
    out["replicator"] = exp_replicator(pm)
    out["moran_fixation"] = exp_moran_fixation(pm, scale)
    out["moran_mutation"] = exp_moran_mutation(out["tournament"], scale)
    out["evolution_noise"] = exp_evolution_noise(pm, scale)
    out["spatial"] = exp_spatial(scale)
    out["zd"] = exp_zd(pm, scale)
    return out
