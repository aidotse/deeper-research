# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scipy", "scikit-learn", "igraph", "leidenalg"]
# ///
"""Collect fringe candidates for a topic, and test how they behave under the clustering method.

Usage:
  uv run tools/fringe.py collect <topic> [--per-route 60]
  uv run tools/fringe.py analyse <topic> [--level 6]

`collect` gathers candidates outside the pool by the two routes of docs/process.md, "Fringe routes", by script and at
no model cost. It needs the pool sidecar (tools/pool.py) and the survey's retrieval log, not a clustering.

  hidden     cited by at least two pool papers, at least a year old, and the least cited overall for its age
  new        Semantic Scholar recommendations (POST /recommendations/v1/papers, positivePaperIds) from one seed set;
             the endpoint returns only the last ~2 months

The `new` route's seeds are chosen deterministically, from the pool as it stands:

  1. the frontier candidates named in the latest pass's `Orientation` line ("frontier candidates: <id>, ..."), in the
     order the line gives them, those with a record in pool.json; one without is reported and skipped;
  2. then the CITED_SEEDS (10) pool papers most cited within the pool (in-degree over pool.json's references, at
     least 1), not already seeds, ties broken by paper ID.

If the log names no frontier candidates, the route is seeded from the most-cited papers alone, with a warning. The
seeds are recorded in fringe.json. The seeding is deterministic; the endpoint's answer is not, since new papers appear.
The route keeps the first --per-route recommendations not already in the pool.

A third route, `followers` (low-cited citers of each cluster's most-cited paper), was tested and dropped.

It fetches their metadata, references and embeddings into graphs/<topic>/fringe.json, and writes a blind screening
sheet, graphs/<topic>/fringe-screen.md: titles and abstracts in shuffled order, without the route, for an agent to
mark in or out of scope. A rerun keeps the judgements already on the sheet. Each candidate records its arXiv ID or,
failing that, its CorpusId; tools/assign.py add-fringe then adds the in-scope ones to the pool.

`analyse` adds the in-scope candidates to the pool and reclusters with the chosen measure. Per route, it reports how
consistently papers keep their cluster-mates across reruns, how close they sit to their nearest neighbours, and whether
they form clusters of their own. See docs/process.md, "Fringe routes". Calls are unauthenticated.
"""

import json
import random
import re
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from check import BARE_ID, sections  # noqa: E402
from graph import parse, topic_dir  # noqa: E402
from net import get_json  # noqa: E402

API = "https://api.semanticscholar.org"
FIELDS = ("title,abstract,externalIds,publicationDate,year,citationCount,referenceCount,references.paperId,"
          "embedding.specter_v2")
CITED_SEEDS = 10  # the most-cited pool papers added to the frontier candidates as seeds for the `new` route


def call(url, body=None):
    # The unauthenticated endpoint shares one rate limit across all users and answers 429 freely; net retries.
    return get_json(url, body)


def fetch_s2(ids):
    out = {}
    for i in range(0, len(ids), 100):
        data = call(f"{API}/graph/v1/paper/batch?fields={FIELDS}", {"ids": ids[i:i + 100]})
        for rec in data:
            if not rec or not (rec.get("embedding") or {}).get("vector"):
                continue
            out[rec["paperId"]] = {
                "s2": rec["paperId"], "title": rec.get("title") or "", "abstract": rec.get("abstract") or "",
                "arxiv": (rec.get("externalIds") or {}).get("ArXiv"), "date": rec.get("publicationDate"),
                "corpus": f"CorpusId:{rec['externalIds']['CorpusId']}" if (rec.get("externalIds") or {}).get("CorpusId") else None,
                "year": rec.get("year"), "citations": rec.get("citationCount") or 0,
                "refs": sorted({x["paperId"] for x in rec.get("references") or [] if x.get("paperId")}),
                "embedding": [round(v, 5) for v in rec["embedding"]["vector"]],
            }
        time.sleep(1)
    return out


def age_years(rec, today):
    d = rec.get("date") or (f"{rec['year']}-07-01" if rec.get("year") else None)
    return (today - date.fromisoformat(d)).days / 365.25 if d else None


def rate(rec, today):
    a = age_years(rec, today)
    return rec["citations"] / max(a, 0.25) if a is not None else None


def frontier_candidates(topic):
    """The frontier candidates named in the latest pass's `Orientation` line, in order, without repeats."""
    from gates import log_entries
    log = sections((ROOT / "surveys" / f"{topic}.md").read_text()).get("Retrieval log", "")
    entries = log_entries(log)
    line = " ".join(entries[-1]["lines"].get("Orientation", [])) if entries else ""
    m = re.search(r"frontier candidates:\s*(.*)$", line)
    return list(dict.fromkeys(BARE_ID.findall(m.group(1)))) if m else []


def new_route_seeds(topic, pool):
    """The `new` route's seeds, as pool paper IDs: the frontier candidates, then the most-cited pool papers."""
    named = frontier_candidates(topic)
    frontier = [a for a in named if a in pool]
    missing = [a for a in named if a not in pool]
    by_s2 = {r["s2"]: a for a, r in pool.items()}
    indeg = {a: 0 for a in pool}
    for a, r in pool.items():
        for x in set(r["refs"]):
            if x in by_s2 and by_s2[x] != a:
                indeg[by_s2[x]] += 1
    cited = [a for a in sorted(pool, key=lambda a: (-indeg[a], a)) if a not in frontier and indeg[a] > 0][:CITED_SEEDS]
    return frontier, cited, missing, indeg


def collect(topic, per_route):
    d = topic_dir(topic)
    pool = json.loads((d / "pool.json").read_text())["papers"]
    in_pool = {r["s2"] for r in pool.values()}
    latest = max(date.fromisoformat(r["date"]) for r in pool.values() if r.get("date"))
    routes = {}

    # hidden: references the pool cites repeatedly, but the wider literature does not.
    counts = {}
    for r in pool.values():
        for x in r["refs"]:
            if x not in in_pool:
                counts[x] = counts.get(x, 0) + 1
    multi = [x for x, n in counts.items() if n >= 2]
    print(f"hidden: {len(multi)} out-of-pool references cited by >= 2 pool papers; fetching...")
    meta = fetch_s2(multi)
    old = [m for m in meta.values() if (age_years(m, latest) or 0) >= 1]
    old.sort(key=lambda m: (rate(m, latest), -counts[m["s2"]]))
    routes["hidden"] = [m["s2"] for m in old[:per_route]]

    # new: recommendations from one seed set, the frontier candidates and the most-cited pool papers (the endpoint
    # returns only very recent work).
    frontier, cited, missing, indeg = new_route_seeds(topic, pool)
    if missing:
        print(f"WARNING: frontier candidates without a record in pool.json, not used as seeds: {', '.join(missing)}; "
              f"run `python3 tools/pool.py {topic}` first")
    if not frontier:
        print("WARNING: the latest pass's `Orientation` line names no frontier candidate in the pool; the `new` route is "
              "seeded from the most-cited pool papers alone")
    print(f"new: seeded from {len(frontier)} frontier candidate(s) ({', '.join(frontier) or 'none'}) and the "
          f"{len(cited)} most-cited pool papers ({', '.join(f'{a} ({indeg[a]})' for a in cited)})")
    pos = [pool[a]["s2"] for a in frontier + cited]
    recs = call(f"{API}/recommendations/v1/papers?fields=paperId&limit={min(500, 2 * per_route)}",
                {"positivePaperIds": pos})
    new = [p["paperId"] for p in recs["recommendedPapers"] if p["paperId"] not in in_pool]
    routes["new"] = list(dict.fromkeys(new))[:per_route]
    seeds = {"frontier": frontier, "cited": cited, "frontier_missing": missing}

    wanted = sorted({x for ids in routes.values() for x in ids} - set(meta))
    meta.update(fetch_s2(wanted))
    cands = {}
    for route, ids in routes.items():
        for x in ids:
            if x in meta:
                m = cands.setdefault(x, dict(meta[x], routes=[]))
                m["routes"].append(route)
                if route == "hidden":
                    m["pool_citers"] = counts.get(x, 0)
    (d / "fringe.json").write_text(json.dumps({"collected": time.strftime("%Y-%m-%d"), "routes": routes,
                                                "new_seeds": seeds, "candidates": cands}, separators=(",", ":")))

    # Blind screening sheet: shuffled, no route, no citation counts. Judgements already on the sheet, from an earlier
    # collect, are carried over, so a rerun never erases screening work.
    earlier = {}
    if (d / "fringe-screen.md").exists():
        for line in (d / "fringe-screen.md").read_text().splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 6 and re.fullmatch(r"[0-9a-f]{40}", cells[0]) and cells[4]:
                earlier[cells[0]] = (cells[4], cells[5])
    order = sorted(cands)
    random.Random(0).shuffle(order)
    clean = lambda s: re.sub(r"\s+", " ", s).replace("|", "/").strip()
    rows = [f"| {x} | {clean(cands[x]['title'])} | {cands[x]['year'] or ''} | {clean(cands[x]['abstract'])[:700] or '(no abstract)'} | "
            f"{' | '.join(earlier.get(x, ('', '')))} |" for x in order]
    (d / "fringe-screen.md").write_text(
        "# Fringe screening sheet\n\n"
        f"Candidates for `{topic}`, in shuffled order. Mark `in scope` as `yes` or `no`, with a short reason.\n\n"
        "| s2 | title | year | abstract | in scope | reason |\n| -- | -- | -- | -- | -- | -- |\n" + "\n".join(rows) + "\n")
    for route, ids in routes.items():
        got = [cands[x] for x in ids if x in cands]
        print(f"{route:9} {len(got):3} candidates; median citations {sorted(m['citations'] for m in got)[len(got) // 2] if got else '-'}; "
              f"with arXiv id {sum(1 for m in got if m['arxiv'])}")
    print(f"wrote {(d / 'fringe.json').relative_to(ROOT)} and {(d / 'fringe-screen.md').relative_to(ROOT)} "
          f"({len(cands)} unique candidates; {sum(x in earlier for x in cands)} already judged, carried over)")


def main(argv):
    if len(argv) < 2 or argv[0] not in ("collect", "analyse"):
        sys.exit(__doc__)
    per_route = int(argv[argv.index("--per-route") + 1]) if "--per-route" in argv else 60
    if argv[0] == "collect":
        collect(argv[1], per_route)
    else:
        analyse(argv[1], int(argv[argv.index("--level") + 1]) if "--level" in argv else None)


def screened(d):
    """In-scope s2 ids from the screening sheet, and the count of rows still unscreened."""
    keep, blank = set(), 0
    for line in (d / "fringe-screen.md").read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6 or not re.fullmatch(r"[0-9a-f]{40}", cells[0]):
            continue
        v = cells[4].lower()
        if v.startswith("yes"):
            keep.add(cells[0])
        elif not v.startswith("no"):
            blank += 1
    return keep, blank


def analyse(topic, level):
    import numpy as np
    from scipy.stats import mannwhitneyu
    from sklearn.metrics import adjusted_rand_score as ari
    from cluster import combined_sim, knn_graph, leiden, refs_sim, text_sim, tune

    d = topic_dir(topic)
    pool = json.loads((d / "pool.json").read_text())["papers"]
    report = json.loads((d / "clusters.json").read_text())
    fr = json.loads((d / "fringe.json").read_text())
    keep, blank = screened(d)
    if blank:
        sys.exit(f"{blank} row(s) of fringe-screen.md are not yet screened")
    k, c = report["params"]["k"], report["params"]["c"]
    base_ids = report["ids"]
    recs = [pool[a] for a in base_ids] + [fr["candidates"][x] for x in sorted(keep)]
    cat = ["base"] * len(base_ids) + [fr["candidates"][x]["routes"][0] for x in sorted(keep)]
    cat = np.array(cat)
    n, nb = len(recs), len(base_ids)
    T, C = text_sim(recs), refs_sim(recs)
    S = combined_sim(T, C, recs, c) if report["measure"] == "combined" else (T if report["measure"] == "text" else C)
    today = max(date.fromisoformat(r["date"]) for r in recs if r.get("date"))
    cites = np.array([rate({"date": r.get("date"), "year": r.get("year"), "citations": r.get("citations") or 0}, today) or 0
                      for r in recs])
    off = ~np.eye(n, dtype=bool)
    nn_text = np.array([np.sort(T[i][off[i]])[-10:].mean() for i in range(n)])
    nn_refs = np.array([np.sort(C[i][off[i]])[-10:].mean() for i in range(n)])

    results = {}
    for target in sorted({level or report["level"], 12}):
        g = knn_graph(S, k)
        gamma, got = tune(g, target)
        full = leiden(g, gamma, 0)
        base_only = leiden(knn_graph(S[:nb, :nb], k), tune(knn_graph(S[:nb, :nb], k), target)[0], 0)
        rng = np.random.default_rng(0)
        cons, seen = np.zeros(n), np.zeros(n)
        for r in range(30):
            idx = np.sort(rng.choice(n, int(0.8 * n), replace=False))
            lab = leiden(knn_graph(S[np.ix_(idx, idx)], k), gamma, r)
            f = full[idx]
            for a, i in enumerate(idx):
                A = set(np.flatnonzero(f == f[a])) - {a}
                B = set(np.flatnonzero(lab == lab[a])) - {a}
                cons[i] += len(A & B) / len(A | B) if A | B else 1.0
                seen[i] += 1
        cons = cons / np.maximum(seen, 1)
        comp = []
        for cl in np.unique(full):
            m = full == cl
            comp.append({"size": int(m.sum()), "fringe_share": float((cat[m] != "base").mean()),
                         "routes": {r: int((cat[m] == r).sum()) for r in ("base", "hidden", "followers", "new")}})
        fringe_major = {int(cl) for cl, x in zip(np.unique(full), comp) if x["fringe_share"] > 0.5}
        rows = {}
        for route in ("base", "hidden", "new", "followers"):
            m = cat == route
            if not m.any():
                continue
            row = {"n": int(m.sum()), "consistency": float(np.median(cons[m])), "unstable_share": float((cons[m] < 0.5).mean()),
                   "nn_text": float(np.median(nn_text[m])), "nn_refs": float(np.median(nn_refs[m])),
                   "in_fringe_clusters": float(np.mean([full[i] in fringe_major for i in np.flatnonzero(m)])),
                   "citations_per_year": float(np.median(cites[m]))}
            if route != "base":
                for key, arr in (("consistency", cons), ("nn_text", nn_text), ("nn_refs", nn_refs)):
                    row[f"p_{key}"] = float(mannwhitneyu(arr[m], arr[cat == "base"]).pvalue)
            rows[route] = row
        ids_all = base_ids + sorted(keep)
        titles = {a: v["title"] for a, v in parse(topic)[4].items()}
        papers = [{"id": ids_all[i], "route": str(cat[i]), "title": recs[i].get("title") or titles.get(ids_all[i], ""),
                   "year": recs[i].get("year"),
                   "cluster": int(full[i]), "consistency": round(float(cons[i]), 3), "nn_text": round(float(nn_text[i]), 3),
                   "nn_refs": round(float(nn_refs[i]), 3), "citations_per_year": round(float(cites[i]), 1)} for i in range(n)]
        results[str(got)] = {"clusters": got, "routes": rows, "composition": comp, "papers": papers,
                             "base_ari_with_vs_without_fringe": float(ari(base_only, full[:nb]))}
        print(f"\n{got} clusters (base-paper ARI with vs without fringe: {results[str(got)]['base_ari_with_vs_without_fringe']:.2f})")
        print(f"  {'route':9} {'n':>4} {'consist':>8} {'<0.5':>6} {'nn text':>8} {'nn refs':>8} {'in fringe cl':>12} {'cites/yr':>9}  p(consist, text, refs)")
        for route, r in rows.items():
            ps = "" if route == "base" else f"  {r['p_consistency']:.3f} {r['p_nn_text']:.3f} {r['p_nn_refs']:.3f}"
            print(f"  {route:9} {r['n']:>4} {r['consistency']:>8.2f} {r['unstable_share']:>6.2f} {r['nn_text']:>8.3f} {r['nn_refs']:>8.3f} "
                  f"{r['in_fringe_clusters']:>12.2f} {r['citations_per_year']:>9.1f}{ps}")
        print("  clusters with a fringe majority: " + (", ".join(f"{x['size']} papers {x['routes']}" for x in comp if x["fringe_share"] > 0.5) or "none"))
    (d / "fringe-analysis.json").write_text(json.dumps({"in_scope": len(keep), "results": results}, indent=1))
    print(f"\nwrote {(d / 'fringe-analysis.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
