#!/usr/bin/env python3
"""Write the compact sheets that the naming and fringe-selection agents read, instead of the large JSON files.

Usage: python3 tools/sheets.py <topic>

Reads graphs/<topic>/clusters.json and pool.json and the survey, and writes two files alongside them:

  naming-sheet.md  per computed cluster: size, stability, since when it exists, its diagnostics, its most-cited papers
                   within the pool (in-degree), its most recent papers, and its sub-clusters with their most-cited
                   papers. For step 3, naming. Each cluster shows its name once the Clusters table has one.
  fringe-sheet.md  the highest fringe scores, with year, cluster, number of resolved references, and whether the paper
                   is already a coreset row. For step 4, fringe selection; read the abstracts through Asta.

Standard library only; nothing is fetched.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from check import row_id, sections, table_rows  # noqa: E402
from graph import parse, topic_dir  # noqa: E402

TOP, RECENT, SUB_TOP, FRINGE = 8, 3, 3, 25


def main(argv):
    if len(argv) != 1:
        print(__doc__.strip())
        return 2
    topic = argv[0]
    d = topic_dir(topic)
    report = json.loads((d / "clusters.json").read_text())
    cache = json.loads((d / "pool.json").read_text())["papers"]
    papers = parse(topic)[4]
    secs = sections((ROOT / "surveys" / f"{topic}.md").read_text())
    names = {}
    for h, c, _, _ in table_rows(secs.get("Clusters", "")):
        if h and h[0] == "id" and "computed" in h and c[h.index("computed")]:
            names[c[h.index("computed")]] = c[0]
    coreset = {row_id(l) for h, _, _, l in table_rows(secs.get("Coreset", "")) if h and h[0] == "paper"}

    assigned = dict(report["assignment"])
    assigned.update({p: x["cluster"] for p, x in report.get("late", {}).items()})
    by_s2 = {cache[a]["s2"]: a for a in assigned if a in cache}
    indeg = {a: 0 for a in assigned}
    for a in assigned:
        for x in set(cache.get(a, {}).get("refs", [])):
            if x in by_s2 and by_s2[x] != a:
                indeg[by_s2[x]] += 1

    def title(a):
        return papers.get(a, {}).get("title") or a

    def year(a):
        return cache.get(a, {}).get("year") or ""

    def label(c):
        return f"{c} ({names[c]})" if c in names else c

    diag = {}
    for x in report.get("diagnostics", []):
        for c in x.get("clusters", []):
            diag.setdefault(c, []).append(f"{x['case']}: {x['detail']}")
    whole = [f"{x['case']}: {x['detail']}" for x in report.get("diagnostics", []) if not x.get("clusters")]

    out = [f"# Naming sheet: {topic}", "",
           f"Clustering of {report['generated']}: measure `{report['measure']}`, {report['level']} clusters "
           f"({report['level_reason']}). Membership is computed: name and define each cluster, rate its alignment, "
           "and never move papers between clusters (docs/process.md, step 3).", ""]
    if whole:
        out += ["Whole-clustering diagnostics: " + "; ".join(whole), ""]
    history = report.get("history", {}).get("clusters", {})
    for cl in report["clusters"]:
        c = cl["id"]
        members = [a for a, x in assigned.items() if x == c]
        st = f"{cl['stability']:.2f}" if cl["stability"] is not None else "none (fewer than 3 papers)"
        out += [f"## {label(c)} — {len(members)} papers, stability {st}", ""]
        if c in history:
            out.append(f"- Since: {history[c]['statement']}")
        for line in diag.get(c, []):
            out.append(f"- Diagnostic: {line}")
        out.append(f"- Sub-clusters at the next finer level: {len(cl['subclusters'])}"
                   + (" (internally divided)" if cl["divided"] else ""))
        out += ["", "Most cited within the pool:", ""]
        for a in sorted(members, key=lambda a: -indeg[a])[:TOP]:
            out.append(f"- {indeg[a]} — `{a}` — {title(a)} ({year(a)})")
        out += ["", "Most recent:", ""]
        for a in sorted(members, key=lambda a: str(cache.get(a, {}).get("date") or year(a)), reverse=True)[:RECENT]:
            out.append(f"- `{a}` — {title(a)} ({cache.get(a, {}).get('date') or year(a)})")
        for i, sub in enumerate(cl["subclusters"], 1):
            sst = f"{sub['stability']:.2f}" if sub["stability"] is not None else "none"
            out += ["", f"Sub-cluster {i}: {sub['size']} papers, stability {sst}", ""]
            for a in sorted(sub["members"], key=lambda a: -indeg.get(a, 0))[:SUB_TOP]:
                out.append(f"- {indeg.get(a, 0)} — `{a}` — {title(a)}")
        out.append("")
    (d / "naming-sheet.md").write_text("\n".join(out))

    rows = [f"# Fringe sheet: {topic}", "",
            "The highest fringe scores: distance to the nearest neighbours in the pool, ranked within the paper's age "
            "cohort (docs/process.md, \"Clustering method\"). Read the abstracts through Asta (`get_paper_batch`), and "
            "keep five to ten papers that each carry an idea no other coreset row has (step 4, `fringe`).", "",
            "| score | year | cluster | refs | coreset | paper |", "| -- | -- | -- | -- | -- | -- |"]
    for f in report["fringe"][:FRINGE]:
        a = f["id"]
        rows.append(f"| {f['score']:.2f} | {f['year'] or ''} | {label(f['cluster'])} | "
                    f"{len(cache.get(a, {}).get('refs', []))} | {'yes' if a in coreset else ''} | "
                    f"`{a}` {title(a).replace('|', '/')} |")
    (d / "fringe-sheet.md").write_text("\n".join(rows) + "\n")
    for name in ("naming-sheet.md", "fringe-sheet.md"):
        text = (d / name).read_text()
        print(f"wrote {(d / name).relative_to(ROOT)}: {len(text):,} chars (about {len(text) // 4:,} tokens)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
