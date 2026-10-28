"""Experiment: recursive clustering with a per-cluster stopping rule, against the global levels of deeper_research/cluster.py.

Usage: uv run python -m deeper_research.recursive <topic> [--rules tau,strict,partial,confirmed,partial-confirmed] [--min-node 20]
                                          [--max-split 6] [--tau 0.75] [--child 0.6] [--delta 0.15] [--reps 20]
                                          [--reruns 10] [--workers 12]

The global method picks one level for the whole pool. This experiment starts from that clustering and then splits each
cluster on its own, and so on, until a cluster no longer divides reliably. Each cluster is clustered as if it were a
pool of its own: its own similarity scale, its own neighbour graph and its own resolution. A cluster is tried as 2 to
--max-split parts, and a split is accepted under one of these rules:

  tau      the finest split whose stability, tested on the cluster's own papers, reaches --tau;
  null     as tau, and the split must also beat the same split on structure-free data by --delta;
  strict   as tau, and every part of 3 or more papers must come back end to end with a score of at least --child;
  partial  the parts that come back end to end with a score of at least --child are kept; the rest of the cluster is
           merged into one remainder, which is not split further. No whole-split tau gate.
  confirmed, partial-confirmed
           strict or partial, then a shakedown: on every disturbed version of the cluster, the split decision is made
           again from scratch (resolution, number of parts, and the rule's own tests), with the rounds above held fixed.
           Only parts that come back in those reruns with a score of at least --child are kept. Under strict, a part
           that fails means no split; under partial, it joins the remainder. Only the chosen candidate is shaken.
           Reruns on 80% of the data shrink every cluster, so a split close to a threshold tends to fail: the shakedown
           leans towards coarse clusters by design. In effect --min-node rises to about --min-node / 0.8.

"End to end" means the whole pool is disturbed (time holdouts and resamples of 80%), every step from the top down is
reclustered at the resolution it used, and at each step the cluster best matching the path is followed. A part's score
is its best Jaccard match at the end: the mean over the holdouts and the mean over the resamples, averaged. A local test
keeps the parent's papers fixed, so it cannot see the parent's boundary moving; this one can.

Clusters smaller than --min-node are not split; in a rerun on part of the pool, the minimum shrinks in proportion.
Each tree is then compared with the global method by rerunning both from scratch on the time holdouts and on --reruns
resamples: overall agreement, per-cluster scores, cluster counts, and AMI with the survey's own grouping.

Reads graphs/<topic>/pool.json and graphs/<topic>/clusters.json (for the measure and settings); writes
graphs/<topic>/recursive.json. Not part of a pass. Deterministic: every random choice is seeded.
"""

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path

import numpy as np
from sklearn.metrics import adjusted_mutual_info_score as ami
from sklearn.metrics import adjusted_rand_score as ari

ROOT = Path(__file__).resolve().parent.parent
from deeper_research.cluster import (HOLDOUT_MONTHS, LEVELS, MIN_CLUSTER, MIN_HOLDOUT_SHARE, NO_STRUCTURE,  # noqa: E402
                     SUBCLUSTER_SCORE, TAU, best_jaccard, combined_sim, knn_graph, leiden, level_stats, month_back,
                     n_clusters, null_refs, null_text, opt, refs_sim, text_sim, tune)
from deeper_research.graph import parse, topic_dir  # noqa: E402

# Set in each worker by setup(): the pool's records, dates and the run's settings.
RECS, DATES, CFG = None, None, None


def setup(recs, dates, cfg):
    global RECS, DATES, CFG
    RECS, DATES, CFG = recs, dates, cfg


def similarity(idx, rng=None):
    """The measure on the papers idx alone, or, with rng, on structure-free data of the same shape."""
    recs, m = [RECS[i] for i in idx], CFG["measure"]
    if rng is None:
        T, C = (text_sim(recs) if m != "refs" else None), (refs_sim(recs) if m != "text" else None)
    else:
        T, C = (null_text(recs, rng) if m != "refs" else None), (null_refs(recs, rng) if m != "text" else None)
    return {"text": T, "refs": C}.get(m) if m != "combined" else combined_sim(T, C, recs, CFG["c"])


def cutoffs_for(dates):
    latest = date.fromisoformat(max(dates))
    return [cut for cut in (month_back(latest, m) for m in HOLDOUT_MONTHS) if (dates < cut).mean() >= MIN_HOLDOUT_SHARE]


def stats(S, target, cuts, dates):
    st = level_stats(S, CFG["k"], target, cuts, dates, CFG["reps"], np.random.default_rng(0))
    if not cuts:  # too few older papers in this cluster for a time holdout: resampling alone
        st["stability"] = st["resample_ari"]
    return st


def groups(idx, lab):
    return [idx[lab == c] for c in np.unique(lab)]


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


# --- end-to-end scores ----------------------------------------------------------------------------
# Every node carries its perturbed versions: for each disturbed pool, the set of papers that, after reclustering every
# step above it, best matches the node. A candidate split is scored by reclustering each perturbed version.


def perturbations(root):
    """Disturbed versions of the pool: time holdouts (three seeds each) and resamples of 80%."""
    d = DATES[root]
    out = [("holdout", root[d < cut], s) for cut in cutoffs_for(d) for s in range(3)]
    rng = np.random.default_rng(0)
    out += [("resample", np.sort(rng.choice(root, int(0.8 * len(root)), replace=False)), r) for r in range(CFG["reps"])]
    return out


def follow(perts, versions, gamma, parts):
    """Recluster each perturbed version at gamma; per part, its best-matching group in each, and its score."""
    found = [[] for _ in parts]
    sims = [[] for _ in parts]
    for (kind, P, seed), Q in zip(perts, versions):
        if len(Q) < 4:
            gs = [Q]
        else:
            gs = groups(Q, leiden(knn_graph(similarity(Q), CFG["k"]), gamma, seed))
        Pset = set(P)
        for j, part in enumerate(parts):
            target = [i for i in part if i in Pset]
            best = max(gs, key=lambda g: jaccard(g, target))
            found[j].append(best)
            sims[j].append((kind, jaccard(best, target)))
    scores = []
    for s in sims:
        h = [x for k, x in s if k == "holdout"]
        r = [x for k, x in s if k == "resample"]
        scores.append(float((np.mean(h) + np.mean(r)) / 2) if h else float(np.mean(r)))
    return found, scores


# --- recursive method -----------------------------------------------------------------------------


def try_splits(node, rule, perts):
    """Every candidate split of the node, with its local stability and, if needed, its parts' end-to-end scores."""
    idx = node["idx"]
    S, dates = similarity(idx), DATES[idx]
    cuts = cutoffs_for(dates)
    nulls = [similarity(idx, np.random.default_rng(1000 + d)) for d in range(CFG["nulls"])] if rule == "null" else []
    cands = []
    for t in range(2, min(CFG["max_split"], len(idx) // 4) + 1):
        st = stats(S, t, cuts, dates)
        if st["clusters"] < 2 or any(x["clusters"] == st["clusters"] for x in cands):
            continue
        parts = sorted(groups(idx, np.array(st["labels"])), key=len, reverse=True)
        x = {"clusters": st["clusters"], "stability": st["stability"], "gamma": st["gamma"], "parts": parts}
        if nulls:
            x["null"] = float(np.mean([stats(N, t, cuts, dates)["stability"] for N in nulls]))
        x["found"], x["scores"] = follow(perts, node["versions"], st["gamma"], parts)
        cands.append(x)
    return cands


BASE = {"confirmed": "strict", "partial-confirmed": "partial"}


def shakedown(node, x, keep, perts, base):
    """Redo the split decision from scratch on each disturbed version of the node; per kept part, its score."""
    sims, made = [[] for _ in keep], 0
    for (kind, P, _), V in zip(perts, node["versions"]):
        parts = [V]
        if len(V) >= CFG["min_node"]:
            local = perturbations(V)
            pick = choose(try_splits({"idx": V, "versions": [Q for _, Q, _ in local]}, base, local), base)
            if pick:
                y, kp = pick
                made += 1
                rest = [i for j in range(len(y["parts"])) if j not in kp for i in y["parts"][j]]
                parts = [y["parts"][j] for j in kp] + ([np.array(rest)] if rest else [])
        Pset = set(P)
        for t, j in enumerate(keep):
            target = [i for i in x["parts"][j] if i in Pset]
            sims[t].append((kind, max(jaccard(g, target) for g in parts)))
    scores = []
    for s in sims:
        h, r = [v for k, v in s if k == "holdout"], [v for k, v in s if k == "resample"]
        scores.append(float((np.mean(h) + np.mean(r)) / 2) if h else float(np.mean(r)))
    return scores, made


def choose(cands, rule):
    """The accepted candidate under the rule, and which of its parts are kept as clusters; or None."""
    tau, child = CFG["tau"], CFG["child"]
    if rule == "partial":
        best = None
        for x in cands:
            keep = [j for j, p in enumerate(x["parts"]) if len(p) >= MIN_CLUSTER and x["scores"][j] >= child]
            rest = sum(len(x["parts"][j]) for j in range(len(x["parts"])) if j not in keep)
            if len(keep) + (rest > 0) < 2 or not keep:
                continue
            key = (sum(len(x["parts"][j]) for j in keep), len(keep))
            if best is None or key > best[0]:
                best = (key, x, keep)
        return (best[1], best[2]) if best else None
    ok = []
    for x in cands:
        big = [j for j, p in enumerate(x["parts"]) if len(p) >= MIN_CLUSTER]
        if x["stability"] < tau:
            continue
        if rule == "null" and x["stability"] - x["null"] < CFG["delta"]:
            continue
        if rule == "strict" and any(x["scores"][j] < child for j in big):
            continue
        ok.append(x)
    if not ok:
        return None
    x = max(ok, key=lambda x: x["clusters"])
    return x, list(range(len(x["parts"])))


def refine(node, rule, perts):
    if node["size"] < CFG["min_node"]:
        node["stop"] = "too small to split"
        return node
    base = BASE.get(rule, rule)
    cands = try_splits(node, base, perts)
    node["candidates"] = [{"clusters": x["clusters"], "stability": x["stability"], "null": x.get("null"),
                           "parts": [len(p) for p in x["parts"]], "scores": x["scores"]} for x in cands]
    pick = choose(cands, base)
    if pick is None:
        node["stop"] = "no split passes"
        return node
    x, keep = pick
    if rule in BASE:
        big = [j for j in keep if len(x["parts"][j]) >= MIN_CLUSTER]
        scores, made = shakedown(node, x, big, perts, base)
        node["shakedown"] = {"clusters": x["clusters"], "parts": [len(x["parts"][j]) for j in big], "scores": scores,
                             "splits_made": made, "reruns": len(perts)}
        passed = [j for j, sc in zip(big, scores) if sc >= CFG["child"]]
        if base == "strict" and len(passed) < len(big):
            node["stop"] = "split not confirmed"
            return node
        rest = sum(len(x["parts"][j]) for j in range(len(x["parts"])) if j not in passed)
        if base == "partial" and (not passed or len(passed) + (rest > 0) < 2):
            node["stop"] = "split not confirmed"
            return node
        keep = passed if base == "partial" else keep
    node["split"] = {"clusters": x["clusters"], "stability": x["stability"], "kept": len(keep)}
    node["children"] = []
    for j in keep:
        child = {"depth": node["depth"] + 1, "size": len(x["parts"][j]), "idx": x["parts"][j],
                 "score": x["scores"][j], "versions": x["found"][j]}
        node["children"].append(refine(child, rule, perts))
    rest = [i for j in range(len(x["parts"])) if j not in keep for i in x["parts"][j]]
    if rest:
        node["children"].append({"depth": node["depth"] + 1, "size": len(rest), "idx": np.array(sorted(rest)),
                                 "stop": "remainder", "score": None})
    return node


def build(root, rule):
    """The global clustering of the papers root, then each of its clusters refined under the rule."""
    gamma, lab = global_split(root)
    perts = perturbations(root)
    parts = sorted(groups(root, lab), key=len, reverse=True)
    found, scores = follow(perts, [P for _, P, _ in perts], gamma, parts)
    tree = {"depth": 0, "size": len(root), "idx": root, "split": {"clusters": len(parts), "global": True}, "children": []}
    for p, f, s in zip(parts, found, scores):
        tree["children"].append(refine({"depth": 1, "size": len(p), "idx": p, "score": s, "versions": f}, rule, perts))
    return tree


def leaves(node):
    return [node] if "children" not in node else [x for ch in node["children"] for x in leaves(ch)]


def leaf_labels(tree, n):
    lab = np.full(n, -1)
    for j, lf in enumerate(leaves(tree)):
        lab[lf["idx"]] = j
    return lab


# --- global method --------------------------------------------------------------------------------


def global_split(idx, target=None):
    """The global method on the papers idx: the finest level reaching tau, or, with target, that many clusters."""
    S = similarity(idx)
    if target is not None:
        g = knn_graph(S, CFG["k"])
        gamma = tune(g, target)[0]
        return gamma, leiden(g, gamma, 0)
    cuts = cutoffs_for(DATES[idx])
    levels = [stats(S, L, cuts, DATES[idx]) for L in LEVELS if L <= len(idx) // 4]
    ok = [l for l in levels if l["stability"] >= CFG["tau"]] or levels[:1]
    best = max(ok, key=lambda l: l["clusters"])
    return best["gamma"], np.array(best["labels"])


# --- reruns from scratch --------------------------------------------------------------------------


def run(job):
    """One method on the papers idx, from scratch; returns (labels over idx, tree or None)."""
    method, idx = job
    # Size thresholds scale with the share of the pool a rerun sees; otherwise a rerun on 80% meets a stricter rule.
    CFG["min_node"] = CFG["min_node_full"] * len(idx) / len(RECS)
    if method == "global":
        return global_split(idx)[1], None
    if method.startswith("global@"):
        return global_split(idx, int(method[7:]))[1], None
    tree = build(idx, method)
    return leaf_labels(tree, len(RECS))[idx], tree


def compare(ref, idx, lab):
    """ARI against the reference over the rerun's papers, and per reference cluster of 3+ its best Jaccard match."""
    r = ref[idx]
    big = [c for c in np.unique(ref) if (ref == c).sum() >= MIN_CLUSTER]
    bj = best_jaccard(r, lab)
    return float(ari(r, lab)), {int(c): bj[int(c)] for c in big if int(c) in bj}


def main(argv):
    if not argv or argv[0].startswith("-"):
        sys.exit(__doc__)
    topic = argv[0]
    report_in = json.loads((topic_dir(topic) / "clusters.json").read_text())
    cfg = {"measure": report_in["measure"], "k": report_in["params"]["k"], "c": report_in["params"]["c"],
           "nulls": report_in["params"]["nulls"], "tau": opt(argv, "--tau", TAU, float),
           "child": opt(argv, "--child", SUBCLUSTER_SCORE, float), "delta": opt(argv, "--delta", NO_STRUCTURE, float),
           "reps": opt(argv, "--reps", 20, int), "min_node_full": opt(argv, "--min-node", 20, int),
           "max_split": opt(argv, "--max-split", 6, int)}
    rules = opt(argv, "--rules", ["tau", "strict", "partial"], lambda s: s.split(","))
    reruns, workers = opt(argv, "--reruns", 10, int), opt(argv, "--workers", 12, int)

    papers = parse(topic)[4]
    cache = json.loads((topic_dir(topic) / "pool.json").read_text())["papers"]
    ids = report_in["ids"]
    recs = [cache[a] for a in ids]
    n = len(ids)
    dates = np.array([r["date"] or f"{r['year'] or 9999}-07-01" for r in recs])
    setup(recs, dates, cfg)
    survey = [papers[a].get("cluster") or "" for a in ids]
    glob = np.array([int(report_in["assignment"][a][1:]) for a in ids])
    print(f"{topic}: {n} papers; measure {cfg['measure']}; global level {report_in['level']}; rules {rules}; {cfg}")

    t0 = time.time()
    everyone = np.arange(n)
    with ProcessPoolExecutor(workers, initializer=setup, initargs=(recs, dates, cfg)) as ex:
        full = dict(zip(["global"] + rules, ex.map(run, [(m, everyone) for m in ["global"] + rules])))
        print(f"full-pool runs done in {time.time() - t0:.0f}s")
        refs = {m: lab for m, (lab, _) in full.items()}
        trees = {m: t for m, (_, t) in full.items() if t is not None}
        counts = sorted({n_clusters(refs[r]) for r in rules} - {n_clusters(refs["global"])})
        for N in counts:
            refs[f"global@{N}"] = global_split(everyone, N)[1]
        methods = ["global"] + [f"global@{N}" for N in counts] + rules

        # Reruns from scratch: the time holdouts, then resamples of 80%.
        subsets = [("holdout", np.flatnonzero(dates < cut)) for cut in cutoffs_for(dates)]
        rng = np.random.default_rng(7)
        subsets += [("resample", np.sort(rng.choice(n, int(0.8 * n), replace=False))) for _ in range(reruns)]
        results = list(ex.map(run, [(m, idx) for m in methods for _, idx in subsets]))
    print(f"reruns done in {time.time() - t0:.0f}s")

    summary = {}
    kinds = np.array([k for k, _ in subsets])
    for mi, m in enumerate(methods):
        rows = results[mi * len(subsets):(mi + 1) * len(subsets)]
        comp = [compare(refs[m], idx, lab) for (_, idx), (lab, _) in zip(subsets, rows)]
        aris = np.array([a for a, _ in comp])
        cw = {}
        for _, d in comp:
            for c, j in d.items():
                cw.setdefault(c, []).append(j)
        sizes = np.bincount(refs[m])
        summary[m] = {
            "clusters": n_clusters(refs[m]), f"clusters_{MIN_CLUSTER}plus": int((sizes >= MIN_CLUSTER).sum()),
            "holdout_ari": float(aris[kinds == "holdout"].mean()), "resample_ari": float(aris[kinds == "resample"].mean()),
            "ami_vs_survey": float(ami(survey, refs[m])),
            "cluster_scores": {int(c): float(np.mean(v)) for c, v in cw.items()},
            "sizes": {int(c): int(sizes[c]) for c in cw},
        }

    cites = np.array([r["citations"] or 0 for r in recs])

    def show(node, out, prefix=""):
        comp = np.bincount(glob[node["idx"]], minlength=7)[1:]
        mix = ", ".join(f"c{j + 1}:{x}" for j, x in sorted(enumerate(comp), key=lambda t: -t[1]) if x)
        score = f" e2e {node['score']:.2f}" if node.get("score") is not None else ""
        if "split" in node:
            s = node["split"]
            what = ("global level" if s.get("global") else
                    f"split {s['clusters']}, stability {s['stability']:.2f}, {s['kept']} kept")
        else:
            what = f"leaf, {node['stop']}"
        out.append(f"{prefix}{node['size']:>3} [{mix}]{score} {what}")
        if "shakedown" in node:
            sd = node["shakedown"]
            out.append(f"{prefix}      shakedown of the {sd['clusters']}-split: made in {sd['splits_made']} of {sd['reruns']} "
                       "reruns; parts " + " ".join(f"{p}:{v:.2f}" for p, v in zip(sd["parts"], sd["scores"])))
        for x in node.get("candidates", []):
            out.append(f"{prefix}      try {x['clusters']}: stability {x['stability']:.2f}; parts "
                       + " ".join(f"{p}:{s:.2f}" for p, s in zip(x["parts"], x["scores"])))
        if "children" not in node:
            top = node["idx"][np.argmax(cites[node["idx"]])]
            out.append(f"{prefix}      e.g. {papers[ids[top]]['title'][:70]}")
        for ch in node.get("children", []):
            show(ch, out, prefix + "    ")

    for r, t in trees.items():
        lines = []
        show(t, lines)
        print(f"\nrule {r}: tree (size [global clusters inside], end-to-end score, decision; "
              f"tries with part size:end-to-end score):\n" + "\n".join(lines))
    print("\nreruns from scratch on each time holdout and each resample, compared with the full-pool result")
    print(f"{'method':12}{'clusters':>9}{'(3+)':>6}{'holdout':>9}{'resample':>10}{'AMI blocks':>12}  per-cluster scores (size:score)")
    for m, s in summary.items():
        cs = " ".join(f"{s['sizes'][c]}:{v:.2f}" for c, v in sorted(s["cluster_scores"].items(), key=lambda kv: -s["sizes"][kv[0]]))
        print(f"{m:12}{s['clusters']:>9}{s[f'clusters_{MIN_CLUSTER}plus']:>6}{s['holdout_ari']:>9.2f}{s['resample_ari']:>10.2f}"
              f"{s['ami_vs_survey']:>12.2f}  {cs}")

    def strip(node):
        out = {x: node[x] for x in node if x not in ("idx", "children", "versions")}
        out["members"] = [ids[i] for i in node["idx"]] if "children" not in node else None
        if "children" in node:
            out["children"] = [strip(ch) for ch in node["children"]]
        return out

    report = {"generated": time.strftime("%Y-%m-%d"), "params": {**cfg, "rules": rules, "reruns": reruns},
              "summary": summary, "trees": {r: strip(t) for r, t in trees.items()}}
    out = topic_dir(topic) / "recursive.json"
    out.write_text(json.dumps(report, indent=1))
    print(f"\nwrote {out.relative_to(ROOT)} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1:])
