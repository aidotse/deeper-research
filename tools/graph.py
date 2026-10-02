#!/usr/bin/env python3
"""Build an interactive citation-graph viewer for one topic's survey.

Usage: python3 tools/graph.py <topic> [--refresh]

Reads surveys/<topic>.md and writes graphs/<topic>/graph.html: a single
self-contained page (data, libraries and code inlined) that opens straight from
the file system, with no server and no network.

Nodes are papers, coloured by cluster, sized by how often the other papers in
the set cite them. Edges are citations within the set.

Where the citation edges come from depends on the survey:

  - A coreset survey (with `## Clusters` and `## Pool` sections) carries its own
    graph: the pool's `cites` column. Nothing is fetched.
  - A legacy survey (Coreset section only) has no citation data, so the
    references of every paper are fetched from the Semantic Scholar API and
    cached in graphs/<topic>/references.json. Later runs use the cache; pass
    --refresh to refetch. The cache records its fetch date, and so does the page.

Alongside the survey's own clusters, the script computes citation communities
(Louvain modularity maximisation over the undirected citation graph), so that
the survey's hand-drawn clusters can be compared against the structure the
citations themselves suggest.

If tools/cluster.py has written graphs/<topic>/clusters.json, the page
also shows how the clusters were computed: the measure and level chosen, the
parameters, the stability curves, and each computed cluster and sub-cluster.

Vendored libraries, in tools/vendor/, all MIT-licensed: cytoscape 3.30.2,
layout-base 2.0.1, cose-base 2.2.0, cytoscape-fcose 2.2.0.
"""

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import ARXIV, BARE_ARXIV, ROOT, cells_of, sections, table_rows  # noqa: E402

TOOLS = Path(__file__).resolve().parent
S2_BATCH = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,year,citationCount,references.externalIds"
VENDOR = ["cytoscape.min.js", "layout-base.js", "cose-base.js", "cytoscape-fcose.js"]
DIMENSIONS = ["evidence", "measures", "elicitation", "pressure"]


def topic_dir(topic):
    """Everything derived from a topic's survey: the viewer page and the data behind it."""
    return ROOT / "graphs" / topic


# --- survey parsing -------------------------------------------------------------------------------


def plain(text):
    """Strip the markdown a table cell may carry, for display as plain text."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("**", "").replace("`", "").replace("\\|", "|").replace("\\*", "*")
    return text.replace("\0", "|").strip()


def arxiv_month(aid):
    """An arXiv ID encodes its submission month: 2504.13837 is April 2025."""
    return 2000 + int(aid[:2]) + (int(aid[2:4]) - 1) / 12


def parse(topic):
    text = (ROOT / "surveys" / f"{topic}.md").read_text()
    secs = sections(text)
    title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), topic)
    coreset_layout = "Clusters" in secs and "Pool" in secs

    clusters, order = {}, []
    if coreset_layout:
        for h, c, _, _ in table_rows(secs["Clusters"]):
            if h and h[0] == "id":
                row = dict(zip(h, c))
                clusters[row["id"]] = {
                    "id": row["id"],
                    "name": plain(row.get("name", row["id"])),
                    "definition": plain(row.get("definition", "")),
                    "alignment": row.get("alignment", ""),
                    "reason": plain(row.get("alignment reason", "")),
                }
                order.append(row["id"])

    papers = {}
    for h, c, block, line in table_rows(secs["Coreset"]):
        if not h or h[0] != "paper":
            continue
        m = ARXIV.search(line)
        if not m:
            continue
        aid = m.group(1)
        block = block or "(no block)"
        if coreset_layout:
            cid = block.split(" — ")[0].strip()
        else:
            # Legacy blocks are headed "A. Name"; the letter is the id.
            cid, _, name = block.partition(". ")
            if cid not in clusters:
                clusters[cid] = {"id": cid, "name": name.strip() or cid, "definition": "", "alignment": ""}
                order.append(cid)
        row = dict(zip(h, c))
        papers[aid] = {
            "id": aid,
            "title": plain(row["paper"]),
            "cluster": cid,
            "coreset": True,
            "role": row.get("role", "").split(":")[0] or None,
            "bridge": row.get("role", "").partition(":")[2] or None,
            "fields": [[k, plain(v)] for k, v in row.items() if k != "paper"],
            "dims": {d: row[d] for d in DIMENSIONS if d in row},
            "source": c[-1],
        }

    cites = {}
    if coreset_layout:
        for h, c, _, line in table_rows(secs["Pool"]):
            if not h or h[0] != "paper":
                continue
            m = ARXIV.search(line)
            if not m:
                continue
            aid, row = m.group(1), dict(zip(h, c))
            p = papers.setdefault(
                aid,
                {"id": aid, "title": plain(row["paper"]), "coreset": False, "role": None, "bridge": None,
                 "fields": [], "dims": {}, "source": None},
            )
            p["cluster"] = row.get("cluster", p.get("cluster"))
            p["citations"] = int(row["citations"]) if row.get("citations", "").isdigit() else None
            p["year"] = int(row["year"]) if row.get("year", "").isdigit() else None
            cites[aid] = set(BARE_ARXIV.findall(row.get("cites", "")))
    return title, coreset_layout, clusters, order, papers, cites


# --- citation data for legacy surveys -------------------------------------------------------------


def fetch_s2(ids):
    """Fetch title, year, citation count and references for arXiv IDs, in batches of 500."""
    out = {}
    for i in range(0, len(ids), 500):
        batch = ids[i : i + 500]
        body = json.dumps({"ids": [f"ARXIV:{a}" for a in batch]}).encode()
        req = urllib.request.Request(S2_BATCH, data=body, headers={"Content-Type": "application/json"})
        # The unauthenticated endpoint shares one rate limit across all users
        # and answers 429 freely; back off and retry rather than failing.
        for attempt in range(8):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or attempt == 7:
                    raise
                time.sleep(5 * (attempt + 1))
        for aid, rec in zip(batch, data):
            if rec is None:
                continue
            refs = [
                (x.get("externalIds") or {}).get("ArXiv")
                for x in rec.get("references") or []
            ]
            out[aid] = {
                "year": rec.get("year"),
                "citations": rec.get("citationCount"),
                "refs": sorted({r for r in refs if r}),
            }
    return out


def legacy_cites(topic, papers, refresh):
    cache_path = topic_dir(topic) / "references.json"
    cache = {} if refresh or not cache_path.exists() else json.loads(cache_path.read_text())
    records = cache.get("papers", {})
    missing = [a for a in papers if a not in records]
    if missing:
        print(f"fetching {len(missing)} paper(s) from Semantic Scholar...")
        records.update(fetch_s2(missing))
        cache = {"fetched": time.strftime("%Y-%m-%d"), "papers": records}
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, indent=1, sort_keys=True))
    for aid, p in papers.items():
        rec = records.get(aid, {})
        p["citations"] = rec.get("citations")
        p["year"] = rec.get("year")
    unresolved = sorted(a for a in papers if a not in records)
    return {a: set(records[a]["refs"]) for a in papers if a in records}, cache.get("fetched"), unresolved


# --- graph metrics --------------------------------------------------------------------------------


def undirected(nodes, edges):
    adj = {n: {} for n in nodes}
    for a, b in edges:
        if a != b:
            adj[a][b] = adj[a].get(b, 0) + 1
            adj[b][a] = adj[b].get(a, 0) + 1
    return adj


def modularity(adj, part):
    m2 = sum(sum(nb.values()) for nb in adj.values())
    if not m2:
        return 0.0
    inner, tot = {}, {}
    for n, nb in adj.items():
        c = part[n]
        tot[c] = tot.get(c, 0) + sum(nb.values())
        inner[c] = inner.get(c, 0) + sum(w for x, w in nb.items() if part[x] == c)
    return sum(inner[c] / m2 - (tot[c] / m2) ** 2 for c in tot)


def louvain(adj):
    """Louvain community detection, deterministic (nodes visited in sorted order).

    Returns a map from node to community index, with communities numbered by
    size, largest first, so that colour assignment is stable across runs.
    """
    membership = {n: n for n in adj}  # original node -> current super-node
    graph = {n: dict(nb) for n, nb in adj.items()}
    while True:
        m2 = sum(sum(nb.values()) for nb in graph.values())
        if not m2:
            break
        # A super-node's self-loop already holds both directions of its internal
        # edges, so its degree is simply its row sum.
        deg = {n: sum(nb.values()) for n, nb in graph.items()}
        comm = {n: n for n in graph}
        tot = dict(deg)
        moved = True
        improved = False
        while moved:
            moved = False
            for n in sorted(graph):
                c_old = comm[n]
                tot[c_old] -= deg[n]
                links = {}
                for x, w in graph[n].items():
                    if x != n:
                        links[comm[x]] = links.get(comm[x], 0) + w
                best, gain = c_old, links.get(c_old, 0) - tot[c_old] * deg[n] / m2
                for c, k in sorted(links.items()):
                    g = k - tot[c] * deg[n] / m2
                    if g > gain + 1e-12:
                        best, gain = c, g
                comm[n] = best
                tot[best] += deg[n]
                if best != c_old:
                    moved = improved = True
        if not improved:
            break
        membership = {o: comm[s] for o, s in membership.items()}
        agg = {}
        for n, nb in graph.items():
            cn = comm[n]
            row = agg.setdefault(cn, {})
            for x, w in nb.items():
                row[comm[x]] = row.get(comm[x], 0) + w
        graph = agg
    groups = {}
    for n, c in membership.items():
        groups.setdefault(c, []).append(n)
    ranked = sorted(groups.values(), key=lambda g: (-len(g), min(g)))
    return {n: i for i, g in enumerate(ranked) for n in g}


# --- output ---------------------------------------------------------------------------------------


def load_clustering(topic, nodes):
    """The report from tools/cluster.py, if one exists: how the clusters were computed, and each paper's assignment."""
    path = topic_dir(topic) / "clusters.json"
    if not path.exists():
        return None
    r = json.loads(path.read_text())
    sub_of = {}
    for c in r["clusters"]:
        for i, s in enumerate(c["subclusters"]):
            for a in s["members"]:
                sub_of[a] = f"{c['id']}.{i + 1}"
    pos = {a: i for i, a in enumerate(r.get("ids", []))}
    for n in nodes:
        n["computed"] = r["assignment"].get(n["id"])
        n["sub"] = sub_of.get(n["id"])
        if n["id"] in pos and "slider" in r:
            n["levels"] = [lv["labels"][pos[n["id"]]] for lv in r["slider"]]
    keep = ["generated", "measure", "measure_reason", "grid_mean", "level", "level_reason", "tau_sensitivity", "params",
            "cohesion", "ami_vs_survey_clusters", "rule", "level_tau", "level_tau_reason", "level_null",
            "level_null_reason", "knn", "diagnostics", "health"]
    out = {k: r.get(k) for k in keep}
    out["null_curves"] = {m: [{"clusters": l["clusters"], "stability": l["stability"]} for l in ls]
                          for m, ls in r.get("null_curves", {}).items()}
    out["slider"] = [{"clusters": lv["clusters"], "stability": lv["stability"], "null_stability": lv["null_stability"]}
                     for lv in r.get("slider", [])]
    out["curves"] = {m: [{k: l[k] for k in ("clusters", "stability", "stability_se", "holdout_ari", "resample_ari",
                                            "median_clusterwise")} for l in ls] for m, ls in r["curves"].items()}
    out["clusters"] = [{
        "id": c["id"], "size": c["size"], "stability": c["stability"], "divided": c["divided"],
        "subclusters": [{"id": f"{c['id']}.{i + 1}", "size": s["size"], "stability": s["stability"]}
                        for i, s in enumerate(c["subclusters"])],
    } for c in r["clusters"]]
    return out


def build(topic, refresh=False):
    title, coreset_layout, clusters, order, papers, cites = parse(topic)
    fetched, unresolved = None, []
    if not coreset_layout:
        cites, fetched, unresolved = legacy_cites(topic, papers, refresh)

    ids = set(papers)
    edges = sorted({(a, b) for a, cs in cites.items() for b in cs & ids if a != b and a in ids})
    indeg = {a: 0 for a in ids}
    for _, b in edges:
        indeg[b] += 1

    adj = undirected(ids, edges)
    connected = {n for n, nb in adj.items() if nb}
    communities = louvain({n: nb for n, nb in adj.items() if n in connected})
    declared = {n: papers[n]["cluster"] for n in connected}

    # Cohesion: of the citation links touching a cluster, the share that stay
    # inside it. A cluster whose papers mostly cite other clusters is a label,
    # not a neighbourhood.
    cohesion = {}
    for cid in order:
        inner = sum(1 for a, b in edges if papers[a]["cluster"] == cid and papers[b]["cluster"] == cid)
        touching = sum(1 for a, b in edges if cid in (papers[a]["cluster"], papers[b]["cluster"]))
        cohesion[cid] = round(inner / touching, 3) if touching else None

    comm_list = []
    for i in sorted(set(communities.values())):
        members = [n for n, c in communities.items() if c == i]
        mix = {}
        for n in members:
            mix[papers[n]["cluster"]] = mix.get(papers[n]["cluster"], 0) + 1
        comm_list.append({"id": f"c{i + 1}", "size": len(members),
                          "mix": sorted(mix.items(), key=lambda t: -t[1])})

    nodes = []
    for aid in sorted(ids):
        p = papers[aid]
        nodes.append({
            "id": aid,
            "title": p["title"],
            "cluster": p.get("cluster"),
            "community": f"c{communities[aid] + 1}" if aid in communities else None,
            "coreset": p["coreset"],
            "role": p["role"],
            "bridge": p["bridge"],
            "year": p.get("year"),
            "month": round(arxiv_month(aid), 3),
            "citations": p.get("citations"),
            "indeg": indeg[aid],
            "source": p["source"],
            "dims": p["dims"],
            "fields": p["fields"],
        })

    clustering = load_clustering(topic, nodes)

    data = {
        "topic": topic,
        "title": title,
        "layout": "coreset" if coreset_layout else "legacy",
        "built": time.strftime("%Y-%m-%d"),
        "edgesFrom": "the survey's pool table" if coreset_layout else f"Semantic Scholar references, fetched {fetched}",
        "clusters": [dict(clusters[c], cohesion=cohesion[c]) for c in order],
        "communities": comm_list,
        "modularity": {
            "declared": round(modularity({n: adj[n] for n in connected}, declared), 3) if connected else None,
            "citation": round(modularity({n: adj[n] for n in connected}, communities), 3) if connected else None,
        },
        "unresolved": unresolved,
        "clustering": clustering,
        "nodes": nodes,
        "edges": [[a, b] for a, b in edges],
    }

    vendor = ";\n".join((TOOLS / "vendor" / f).read_text() for f in VENDOR)
    template = (TOOLS / "graph_template.html").read_text()
    # Neutralise "</" so that no survey text can close the inline script.
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = template.replace("/*__VENDOR__*/", vendor).replace("/*__DATA__*/null", payload)

    out = topic_dir(topic) / "graph.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    print(f"graph:   {len(nodes)} nodes, {len(edges)} citation edges, {len(order)} clusters, "
          f"{len(comm_list)} citation communities")
    print(f"modularity: declared clusters {data['modularity']['declared']}, "
          f"citation communities {data['modularity']['citation']}")
    if unresolved:
        print(f"note:    Semantic Scholar returned nothing for {len(unresolved)} paper(s): {unresolved}")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__.strip())
        sys.exit(2)
    sys.exit(build(args[0], refresh="--refresh" in sys.argv))
