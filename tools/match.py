# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scikit-learn", "igraph", "leidenalg"]
# ///
"""Matching clusters across passes: the matching rule, and a simulation of earlier passes on one topic.

Usage: uv run tools/match.py simulate <topic> [--months 3,6,9] [--reps 20] [--workers 12]
       uv run tools/match.py history <topic> [--segments 4] [--seeds 5] [--reps 20] [--workers 12]

Clusters are matched by their members, on the papers both passes contain. For each old cluster, its main destination
is the new cluster holding most of its papers; for each new cluster, its main source is the old cluster contributing
most of its old papers. Then:

  matched   an old and a new cluster that are each other's main destination and source, with a majority both ways;
            the new cluster keeps the old id and name;
  split     an old cluster, not matched, whose papers form the majority of two or more new clusters that together hold
            at least half of it;
  merged    two or more old clusters whose majorities went into the same new cluster;
  absorbed  an old cluster, not matched, whose majority went into a new cluster that is mainly another cluster;
  vanished  an old cluster with no majority anywhere: its papers scattered;
  new       a new cluster made mostly of papers the old pass did not have;
  reshuffled a new cluster of old papers drawn from several old clusters, none of them a majority.

Clusters smaller than 3 papers on either side are fragments: they are counted, not matched, and their papers are left
out of the shares.

`simulate` treats the pool as it stood --months ago as an earlier pass: the full method of tools/cluster.py (measure
choice, then the finest level reaching tau) on the papers dated before each cutoff. It matches each to today's
clustering from graphs/<topic>/clusters.json, and separates the two causes of change by also clustering the old papers
with today's settings (today's measure and number of clusters):

  old pass vs old papers, today's settings      the change due to settings: a different measure or level;
  old papers, today's settings vs today          the change due to the new papers.

`history` asks, per cluster, since when today's clusters exist. It divides the pool by publication date into
--segments segments with the same number of papers each, so that a busy period gets narrower segments, and takes the
pool as it stood at the end of each segment: a snapshot. Each snapshot is clustered with today's measure and number of
clusters, at --seeds seeds, and matched to today's clustering. A cluster is first seen at the earliest snapshot from
which it is matched in a majority of seeds at every later snapshot. Where it is not matched, the report says why, from
how many of its papers the snapshot already had: fewer than 10 is a lack of data, not a change in the field; more means
its papers were grouped differently. Snapshots are cumulative and drawn from today's pool, whose old papers are the ones
still relevant today, so the history is optimistic: a real earlier pass would have looked messier.

Writes graphs/<topic>/match-simulation.json (simulate) or graphs/<topic>/history.json (history). Not part of a pass.
Deterministic: every random choice is seeded.
"""

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path

import numpy as np
from sklearn.metrics import adjusted_rand_score as ari

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from cluster import (HOLDOUT_MONTHS, LEVELS, MEASURES, MIN_CLUSTER, MIN_HOLDOUT_SHARE, SMALL, TAU,  # noqa: E402
                     choose_level,
                     choose_measure, combined_sim, knn_graph, leiden, level_stats, month_back, opt, refs_sim, text_sim,
                     tune)
from graph import parse, topic_dir  # noqa: E402

MAJORITY = 0.5  # the share that makes a cluster the main destination or source "by a majority"


# --- the matching rule ----------------------------------------------------------------------------


def match(old, new):
    """Match two clusterings, given as {paper id: cluster id}; returns one record per old and per new cluster."""
    def drop_fragments(lab):
        size = {}
        for c in lab.values():
            size[c] = size.get(c, 0) + 1
        return {p: c for p, c in lab.items() if size[c] >= MIN_CLUSTER}, sum(1 for n in size.values() if n < MIN_CLUSTER)
    old, frag_old = drop_fragments(old)
    new, frag_new = drop_fragments(new)
    shared = set(old) & set(new)
    O = {c: {p for p in old if old[p] == c} for c in set(old.values())}
    N = {c: {p for p in new if new[p] == c} for c in set(new.values())}
    Os = {a: A & shared for a, A in O.items()}
    Ns = {b: B & shared for b, B in N.items()}
    inter = {(a, b): len(Os[a] & Ns[b]) for a in O for b in N}
    dest = {a: max(N, key=lambda b: inter[a, b]) for a in O}
    src = {b: max(O, key=lambda a: inter[a, b]) for b in N}
    s = {a: inter[a, dest[a]] / len(Os[a]) if Os[a] else 0.0 for a in O}  # share of a going to its destination
    t = {b: inter[src[b], b] / len(Ns[b]) if Ns[b] else 0.0 for b in N}  # share of b's old papers from its source

    out_old, out_new = {}, {}
    for a in O:
        b = dest[a]
        if src[b] == a and s[a] >= MAJORITY and t[b] >= MAJORITY:
            out_old[a] = {"case": "matched", "to": [b], "share": s[a]}
            out_new[b] = {"case": "matched", "from": [a], "share": t[b]}
    for a in O:
        if a in out_old:
            continue
        parts = [b for b in N if b not in out_new and src[b] == a and t[b] >= MAJORITY]
        taken = sum(inter[a, b] for b in parts) / len(Os[a]) if Os[a] else 0.0
        if len(parts) >= 2 and taken >= MAJORITY:
            out_old[a] = {"case": "split", "to": parts, "share": taken}
            for b in parts:
                out_new[b] = {"case": "split", "from": [a], "share": t[b]}
    into = {}
    for a in O:
        if a not in out_old and s[a] >= MAJORITY:
            into.setdefault(dest[a], []).append(a)
    for b, srcs in into.items():
        case = "merged" if len(srcs) >= 2 and b not in out_new else "absorbed"
        for a in srcs:
            out_old[a] = {"case": case, "to": [b], "share": s[a]}
        if case == "merged":
            out_new[b] = {"case": "merged", "from": srcs, "share": sum(inter[a, b] for a in srcs) / len(Ns[b])}
    for a in O:
        out_old.setdefault(a, {"case": "vanished", "to": [], "share": s[a]})
    for b in N:
        if b in out_new:
            continue
        fresh = 1 - len(Ns[b]) / len(N[b])
        out_new[b] = {"case": "new" if fresh >= MAJORITY else "reshuffled", "from": [], "share": t[b], "fresh": fresh}
    return out_old, out_new, {"old": frag_old, "new": frag_new}


# --- simulation -----------------------------------------------------------------------------------

RECS, DATES = None, None


def setup(recs, dates):
    global RECS, DATES
    RECS, DATES = recs, dates


def sim(idx, measure, c):
    recs = [RECS[i] for i in idx]
    if measure == "text":
        return text_sim(recs)
    if measure == "refs":
        return refs_sim(recs)
    return combined_sim(text_sim(recs), refs_sim(recs), recs, c)


def cutoffs_for(dates):
    latest = date.fromisoformat(max(dates))
    return [cut for cut in (month_back(latest, m) for m in HOLDOUT_MONTHS) if (dates < cut).mean() >= MIN_HOLDOUT_SHARE]


def curve(job):
    """The stability curve of one measure on the papers idx, as tools/cluster.py computes it."""
    idx, measure, k, c, reps = job
    S, d = sim(idx, measure, c), DATES[idx]
    rng = np.random.default_rng(0)
    return [level_stats(S, k, L, cutoffs_for(d), d, reps, rng) for L in LEVELS if L <= len(idx) // 4]


def today_settings(job):
    """The papers idx clustered with today's measure and number of clusters."""
    idx, measure, k, c, target = job
    g = knn_graph(sim(idx, measure, c), k)
    return leiden(g, tune(g, target)[0], 0)


def simulate(argv):
    topic = argv[0]
    months = opt(argv, "--months", [3, 6, 9], lambda s: [int(x) for x in s.split(",")])
    reps, workers = opt(argv, "--reps", 20, int), opt(argv, "--workers", 12, int)
    rep = json.loads((topic_dir(topic) / "clusters.json").read_text())
    k, c, tau = rep["params"]["k"], rep["params"]["c"], rep["params"]["tau"]
    papers = parse(topic)[4]
    cache = json.loads((topic_dir(topic) / "pool.json").read_text())["papers"]
    ids = rep["ids"]
    recs = [cache[a] for a in ids]
    dates = np.array([r["date"] or f"{r['year'] or 9999}-07-01" for r in recs])
    setup(recs, dates)
    today = rep["assignment"]
    cites = {a: r["citations"] or 0 for a, r in zip(ids, recs)}
    latest = date.fromisoformat(max(dates))
    passes = [(m, np.flatnonzero(dates < month_back(latest, m))) for m in months]
    print(f"{topic}: {len(ids)} papers today; measure {rep['measure']}, level {rep['level']}; "
          f"earlier passes {', '.join(f'{m} months ago ({len(i)} papers)' for m, i in passes)}")

    t0 = time.time()
    with ProcessPoolExecutor(workers, initializer=setup, initargs=(recs, dates)) as ex:
        curves = list(ex.map(curve, [(idx, m, k, c, reps) for _, idx in passes for m in MEASURES]))
        settled = list(ex.map(today_settings, [(idx, rep["measure"], k, c, rep["level"]) for _, idx in passes]))
    print(f"done in {time.time() - t0:.0f}s")

    def label(members):
        top = max(members, key=lambda a: cites[a])
        return f"{len(members):>3} papers, e.g. {papers[top]['title'][:60]}"

    report = []
    for pi, (m, idx) in enumerate(passes):
        cv = {meas: curves[pi * len(MEASURES) + j] for j, meas in enumerate(MEASURES)}
        measure, _, why = choose_measure(cv)
        li, level_why = choose_level(cv[measure], tau)
        lab = np.array(cv[measure][li]["labels"])
        old = {ids[i]: f"o{int(x) + 1}" for i, x in zip(idx, lab)}
        old_ids = [ids[i] for i in idx]
        now_old = [today[a] for a in old_ids]
        aris = {"old pass vs today": float(ari(lab, now_old)),
                "old pass vs old papers at today's settings": float(ari(lab, settled[pi])),
                "old papers at today's settings vs today": float(ari(settled[pi], now_old))}
        mo, mn, frags = match(old, today)
        counts = {f"fragments in the old pass": frags["old"]} if frags["old"] else {}
        for r in list(mo.values()) + [v for v in mn.values() if v["case"] in ("new", "reshuffled")]:
            counts[r["case"]] = counts.get(r["case"], 0) + 1
        print(f"\n{m} months ago: {len(idx)} papers; measure {measure} ({why}); level {cv[measure][li]['clusters']} "
              f"({level_why})")
        print("  ARI " + "; ".join(f"{a}: {b:.2f}" for a, b in aris.items()))
        print("  " + ", ".join(f"{n} {case}" for case, n in sorted(counts.items(), key=lambda kv: -kv[1])))
        members_old = {a: [p for p in old if old[p] == a] for a in mo}  # fragments are not in mo
        for a in sorted(mo, key=lambda a: -len(members_old[a])):
            r = mo[a]
            print(f"    {a:>4} {label(members_old[a])}  -> {r['case']} {', '.join(r['to'])} ({r['share']:.0%})")
        for b, r in sorted(mn.items()):
            if r["case"] in ("new", "reshuffled"):
                members = [p for p in today if today[p] == b]
                print(f"    {b:>4} {label(members)}  <- {r['case']} ({r['fresh']:.0%} papers new)")
        report.append({"months_ago": m, "papers": len(idx), "measure": measure, "measure_reason": why,
                       "level": cv[measure][li]["clusters"], "level_reason": level_why, "ari": aris,
                       "counts": counts, "fragments": frags, "old": mo, "new": mn, "assignment": old})
    out = topic_dir(topic) / "match-simulation.json"
    out.write_text(json.dumps({"generated": time.strftime("%Y-%m-%d"), "today_level": rep["level"],
                               "today_measure": rep["measure"], "passes": report}, indent=1))
    print(f"\nwrote {out.relative_to(ROOT)}")


# --- history --------------------------------------------------------------------------------------


def snapshot(job):
    """One snapshot clustered with today's settings: its stability at that count, and its labels at several seeds."""
    idx, measure, k, c, target, seeds, reps = job
    S, d = sim(idx, measure, c), DATES[idx]
    g = knn_graph(S, k)
    gamma, got = tune(g, target)
    st = level_stats(S, k, target, cutoffs_for(d), d, reps, np.random.default_rng(0))
    return {"clusters": got, "stability": st["stability"], "labels": [leiden(g, gamma, s) for s in range(seeds)]}


def cluster_history(ids, recs, dates, today, measure, level, k, c, tau, segments=4, seeds=5, reps=20, workers=12):
    """Since when each of today's clusters exists, from snapshots of the pool at equal-count date cutoffs.

    today maps each paper id to its cluster id. Returns the snapshots, and per cluster its first-seen cutoff, a
    statement in words, and at each snapshot how many of its papers existed and whether it was matched.
    """
    setup(recs, dates)
    order = np.sort(dates)
    cuts = [str(order[int(len(ids) * q / segments)]) for q in range(1, segments)]
    snaps = [(cut, np.flatnonzero(dates < cut)) for cut in cuts]
    with ProcessPoolExecutor(workers, initializer=setup, initargs=(recs, dates)) as ex:
        runs = list(ex.map(snapshot, [(idx, measure, k, c, level, seeds, reps) for _, idx in snaps]))
    names = sorted(set(today.values()), key=lambda b: int(b[1:]) if b[1:].isdigit() else b)
    members = {b: [a for a in ids if today[a] == b] for b in names}
    out = {}
    for b in names:
        rows = []
        for (cut, idx), run in zip(snaps, runs):
            have = {ids[i] for i in idx}
            cases = [match({ids[i]: f"s{int(x)}" for i, x in zip(idx, lab)}, today)[1].get(b, {"case": "fragment"})["case"]
                     for lab in run["labels"]]
            matched, present = cases.count("matched"), sum(a in have for a in members[b])
            common = max(set(cases), key=cases.count)
            why = ("found" if matched > seeds // 2 else
                   f"too few papers ({present})" if present < SMALL else f"its papers were grouped differently ({common})")
            rows.append({"cutoff": cut, "present": present, "matched_seeds": matched, "case": common, "why": why,
                         "snapshot_stability": run["stability"]})
        first = None  # the earliest snapshot from which the cluster is found at every later snapshot
        for j in range(len(rows) - 1, -1, -1):
            if rows[j]["why"] != "found":
                break
            first = j
        out[b] = {"first_seen": cuts[first] if first is not None else None, "snapshots": rows,
                  "statement": statement(rows, first, tau)}
    return {"segments": segments, "seeds": seeds, "cutoffs": cuts,
            "snapshots": [{"cutoff": cut, "papers": len(idx), "clusters": run["clusters"], "stability": run["stability"]}
                          for (cut, idx), run in zip(snaps, runs)],
            "clusters": out}


def statement(rows, first, tau):
    """Since when a cluster exists, in words. A snapshot below tau is itself unreliable, so its finding is hedged."""
    if first is None:
        return f"new since {rows[-1]['cutoff']}; before that, {rows[-1]['why']}"
    st = rows[first]["snapshot_stability"]
    hedge, note = ("probably ", f" (that snapshot's stability {st:.2f})") if st < tau else ("", "")
    if first == 0:
        return f"{hedge}since {rows[0]['cutoff']} or earlier{note}"
    return f"{hedge}since {rows[first]['cutoff']}{note}; before that, {rows[first - 1]['why']}"


def history(argv):
    topic = argv[0]
    segments, seeds = opt(argv, "--segments", 4, int), opt(argv, "--seeds", 5, int)
    reps, workers = opt(argv, "--reps", 20, int), opt(argv, "--workers", 12, int)
    rep = json.loads((topic_dir(topic) / "clusters.json").read_text())
    papers = parse(topic)[4]
    cache = json.loads((topic_dir(topic) / "pool.json").read_text())["papers"]
    ids = rep["ids"]
    recs = [cache[a] for a in ids]
    dates = np.array([r["date"] or f"{r['year'] or 9999}-07-01" for r in recs])
    h = cluster_history(ids, recs, dates, rep["assignment"], rep["measure"], rep["level"], rep["params"]["k"],
                        rep["params"]["c"], rep["params"]["tau"], segments, seeds, reps, workers)
    cites = {a: r["citations"] or 0 for a, r in zip(ids, recs)}
    print(f"{topic}: {len(ids)} papers; today {rep['level']} clusters by {rep['measure']}")
    print("snapshots, clustered with today's settings:")
    for sn in h["snapshots"]:
        print(f"  before {sn['cutoff']}: {sn['papers']:>3} papers, {sn['clusters']} clusters, stability {sn['stability']:.2f}")
    print(f"per cluster (papers present at each snapshot, found in how many of {seeds} seeds):")
    for b, e in h["clusters"].items():
        mem = [a for a in ids if rep["assignment"][a] == b]
        top = max(mem, key=lambda a: cites[a])
        print(f"  {b} ({len(mem)} papers, e.g. {papers[top]['title'][:55]}): {e['statement']}")
        for row in e["snapshots"]:
            print(f"      before {row['cutoff']}: {row['present']:>3} papers, found {row['matched_seeds']}/{seeds}")
    print("\nlog line:\n" + log_line(h))
    out = topic_dir(topic) / "history.json"
    out.write_text(json.dumps({"generated": time.strftime("%Y-%m-%d"), "level": rep["level"], "measure": rep["measure"],
                               **h}, indent=1))
    print(f"\nwrote {out.relative_to(ROOT)}")


def log_line(h):
    """The retrieval log's Temporal stability line; the agent replaces computed ids with the Clusters table's ids."""
    snaps = ", ".join(f"{sn['cutoff']} ({sn['papers']} papers, stability {sn['stability']:.2f})" for sn in h["snapshots"])
    per = " | ".join(f"{b} {e['statement']}" for b, e in h["clusters"].items())
    return f"- **Temporal stability:** {h['segments']} equal-count segments; snapshots {snaps}; {per}"


if __name__ == "__main__":
    commands = {"simulate": simulate, "history": history}
    if len(sys.argv) < 3 or sys.argv[1] not in commands:
        sys.exit(__doc__)
    commands[sys.argv[1]](sys.argv[2:])
