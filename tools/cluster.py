# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scikit-learn", "igraph", "leidenalg"]
# ///
"""Cluster a topic's pool by the method in docs/process.md, "Clustering method".

Usage: uv run tools/cluster.py <topic> [--rule tau|null] [--k 10] [--c 10] [--tau 0.75] [--reps 20] [--nulls 2]
                                        [--levels 3,4,5,6,8,10,12,15,18,22] [--level coarser|finer|N]

Reads the pool sidecar graphs/<topic>/pool.json (from tools/pool.py). For each of three similarity measures
(text, refs, combined) and each level of a grid of cluster counts, it clusters the pool with Leiden and measures
stability by time holdout and resampling. It then chooses the measure (grid-averaged stability; within two standard
errors is a tie, and ties go to combined) and the level (the finest whose stability is at least --tau, 0.75 by default:
the last level before the curve falls off into instability).

It also runs the same pipeline on structure-free null data of the same size and shape, and reports a threshold-free
alternative: the level where real stability most exceeds null stability. --rule picks which of the two decides.

It also scores every paper for how poorly the rest of the pool covers it, the fringe score: its distance to its k
nearest neighbours, ranked within its age cohort. Under refs or combined, the reference rank is weighted per paper by
w = n / (n + c), n being its resolved references, so that a paper without reference data is scored by its text.

Afterwards, as post-processing that changes nothing above, it reports since when each cluster exists: the pool is
divided by date into four segments of equal paper count, each snapshot is clustered with the chosen measure and level,
and matched to the result (tools/match.py, `cluster_history`).

The input's `granularity` steering (docs/formats.md) moves the chosen level one step coarser or finer, or to the
level of N clusters; --level does the same as a user override and takes precedence. A level below tau is flagged.

If a previous clusters.json exists, the new clustering is matched to it by shared papers (tools/match.py, `match`), so
that `tools/assign.py remap` can carry cluster names over.

Writes graphs/<topic>/clusters.json and prints the retrieval log's `Clustering` and `Temporal stability` lines.
Deterministic: every random choice is seeded.
"""

import json
import sys
import time
from datetime import date
from itertools import combinations
from pathlib import Path

import igraph as ig
import leidenalg as la
import numpy as np
from sklearn.metrics import adjusted_mutual_info_score as ami
from sklearn.metrics import adjusted_rand_score as ari
from sklearn.metrics import silhouette_score

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from graph import parse, topic_dir  # noqa: E402

LEVELS = [3, 4, 5, 6, 8, 10, 12, 15, 18, 22]
MEASURES = ["text", "refs", "combined"]
HOLDOUT_MONTHS = [3, 6, 9]
MIN_HOLDOUT_SHARE = 0.3  # skip a cutoff that leaves fewer papers than this
TAU = 0.75  # a level is stable if its stability (mean of holdout and resampling ARI) reaches this
SUBCLUSTER_SCORE = 0.6  # a sub-cluster counts as stable if its clusterwise score reaches this
MIN_CLUSTER = 3  # clusters and sub-clusters smaller than this get no stability score
# Diagnostics for when stability fails; see docs/process.md, "When stability fails".
UNSTABLE = 0.6  # a cluster below this clusterwise score is unstable
SMALL = 10  # an unstable cluster smaller than this is thin: expand its region
EXCHANGE = 0.2  # two unstable clusters whose papers are co-assigned this often in reruns trade papers
NO_STRUCTURE = 0.15  # if real stability never exceeds the null by this much, there is little structure
BROAD = 0.9  # a coarsest level this stable, with nothing finer reaching tau: a broad scope, reported, not a failure
THIN_REFS = 10  # papers with fewer resolved references than this carry little reference signal


def opt(argv, name, default, cast):
    return cast(argv[argv.index(name) + 1]) if name in argv else default


# --- similarity measures --------------------------------------------------------------------------


def text_sim(recs):
    X = np.array([r["embedding"] for r in recs], dtype=float)
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    return X @ X.T


def refs_sim(recs):
    sets = [set(r["refs"]) for r in recs]
    n = len(sets)
    S = np.zeros((n, n))
    for i, j in combinations(range(n), 2):
        if sets[i] and sets[j]:
            S[i, j] = S[j, i] = len(sets[i] & sets[j]) / np.sqrt(len(sets[i]) * len(sets[j]))
    np.fill_diagonal(S, 1.0)
    return S


def rank_norm(S, zero_is_missing=False):
    """Per-paper percentile rank of every other paper, symmetrised, so that two measures share one scale."""
    n = len(S)
    R = np.zeros_like(S)
    for i in range(n):
        row = S[i].copy()
        row[i] = -np.inf
        R[i] = np.argsort(np.argsort(row)) / (n - 2)
        if zero_is_missing:
            R[i][S[i] <= 0] = 0.0
        R[i, i] = 0.0
    return (R + R.T) / 2


def combined_sim(T, C, recs, c):
    n_refs = np.array([len(r["refs"]) for r in recs], dtype=float)
    n = np.minimum.outer(n_refs, n_refs)
    w = n / (n + c)
    return w * rank_norm(C, zero_is_missing=True) + (1 - w) * rank_norm(T)


# --- clustering -----------------------------------------------------------------------------------


def knn_graph(S, k):
    edges = {}
    for i in range(len(S)):
        row = S[i].copy()
        row[i] = -np.inf
        for j in np.argsort(row)[::-1][:k]:
            if row[j] > 0:
                key = (min(i, j), max(i, j))
                edges[key] = max(edges.get(key, 0.0), float(row[j]))
    g = ig.Graph(n=len(S), edges=list(edges))
    g.es["weight"] = list(edges.values())
    return g


def leiden(g, gamma, seed):
    p = la.find_partition(g, la.RBConfigurationVertexPartition, weights="weight",
                          resolution_parameter=gamma, seed=seed, n_iterations=-1)
    return np.array(p.membership)


def n_clusters(labels):
    return int(sum(np.bincount(labels) >= 2))


def tune(g, target):
    """Bisect the resolution towards `target` clusters of two or more papers; return the closest found."""
    lo, hi, best = 0.02, 50.0, None
    for _ in range(40):
        mid = np.sqrt(lo * hi)
        got = n_clusters(leiden(g, mid, 0))
        if best is None or abs(got - target) < abs(best[1] - target):
            best = (mid, got)
        if got == target:
            break
        lo, hi = (mid, hi) if got < target else (lo, mid)
    return best


# --- null model -----------------------------------------------------------------------------------
# Structure-free data of the same size and overall shape. Coarse splits can be stable even with no clusters at all,
# because a featureless cloud can be cut into a few large pieces the same way each time; subtracting the null
# stability removes that.


def null_text(recs, rng):
    """Gaussian vectors with the embeddings' mean and covariance: same spread, no cluster structure."""
    X = np.array([r["embedding"] for r in recs], dtype=float)
    mu, Xc = X.mean(axis=0), X - X.mean(axis=0)
    Z = rng.standard_normal((len(X), len(X))) / np.sqrt(len(X) - 1)
    Y = mu + Z @ Xc
    Y /= np.linalg.norm(Y, axis=1, keepdims=True)
    return Y @ Y.T


def null_refs(recs, rng):
    """Reference lists reshuffled among papers, keeping each paper's list length and each reference's popularity."""
    stubs = [x for r in recs for x in r["refs"]]
    rng.shuffle(stubs)
    fake, i = [], 0
    for r in recs:
        fake.append({"refs": stubs[i:i + len(r["refs"])]})
        i += len(r["refs"])
    return refs_sim(fake)


def recluster(S, idx, k, gamma, seed):
    return leiden(knn_graph(S[np.ix_(idx, idx)], k), gamma, seed)


# --- scores ---------------------------------------------------------------------------------------


def best_jaccard(ref, labels):
    out = {}
    for c in np.unique(ref):
        A = set(np.flatnonzero(ref == c))
        out[int(c)] = max(len(A & B) / len(A | B) for B in (set(np.flatnonzero(labels == d)) for d in np.unique(labels)))
    return out


def mean_se(xs):
    xs = np.asarray(xs, dtype=float)
    return float(xs.mean()), float(xs.std(ddof=1) / np.sqrt(len(xs))) if len(xs) > 1 else 0.0


def link_lift(labels, edges):
    if not edges:
        return None
    inside = np.mean([labels[a] == labels[b] for a, b in edges])
    return float(inside / (np.bincount(labels) / len(labels)).__pow__(2).sum())


def cohesion(labels, T, C, edges):
    out = {}
    for name, S in (("text", T), ("refs", C)):
        D = np.clip(1 - S, 0, None)
        np.fill_diagonal(D, 0)
        out[f"silhouette_{name}"] = float(silhouette_score(D, labels, metric="precomputed")) if len(set(labels)) > 1 else 0.0
    out["citation_link_lift"] = link_lift(labels, edges)
    return out


def level_stats(S, k, target, cutoffs, dates, reps, rng):
    g = knn_graph(S, k)
    gamma, got = tune(g, target)
    full = leiden(g, gamma, 0)
    n = len(S)
    hold = []
    for cut in cutoffs:
        idx = np.flatnonzero(dates < cut)
        for seed in range(3):
            hold.append(ari(full[idx], recluster(S, idx, k, gamma, seed)))
    res, cw = [], {c: [] for c in np.unique(full) if (full == c).sum() >= MIN_CLUSTER}
    for r in range(reps):
        idx = np.sort(rng.choice(n, int(0.8 * n), replace=False))
        lab = recluster(S, idx, k, gamma, r)
        res.append(ari(full[idx], lab))
        for c, j in best_jaccard(full[idx], lab).items():
            if c in cw:
                cw[c].append(j)
    seeds = [leiden(g, gamma, s) for s in range(5)]
    h, hse = mean_se(hold)
    s, sse = mean_se(res)
    cw = {int(c): float(np.mean(v)) for c, v in cw.items() if v}
    return {
        "target": target, "clusters": got, "gamma": float(gamma), "labels": full.tolist(),
        "holdout_ari": h, "holdout_se": hse, "resample_ari": s, "resample_se": sse,
        "stability": (h + s) / 2, "stability_se": 0.5 * float(np.hypot(hse, sse)),
        "seed_ari": float(np.mean([ari(a, b) for a, b in combinations(seeds, 2)])),
        "clusterwise": cw, "median_clusterwise": float(np.median(list(cw.values()))) if cw else 0.0,
    }


# --- choices --------------------------------------------------------------------------------------


def choose_measure(curves):
    """Grid-averaged stability; anything within two standard errors of the best is tied; ties go to combined."""
    avg = {}
    for m, levels in curves.items():
        vals = [l["stability"] for l in levels]
        se = float(np.sqrt(sum(l["stability_se"] ** 2 for l in levels)) / len(levels))
        avg[m] = {"mean": float(np.mean(vals)), "se": se}
    best = max(avg, key=lambda m: avg[m]["mean"])
    tied = [m for m in avg
            if avg[best]["mean"] - avg[m]["mean"] <= 2 * np.hypot(avg[best]["se"], avg[m]["se"])]
    chosen = "combined" if "combined" in tied else best
    reason = (f"{best} highest; tied within 2 se: {', '.join(sorted(tied))}; ties go to combined"
              if chosen != best else f"{best} highest" + (f"; tied: {', '.join(sorted(tied))}" if len(tied) > 1 else ""))
    return chosen, avg, reason


def choose_level_null(levels, nulls):
    """Threshold-free: the level where stability most exceeds the null model's stability at the same level."""
    excess = [l["stability"] - n["stability"] for l, n in zip(levels, nulls)]
    j = int(np.argmax(excess))
    return j, f"largest excess over the null model: {excess[j]:.2f} (stability {levels[j]['stability']:.2f}, null {nulls[j]['stability']:.2f})"


def choose_level(levels, tau):
    """The finest level whose stability reaches tau: the last level before the curve falls off into instability."""
    ok = [j for j, l in enumerate(levels) if l["stability"] >= tau]
    if not ok:
        return 0, f"no level reaches stability {tau}; coarsest level used"
    j = max(ok, key=lambda j: levels[j]["clusters"])
    after = (f"; next level {levels[j + 1]['clusters']} clusters at {levels[j + 1]['stability']:.2f}"
             if j + 1 < len(levels) else "")
    return j, f"finest level with stability >= {tau}: {levels[j]['stability']:.2f}{after}"


def fringe_scores(T, C, recs, measure, k, c):
    """Per paper: distance to its k nearest neighbours, ranked among papers of similar age (year ± 1), 0 to 1.

    Older papers sit further from current work simply because the field moved on, so the raw distance is ranked within
    an age cohort. With the `refs` or `combined` measure, the reference rank is mixed with the text rank per paper, with
    weight w = n / (n + c) on references, n being the paper's own number of resolved references. A paper with no
    resolved references is equally far from everything by references alone, which would put it at the top of its
    cohort for lack of data, not for being overlooked; the weight makes such a paper lean on text, as `combined` does.
    """
    n = len(recs)
    off = ~np.eye(n, dtype=bool)
    near = {name: np.array([np.sort(S[i][off[i]])[-k:].mean() for i in range(n)]) for name, S in (("text", T), ("refs", C))}
    years = np.array([r.get("year") or 0 for r in recs])
    ranks = {}
    for name in ("text", "refs"):
        dist = 1 - near[name]
        rk = np.zeros(n)
        for i in range(n):
            cohort = np.flatnonzero(np.abs(years - years[i]) <= 1)
            if len(cohort) < 10:
                cohort = np.arange(n)
            rk[i] = (dist[cohort] < dist[i]).mean()
        ranks[name] = rk
    if measure == "text":
        return ranks["text"], near
    n_refs = np.array([len(r["refs"]) for r in recs], dtype=float)
    w = n_refs / (n_refs + c)
    return w * ranks["refs"] + (1 - w) * ranks["text"], near


def exchange_rates(S, full, k, gamma, reps, rng):
    """For each pair of clusters, how often papers of one are grouped with papers of the other in reruns on 80%."""
    n, cl = len(S), np.unique(full)
    hits = {(a, b): [] for a in cl for b in cl if a < b}
    for r in range(reps):
        idx = np.sort(rng.choice(n, int(0.8 * n), replace=False))
        lab, f = recluster(S, idx, k, gamma, r), full[idx]
        for a, b in hits:
            A, B = lab[f == a], lab[f == b]
            if len(A) and len(B):
                hits[(a, b)].append(float((A[:, None] == B[None, :]).mean()))
    return {key: float(np.mean(v)) for key, v in hits.items() if v}


def diagnose(curves_m, nulls_m, chosen, clusters, exchange, tau, recs, rename):
    """Which of the cases in docs/process.md, "When stability fails", apply, each with its action, plus `broad scope`."""
    out = []
    excess = [l["stability"] - nl["stability"] for l, nl in zip(curves_m, nulls_m)]
    thin_share = float(np.mean([len(r["refs"]) < THIN_REFS for r in recs]))
    if max(excess) < NO_STRUCTURE:
        out.append({"case": "no structure", "detail": f"real stability exceeds random by at most {max(excess):.2f}",
                    "action": "use very few clusters, possibly one, and halt for review (H4)"})
    passing = [l for l in curves_m if l["stability"] >= tau]
    if not passing:
        out.append({"case": "no stable level", "detail": f"no level reaches {tau}; {thin_share:.0%} of papers have fewer than {THIN_REFS} references",
                    "action": "expand the thinnest regions (step 2) and rerun; if still unstable, take the coarsest level and halt for review (H5), so that the user chooses with the slider"})
    elif passing == [curves_m[0]] and curves_m[0]["stability"] >= BROAD:
        # Not a failure: the pool divides into a few clearly separate areas. Reported, and the pass continues.
        out.append({"case": "broad scope", "detail": f"only the coarsest level ({curves_m[0]['clusters']} clusters, {curves_m[0]['stability']:.2f}) reaches {tau}",
                    "action": "none; say so in the Clustering rationale and continue; the coverage test checks whether these clusters suffice"})
    by_id = {c["id"]: c for c in clusters}
    unstable = {c["id"] for c in clusters if c["stability"] is not None and c["stability"] < UNSTABLE}
    # A thin cluster that dissolves is absorbed by its neighbours, so its exchange with them is a symptom of being
    # thin, not an open boundary. Thin clusters are diagnosed first and kept out of the trading pairs.
    thin = {cid for cid in unstable if by_id[cid]["size"] < SMALL}
    rates = {(rename[a], rename[b]): x for (a, b), x in exchange.items()}
    for cid in sorted(thin):
        c = by_id[cid]
        into = sorted(((x, b if a == cid else a) for (a, b), x in rates.items() if cid in (a, b)), reverse=True)[:2]
        out.append({"case": "thin cluster", "clusters": [cid],
                    "detail": f"{cid}: {c['size']} papers, stability {c['stability']:.2f}; absorbed mostly by "
                              + ", ".join(f"{o} ({x:.0%})" for x, o in into),
                    "action": "expand this region in a targeted way (step 2) and rerun"})
    trading = set()
    for (a, b), x in sorted(rates.items(), key=lambda kv: -kv[1]):
        if x >= EXCHANGE and {a, b} <= unstable - thin:
            trading |= {a, b}
            out.append({"case": "clusters trade papers", "clusters": [a, b],
                        "detail": f"{a} ({by_id[a]['stability']:.2f}) and {b} ({by_id[b]['stability']:.2f}) are grouped together in {x:.0%} of rerun pairs",
                        "action": "keep both; treat the boundary as open, require a bridge paper between them, and note the tension for the Landscape"})
    for cid in sorted(unstable - thin - trading):
        c = by_id[cid]
        out.append({"case": "unstable cluster", "clusters": [cid], "detail": f"{cid}: {c['size']} papers, stability {c['stability']:.2f}",
                    "action": "flag it in the report and the viewer; it does not halt the pass"})
    return out, {"max_null_excess": float(max(excess)), "chosen_null_excess": float(excess[curves_m.index(chosen)]),
                 "thin_reference_share": thin_share}


def named_computed(topic):
    """The computed ids the survey's Clusters table names (its `computed` column)."""
    from check import sections, table_rows
    secs = sections((ROOT / "surveys" / f"{topic}.md").read_text())
    return {c[h.index("computed")] for h, c, _, _ in table_rows(secs.get("Clusters", ""))
            if h and h[0] == "id" and "computed" in h and c[h.index("computed")]}


def steer(argv, topic, levels, li, rule, reason, curve, tau):
    """Apply --level, or else the input's granularity steering, to the level the rule chose."""
    from inputs import read_input
    how = opt(argv, "--level", None, str)
    source = "user override" if how else "granularity steering"
    if how is None:
        how = ((read_input(topic)[1] or {}).get("granularity") or "").replace("`", "").strip() or None
    if how is None:
        return li, rule, reason
    if how == "coarser":
        new = max(li - 1, 0)
    elif how == "finer":
        new = min(li + 1, len(levels) - 1)
    elif how.isdigit() and int(how) in levels:
        new = levels.index(int(how))
    elif how.isdigit() and int(how) in [l["clusters"] for l in curve]:
        # The viewer's slider shows the number of clusters each level reached, which can differ from its target.
        new = [l["clusters"] for l in curve].index(int(how))
    else:
        sys.exit(f"--level or granularity must be coarser, finer, or one of this pool's levels: targets {levels}, "
                 f"reached {[l['clusters'] for l in curve]}; not {how!r}")
    st = curve[new]["stability"]
    flag = f"; below tau ({st:.2f})" if st < tau else ""
    if flag:
        print(f"WARNING: the steered level, {curve[new]['clusters']} clusters, has stability {st:.2f}, below tau")
    return new, f"{rule}, moved by {source} ({how})", (f"{reason}; moved by {source} ({how}) to "
                                                        f"{curve[new]['clusters']} clusters{flag}")


def clustering_line(measure, g, chosen, rule, curve, li, sensitivity, null_level, tau, k, c, cutoffs, diagnostics,
                    override="none"):
    """The retrieval log's Clustering line, in the form docs/formats.md gives."""
    nxt = (f"; next finer level {curve[li + 1]['clusters']} clusters at {curve[li + 1]['stability']:.2f}"
           if li + 1 < len(curve) else "; no finer level")
    lo, hi = sensitivity[f"{tau - 0.05:.2f}"], sensitivity[f"{tau + 0.05:.2f}"]
    diag = "; ".join(f"{d['case']}: {d['detail']} -> <action taken>" for d in diagnostics) or "none"
    return (f"- **Clustering:** measure {measure} (grid mean stability: "
            + ", ".join(f"{m} {g[m]['mean']:.3f} ± {g[m]['se']:.3f}" for m in MEASURES)
            + f"); level {chosen['clusters']} clusters by rule {rule}, stability {chosen['stability']:.2f}{nxt}; "
            f"τ ± 0.05 would give {lo} | {hi} clusters; null-model rule: {null_level['clusters']} clusters; "
            f"grid {[l['clusters'] for l in curve]}; τ={tau}, k={k}, c={c:g}; holdout cutoffs {', '.join(cutoffs)}; "
            f"diagnostics: {diag}; manual overrides: {override}")


def month_back(d, months):
    y, m = d.year, d.month - months
    while m <= 0:
        y, m = y - 1, m + 12
    return date(y, m, min(d.day, 28)).isoformat()


# --- main -----------------------------------------------------------------------------------------


def main(argv):
    if not argv or argv[0].startswith("-"):
        sys.exit(__doc__)
    topic = argv[0]
    k, c, reps = opt(argv, "--k", 10, int), opt(argv, "--c", 10.0, float), opt(argv, "--reps", 20, int)
    tau = opt(argv, "--tau", TAU, float)
    rule, n_nulls = opt(argv, "--rule", "tau", str), opt(argv, "--nulls", 2, int)
    if rule not in ("tau", "null"):
        sys.exit("--rule must be tau or null")
    papers = parse(topic)[4]
    sidecar = json.loads((topic_dir(topic) / "pool.json").read_text())
    cache = sidecar["papers"]
    ids = sorted(a for a in papers if a in cache and cache[a]["embedding"])
    skipped = sorted(set(papers) - set(ids))
    recs = [cache[a] for a in ids]
    n = len(ids)
    levels = [L for L in opt(argv, "--levels", LEVELS, lambda s: [int(x) for x in s.split(",")]) if L <= n // 4]
    if not levels:
        print(f"STOP: H8 — {n} papers with an embedding ({len(skipped)} without); no level of the grid fits a pool this "
              "small, since levels above a quarter of the pool are dropped (docs/process.md, \"When a pass ends\")")
        sys.exit(1)

    by_s2 = {r["s2"]: i for i, r in enumerate(recs)}
    edges = sorted({tuple(sorted((i, by_s2[x]))) for i, r in enumerate(recs)
                    for x in r["refs"] if x in by_s2 and by_s2[x] != i})
    dates = np.array([r["date"] or f"{r['year'] or 9999}-07-01" for r in recs])
    latest = date.fromisoformat(max(dates))
    cutoffs = [cut for cut in (month_back(latest, m) for m in HOLDOUT_MONTHS)
               if (dates < cut).mean() >= MIN_HOLDOUT_SHARE]

    T, C = text_sim(recs), refs_sim(recs)
    sims = {"text": T, "refs": C, "combined": combined_sim(T, C, recs, c)}
    print(f"{topic}: {n} papers ({len(skipped)} without data), {len(edges)} citation links; levels {levels}; "
          f"rule {rule}, tau={tau}, k={k}, c={c}; holdout cutoffs {cutoffs}")

    curves = {}
    for m in MEASURES:
        rng = np.random.default_rng(0)
        curves[m] = [level_stats(sims[m], k, L, cutoffs, dates, reps, rng) for L in levels]
        print(f"  {m:9}" + " ".join(f"{l['clusters']:>3}:{l['stability']:.2f}" for l in curves[m]))

    # Null curves: the same pipeline on structure-free data, averaged over a few draws.
    null_curves = {m: [] for m in MEASURES}
    draws = []
    for d in range(n_nulls):
        rng = np.random.default_rng(1000 + d)
        Tn, Cn = null_text(recs, rng), null_refs(recs, rng)
        draws.append({"text": Tn, "refs": Cn, "combined": combined_sim(Tn, Cn, recs, c)})
    for m in MEASURES:
        for L in levels:
            runs = [level_stats(dr[m], k, L, cutoffs, dates, reps, np.random.default_rng(0)) for dr in draws]
            null_curves[m].append({"clusters": float(np.mean([r["clusters"] for r in runs])),
                                   "stability": float(np.mean([r["stability"] for r in runs])),
                                   "stability_se": float(np.sqrt(sum(r["stability_se"] ** 2 for r in runs)) / len(runs))})
        print(f"  null {m:4}" + " ".join(f"{l['clusters']:>5.1f}:{l['stability']:.2f}" for l in null_curves[m]))

    measure, avg, measure_reason = choose_measure(curves)
    li_tau, tau_reason = choose_level(curves[measure], tau)
    li_null, null_reason = choose_level_null(curves[measure], null_curves[measure])
    li, level_reason = (li_tau, tau_reason) if rule == "tau" else (li_null, null_reason)
    li, rule, level_reason = steer(argv, topic, levels, li, rule, level_reason, curves[measure], tau)
    sensitivity = {f"{x:.2f}": curves[measure][choose_level(curves[measure], x)[0]]["clusters"]
                   for x in (tau - 0.05, tau, tau + 0.05)}
    chosen = curves[measure][li]
    labels = np.array(chosen["labels"])

    # Renumber clusters by size, largest first, as c1, c2, ...
    order = [int(x) for x in np.argsort(-np.bincount(labels), kind="stable")]
    rename = {old: f"c{i + 1}" for i, old in enumerate(order)}
    # In-degree within the pool: how many pool papers cite each paper. `edges` above is undirected, for cohesion.
    indeg = np.bincount([by_s2[x] for i, r in enumerate(recs) for x in set(r["refs"]) if x in by_s2 and by_s2[x] != i],
                        minlength=n)
    finer = curves[measure][li + 1] if li + 1 < len(levels) else None
    clusters = []
    for old in order:
        members = np.flatnonzero(labels == old)
        top = sorted(members, key=lambda i: -indeg[i])[:8]
        sub = []
        if finer:
            fl = np.array(finer["labels"])
            for f in np.unique(fl[members]):
                part = members[fl[members] == f]
                if len(part) >= MIN_CLUSTER:
                    sub.append({"size": len(part), "stability": finer["clusterwise"].get(int(f)),
                                "members": [ids[i] for i in part]})
            sub.sort(key=lambda s: -s["size"])
        divided = sum(1 for s in sub if (s["stability"] or 0) >= SUBCLUSTER_SCORE) >= 2
        clusters.append({
            "id": rename[old], "size": len(members), "stability": chosen["clusterwise"].get(old),
            "members": [ids[i] for i in members], "top": [[ids[i], papers[ids[i]]["title"]] for i in top],
            "subclusters": sub, "divided": divided,
        })

    def by_size(lab):
        lab = np.asarray(lab)
        order = [int(x) for x in np.argsort(-np.bincount(lab), kind="stable")]
        names = {old: f"c{i + 1}" for i, old in enumerate(order)}
        return [names[int(x)] for x in lab]

    slider = [{
        "clusters": l["clusters"], "stability": l["stability"], "null_stability": nl["stability"],
        "labels": by_size(l["labels"]),
    } for l, nl in zip(curves[measure], null_curves[measure])]
    g_knn = knn_graph(sims[measure], k)
    knn = [[ids[e.source], ids[e.target], round(w, 3)] for e, w in zip(g_knn.es, g_knn.es["weight"])]

    score, near = fringe_scores(T, C, recs, measure, k, c)
    fringe = sorted(({"id": ids[i], "score": round(float(score[i]), 3), "nn_text": round(float(near["text"][i]), 3),
                      "nn_refs": round(float(near["refs"][i]), 3), "refs": len(recs[i]["refs"]), "year": recs[i].get("year"),
                      "cluster": rename[int(labels[i])]} for i in range(n)), key=lambda x: -x["score"])

    # Post-processing: since when each cluster exists. Nothing above depends on it.
    from match import cluster_history, log_line
    assignment = {ids[i]: rename[int(labels[i])] for i in range(n)}
    history = cluster_history(ids, recs, dates, assignment, measure, chosen["clusters"], k, c, tau, reps=reps)

    survey_labels = [papers[a].get("cluster") or "" for a in ids]
    exchange = exchange_rates(sims[measure], labels, k, chosen["gamma"], reps, np.random.default_rng(1))
    diagnostics, health = diagnose(curves[measure], null_curves[measure], chosen, clusters, exchange, tau, recs, rename)

    report = {
        "generated": time.strftime("%Y-%m-%d"), "pool_fetched": sorted({r.get("fetched") or sidecar.get("fetched") for r in recs} - {None}),
        "params": {"k": k, "c": c, "reps": reps, "nulls": n_nulls, "levels": levels, "cutoffs": cutoffs,
                   "tau": tau, "subcluster_score": SUBCLUSTER_SCORE},
        "measure": measure, "measure_reason": measure_reason, "grid_mean": avg,
        "rule": rule, "level": chosen["clusters"], "level_reason": level_reason, "tau_sensitivity": sensitivity,
        "level_tau": curves[measure][li_tau]["clusters"], "level_tau_reason": tau_reason,
        "level_null": curves[measure][li_null]["clusters"], "level_null_reason": null_reason,
        "null_curves": null_curves, "slider": slider, "knn": knn, "fringe": fringe,
        "diagnostics": diagnostics, "health": health,
        "cohesion": cohesion(labels, T, C, edges),
        "ami_vs_survey_clusters": float(ami(survey_labels, labels)),
        "curves": {m: [{x: l[x] for x in l if x not in ("labels", "clusterwise")} for l in curves[m]] for m in curves},
        "ids": ids, "assignment": assignment, "history": history,
        "clusters": clusters, "skipped": skipped,
    }
    out = topic_dir(topic) / "clusters.json"
    if out.exists() and named_computed(topic):
        # The Clusters table names the clustering its `computed` ids refer to. Match the new clustering to that one, so
        # that tools/assign.py remap can carry the names over. If the clustering has been rerun since without a remap
        # (a provisional run at step 2, a --level rerun), the named one is the baseline stored by that run. With no
        # names yet, as on a first pass, there is nothing to carry, and no matching is recorded.
        from match import match
        prev = json.loads(out.read_text())
        if prev.get("previous") and not prev["previous"].get("remapped"):
            base, when = prev["previous"]["assignment"], prev["previous"]["generated"]
        else:
            base, when = dict(prev.get("assignment", {})), prev.get("generated")
            base.update({p: x["cluster"] for p, x in prev.get("late", {}).items()})
        m_old, m_new, frags = match(base, assignment)
        report["previous"] = {"generated": when, "assignment": base, "old": m_old, "new": m_new, "fragments": frags}
    out.write_text(json.dumps(report, indent=1))

    g = avg
    print(f"\nmeasure: {measure} ({measure_reason})")
    print(f"level: {chosen['clusters']} clusters ({level_reason})")
    print("tau sensitivity: " + ", ".join(f"{a} -> {b} clusters" for a, b in sensitivity.items()))
    print(f"rule tau:  {curves[measure][li_tau]['clusters']} clusters ({tau_reason})")
    print(f"rule null: {curves[measure][li_null]['clusters']} clusters ({null_reason})")
    print(f"cohesion: " + ", ".join(f"{a} {b:.3f}" for a, b in report["cohesion"].items() if b is not None)
          + f"; AMI vs survey clusters {report['ami_vs_survey_clusters']:.3f}")
    for cl in clusters:
        st = f"{cl['stability']:.2f}" if cl["stability"] is not None else "n/a"
        print(f"  {cl['id']:>4} {cl['size']:>3} papers, stability {st}, {len(cl['subclusters'])} sub-clusters"
              + (" (divided)" if cl["divided"] else "") + f"; e.g. {cl['top'][0][1][:70]}")
    print(f"\nstability diagnostics (excess over random: {health['chosen_null_excess']:.2f} at the chosen level, "
          f"{health['max_null_excess']:.2f} at most; {health['thin_reference_share']:.0%} of papers with few references):")
    for d in diagnostics or [{"case": "none", "detail": "every cluster at the chosen level is stable", "action": "proceed"}]:
        print(f"  {d['case']}: {d['detail']}\n      -> {d['action']}")
    print("\nhighest fringe scores (distance to nearest neighbours, ranked within age cohort):")
    for f in fringe[:8]:
        print(f"  {f['score']:.2f}  {f['year']}  {f['cluster']:>4}  {f['refs']:>3} refs  {papers[f['id']]['title'][:72]}")
    print("\nlog lines (replace the computed ids c1, c2, ... with the Clusters table's ids, and each <action taken>):")
    override = f"level {opt(argv, '--level', None, str)} (--level)" if "--level" in argv else "none"
    print(clustering_line(measure, g, chosen, rule, curves[measure], li, sensitivity, curves[measure][li_null], tau, k,
                          c, cutoffs, diagnostics, override))
    print(log_line(history))
    if "previous" in report:
        print(f"\nmatched to the previous clustering ({report['previous']['generated']}; tools/match.py):")
        for b, x in sorted(report["previous"]["new"].items(), key=lambda kv: int(kv[0][1:])):
            print(f"  {b}: {x['case']}" + (f" from {', '.join(x['from'])}" if x.get("from") else "")
                  + f" ({x['share']:.0%})")
        gone = [f"{a} {x['case']}" for a, x in report["previous"]["old"].items() if x["case"] in ("vanished",)]
        if gone:
            print("  " + "; ".join(gone))
        print(f"  carry the names over with `python3 tools/assign.py remap {topic}`")
    print(f"\nwrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
