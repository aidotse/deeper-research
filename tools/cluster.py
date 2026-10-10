# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy==2.5.3", "scikit-learn==1.9.1", "igraph==1.0.0", "leidenalg==0.12.0"]
# ///
"""Cluster a topic's pool by the method in docs/process.md, "Clustering method".

Usage: uv run tools/cluster.py <topic> [--k 10] [--c 10] [--tau 0.75] [--reps 20] [--nulls 1]
                                        [--levels 3,4,5,6,8,10,12,15,18,22] [--level coarser|finer|N]

Reads the pool sidecar graphs/<topic>/pool.json (from tools/pool.py). The similarity measure is fixed: `combined`, the
text similarity (SPECTER2 embeddings) and the reference similarity (bibliographic coupling), each converted to
per-paper neighbour ranks and mixed per pair with weight w = n / (n + c) on references, n being the shorter of the two
reference lists. For each level of a grid of cluster counts, it clusters the pool with Leiden and measures stability by
time holdout and resampling. A holdout rerun recomputes the similarity on the older papers alone, rank normalisation
included, as the pool would have been months ago. The chosen level is the finest whose stability is at least --tau,
0.75 by default, even if a coarser level dips below it. If every holdout cutoff is skipped (less
than 30% of the pool older than it), stability is the resampling score alone, and the printout says so.

It also runs the same pipeline once on structure-free null data of the same size and shape (--nulls draws, 1 by
default, averaged). The null serves only as the `no structure` guard: real stability exceeding it by less than 0.15 at
every level. --nulls 0 is refused, since without a null draw the guard cannot run.

It also scores every paper for how poorly the rest of the pool covers it, the fringe score: its distance to its k
nearest neighbours, text and references mixed per paper by w = n / (n + c), n being its resolved references, so that a
paper without reference data is scored by its text; then ranked once within its age cohort, the COHORT (30) papers
nearest to it by publication date. The score is a percentile within that cohort.

The input's `granularity` steering (docs/formats.md) moves the chosen level one step coarser or finer, or to the
level of N clusters; --level does the same as a user override and takes precedence. A level below tau is flagged.

If a previous clusters.json exists, the new clustering is matched to it by shared papers (tools/match.py, `match`), so
that `tools/assign.py remap` can carry cluster names over.

Writes graphs/<topic>/clusters.json and prints the retrieval log's `Clustering` line. Deterministic: every random
choice is seeded, and `params` records the seeds, the defaults used and the installed package versions. Usage errors
exit with status 2.
"""

import json
import platform
import sys
import time
from datetime import date
from importlib.metadata import version
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
MEASURE = "combined"  # fixed; `text` and `refs` are its inputs, and the fringe score's
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
BROAD = 0.9  # a coarsest level this stable, with nothing finer reaching tau: a broad scope, noted, not a diagnostic
THIN_REFS = 10  # papers with fewer resolved references than this carry little reference signal
# Defaults of the command-line settings, recorded in `params`. The spec fixes none of these values.
K = 10  # --k: neighbours per paper in the graph, and in the fringe score
C_REFS = 10.0  # --c: the reference weight w = n / (n + c) reaches 0.5 at c resolved references
REPS = 20  # --reps: resampling reruns per level
NULLS = 1  # --nulls: structure-free null draws, averaged
COHORT = 30  # the fringe score's age cohort: the papers nearest by publication date (more on ties)
# Every seed the method uses, recorded in `params`.
SEEDS = {"leiden": 0, "resolution_search": 0, "holdout_leiden": [0, 1, 2], "resample_draws": "default_rng(0)",
         "resample_leiden": "rerun index", "seed_agreement": [0, 1, 2, 3, 4], "exchange_draws": "default_rng(1)",
         "null_data": "default_rng(1000 + draw)", "null_resample_draws": "default_rng(0) per level"}
PACKAGES = ["numpy", "scikit-learn", "igraph", "leidenalg"]


def usage(msg):
    print(f"usage error: {msg}", file=sys.stderr)
    sys.exit(2)


def opt(argv, name, default, cast):
    if name not in argv:
        return default
    try:
        return cast(argv[argv.index(name) + 1])
    except (IndexError, ValueError):
        usage(f"{name} needs a value" + (f" such as {default}" if default is not None else ""))


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


def subset_sim(T, C, recs, c):
    """The `combined` measure recomputed on a subset of papers, given by their indices: rank normalisation included."""
    return lambda idx: combined_sim(T[np.ix_(idx, idx)], C[np.ix_(idx, idx)], [recs[i] for i in idx], c)


# --- scores ---------------------------------------------------------------------------------------


def best_jaccard(ref, labels):
    out = {}
    for c in np.unique(ref):
        A = set(np.flatnonzero(ref == c))
        out[int(c)] = max(len(A & B) / len(A | B) for B in (set(np.flatnonzero(labels == d)) for d in np.unique(labels)))
    return out


def part_score(part, reruns):
    """The clusterwise score of any set of papers: its best Jaccard overlap with a cluster of each resampling rerun, on
    the papers the rerun kept, averaged. For a whole cluster it equals that cluster's clusterwise score."""
    part, js = set(int(i) for i in part), []
    for idx, lab in reruns:
        A = {j for j, i in enumerate(idx) if i in part}
        if A:
            js.append(max(len(A & B) / len(A | B) for B in (set(np.flatnonzero(lab == d)) for d in np.unique(lab))))
    return float(np.mean(js)) if js else None


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


def level_stats(S, k, target, cutoffs, dates, reps, rng, sub=None):
    """Stability at one level. `sub(idx)`, if given, recomputes the similarity on the papers idx alone, for the time
    holdout: the older papers on their own, as an earlier pass would have measured them. Without it, S is sliced."""
    g = knn_graph(S, k)
    gamma, got = tune(g, target)
    full = leiden(g, gamma, 0)
    n = len(S)
    hold = []
    for cut in cutoffs:
        idx = np.flatnonzero(dates < cut)
        g_old = knn_graph(sub(idx) if sub else S[np.ix_(idx, idx)], k)
        for seed in range(3):
            hold.append(ari(full[idx], leiden(g_old, gamma, seed)))
    res, cw, reruns = [], {c: [] for c in np.unique(full) if (full == c).sum() >= MIN_CLUSTER}, []
    for r in range(reps):
        idx = np.sort(rng.choice(n, int(0.8 * n), replace=False))
        lab = recluster(S, idx, k, gamma, r)
        reruns.append((idx, lab))
        res.append(ari(full[idx], lab))
        for c, j in best_jaccard(full[idx], lab).items():
            if c in cw:
                cw[c].append(j)
    seeds = [leiden(g, gamma, s) for s in range(5)]
    s, sse = mean_se(res)
    if hold:
        h, hse = mean_se(hold)
        st, st_se = (h + s) / 2, 0.5 * float(np.hypot(hse, sse))
    else:
        # Every holdout cutoff was skipped: stability falls back to resampling alone, rather than becoming NaN.
        h, hse, st, st_se = None, None, s, sse
    cw = {int(c): float(np.mean(v)) for c, v in cw.items() if v}
    return {
        "target": target, "clusters": got, "gamma": float(gamma), "labels": full.tolist(),
        "holdout_ari": h, "holdout_se": hse, "resample_ari": s, "resample_se": sse,
        "stability": st, "stability_se": st_se,
        "seed_ari": float(np.mean([ari(a, b) for a, b in combinations(seeds, 2)])),
        "clusterwise": cw, "median_clusterwise": float(np.median(list(cw.values()))) if cw else 0.0,
        "reruns": reruns,  # the resampling reruns, for scoring sub-clusters; not written out
    }


# --- choices --------------------------------------------------------------------------------------


def choose_level(levels, tau):
    """The finest level whose stability reaches tau, even if a coarser level dips below it (docs/process.md)."""
    ok = [j for j, l in enumerate(levels) if l["stability"] >= tau]
    if not ok:
        return 0, f"no level reaches stability {tau}; coarsest level used"
    j = max(ok, key=lambda j: levels[j]["clusters"])
    after = (f"; next level {levels[j + 1]['clusters']} clusters at {levels[j + 1]['stability']:.2f}"
             if j + 1 < len(levels) else "")
    return j, f"finest level with stability >= {tau}: {levels[j]['stability']:.2f}{after}"


def mid_percentile(x):
    """Each value's percentile within x, strictly between 0 and 1; tied values share the middle of their ranks."""
    _, inv, counts = np.unique(x, return_inverse=True, return_counts=True)
    below = np.concatenate([[0], np.cumsum(counts)[:-1]])
    return (below[inv] + counts[inv] / 2) / len(x)


def age_cohorts(recs, size):
    """Per paper, its age cohort: the `size` papers nearest to it by publication date (itself included), widened to
    take in every paper tied with the last. The date is the record's, or else mid-year of its year. An undated paper,
    and every paper of a pool no larger than `size`, has the whole pool as its cohort."""
    n = len(recs)
    day = [date.fromisoformat(r["date"]).toordinal() if r.get("date") else
           date(r["year"], 7, 1).toordinal() if r.get("year") else None for r in recs]
    known = np.array([d is not None for d in day])
    days = np.array([d if d is not None else 0 for d in day], dtype=float)
    out = []
    for i in range(n):
        if day[i] is None or known.sum() <= size:
            out.append(np.arange(n))
            continue
        gap = np.where(known, np.abs(days - days[i]), np.inf)
        out.append(np.flatnonzero(gap <= np.sort(gap)[size - 1]))
    return out


def fringe_scores(T, C, recs, k, c, cohort=COHORT):
    """Per paper: distance to its k nearest neighbours, text and references mixed, ranked within its age cohort, 0 to 1.

    The two distances live on different scales, so each is first put on a common one: its normal score, from its
    percentile in the pool; for references, among the papers that have any. They are then mixed per paper, as in
    `combined`, with weight w = n / (n + c) on references, n being the paper's own number of resolved references. A
    paper with no resolved references is equally far from everything by references alone, for lack of data rather than
    for being overlooked; with w = 0 it is scored by its text. The mix is divided by its spread under the two scores'
    correlation in the pool, so that every paper's mixed score has the same spread whatever its weight. Without that,
    a mix of two partly independent scores is less extreme than either, and papers scored by one alone, those without
    references, would crowd both ends of the ranking.

    Older papers sit further from current work simply because the field moved on, so the mixed score is ranked once,
    within the paper's age cohort (`age_cohorts`): the share of its cohort that it exceeds. Returns that percentile, the
    mixed score (for breaking ties between percentiles), and the nearest-neighbour similarities.
    """
    from statistics import NormalDist
    n = len(recs)
    off = ~np.eye(n, dtype=bool)
    near = {name: np.array([np.sort(S[i][off[i]])[-k:].mean() for i in range(n)]) for name, S in (("text", T), ("refs", C))}
    normal = np.vectorize(NormalDist().inv_cdf)
    n_refs = np.array([len(r["refs"]) for r in recs], dtype=float)
    has = n_refs > 0
    z_text, z_refs = normal(mid_percentile(1 - near["text"])), np.zeros(n)
    if has.any():
        z_refs[has] = normal(mid_percentile(1 - near["refs"][has]))
    rho = float(np.corrcoef(z_text[has], z_refs[has])[0, 1]) if has.sum() > 2 else 0.0
    rho = 0.0 if np.isnan(rho) else rho
    w = n_refs / (n_refs + c)
    mixed = (w * z_refs + (1 - w) * z_text) / np.sqrt(np.maximum(w**2 + (1 - w)**2 + 2 * w * (1 - w) * rho, 1e-9))
    score = np.array([(mixed[co] < mixed[i]).mean() for i, co in enumerate(age_cohorts(recs, cohort))])
    return score, mixed, near


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


def diagnose(curve, null_curve, chosen, clusters, exchange, tau, recs, rename):
    """The cases in docs/process.md, "When stability fails", each with its action; and the plain notes.

    Diagnostics, each with an action: `no structure`, `no stable level`, `thin cluster`, `clusters trade papers`.
    Notes, plain text that drives no action: a broad scope (only the coarsest level reaches tau, very stably), and an
    unstable cluster that is neither thin nor trading papers.
    """
    out, notes = [], []
    excess = [l["stability"] - nl["stability"] for l, nl in zip(curve, null_curve)]
    thin_share = float(np.mean([len(r["refs"]) < THIN_REFS for r in recs]))
    if max(excess) < NO_STRUCTURE:
        out.append({"case": "no structure", "detail": f"real stability exceeds random by at most {max(excess):.2f}",
                    "action": "use very few clusters, possibly one, and halt for review (H4)"})
    passing = [l for l in curve if l["stability"] >= tau]
    if not passing:
        out.append({"case": "no stable level", "detail": f"no level reaches {tau}; {thin_share:.0%} of papers have fewer than {THIN_REFS} references",
                    "action": "expand the thinnest regions (step 2) and rerun; if still unstable, take the coarsest level and halt for review (H5), so that the user chooses with the slider"})
    elif passing == [curve[0]] and curve[0]["stability"] >= BROAD:
        # Not a failure: the pool divides into a few clearly separate areas. Noted, and the pass continues.
        notes.append({"clusters": [], "text": f"Broad scope: only the coarsest level ({curve[0]['clusters']} clusters, "
                                              f"stability {curve[0]['stability']:.2f}) reaches {tau}. The clusters are "
                                              "real; say so in the Clustering rationale and continue."})
    by_id = {c["id"]: c for c in clusters}
    unstable = {c["id"] for c in clusters if c["stability"] is not None and c["stability"] < UNSTABLE}
    # A thin cluster that dissolves is absorbed by its neighbours, so its exchange with them is a symptom of being
    # thin, not an open boundary. Thin clusters are diagnosed first and kept out of the trading pairs. A cluster too
    # small for a clusterwise score (fewer than MIN_CLUSTER papers) is thin on its size alone.
    tiny = {c["id"] for c in clusters if c["stability"] is None}
    thin = {cid for cid in unstable if by_id[cid]["size"] < SMALL} | tiny
    rates = {(rename[a], rename[b]): x for (a, b), x in exchange.items()}
    for cid in sorted(thin):
        c = by_id[cid]
        into = sorted(((x, b if a == cid else a) for (a, b), x in rates.items() if cid in (a, b)), reverse=True)[:2]
        score = (f"stability {c['stability']:.2f}" if c["stability"] is not None
                 else f"no stability score (fewer than {MIN_CLUSTER} papers)")
        out.append({"case": "thin cluster", "clusters": [cid],
                    "detail": f"{cid}: {c['size']} papers, {score}"
                              + ("; absorbed mostly by " + ", ".join(f"{o} ({x:.0%})" for x, o in into) if into else ""),
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
        notes.append({"clusters": [cid], "text": f"{cid} is unstable ({c['size']} papers, stability "
                                                  f"{c['stability']:.2f}, below {UNSTABLE}), but neither thin nor "
                                                  "trading papers; it does not halt the pass."})
    return out, notes, {"max_null_excess": float(max(excess)), "chosen_null_excess": float(excess[curve.index(chosen)]),
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
        msg = (f"--level or granularity must be coarser, finer, or one of this pool's levels: targets {levels}, "
               f"reached {[l['clusters'] for l in curve]}; not {how!r}")
        if source == "user override":
            usage(msg)  # a bad --level is a usage error; a bad granularity in the input is not
        sys.exit(msg)
    st = curve[new]["stability"]
    flag = f"; below tau ({st:.2f})" if st < tau else ""
    if flag:
        print(f"WARNING: the steered level, {curve[new]['clusters']} clusters, has stability {st:.2f}, below tau")
    return new, f"{rule}, moved by {source} ({how})", (f"{reason}; moved by {source} ({how}) to "
                                                        f"{curve[new]['clusters']} clusters{flag}")


def clustering_line(chosen, rule, curve, li, sensitivity, tau, k, c, cutoffs, diagnostics, override="none"):
    """The retrieval log's Clustering line, in the form docs/formats.md gives."""
    nxt = (f"; next finer level {curve[li + 1]['clusters']} clusters at {curve[li + 1]['stability']:.2f}"
           if li + 1 < len(curve) else "; no finer level")
    lo, hi = sensitivity[f"{tau - 0.05:.2f}"], sensitivity[f"{tau + 0.05:.2f}"]
    diag = "; ".join(f"{d['case']}: {d['detail']} -> <action taken>" for d in diagnostics) or "none"
    cuts = ", ".join(cutoffs) if cutoffs else "none (all skipped; stability from resampling only)"
    return (f"- **Clustering:** measure {MEASURE}; level {chosen['clusters']} clusters by rule {rule}, "
            f"stability {chosen['stability']:.2f}{nxt}; τ ± 0.05 would give {lo} | {hi} clusters; "
            f"grid {[l['clusters'] for l in curve]}; τ={tau}, k={k}, c={c:g}; holdout cutoffs {cuts}; "
            f"diagnostics: {diag}; manual overrides: {override}")


def match_lines(prev):
    """The printout of a match to the previous clustering: each new cluster and where it came from, then every change
    in one line: splits, merges, absorptions, new and reshuffled clusters, and vanished ones."""
    def num(key):
        return (int(key[1:]), key) if key[1:].isdigit() else (1 << 30, key)

    def names(xs):
        return ", ".join(sorted(xs, key=num))
    old, new = prev["old"], prev["new"]
    lines = [f"  {b}: {x['case']}" + (f" from {names(x['from'])}" if x.get("from") else "") + f" ({x['share']:.0%})"
             for b, x in sorted(new.items(), key=lambda kv: num(kv[0]))]
    changes = []
    for a, x in sorted(old.items(), key=lambda kv: num(kv[0])):
        if x["case"] == "split":
            changes.append(f"{a} split into {names(x['to'])}")
        elif x["case"] == "absorbed":
            changes.append(f"{a} absorbed into {x['to'][0]}")
        elif x["case"] == "vanished":
            changes.append(f"{a} vanished")
    for b, x in sorted(new.items(), key=lambda kv: num(kv[0])):
        if x["case"] == "merged":
            changes.append(f"{names(x['from'])} merged into {b}")
        elif x["case"] == "new":
            changes.append(f"{b} new ({x['fresh']:.0%} of its papers new)")
        elif x["case"] == "reshuffled":
            changes.append(f"{b} reshuffled from several clusters")
    frags = prev.get("fragments") or {}
    if frags.get("old") or frags.get("new"):
        changes.append(f"fragments under {MIN_CLUSTER} papers, not matched: {frags.get('old', 0)} old, "
                       f"{frags.get('new', 0)} new")
    lines.append("  changes: " + ("; ".join(changes) if changes else "none; every cluster matched"))
    return lines


def month_back(d, months):
    y, m = d.year, d.month - months
    while m <= 0:
        y, m = y - 1, m + 12
    return date(y, m, min(d.day, 28)).isoformat()


# --- main -----------------------------------------------------------------------------------------


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    topic = argv[0]
    for gone in ("--rule",):
        if gone in argv:
            usage(f"{gone} was removed; the level is always the finest reaching --tau")
    k, c, reps = opt(argv, "--k", K, int), opt(argv, "--c", C_REFS, float), opt(argv, "--reps", REPS, int)
    tau, n_nulls = opt(argv, "--tau", TAU, float), opt(argv, "--nulls", NULLS, int)
    if n_nulls < 1:
        usage("--nulls must be at least 1; the null draw is the `no structure` guard")
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
    S = combined_sim(T, C, recs, c)
    print(f"{topic}: {n} papers ({len(skipped)} without data), {len(edges)} citation links; levels {levels}; "
          f"measure {MEASURE}, tau={tau}, k={k}, c={c}; holdout cutoffs {cutoffs}")
    if not cutoffs:
        print(f"NOTE: every holdout cutoff ({', '.join(f'{m} months' for m in HOLDOUT_MONTHS)} back) leaves less than "
              f"{MIN_HOLDOUT_SHARE:.0%} of the pool, so all are skipped: stability is the resampling score alone")

    rng = np.random.default_rng(0)  # one stream across the levels, so the resamples match earlier runs of this method
    curve = [level_stats(S, k, L, cutoffs, dates, reps, rng, subset_sim(T, C, recs, c)) for L in levels]
    print(f"  {MEASURE:9}" + " ".join(f"{l['clusters']:>3}:{l['stability']:.2f}" for l in curve))

    # The null curve: the same pipeline on structure-free data, for the `no structure` guard only.
    draws = []
    for d in range(n_nulls):
        rng = np.random.default_rng(1000 + d)
        Tn, Cn = null_text(recs, rng), null_refs(recs, rng)
        draws.append((combined_sim(Tn, Cn, recs, c), subset_sim(Tn, Cn, recs, c)))
    null_curve = []
    for L in levels:
        runs = [level_stats(dr, k, L, cutoffs, dates, reps, np.random.default_rng(0), sub) for dr, sub in draws]
        null_curve.append({"clusters": float(np.mean([r["clusters"] for r in runs])),
                           "stability": float(np.mean([r["stability"] for r in runs])),
                           "stability_se": float(np.sqrt(sum(r["stability_se"] ** 2 for r in runs)) / len(runs))})
    print(f"  null     " + " ".join(f"{l['clusters']:>5.1f}:{l['stability']:.2f}" for l in null_curve))

    li_tau, tau_reason = choose_level(curve, tau)
    li, rule, level_reason = steer(argv, topic, levels, li_tau, "tau", tau_reason, curve, tau)
    sensitivity = {f"{x:.2f}": curve[choose_level(curve, x)[0]]["clusters"] for x in (tau - 0.05, tau, tau + 0.05)}
    chosen = curve[li]
    labels = np.array(chosen["labels"])

    # Renumber clusters by size, largest first, as c1, c2, ...
    order = [int(x) for x in np.argsort(-np.bincount(labels), kind="stable")]
    rename = {old: f"c{i + 1}" for i, old in enumerate(order)}
    # In-degree within the pool: how many pool papers cite each paper. `edges` above is undirected, for cohesion.
    indeg = np.bincount([by_s2[x] for i, r in enumerate(recs) for x in set(r["refs"]) if x in by_s2 and by_s2[x] != i],
                        minlength=n)
    finer = curve[li + 1] if li + 1 < len(levels) else None
    clusters = []
    for old in order:
        members = np.flatnonzero(labels == old)
        top = sorted(members, key=lambda i: -indeg[i])[:8]
        sub = []
        if finer:
            # Leiden levels are not nested: a finer cluster can straddle several clusters of this level. Each part
            # (finer cluster ∩ this cluster) is scored on its own papers, against the finer level's reruns.
            fl = np.array(finer["labels"])
            for f in np.unique(fl[members]):
                part = members[fl[members] == f]
                if len(part) >= MIN_CLUSTER:
                    sub.append({"size": len(part), "stability": part_score(part, finer["reruns"]),
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
    } for l, nl in zip(curve, null_curve)]
    g_knn = knn_graph(S, k)
    knn = [[ids[e.source], ids[e.target], round(w, 3)] for e, w in zip(g_knn.es, g_knn.es["weight"])]

    score, mixed, near = fringe_scores(T, C, recs, k, c, COHORT)
    # Percentiles within a cohort of about COHORT papers tie often, so ties are broken by the mixed score itself.
    fringe = [{"id": ids[i], "score": round(float(score[i]), 3), "nn_text": round(float(near["text"][i]), 3),
               "nn_refs": round(float(near["refs"][i]), 3), "refs": len(recs[i]["refs"]), "year": recs[i].get("year"),
               "cluster": rename[int(labels[i])]} for i in sorted(range(n), key=lambda i: (-score[i], -mixed[i]))]

    assignment = {ids[i]: rename[int(labels[i])] for i in range(n)}
    survey_labels = [papers[a].get("cluster") or "" for a in ids]
    exchange = exchange_rates(S, labels, k, chosen["gamma"], reps, np.random.default_rng(1))
    diagnostics, notes, health = diagnose(curve, null_curve, chosen, clusters, exchange, tau, recs, rename)

    report = {
        "generated": time.strftime("%Y-%m-%d"), "pool_fetched": sorted({r.get("fetched") or sidecar.get("fetched") for r in recs} - {None}),
        "params": {"k": k, "c": c, "reps": reps, "nulls": n_nulls, "levels": levels, "cutoffs": cutoffs,
                   "tau": tau, "subcluster_score": SUBCLUSTER_SCORE, "fringe_cohort": COHORT,
                   "defaults": {"k": K, "c": C_REFS, "reps": REPS, "nulls": NULLS, "tau": TAU, "levels": LEVELS},
                   "seeds": SEEDS,
                   "versions": {"python": platform.python_version(), **{p: version(p) for p in PACKAGES}}},
        "measure": MEASURE, "stability_from": "holdout and resampling" if cutoffs else "resampling only",
        "rule": rule, "level": chosen["clusters"], "level_reason": level_reason, "tau_sensitivity": sensitivity,
        "null_curves": {MEASURE: null_curve}, "slider": slider, "knn": knn, "fringe": fringe,
        "diagnostics": diagnostics, "notes": notes, "health": health,
        "cohesion": cohesion(labels, T, C, edges),
        "ami_vs_survey_clusters": float(ami(survey_labels, labels)),
        "curves": {MEASURE: [{x: l[x] for x in l if x not in ("labels", "clusterwise", "reruns")} for l in curve]},
        "ids": ids, "assignment": assignment,
        "clusters": clusters, "skipped": skipped,
    }
    out = topic_dir(topic) / "clusters.json"
    if out.exists() and named_computed(topic):
        # The Clusters table names the clustering its `computed` ids refer to. Match the new clustering to that one, so
        # that tools/assign.py remap can carry the names over. If the clustering has been rerun since without a remap
        # (a --level rerun), the named one is the baseline stored by that run. With no names yet, as on a first pass,
        # there is nothing to carry, and no matching is recorded.
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

    print(f"\nlevel: {chosen['clusters']} clusters ({level_reason})")
    print("tau sensitivity: " + ", ".join(f"{a} -> {b} clusters" for a, b in sensitivity.items()))
    print(f"cohesion: " + ", ".join(f"{a} {b:.3f}" for a, b in report["cohesion"].items() if b is not None)
          + f"; AMI vs survey clusters {report['ami_vs_survey_clusters']:.3f}")
    for cl in clusters:
        st = f"{cl['stability']:.2f}" if cl["stability"] is not None else "n/a"
        print(f"  {cl['id']:>4} {cl['size']:>3} papers, stability {st}, {len(cl['subclusters'])} sub-clusters"
              + (" (divided)" if cl["divided"] else "") + f"; e.g. {cl['top'][0][1][:70]}")
    print(f"\nstability diagnostics (excess over random: {health['chosen_null_excess']:.2f} at the chosen level, "
          f"{health['max_null_excess']:.2f} at most; {health['thin_reference_share']:.0%} of papers with few references):")
    for d in diagnostics or [{"case": "none", "detail": "no case of docs/process.md, \"When stability fails\", applies",
                              "action": "proceed"}]:
        print(f"  {d['case']}: {d['detail']}\n      -> {d['action']}")
    if notes:
        print("notes (no action; mention them in the Clustering rationale):")
        for x in notes:
            print(f"  {x['text']}")
    print("\nhighest fringe scores (distance to nearest neighbours, ranked within age cohort):")
    for f in fringe[:8]:
        print(f"  {f['score']:.2f}  {f['year']}  {f['cluster']:>4}  {f['refs']:>3} refs  {papers[f['id']]['title'][:72]}")
    print("\nlog line (replace the computed ids c1, c2, ... with the Clusters table's ids, and each <action taken>):")
    override = f"level {opt(argv, '--level', None, str)} (--level)" if "--level" in argv else "none"
    print(clustering_line(chosen, rule, curve, li, sensitivity, tau, k, c, cutoffs, diagnostics, override))
    if "previous" in report:
        print(f"\nmatched to the previous clustering ({report['previous']['generated']}; tools/match.py):")
        print("\n".join(match_lines(report["previous"])))
        print(f"  carry the names over with `python3 tools/assign.py remap {topic}`")
    print(f"\nwrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
