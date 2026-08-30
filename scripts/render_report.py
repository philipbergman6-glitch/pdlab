"""Substitute canonical numbers and generated tables into the report chapters.

Chapters in report/*.md may contain
  {{path.to.value}}          -> scalar from results/canonical.json (dot path, [i] indices)
  {{path.to.value|.3f}}      -> formatted with a Python format spec
  {{table:NAME}}             -> a markdown table generated below
Rendered copies go to report/build/ and pandoc compiles those.  Missing keys
are a hard error, so the report can never quote a stale or invented number.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "results" / "canonical.json"
REPORT = ROOT / "report"
BUILD = REPORT / "build"

TOKEN = re.compile(r"\{\{([^{}|]+?)(?:\|([^{}]+?))?\}\}")


def lookup(data: Any, path: str) -> Any:
    cur = data
    for part in re.split(r"\.(?![^\[]*\])", path.strip()):
        m = re.fullmatch(r"([^\[]+)((?:\[[^\]]+\])*)", part)
        if not m:
            raise KeyError(path)
        key, idx = m.group(1), m.group(2)
        if isinstance(cur, dict):
            if key not in cur:
                raise KeyError(f"{path}: missing key {key!r}")
            cur = cur[key]
        else:
            raise KeyError(f"{path}: cannot index {type(cur).__name__} with {key!r}")
        for i in re.findall(r"\[([^\]]+)\]", idx):
            cur = cur[int(i)] if isinstance(cur, list) else cur[i]
    return cur


def fmt(v: Any, spec: str | None) -> str:
    if spec:
        return format(v, spec)
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


# --------------------------------------------------------------------------
def md_table(header: list[str], rows: list[list[Any]], align: str | None = None) -> str:
    al = align or "l" + "r" * (len(header) - 1)
    sep = ["---" if a == "l" else "---:" for a in al]
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join(sep) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def tables(d: dict[str, Any]) -> dict[str, str]:
    t: dict[str, str] = {}
    # thresholds simulation
    rows = []
    for s in d["thresholds"]["simulation"]:
        f = 1 - s["delta"]
        rows.append(
            [
                f"{s['delta']:.3f}",
                f"{f * s['coop_exact']:.3f}",
                f"{f * s['coop_sim']:.3f} ± {2 * f * s['coop_se']:.3f}",
                f"{f * s['alld_exact']:.3f}",
                f"{f * s['alld_sim']:.3f} ± {2 * f * s['alld_se']:.3f}",
                f"{f * s['alt_exact']:.3f}",
                f"{f * s['alt_sim']:.3f} ± {2 * f * s['alt_se']:.3f}",
            ]
        )
    t["thresholds_sim"] = md_table(
        ["$\\delta$", "$R$ (exact)", "coop. (sim)", "$(1-\\delta)T+\\delta P$", "ALLD dev. (sim)", "$\\frac{T+\\delta S}{1+\\delta}$", "alt. dev. (sim)"],
        rows,
    )
    # leaderboard across noise
    lv = [str(e) for e in d["tournament"]["noise_levels"]]
    boards = {e: {r["strategy"]: r for r in d["tournament"]["leaderboards"][e]} for e in lv}
    order = [r["strategy"] for r in d["tournament"]["leaderboards"]["0.0"]]
    rows = []
    for nm in order:
        row = [nm]
        for e in lv:
            r = boards[e][nm]
            row.append(f"{r['score']:.3f} ({r['rank']})")
        row.append(f"{boards['0.0'][nm]['coop_rate']:.2f}")
        rows.append(row)
    t["leaderboard"] = md_table(["strategy"] + [f"$\\varepsilon={e}$" for e in lv] + ["coop. rate ($\\varepsilon=0$)"], rows)
    # finite
    t["finite"] = md_table(["$n$", "SPE path all-$D$", "row total"], [[r["n"], "yes" if r["all_defect"] else "no", f"{r['row_total']:g}"] for r in d["finite"]["rows"]])
    # replicator eigenvalues
    ev = d["replicator"]["eigenvalues"]
    evs = d["replicator"]["eigenvalues_symbolic"]
    rows = []
    for k in ("ALLC", "ALLD", "TFT", "TFT_ALLD_edge"):
        nums = ", ".join(f"{x:.4f}" for x in ev[k])
        rows.append([k.replace("_", "–"), "; ".join(f"${e}$" for e in evs[k]).replace("delta", "\\delta"), nums])
    t["eigenvalues"] = md_table(["fixed point", "eigenvalues (symbolic)", "numeric ($\\delta=0.9$)"], rows, "lll")
    # moran fixation
    rows = [[r["N"], f"{r['exact']:.4f}", f"{r['sim']:.4f}", f"{(r['sim'] * (1 - r['sim']) / r['runs']) ** 0.5:.4f}", f"{r['neutral']:.4f}"] for r in d["moran_fixation"]["rows"]]
    t["moran_fixation"] = md_table(["$N$", "$\\rho$ exact", "$\\rho$ simulated", "s.e.", "$1/N$"], rows)
    # moran mutation 18
    rows = [[r["mu"], r["dominant"], f"{r['coop_rate']:.3f}", f"{r['mean_payoff']:.3f}"] for r in d["moran_mutation"]["rows"]]
    t["moran_mutation"] = md_table(["$\\mu$", "most frequent", "cooperation rate", "mean payoff"], rows)
    if "three" in d["moran_mutation"]:
        rows = [[r["mu"], *[f"{x:.3f}" for x in r["mean_freq"]], f"{r['coop_rate']:.3f}", f"{r['frac_time_alld_majority']:.2f}"] for r in d["moran_mutation"]["three"]["rows"]]
        t["moran_three"] = md_table(["$\\mu$", "ALLC", "ALLD", "TFT", "cooperation", "time ALLD $>1/2$"], rows)
    # evolution noise
    names = d["evolution_noise"]["names"]
    rows = []
    for r in d["evolution_noise"]["rows"]:
        top = sorted(zip(names, r["mean_freq"], strict=True), key=lambda kv: -kv[1])[:3]
        rows.append([r["eps"], ", ".join(f"{n} ({f:.2f})" for n, f in top), f"{r['mean_payoff']:.3f}"])
    t["evolution_noise"] = md_table(["$\\varepsilon$", "top three (time-averaged frequency)", "mean payoff"], rows, "lll")
    # noise self play closed forms
    rows = []
    for nm, v in d["noise_selfplay"]["strategies"].items():
        rows.append([nm, "(" + ", ".join(f"{x:.3g}" for x in v["p"]) + ")", f"${v['series_axelrod'].replace('varepsilon', chr(92) + 'varepsilon').replace('*', '')}$", f"{v['noiseless']:.3f}", f"{v['exact'][-1]:.3f}"])
    t["noise_selfplay"] = md_table(["strategy", "$p$", "self-play payoff, $\\varepsilon \\to 0$ expansion", "$\\varepsilon=10^{-9}$", f"$\\varepsilon={d['noise_selfplay']['eps'][-1]:.2f}$"], rows, "llllr")
    # spatial phase
    rows = [[f"{r['b']:.3f}", f"{r['coop_mean']:.3f}", f"{r['coop_sd']:.3f}"] for r in d["spatial"]["phase"]]
    t["spatial_phase"] = md_table(["$b$", "$f_C$ (mean over seeds)", "s.d."], rows)
    t["spatial_init"] = md_table(["initial $f_C$", "asymptotic $f_C$"], [[r["f0"], f"{r['coop_final']:.3f}"] for r in d["spatial"]["init_independence"]])
    # zd scatter named
    rows = [[s["opponent"], f"{s['s_Y']:.3f}", f"{s['s_X']:.3f}", f"{(s['s_X'] - 1) / (s['s_Y'] - 1) if abs(s['s_Y'] - 1) > 1e-9 else float('nan'):.3f}"] for s in d["zd"]["scatter"] if s["opponent"] != "random"]
    t["zd_named"] = md_table(["opponent", "$s_Y$", "$s_X$ (Extort-2)", "$(s_X-P)/(s_Y-P)$"], rows)
    # learner
    rows = []
    for opp in ("EXTORT2", "ZDGTFT2", "TFT"):
        runs = [r for r in d["zd"]["learner"] if r["opponent"] == opp]
        lm = sum(r["final_learner"] for r in runs) / len(runs)
        om = sum(r["final_opponent"] for r in runs) / len(runs)
        rows.append([opp, len(runs), f"{lm:.3f}", f"{om:.3f}", f"{min(r['final_learner'] for r in runs):.2f}–{max(r['final_learner'] for r in runs):.2f}"])
    t["learner"] = md_table(["opponent", "seeds", "learner payoff (mean)", "opponent payoff (mean)", "learner range"], rows)
    ev = d["zd"]["evolution"]
    rows = [[n, f"{x:.3f}", f"{m:.3f}"] for n, x, m in zip(ev["names"], ev["replicator_final"], ev["moran_mean_freq"], strict=True)]
    t["zd_evolution"] = md_table(["strategy", "replicator, $t=300$", "Moran ($\\mu=0.01$), time average"], rows)
    return t


def render(text: str, d: dict[str, Any], t: dict[str, str]) -> str:
    def sub(m: re.Match[str]) -> str:
        key, spec = m.group(1), m.group(2)
        if key.startswith("table:"):
            name = key[6:].strip()
            if name not in t:
                raise KeyError(f"unknown table {name!r}; known: {sorted(t)}")
            return t[name]
        return fmt(lookup(d, key), spec)

    return TOKEN.sub(sub, text)


def main() -> None:
    if not CANON.exists():
        sys.exit(f"{CANON} missing: run `make reproduce` first")
    d = json.loads(CANON.read_text())
    t = tables(d)
    BUILD.mkdir(exist_ok=True)
    n = 0
    for src in sorted(REPORT.glob("*.md")):
        out = BUILD / src.name
        out.write_text(render(src.read_text(), d, t))
        n += 1
    for extra in ("00_meta.yaml", "references.bib", "apa.csl"):
        p = REPORT / extra
        if p.exists():
            (BUILD / extra).write_text(render(p.read_text(), d, t) if extra.endswith("yaml") else p.read_text())
    print(f"rendered {n} chapters into {BUILD}")


if __name__ == "__main__":
    main()
