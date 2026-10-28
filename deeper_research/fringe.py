"""Collect fringe candidates for a topic, and test how they behave under the clustering method.

Usage:
  uv run python -m deeper_research.fringe collect <topic> [--per-route 60]
  uv run python -m deeper_research.fringe judge <topic> < lines
      (one `<s2><TAB>yes|no|maybe<TAB><reason>` per line)
  uv run python -m deeper_research.fringe analyse <topic> [--level 6]

`collect` gathers candidates outside the pool by the two routes of docs/process.md, "Fringe routes", by script and at
no model cost. It needs the pool sidecar (deeper_research/pool.py) and the survey's retrieval log, not a clustering. A
paper already recorded as out of scope in graphs/<topic>/rejected.md is not collected again, nor one whose title matches
a pool paper's, which is most likely a second record of it.

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
sheet, graphs/<topic>/fringe-screen.md: titles and abstracts in shuffled order, without the route and without the
year, which would give the route away (`new` finds only recent work), for agents to mark in or out of scope. Its rows
are numbered, so that they can be handed to screening agents as ranges. A rerun keeps the judgements already on the
sheet. Each candidate records its arXiv ID or, failing that, its CorpusId;
deeper_research/assign.py add-fringe then adds the in-scope ones to the pool.

`judge` writes screening verdicts into the sheet's `in scope` and `reason` cells, from stdin, so that an agent need not
edit the rows by hand. It is the shared judge of deeper_research/screen.py, which says what it refuses. A `maybe` is a
reminder to come back: until it is resolved to yes or no, the row counts as unjudged, for deeper_research/assign.py
add-fringe and for the G1 gate alike.

`analyse` adds the in-scope candidates to the pool and reclusters with the chosen measure. Per route, it reports how
consistently papers keep their cluster-mates across reruns, how close they sit to their nearest neighbours, and whether
they form clusters of their own. See docs/process.md, "Fringe routes". Calls are unauthenticated.
"""

import json
import random
import sys
import time
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from deeper_research.assign import rejected
from deeper_research.check import sections
from deeper_research.expand import orientation_parts
from deeper_research.gates import log_entries
from deeper_research.graph import parse, topic_dir
from deeper_research.net import get_json
from deeper_research.screen import clean, judge, pool_titles, title_key, verdicts

if TYPE_CHECKING:
    from numpy.typing import NDArray

ROOT = Path(__file__).resolve().parent.parent

API = "https://api.semanticscholar.org"
FIELDS = (
    "title,abstract,externalIds,publicationDate,year,citationCount,referenceCount,references.paperId,"
    "embedding.specter_v2"
)
CITED_SEEDS = 10  # the most-cited pool papers added to the frontier candidates as seeds for the `new` route


def need(path: Path, then: str) -> None:
    """Exit with what to run first, if `path` is missing."""
    if not path.exists():
        sys.exit(f"no {path.relative_to(ROOT)}; run {then} first")


# Any: the parsed JSON answer, an object or a list as the endpoint gives it
def call(url: str, body: dict[str, Any] | None = None) -> Any:  # noqa: ANN401
    """The parsed JSON answer of a Semantic Scholar endpoint: a GET of `url`, or a POST of `body` to it."""
    # The unauthenticated endpoint shares one rate limit across all users and answers 429 freely; net retries.
    return get_json(url, body)


def fetch_s2(ids: list[str]) -> dict[str, dict[str, Any]]:
    """{s2 ID: record} for the Semantic Scholar IDs `ids`, fetched in batches; those without an embedding left out."""
    out: dict[str, dict[str, Any]] = {}
    for i in range(0, len(ids), 100):
        data = call(f"{API}/graph/v1/paper/batch?fields={FIELDS}", {"ids": ids[i : i + 100]})
        for rec in data:
            if not rec or not (rec.get("embedding") or {}).get("vector"):
                continue
            out[rec["paperId"]] = {
                "s2": rec["paperId"],
                "title": rec.get("title") or "",
                "abstract": rec.get("abstract") or "",
                "arxiv": (rec.get("externalIds") or {}).get("ArXiv"),
                "date": rec.get("publicationDate"),
                "corpus": f"CorpusId:{rec['externalIds']['CorpusId']}"
                if (rec.get("externalIds") or {}).get("CorpusId")
                else None,
                "year": rec.get("year"),
                "citations": rec.get("citationCount") or 0,
                "refs": sorted({x["paperId"] for x in rec.get("references") or [] if x.get("paperId")}),
                "embedding": [round(v, 5) for v in rec["embedding"]["vector"]],
            }
        time.sleep(1)
    return out


def age_years(rec: dict[str, Any], today: date) -> float | None:
    """The record's age in years at `today`, from its date or else the middle of its year; None with neither."""
    d = rec.get("date") or (f"{rec['year']}-07-01" if rec.get("year") else None)
    return (today - date.fromisoformat(d)).days / 365.25 if d else None


def rate(rec: dict[str, Any], today: date) -> float | None:
    """The record's citations per year of age, the age taken as at least a quarter year; None without an age."""
    a = age_years(rec, today)
    return rec["citations"] / max(a, 0.25) if a is not None else None


def frontier_candidates(topic: str) -> list[str]:
    """The frontier candidates named in the latest pass's `Orientation` line, in order, without repeats."""
    log = sections((ROOT / "surveys" / f"{topic}.md").read_text()).get("Retrieval log", "")
    entries = log_entries(log)
    return orientation_parts(" ".join(entries[-1]["lines"].get("Orientation", [])) if entries else "")[1]


def new_route_seeds(
    topic: str, pool: dict[str, dict[str, Any]]
) -> tuple[list[str], list[str], list[str], dict[str, int]]:
    """The `new` route's seeds, as pool paper IDs: the frontier candidates, then the most-cited pool papers."""
    named = frontier_candidates(topic)
    frontier = [a for a in named if a in pool]
    missing = [a for a in named if a not in pool]
    by_s2 = {r["s2"]: a for a, r in pool.items()}
    indeg = dict.fromkeys(pool, 0)
    for a, r in pool.items():
        for x in set(r["refs"]):
            if x in by_s2 and by_s2[x] != a:
                indeg[by_s2[x]] += 1
    cited = [a for a in sorted(pool, key=lambda a: (-indeg[a], a)) if a not in frontier and indeg[a] > 0][:CITED_SEEDS]
    return frontier, cited, missing, indeg


def collect(topic: str, per_route: int) -> None:  # noqa: C901
    """Collect the fringe candidates of both routes into fringe.json, and write the blind sheet fringe-screen.md."""
    d = topic_dir(topic)
    need(ROOT / "surveys" / f"{topic}.md", "steps 0 and 1 of docs/process.md")
    need(d / "pool.json", f"`uv run python -m deeper_research.pool {topic}`")
    pool = json.loads((d / "pool.json").read_text())["papers"]
    in_pool = {r["s2"] for r in pool.values()}
    dated = [date.fromisoformat(r["date"]) for r in pool.values() if r.get("date")]
    if not dated:
        sys.exit(
            f"no pool paper in pool.json has a publication date; run `uv run python -m deeper_research.pool {topic}` "
            f"first"
        )
    latest = max(dated)
    routes: dict[str, list[str]] = {}
    # A paper screened out earlier is not collected again, so that it cannot get a second, opposite verdict.
    rej = set(rejected(topic))

    def is_rejected(m: dict[str, Any]) -> bool:
        return bool({m.get("arxiv"), m.get("corpus")} & rej)

    excluded: dict[str, int]
    same_title: dict[str, int]
    excluded, same_title = {}, {}

    # hidden: references the pool cites repeatedly, but the wider literature does not.
    counts: dict[str, int] = {}
    for r in pool.values():
        for x in r["refs"]:
            if x not in in_pool:
                counts[x] = counts.get(x, 0) + 1
    multi = [x for x, n in counts.items() if n >= 2]
    print(f"hidden: {len(multi)} out-of-pool references cited by >= 2 pool papers; fetching...")
    meta = fetch_s2(multi)
    old = [m for m in meta.values() if (age_years(m, latest) or 0) >= 1]
    excluded["hidden"] = sum(1 for m in old if is_rejected(m))
    old = [m for m in old if not is_rejected(m)]
    old.sort(key=lambda m: (rate(m, latest), -counts[m["s2"]]))
    routes["hidden"] = [m["s2"] for m in old[:per_route]]

    # new: recommendations from one seed set, the frontier candidates and the most-cited pool papers (the endpoint
    # returns only very recent work).
    frontier, cited, missing, indeg = new_route_seeds(topic, pool)
    if missing:
        print(
            f"WARNING: frontier candidates without a record in pool.json, not used as seeds: {', '.join(missing)}; "
            f"run `uv run python -m deeper_research.pool {topic}` first"
        )
    if not frontier:
        print(
            "WARNING: the latest pass's `Orientation` line names no frontier candidate in the pool; the `new` route is "
            "seeded from the most-cited pool papers alone"
        )
    print(
        f"new: seeded from {len(frontier)} frontier candidate(s) ({', '.join(frontier) or 'none'}) and the "
        f"{len(cited)} most-cited pool papers ({', '.join(f'{a} ({indeg[a]})' for a in cited)})"
    )
    pos = [pool[a]["s2"] for a in frontier + cited]
    recs = call(
        f"{API}/recommendations/v1/papers?fields=paperId,externalIds&limit={min(500, 2 * per_route)}",
        {"positivePaperIds": pos},
    )
    new = []
    for p in recs["recommendedPapers"]:
        ext = p.get("externalIds") or {}
        if p["paperId"] in in_pool:
            continue
        if is_rejected(
            {"arxiv": ext.get("ArXiv"), "corpus": f"CorpusId:{ext['CorpusId']}" if ext.get("CorpusId") else None}
        ):
            excluded["new"] = excluded.get("new", 0) + 1
            continue
        new.append(p["paperId"])
    routes["new"] = list(dict.fromkeys(new))[:per_route]
    seeds = {"frontier": frontier, "cited": cited, "frontier_missing": missing}

    wanted = sorted({x for ids in routes.values() for x in ids} - set(meta))
    meta.update(fetch_s2(wanted))
    cands: dict[str, dict[str, Any]] = {}
    titles = pool_titles(topic)
    for route, ids in routes.items():
        for x in ids:
            # Again on the fetched record, in case a recommendation came back without its external IDs.
            if x in meta and is_rejected(meta[x]):
                excluded[route] = excluded.get(route, 0) + 1
            elif x in meta and title_key(meta[x]["title"]) in titles:
                same_title[route] = same_title.get(route, 0) + 1
            elif x in meta:
                m = cands.setdefault(x, dict(meta[x], routes=[]))
                m["routes"].append(route)
                if route == "hidden":
                    m["pool_citers"] = counts.get(x, 0)
    (d / "fringe.json").write_text(
        json.dumps(
            {"collected": time.strftime("%Y-%m-%d"), "routes": routes, "new_seeds": seeds, "candidates": cands},
            separators=(",", ":"),
        )
    )

    # Blind screening sheet: shuffled, no route, no year (the `new` route finds only recent work), no citation counts.
    # Judgements already on the sheet, from an earlier collect, are carried over, so a rerun never erases screening
    # work.
    earlier: dict[str, tuple[str, ...]] = {}
    if (d / "fringe-screen.md").exists():
        earlier = {
            x: tuple(c.replace("\0", "/") for c in v)
            for x, v in verdicts((d / "fringe-screen.md").read_text()).items()
            if v[0]
        }
    order = sorted(cands)
    # seeded shuffle, so that the sheet's order is reproducible; not a security use
    random.Random(0).shuffle(order)  # noqa: S311
    # Numbered, so that the main session can hand the rows to screening agents as ranges.
    rows = [
        f"| {n} | {x} | {clean(cands[x]['title'])} | {clean(cands[x]['abstract']) or '(no abstract)'} | "
        f"{' | '.join(earlier.get(x, ('', '')))} |"
        for n, x in enumerate(order, 1)
    ]
    (d / "fringe-screen.md").write_text(
        "# Fringe screening sheet\n\n"
        f"Candidates for `{topic}`, in shuffled order. Mark `in scope` as `yes` or `no`, with a reason "
        f"of at least two words (`uv run python -m deeper_research.fringe judge {topic}`).\n\n"
        "| # | s2 | title | abstract | in scope | reason |\n| -- | -- | -- | -- | -- | -- |\n" + "\n".join(rows) + "\n"
    )
    if any(excluded.values()):
        print(
            f"left out as already rejected (graphs/{topic}/rejected.md): "
            + ", ".join(f"{r} {excluded.get(r, 0)}" for r in routes)
        )
    if any(same_title.values()):
        print(
            "left out as another record of a pool paper, by title: "
            + ", ".join(f"{r} {same_title.get(r, 0)}" for r in routes)
        )
    for route, ids in routes.items():
        got = [cands[x] for x in ids if x in cands]
        print(
            f"{route:9} {len(got):3} candidates; median citations "
            f"{sorted(m['citations'] for m in got)[len(got) // 2] if got else '-'}; "
            f"with arXiv id {sum(1 for m in got if m['arxiv'])}"
        )
    print(
        f"wrote {(d / 'fringe.json').relative_to(ROOT)} and {(d / 'fringe-screen.md').relative_to(ROOT)} "
        f"({len(cands)} unique candidates; {sum(x in earlier for x in cands)} already judged, carried over)"
    )


def main(argv: list[str]) -> int:
    """Run the command `argv` names; print the usage and return 2 on a malformed command line."""
    flags = {"--per-route": int, "--level": int}
    opts: dict[str, int] | None
    try:
        opts = {argv[i]: flags[argv[i]](argv[i + 1]) for i in range(2, len(argv), 2)}
    except (KeyError, IndexError, ValueError):
        opts = None
    if (
        len(argv) < 2
        or argv[0] not in ("collect", "judge", "analyse")
        or opts is None
        or (argv[0] == "judge" and (opts or sys.stdin.isatty()))
    ):
        print(__doc__.strip())
        return 2
    if argv[0] == "collect":
        collect(argv[1], opts.get("--per-route", 60))
    elif argv[0] == "judge":
        return judge(
            topic_dir(argv[1]) / "fringe-screen.md", f"`uv run python -m deeper_research.fringe collect {argv[1]}`"
        )
    else:
        analyse(argv[1], opts.get("--level"))
    return 0


def screened(d: Path) -> tuple[set[str], int]:
    """In-scope s2 ids from the screening sheet, and the count of rows still unscreened."""
    keep: set[str]
    keep, blank = set(), 0
    for x, (v, _) in verdicts((d / "fringe-screen.md").read_text()).items():
        if v.startswith("yes"):
            keep.add(x)
        elif not v.startswith("no"):
            blank += 1
    return keep, blank


def analyse(topic: str, level: int | None) -> None:  # noqa: C901
    """Add the in-scope candidates to the pool, recluster, and report per route how the candidates behave."""
    d = topic_dir(topic)
    need(d / "pool.json", f"`uv run python -m deeper_research.pool {topic}`")
    need(d / "clusters.json", f"`uv run python -m deeper_research.cluster {topic}`")
    need(d / "fringe.json", f"`uv run python -m deeper_research.fringe collect {topic}`")
    need(d / "fringe-screen.md", f"`uv run python -m deeper_research.fringe collect {topic}`")

    # local: keeps numpy, scipy, scikit-learn and the clustering's packages out of collect and judge
    import numpy as np  # noqa: PLC0415
    from scipy.stats import mannwhitneyu  # noqa: PLC0415
    from sklearn.metrics import adjusted_rand_score as ari  # noqa: PLC0415

    from deeper_research.cluster import combined_sim, knn_graph, leiden, refs_sim, text_sim, tune  # noqa: PLC0415

    pool = json.loads((d / "pool.json").read_text())["papers"]
    report = json.loads((d / "clusters.json").read_text())
    fr = json.loads((d / "fringe.json").read_text())
    keep, blank = screened(d)
    if blank:
        sys.exit(f"{blank} row(s) of fringe-screen.md are not yet screened")
    k, c = report["params"]["k"], report["params"]["c"]
    base_ids = report["ids"]
    recs = [pool[a] for a in base_ids] + [fr["candidates"][x] for x in sorted(keep)]
    cat: list[str] | NDArray[np.str_] = ["base"] * len(base_ids) + [
        fr["candidates"][x]["routes"][0] for x in sorted(keep)
    ]
    cat = np.array(cat)
    n, nb = len(recs), len(base_ids)
    T, C = text_sim(recs), refs_sim(recs)
    S = combined_sim(T, C, recs, c) if report["measure"] == "combined" else (T if report["measure"] == "text" else C)
    today = max(date.fromisoformat(r["date"]) for r in recs if r.get("date"))
    cites = np.array(
        [
            rate({"date": r.get("date"), "year": r.get("year"), "citations": r.get("citations") or 0}, today) or 0
            for r in recs
        ]
    )
    off = ~np.eye(n, dtype=bool)
    nn_text = np.array([np.sort(T[i][off[i]])[-10:].mean() for i in range(n)])
    nn_refs = np.array([np.sort(C[i][off[i]])[-10:].mean() for i in range(n)])

    results: dict[str, dict[str, Any]] = {}
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
                A = cast("set[int]", set(np.flatnonzero(f == f[a]))) - {a}
                B = cast("set[int]", set(np.flatnonzero(lab == lab[a]))) - {a}
                cons[i] += len(A & B) / len(A | B) if A | B else 1.0
                seen[i] += 1
        cons = cons / np.maximum(seen, 1)
        comp: list[dict[str, Any]] = []
        for cl in np.unique(full):
            m = full == cl
            comp.append(
                {
                    "size": int(m.sum()),
                    "fringe_share": float((cat[m] != "base").mean()),
                    "routes": {r: int((cat[m] == r).sum()) for r in ("base", "hidden", "followers", "new")},
                }
            )
        fringe_major = {int(cl) for cl, x in zip(np.unique(full), comp, strict=False) if x["fringe_share"] > 0.5}
        rows: dict[str, dict[str, float]] = {}
        for route in ("base", "hidden", "new", "followers"):
            m = cat == route
            if not m.any():
                continue
            row = {
                "n": int(m.sum()),
                "consistency": float(np.median(cons[m])),
                "unstable_share": float((cons[m] < 0.5).mean()),
                "nn_text": float(np.median(nn_text[m])),
                "nn_refs": float(np.median(nn_refs[m])),
                "in_fringe_clusters": float(np.mean([full[i] in fringe_major for i in np.flatnonzero(m)])),
                "citations_per_year": float(np.median(cites[m])),
            }
            if route != "base":
                for key, arr in (("consistency", cons), ("nn_text", nn_text), ("nn_refs", nn_refs)):
                    row[f"p_{key}"] = float(mannwhitneyu(arr[m], arr[cat == "base"]).pvalue)
            rows[route] = row
        ids_all = base_ids + sorted(keep)
        titles = {a: v["title"] for a, v in parse(topic)[4].items()}
        papers = [
            {
                "id": ids_all[i],
                "route": str(cat[i]),
                "title": recs[i].get("title") or titles.get(ids_all[i], ""),
                "year": recs[i].get("year"),
                "cluster": int(full[i]),
                "consistency": round(float(cons[i]), 3),
                "nn_text": round(float(nn_text[i]), 3),
                "nn_refs": round(float(nn_refs[i]), 3),
                "citations_per_year": round(float(cites[i]), 1),
            }
            for i in range(n)
        ]
        results[str(got)] = {
            "clusters": got,
            "routes": rows,
            "composition": comp,
            "papers": papers,
            "base_ari_with_vs_without_fringe": float(ari(base_only, full[:nb])),
        }
        print(
            f"\n{got} clusters (base-paper ARI with vs without fringe: "
            f"{results[str(got)]['base_ari_with_vs_without_fringe']:.2f})"
        )
        print(
            f"  {'route':9} {'n':>4} {'consist':>8} {'<0.5':>6} {'nn text':>8} {'nn refs':>8} {'in fringe cl':>12} "
            f"{'cites/yr':>9}  p(consist, text, refs)"
        )
        for route, st in rows.items():
            ps = "" if route == "base" else f"  {st['p_consistency']:.3f} {st['p_nn_text']:.3f} {st['p_nn_refs']:.3f}"
            print(
                f"  {route:9} {st['n']:>4} {st['consistency']:>8.2f} {st['unstable_share']:>6.2f} "
                f"{st['nn_text']:>8.3f} {st['nn_refs']:>8.3f} "
                f"{st['in_fringe_clusters']:>12.2f} {st['citations_per_year']:>9.1f}{ps}"
            )
        print(
            "  clusters with a fringe majority: "
            + (", ".join(f"{x['size']} papers {x['routes']}" for x in comp if x["fringe_share"] > 0.5) or "none")
        )
    (d / "fringe-analysis.json").write_text(json.dumps({"in_scope": len(keep), "results": results}, indent=1))
    print(f"\nwrote {(d / 'fringe-analysis.json').relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
