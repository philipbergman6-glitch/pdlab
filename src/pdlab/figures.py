"""Publication-quality figures generated from the canonical results dict."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from pdlab.game import PayoffMatrix  # noqa: E402

COOP = "#2A6F97"
DEFECT = "#C9463D"
ACCENT = "#E0A458"
INK = "#1F2933"
MUTED = "#8A94A6"
PALETTE = [COOP, DEFECT, ACCENT, "#5B8C5A", "#7B5EA7", "#3EA5A5", "#B85C8C", "#6E7B8B"]
LATTICE_CMAP = ListedColormap([DEFECT, COOP])


def setup_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 110,
            "savefig.dpi": 220,
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.prop_cycle": matplotlib.cycler(color=PALETTE),
            "xtick.color": INK,
            "ytick.color": INK,
            "legend.frameon": False,
            "legend.fontsize": 9,
            "grid.color": "#E4E7EB",
            "grid.linewidth": 0.6,
            "axes.grid": True,
            "axes.axisbelow": True,
        }
    )


def save(fig: Figure, out_dir: Path, name: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("pdf", "png"):
        p = out_dir / f"{name}.{ext}"
        fig.savefig(p, bbox_inches="tight")
        paths.append(p)
    plt.close(fig)
    return paths


# --------------------------------------------------------------------------
def fig_folk_theorem(pm: PayoffMatrix, out: Path) -> list[Path]:
    pts = {"(C,C)": (pm.R, pm.R), "(C,D)": (pm.S, pm.T), "(D,C)": (pm.T, pm.S), "(D,D)": (pm.P, pm.P)}
    hull = [pts["(C,C)"], pts["(C,D)"], pts["(D,D)"], pts["(D,C)"]]
    fig, ax = plt.subplots(figsize=(5, 4.6))
    poly = np.array(hull + [hull[0]])
    ax.fill(poly[:, 0], poly[:, 1], color=MUTED, alpha=0.18, label="feasible set $F$")
    ax.plot(poly[:, 0], poly[:, 1], color=INK, lw=1)
    # individually rational region: feasible and both payoffs >= P
    m = pm.P
    xs = np.linspace(m, pm.R, 200)
    # upper boundary of F for x in [P, R]: line from (P,P)? boundary is (S,T)-(R,R) edge for x<R
    # compute polygon clip numerically
    from matplotlib.path import Path as MplPath

    path = MplPath(poly)
    grid_x, grid_y = np.meshgrid(np.linspace(pm.S, pm.T, 400), np.linspace(pm.S, pm.T, 400))
    inside = path.contains_points(np.c_[grid_x.ravel(), grid_y.ravel()]).reshape(grid_x.shape)
    ir = inside & (grid_x >= m) & (grid_y >= m)
    ax.contourf(grid_x, grid_y, ir.astype(float), levels=[0.5, 1.5], colors=[COOP], alpha=0.35)
    ax.plot([], [], color=COOP, lw=8, alpha=0.35, label="feasible & individually rational")
    for k, (x, y) in pts.items():
        ax.scatter([x], [y], color=INK, zorder=5, s=28)
        ax.annotate(k, (x, y), textcoords="offset points", xytext=(6, 6), fontsize=9)
    ax.axvline(m, color=DEFECT, ls="--", lw=1)
    ax.axhline(m, color=DEFECT, ls="--", lw=1)
    ax.text(m + 0.08, pm.T - 0.3, "minmax $= P$", color=DEFECT, fontsize=9)
    ax.set_xlabel("player 1 payoff")
    ax.set_ylabel("player 2 payoff")
    ax.set_title("Feasible and individually rational payoffs")
    ax.set_aspect("equal")
    ax.legend(loc="upper right")
    del xs
    return save(fig, out, "folk_theorem")


def fig_thresholds(res: dict[str, Any], out: Path) -> list[Path]:
    """Normalised values (1-delta) V so every curve is a per-round payoff."""
    c = res["curves"]
    d = np.array(c["delta"])
    th = res["thresholds"]
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.plot(d, (1 - d) * np.array(c["V_coop"]), color=COOP, lw=2, label=r"cooperate forever: $R$")
    ax.plot(d, (1 - d) * np.array(c["V_dev_alld"]), color=DEFECT, lw=2, label=r"defect forever vs Grim/TFT: $(1-\delta)T+\delta P$")
    ax.plot(d, (1 - d) * np.array(c["V_dev_alt"]), color=ACCENT, lw=2, label=r"alternate vs TFT: $(T+\delta S)/(1+\delta)$")
    for s in res["simulation"]:
        f = 1 - s["delta"]
        ax.errorbar(s["delta"], f * s["coop_sim"], yerr=2 * f * s["coop_se"], fmt="o", color=COOP, ms=4, capsize=2)
        ax.errorbar(s["delta"], f * s["alld_sim"], yerr=2 * f * s["alld_se"], fmt="s", color=DEFECT, ms=4, capsize=2)
        ax.errorbar(s["delta"], f * s["alt_sim"], yerr=2 * f * s["alt_se"], fmt="^", color=ACCENT, ms=4, capsize=2)
    ax.axvline(th["grim_spe"], color=DEFECT, ls=":", lw=1)
    ax.axvline(th["tft_vs_alternate"], color=ACCENT, ls=":", lw=1)
    ax.text(th["grim_spe"] + 0.01, 1.3, r"$\delta^*_{\mathrm{Grim}}=%.2f$" % th["grim_spe"], color=DEFECT, fontsize=9)
    ax.text(th["tft_vs_alternate"] + 0.01, 1.0, r"$\delta^*_{\mathrm{TFT}}=%.2f$" % th["tft_vs_alternate"], color=ACCENT, fontsize=9)
    ax.set_ylim(0.5, 5.2)
    ax.set_xlabel(r"discount factor $\delta$")
    ax.set_ylabel(r"normalised payoff $(1-\delta)\,V$")
    ax.set_title("Cooperation vs. deviation (lines: exact; markers: geometric-stopping simulation, $\pm 2$ s.e.)")
    ax.legend(loc="upper right")
    return save(fig, out, "thresholds")


def fig_tournament(res: dict[str, Any], out: Path) -> list[Path]:
    paths = []
    board = res["leaderboards"]["0.0"]
    names = [r["strategy"] for r in board]
    scores = [r["score"] for r in board]
    sds = [r["score_sd"] for r in board]
    coop = [r["coop_rate"] for r in board]
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    colors = [plt.get_cmap("RdBu")(0.15 + 0.7 * c) for c in coop]
    ax.barh(names[::-1], scores[::-1], xerr=sds[::-1], color=colors[::-1], edgecolor=INK, lw=0.4)
    ax.set_xlabel("mean payoff per round (all opponents incl. self)")
    ax.set_title(f"Round-robin tournament, {res['rounds']} rounds, {res['reps']} reps, no noise")
    ax.axvline(3, color=MUTED, ls="--", lw=1)
    ax.text(3.02, 0.2, "R = 3", color=MUTED, fontsize=8)
    ax.set_xlim(0, 4)
    sm = plt.cm.ScalarMappable(cmap="RdBu", norm=plt.Normalize(0, 1))
    cb = fig.colorbar(sm, ax=ax, fraction=0.04, pad=0.02)
    cb.set_label("cooperation rate")
    paths += save(fig, out, "tournament_leaderboard")

    pm = res["payoff_matrix"]
    M = np.array(pm["values"])
    order = [pm["names"].index(n) for n in names]
    M = M[np.ix_(order, order)]
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(M, cmap="viridis", vmin=0, vmax=5)
    ax.set_xticks(range(len(names)), names, rotation=90, fontsize=8)
    ax.set_yticks(range(len(names)), names, fontsize=8)
    ax.grid(False)
    for i in range(len(names)):
        for j in range(len(names)):
            ax.text(j, i, f"{M[i, j]:.1f}", ha="center", va="center", fontsize=5.5, color="white" if M[i, j] < 3 else "black")
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02, label="row payoff per round vs column")
    ax.set_title("Pairwise payoff matrix (row vs column), no noise")
    paths += save(fig, out, "tournament_matrix")

    # rank vs noise bump chart
    levels = [str(e) for e in res["noise_levels"]]
    fig, ax = plt.subplots(figsize=(6.4, 5))
    ranks: dict[str, list[int]] = {}
    for lv in levels:
        for r in res["leaderboards"][lv]:
            ranks.setdefault(r["strategy"], []).append(r["rank"])
    for k, (nm, rk) in enumerate(sorted(ranks.items(), key=lambda kv: kv[1][0])):
        col = PALETTE[k % len(PALETTE)]
        ax.plot(range(len(levels)), rk, "-o", color=col, lw=1.4, ms=4, alpha=0.9)
        ax.text(-0.15, rk[0], nm, ha="right", va="center", fontsize=7.5, color=col)
        ax.text(len(levels) - 1 + 0.15, rk[-1], nm, ha="left", va="center", fontsize=7.5, color=col)
    ax.set_xticks(range(len(levels)), [rf"$\varepsilon$={lv}" for lv in levels])
    ax.invert_yaxis()
    ax.set_ylabel("rank")
    ax.set_xlim(-1.2, len(levels) - 1 + 1.2)
    ax.set_title("Tournament rank as implementation noise increases")
    paths += save(fig, out, "tournament_noise_ranks")
    return paths


def fig_noise_selfplay(res: dict[str, Any], out: Path) -> list[Path]:
    eps = np.array(res["eps"])
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    for k, (nm, d) in enumerate(res["strategies"].items()):
        col = PALETTE[k % len(PALETTE)]
        ax.plot(eps, d["exact"], color=col, lw=2, label=nm)
        ax.scatter([s["eps"] for s in d["sim"]], [s["sim"] for s in d["sim"]], color=col, s=22, zorder=5, edgecolor="white", lw=0.5)
    ax.set_xlabel(r"implementation error rate $\varepsilon$")
    ax.set_ylabel("self-play payoff per round")
    ax.set_title("Exact stationary payoff (lines) vs simulation (dots) in self-play")
    ax.legend(ncol=2)
    return save(fig, out, "noise_selfplay")


def _tern(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Project (ALLC, ALLD, TFT) onto the triangle with corners (0,0), (1,0), (1/2, sqrt3/2)."""
    x = np.asarray(x)
    return x[..., 1] + 0.5 * x[..., 2], (np.sqrt(3) / 2) * x[..., 2]


def fig_replicator(res: dict[str, Any], out: Path) -> list[Path]:
    fig, ax = plt.subplots(figsize=(6, 5.4))
    tri = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=float)
    tx, ty = _tern(tri)
    ax.plot(tx, ty, color=INK, lw=1.2)
    for tr in res["trajectories"]:
        px, py = _tern(np.array(tr["x"]))
        ax.plot(px, py, color=MUTED, lw=0.8, alpha=0.8)
        # arrow at 1/4 of the way
        i = len(px) // 6
        ax.annotate("", xy=(px[i + 1], py[i + 1]), xytext=(px[i], py[i]), arrowprops={"arrowstyle": "->", "color": MUTED, "lw": 0.8})
        fx, fy = _tern(np.array(tr["final"]))
        ax.scatter([fx], [fy], color=COOP if tr["final"][1] < 0.5 else DEFECT, s=10, zorder=4)
    for name, fp in res["fixed_points"].items():
        fx, fy = _tern(np.array(fp, dtype=float))
        ax.scatter([fx], [fy], color=ACCENT if "edge" in name else INK, s=60, zorder=6, edgecolor="white")
    ax.text(-0.02, -0.05, "ALLC", ha="center", fontsize=10)
    ax.text(1.02, -0.05, "ALLD", ha="center", fontsize=10)
    ax.text(0.5, np.sqrt(3) / 2 + 0.03, "TFT", ha="center", fontsize=10)
    xs = res["x_star"]
    ex, ey = _tern(np.array([0, 1 - xs, xs]))
    ax.annotate(rf"$x^*_{{TFT}}={xs:.3f}$", (ex, ey), xytext=(0.62, 0.18), fontsize=9, color=ACCENT, arrowprops={"arrowstyle": "->", "color": ACCENT})
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(rf"Replicator dynamics, $\delta={res['delta']}$: bistability between ALLD and the ALLC–TFT edge")
    paths = save(fig, out, "replicator_simplex")

    c = res["convergence"]
    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    t = np.array(c["t"])
    x = np.array(c["x_tft"])
    ax.semilogy(t, x, color=COOP, lw=2, label="$x_{TFT}(t)$ (numerical)")
    ax.semilogy(t, x[0] * np.exp(c["predicted_rate"] * t), color=DEFECT, ls="--", lw=1.4, label=rf"$e^{{\lambda t}}$, $\lambda={c['predicted_rate']:.3f}$ (Jacobian)")
    ax.set_xlabel("time")
    ax.set_ylabel("TFT frequency")
    ax.set_title(f"Exponential extinction of TFT below $x^*$; fitted rate {c['fitted_rate']:.3f}")
    ax.legend()
    paths += save(fig, out, "replicator_convergence")
    return paths


def fig_moran(fix: dict[str, Any], mut: dict[str, Any], evo_noise: dict[str, Any], out: Path) -> list[Path]:
    rows = fix["rows"]
    fig, ax = plt.subplots(figsize=(5.6, 3.9))
    N = [r["N"] for r in rows]
    ax.plot(N, [r["exact"] for r in rows], "-", color=COOP, lw=2, label="exact (Nowak 2006, eq. 6.4)")
    se = [np.sqrt(r["sim"] * (1 - r["sim"]) / r["runs"]) for r in rows]
    ax.errorbar(N, [r["sim"] for r in rows], yerr=[2 * s for s in se], fmt="o", color=DEFECT, capsize=3, label=f"simulation ({rows[0]['runs']} runs)")
    ax.plot(N, [r["neutral"] for r in rows], ":", color=MUTED, label="neutral $1/N$")
    ax.set_xlabel("population size $N$")
    ax.set_ylabel("fixation probability of one TFT in ALLD")
    ax.set_title(rf"Moran fixation, $\delta={fix['delta']}$, $w=1$")
    ax.legend()
    paths = save(fig, out, "moran_fixation")

    names = mut["names"]
    mus = [r["mu"] for r in mut["rows"]]
    F = np.array([r["mean_freq"] for r in mut["rows"]])
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.9), gridspec_kw={"width_ratios": [1.6, 1]})
    ax = axes[0]
    xs = np.arange(len(mus))
    bottom = np.zeros(len(mus))
    order = np.argsort(-F.mean(axis=0))
    for k, i in enumerate(order):
        ax.bar(xs, F[:, i], bottom=bottom, color=PALETTE[k % len(PALETTE)] if k < 8 else MUTED, label=names[i] if k < 8 else None, edgecolor="white", lw=0.3)
        bottom += F[:, i]
    ax.set_xticks(xs, [str(m) for m in mus])
    ax.set_xlabel(r"mutation rate $\mu$")
    ax.set_ylabel("time-averaged frequency")
    ax.set_title(f"Moran process, N={mut['N']}, all {len(names)} strategies")
    ax.legend(ncol=2, fontsize=7, loc="upper right")
    ax = axes[1]
    ax.plot(xs, [r["coop_rate"] for r in mut["rows"]], "-o", color=COOP, label="cooperation rate")
    ax.plot(xs, [r["mean_payoff"] / 3 for r in mut["rows"]], "-s", color=ACCENT, label="mean payoff / R")
    ax.set_xticks(xs, [str(m) for m in mus])
    ax.set_xlabel(r"mutation rate $\mu$")
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.set_title("Does mutation break cooperation?")
    paths += save(fig, out, "moran_mutation")

    names = evo_noise["names"]
    eps = [r["eps"] for r in evo_noise["rows"]]
    F = np.array([r["mean_freq"] for r in evo_noise["rows"]])
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    xs = np.arange(len(eps))
    bottom = np.zeros(len(eps))
    order = np.argsort(-F.mean(axis=0))
    for k, i in enumerate(order):
        ax.bar(xs, F[:, i], bottom=bottom, color=PALETTE[k % len(PALETTE)] if k < 8 else MUTED, label=names[i] if k < 8 else None, edgecolor="white", lw=0.3)
        bottom += F[:, i]
    ax.set_xticks(xs, [str(e) for e in eps])
    ax.set_xlabel(r"implementation noise $\varepsilon$")
    ax.set_ylabel("time-averaged frequency")
    ax.set_title(r"Which strategies survive selection as noise rises? (Moran, $\mu=0.01$)")
    ax.legend(ncol=2, fontsize=7, loc="upper right")
    paths += save(fig, out, "evolution_noise")
    return paths


def _show_grid(ax: Any, g: Sequence[Sequence[int]], title: str) -> None:
    ax.imshow(np.array(g), cmap=LATTICE_CMAP, vmin=0, vmax=1, interpolation="nearest")
    ax.set_title(title, fontsize=9)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)


def fig_spatial(res: dict[str, Any], out: Path) -> list[Path]:
    ph = res["phase"]
    fig, ax = plt.subplots(figsize=(6, 3.8))
    b = [r["b"] for r in ph]
    ax.errorbar(b, [r["coop_mean"] for r in ph], yerr=[r["coop_sd"] for r in ph], fmt="-o", color=COOP, ms=4, capsize=2, label="simulation (mean of seeds)")
    ax.axhline(res["b_star_published"], color=DEFECT, ls="--", lw=1, label="Nowak & May (1992): 0.318 for 1.8<b<2")
    ax.axvspan(1.8, 2.0, color=ACCENT, alpha=0.12)
    ax.set_xlabel("temptation $b$")
    ax.set_ylabel("asymptotic cooperator fraction $f_C$")
    ax.set_title("Spatial PD phase diagram (synchronous, 8 neighbours + self)")
    ax.legend(loc="lower left")
    paths = save(fig, out, "spatial_phase")

    snaps = res["kaleidoscope_snapshots"]
    n = min(6, len(snaps))
    fig, axes = plt.subplots(1, n, figsize=(2.3 * n, 2.5))
    steps = len(res["kaleidoscope_series"]) - 1
    every = max(1, steps // 6)
    for k in range(n):
        _show_grid(axes[k], snaps[k], f"t = {k * every}")
    fig.suptitle("Kaleidoscope: one defector in a sea of cooperators, b = 1.9, fixed boundary", fontsize=10)
    paths += save(fig, out, "spatial_kaleidoscope")

    snaps = res["snapshots_b1p9"]
    n = min(6, len(snaps))
    fig, axes = plt.subplots(1, n, figsize=(2.3 * n, 2.5))
    for k in range(n):
        _show_grid(axes[k], snaps[k], f"t = {k * every}")
    fig.suptitle("Random start (90% C), b = 1.9: spatial chaos with $f_C \\approx 0.32$", fontsize=10)
    paths += save(fig, out, "spatial_snapshots")

    sa = res["sync_vs_async"]
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    ax.plot(sa["sync"], color=COOP, lw=2, label="synchronous (Nowak & May)")
    ax.plot(sa["async"], color=DEFECT, lw=2, label="asynchronous (Huberman & Glance)")
    ax.set_xlabel("generation")
    ax.set_ylabel("cooperator fraction")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title(f"Update rule matters: b = 1.9, L = {sa['L']}")
    ax.legend()
    paths += save(fig, out, "spatial_sync_async")

    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.plot(res["series_b1p9"], color=COOP, lw=1.5)
    ax.axhline(0.318, color=DEFECT, ls="--", lw=1)
    ax.set_xlabel("generation")
    ax.set_ylabel("$f_C$")
    ax.set_title("Cooperator fraction over time, b = 1.9 (dashed: 0.318)")
    paths += save(fig, out, "spatial_series")
    return paths


def fig_zd(res: dict[str, Any], pm: PayoffMatrix, out: Path) -> list[Path]:
    chi = res["chi"]
    fig, ax = plt.subplots(figsize=(5.4, 4.6))
    sc = res["scatter"]
    rnd = [s for s in sc if s["opponent"] == "random"]
    nam = [s for s in sc if s["opponent"] != "random"]
    ax.scatter([s["s_Y"] for s in rnd], [s["s_X"] for s in rnd], color=MUTED, s=16, label="random memory-one opponents")
    ax.scatter([s["s_Y"] for s in nam], [s["s_X"] for s in nam], color=DEFECT, s=34, zorder=5, label="named strategies")
    for s in nam:
        ax.annotate(s["opponent"], (s["s_Y"], s["s_X"]), textcoords="offset points", xytext=(4, 3), fontsize=7)
    y = np.linspace(pm.P, 2.3, 50)
    ax.plot(y, pm.P + chi * (y - pm.P), color=COOP, lw=1.5, label=rf"$s_X - P = {chi:g}\,(s_Y - P)$")
    ax.set_xlabel("opponent payoff $s_Y$")
    ax.set_ylabel("Extort-2 payoff $s_X$")
    ax.set_title("Extort-2 pins every opponent to a line")
    ax.legend(fontsize=8, loc="upper left")
    paths = save(fig, out, "zd_scatter")

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
    for ax, opp in zip(axes, ("EXTORT2", "ZDGTFT2", "TFT"), strict=True):
        runs = [r for r in res["learner"] if r["opponent"] == opp]
        for r in runs:
            ax.plot(r["t"], r["learner_payoff"], color=COOP, lw=1, alpha=0.7)
            ax.plot(r["t"], r["opponent_payoff"], color=DEFECT, lw=1, alpha=0.7)
        ax.plot([], [], color=COOP, label="Q-learner")
        ax.plot([], [], color=DEFECT, label=opp)
        ax.axhline(pm.R, color=MUTED, ls=":", lw=1)
        ax.set_title(f"Q-learner vs {opp}")
        ax.set_xlabel("round")
        ax.legend(fontsize=8, loc="lower right")
    axes[0].set_ylabel("payoff per round (moving avg)")
    paths += save(fig, out, "zd_learner")

    ev = res["evolution"]
    fig, ax = plt.subplots(figsize=(6, 3.8))
    X = np.array(ev["replicator_x"])
    for k, nm in enumerate(ev["names"]):
        ax.plot(ev["replicator_t"], X[:, k], lw=2, color=PALETTE[k % len(PALETTE)], label=nm)
    ax.set_xlabel("time")
    ax.set_ylabel("frequency")
    ax.set_title(r"Replicator dynamics among memory-one strategies ($\varepsilon=0.01$)")
    ax.legend(ncol=2, fontsize=8)
    paths += save(fig, out, "zd_evolution")
    return paths


def make_gif(frames: Sequence[np.ndarray], path: Path, fps: int = 8) -> None:
    """Animated GIF of lattice frames (True/1 = cooperator) for the README hero."""
    import imageio.v3 as iio
    from PIL import Image

    rgb = (np.array([201, 70, 61]), np.array([42, 111, 151]))
    imgs = []
    for f in frames:
        f = np.asarray(f).astype(int)
        img = np.where(f[..., None] == 1, rgb[1], rgb[0]).astype(np.uint8)
        im = Image.fromarray(img).resize((400, 400), Image.NEAREST)
        imgs.append(np.asarray(im))
    path.parent.mkdir(parents=True, exist_ok=True)
    iio.imwrite(path, imgs, duration=1000 / fps, loop=0)
