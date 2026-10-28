#!/usr/bin/env python3
"""Write the compact sheets that the naming and fringe-selection agents read, instead of the large JSON files.

Usage: uv run python -m deeper_research.sheets <topic>

Reads graphs/<topic>/clusters.json and pool.json and the survey, and writes two files alongside them:

  naming-sheet.md  per computed cluster: size, stability, its diagnostics and notes, its most-cited papers within the
                   pool (in-degree), its most recent papers, its papers from the last 12 months ranked by citations per
                   month (the candidates for its frontier role), and its sub-clusters with their most-cited papers.
                   For step 3, naming, and step 4, selection. Each cluster shows its name once the Clusters table has
                   one.
  fringe-sheet.md  the highest fringe scores, with year, cluster, number of resolved references, and whether the paper
                   is already a coreset row. For step 4, fringe selection; read the abstracts through Asta.

Standard library only; nothing is fetched.
"""

import json
from datetime import date
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
from deeper_research.check import row_id, sections, table_rows  # noqa: E402
from deeper_research.graph import parse, topic_dir  # noqa: E402

TOP, RECENT, RECENT_RATED, SUB_TOP, FRINGE = 8, 3, 5, 3, 25


def main(argv):
    if len(argv) != 1:
        print(__doc__.strip())
        return 2
    topic = argv[0]
    d = topic_dir(topic)
    for path, then in ((ROOT / "surveys" / f"{topic}.md", "steps 0-2 of docs/process.md"),
                       (d / "pool.json", f"`uv run python -m deeper_research.pool {topic}`"),
                       (d / "clusters.json", f"`uv run python -m deeper_research.cluster {topic}`")):
        if not path.exists():
            sys.exit(f"no {path.relative_to(ROOT)}; run {then} first")
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

    def age_and_rate(a):
        """(months since publication, citations per month), counted to the fetch date, when the citations were
        counted; None without a date or a count. Citations per month is the frontier role's measure of impact
        (docs/process.md, step 4)."""
        rec = cache.get(a, {})
        when = rec.get("date") or (f"{rec['year']}-07-01" if rec.get("year") else None)
        if when is None or rec.get("citations") is None:
            return None
        try:
            end = date.fromisoformat(rec["fetched"][:10]) if rec.get("fetched") else date.today()
            months = (end - date.fromisoformat(when[:10])).days / 30.44
        except ValueError:
            return None
        return months, rec["citations"] / max(1.0, months)

    def impact(a):
        ar = age_and_rate(a)
        return "" if ar is None else f" — {cache[a]['citations']} citations, {ar[1]:.1f} per month"

    def label(c):
        return f"{c} ({names[c]})" if c in names else c

    # `unstable cluster` and `broad scope` are notes, not diagnostics; a clusters.json written before that change still
    # lists them as diagnostics, so they are moved to the notes here.
    noted = ("unstable cluster", "broad scope")
    diagnostics = [x for x in report.get("diagnostics", []) if x.get("case") not in noted]
    notes = report.get("notes", []) + [{"clusters": x.get("clusters", []), "text": f"{x['case']}: {x['detail']}"}
                                       for x in report.get("diagnostics", []) if x.get("case") in noted]
    diag = {}
    for x in diagnostics:
        for c in x.get("clusters", []):
            diag.setdefault(c, []).append(f"{x['case']}: {x['detail']}")
    whole = [f"{x['case']}: {x['detail']}" for x in diagnostics if not x.get("clusters")]
    note = {}
    for x in notes:
        for c in x.get("clusters", []):
            note.setdefault(c, []).append(x["text"])
    whole_notes = [x["text"] for x in notes if not x.get("clusters")]

    out = [f"# Naming sheet: {topic}", "",
           f"Clustering of {report['generated']}: measure `{report['measure']}`, {report['level']} clusters "
           f"({report['level_reason']}). Membership is computed: name and define each cluster, rate its alignment, "
           "and never move papers between clusters (docs/process.md, step 3).", ""]
    if whole:
        out += ["Whole-clustering diagnostics: " + "; ".join(whole), ""]
    if whole_notes:
        out += ["Notes: " + " ".join(whole_notes), ""]
    for cl in report["clusters"]:
        c = cl["id"]
        members = [a for a, x in assigned.items() if x == c]
        st = f"{cl['stability']:.2f}" if cl["stability"] is not None else "none (fewer than 3 papers)"
        out += [f"## {label(c)} — {len(members)} papers, stability {st}", ""]
        for line in diag.get(c, []):
            out.append(f"- Diagnostic: {line}")
        for line in note.get(c, []):
            out.append(f"- Note: {line}")
        out.append(f"- Sub-clusters at the next finer level: {len(cl['subclusters'])}"
                   + (" (internally divided)" if cl["divided"] else ""))
        out += ["", "Most cited within the pool:", ""]
        for a in sorted(members, key=lambda a: -indeg[a])[:TOP]:
            out.append(f"- {indeg[a]} — `{a}` — {title(a)} ({year(a)})")
        out += ["", "Most recent:", ""]
        for a in sorted(members, key=lambda a: str(cache.get(a, {}).get("date") or year(a)), reverse=True)[:RECENT]:
            out.append(f"- `{a}` — {title(a)} ({cache.get(a, {}).get('date') or year(a)}){impact(a)}")
        # The frontier role's candidates: the last 12 months, by impact.
        rated = [(ar[1], a) for a in members if (ar := age_and_rate(a)) and ar[0] <= 12]
        out += ["", "Last 12 months, by citations per month:", ""]
        out += [f"- `{a}` — {title(a)} ({cache.get(a, {}).get('date') or year(a)}){impact(a)}"
                for _, a in sorted(rated, key=lambda x: (-x[0], x[1]))[:RECENT_RATED]] or ["- none"]
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
