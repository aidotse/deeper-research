"""Build the zz-gate fixture: a complete, passing coreset-layout pass from reasoning's data.

Used by faults.py and behaviour.py; `clean()` removes every file it writes. Needs graphs/reasoning/.
"""
import json, re, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from graph import parse
from check import link

T, DATE = "zz-gate", "2026-10-09"
# The source is the legacy survey: `reasoning` until it is renamed for the fresh coreset run.
SOURCE = "reasoning-exhaustive" if (ROOT / "graphs/reasoning-exhaustive").exists() else "reasoning"
src, dst = ROOT / f"graphs/{SOURCE}", ROOT / f"graphs/{T}"


def build():
    shutil.rmtree(dst, ignore_errors=True); dst.mkdir(parents=True)
    pool = json.loads((src / "pool.json").read_text())
    (dst / "pool.json").write_text(json.dumps(pool))
    rep = json.loads((src / "clusters.json").read_text()); rep["generated"] = DATE
    (dst / "clusters.json").write_text(json.dumps(rep))
    titles = {p: v["title"] for p, v in parse(SOURCE)[4].items()}
    a = rep["assignment"]
    # fringe: keep the sheet; map three `yes` rows onto pool papers
    fr = json.loads((src / "fringe.json").read_text()); fr["collected"] = DATE
    sheet = (src / "fringe-screen.md").read_text().splitlines()
    pids = sorted(a)
    yes_map, out, k = {}, [], 0
    for line in sheet:
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) >= 6 and re.fullmatch(r"[0-9a-f]{40}", c[0]):
            if k < 3:
                pid = pids[k * 7]; k += 1
                fr["candidates"][c[0]].update(arxiv=pid if not pid.startswith("CorpusId") else None,
                                              corpus=pid if pid.startswith("CorpusId") else None, title=titles[pid])
                c[4], c[5] = "yes", "in scope"
            else:
                c[4], c[5] = "no", "out of scope"
            line = "| " + " | ".join(c[:6]) + " |"
        out.append(line)
    (dst / "fringe-screen.md").write_text("\n".join(out) + "\n")
    (dst / "fringe.json").write_text(json.dumps(fr))
    (dst / "rejected.md").write_text(f"# Rejected candidates: {T}\n\n| paper | date | reason |\n| -- | -- | -- |\n"
                                     f"| [2401.00001](https://arxiv.org/abs/2401.00001) | {DATE} | off topic |\n")
    unique = len(fr["candidates"])

    names = {f"c{i}": n for i, n in enumerate(["one", "two", "three", "four", "five", "six"], 1)}
    align = {"c1": "high", "c2": "high", "c3": "medium", "c4": "medium", "c5": "low", "c6": "low"}
    members = {c: sorted(p for p, x in a.items() if x == c) for c in names}
    used, rows = set(), {c: [] for c in names}

    def take(c, role, why="highest in-degree in the cluster", src_="snippet"):
        p = next(p for p in members[c] if p not in used); used.add(p); rows[c].append((p, role, why, src_))
        return p

    fringe_ids = []
    for f in rep["fringe"]:
        if len(fringe_ids) == 5:
            break
        if f["id"] in a:
            used.add(f["id"]); fringe_ids.append(f["id"])
            rows[a[f["id"]]].append((f["id"], "fringe", "carries an idea no other row has", "snippet"))
    take("c1", "anchor"); take("c1", "frontier", src_="abstract"); take("c1", "frontier")
    take("c1", "dissent", 'reports "accuracy falls when the chain is truncated early" against the cluster')
    take("c2", "anchor"); take("c2", "frontier", src_="abstract")
    take("c2", "dissent", 'finds "no gain from longer reasoning on these tasks" against the cluster')
    take("c2", "bridge:three", "applies the cluster's method to the other's question")
    for c in ("c3", "c4"):
        take(c, "anchor"); take(c, "frontier")
    take("c5", "anchor"); take("c6", "anchor")
    dims = {"evidence": "empirical", "measures": "capability", "elicitation": "elicited", "pressure": "none"}
    cols = ["paper", "venue+year", "role", "selected because", "method name", "method summary", "datasets / models",
            "metric", "result"] + list(dims) + ["source"]
    hdr = "| " + " | ".join(cols) + " |\n| " + " | ".join("--" for _ in cols) + " |"
    blocks, all_rows, abstract = [], [], []
    for c, n in names.items():
        lines = [f"### {n} — cluster {n}", "", hdr]
        for p, role, why, s in rows[c]:
            all_rows.append(p)
            if s == "abstract":
                abstract.append(p)
            lines.append(f"| [{titles[p].replace('|', '/')}]({link(p)}) | arXiv 2025-01 | {role} | {why} | M | does a thing | "
                         f"GSM8K | accuracy | +2 | " + " | ".join(dims.values()) + f" | {s} |")
        blocks.append("\n".join(lines))
    cl_rows = "\n".join(f"| {n} | Cluster {n} | papers about {n} | {align[c]} | bears on the input | {c} |"
                        for c, n in names.items())
    pool_rows = "\n".join(f"| [{titles[p].replace('|', '/')}]({link(p)}) | {pool['papers'][p].get('year') or ''} | {names[a[p]]} | 1 |  |"
                          for p in sorted(a))
    fr1, fr2 = rows["c1"][-4][0], rows["c2"][-4][0]   # two anchors as frontier candidates
    changed = rows["c3"][0][0]
    survey = f"""# Survey: {T}

## Retrieval log

### Pass {DATE}

- **Gates:** G0 {DATE}
- **Preflight:** snippet_search ok | search_papers_by_relevance ok | get_paper ok | get_citations ok | WebSearch ok |
  Graph API ok | arXiv ok | uv ok | Asta key set
- **Orientation (WebSearch):** "reasoning models"; frontier candidates: {fr1}, {fr2}
- **Expansion:** backward from {fr1} (40), {fr2} (35); queries "test-time compute"
- **Errored queries:** none
- **Recency window:** 2026-04-09 to {DATE}, applied to the recency queries only
- **Fringe:** collected {DATE}: hidden 60, new 60 candidates ({unique} unique); in scope 3; added to the pool 3, of
  which 0 without an arXiv ID; left out 0
- **Pool:** {len(a)} papers in scope; metadata fetched {DATE}
- **Clustering:** measure {rep['measure']} (grid mean stability: x); level {len(rep['clusters'])} clusters by rule tau,
  stability 0.80; diagnostics: thin cluster: six -> expanded; manual overrides: none
- **Temporal stability:** 4 equal-count segments; one since 2025-01
- **Clustering rationale:** The level is stable and the two high clusters are long-standing.
- **Clusters:** 6 (2 high, 2 medium, 2 low); halted for review: no; not yet reviewed
- **Dimensions:** declared in the input
- **Dissent searches:** one: "fails to" -> found | two: "does not" -> found
- **Coreset:** {len(all_rows)} rows
- **Demotions:** none
- **Late papers:** none
- **Coverage test:** round 1: 1 of 12 sampled candidates changed the output ({changed}: gap: a new gap); new
  clusters: none
- **Probes:** none
- **Corrections to existing rows:** none
- **Tokens:** step 1: 80k
- **Halts:** none
- **Ended:** finished (F1); 1 of 12

## Clusters

| id | name | definition | alignment | alignment reason | computed |
| -- | -- | -- | -- | -- | -- |
{cl_rows}

## Coreset

{chr(10).join(blocks)}

## Pool

| paper | year | cluster | citations | cites |
| -- | -- | -- | -- | -- |
{pool_rows}

## Open work

- **Clusters not yet reviewed by the user:** {', '.join(names.values())}
- **Empty roles:** none
- **Rows needing verification:** {', '.join(f'{p} — no body text' for p in abstract)}
"""
    (ROOT / f"surveys/{T}.md").write_text(survey)
    ev = dst / "evidence"; ev.mkdir(); ft = dst / "fulltext"; ft.mkdir()
    verified = [p for p in all_rows if p not in abstract]
    for i, p in enumerate(verified):
        name = p.replace("/", "_").replace(":", "_")
        if i == 0:   # one row verified against full text: hyphenation and wrapping differ from the quote
            (ft / f"{name}.txt").write_text("# 4 Results\n\nOn GSM8K the method im-\nproves accuracy by two points over the baseline "
                                             "at equal compute, and the gain holds across all model sizes we tested.\n")
            body = ('- `method summary`, `evidence`, `measures`, `elicitation`, `pressure` — snippet — "we propose a method"\n'
                    '- `result` — full-text, 4 Results — "the method improves accuracy by two points ... the gain holds '
                    'across all model sizes"\n')
        else:
            body = ('- `method summary`, `result`, `evidence`, `measures`, `elicitation`, `pressure` — snippet — '
                    '"we report accuracy gains"\n')
        (ev / f"{name}.md").write_text(f"# Evidence: {p}\n\n" + body)
    shutil.copy(ROOT / f"inputs/{SOURCE}.md", ROOT / f"inputs/{T}.md")
    bib = "".join(f"@misc{{k{i},\n  " + (f"corpusid = {{{p.split(':')[1]}}}" if p.startswith("CorpusId") else f"eprint = {{{p}}}")
                  + "\n}\n" for i, p in enumerate(all_rows))
    (ROOT / f"bib/{T}.bib").write_text(bib)
    cite = [p for p in all_rows if p not in abstract][:4]
    (ROOT / f"outputs/{T}.md").write_text(f"""# Output: {T}

Claims marked [abstract-only] rest on a paper checked against its abstract only.

## Landscape

Two clusters, {cite[0]} and {abstract[0]} [abstract-only].

## Assumptions

That length helps ({cite[1]}).

## Gaps

A tension ({cite[2]}).

## Questions

- Does it hold? Builds on {cite[0]}.

## Reading

1. {cite[3]} — start here.
""")
    return dict(verified=verified, abstract=abstract, rows=all_rows, changed=changed, fr1=fr1, fr2=fr2, names=names, a=a)


def clean():
    shutil.rmtree(dst, ignore_errors=True)
    for f in (f"surveys/{T}.md", f"inputs/{T}.md", f"bib/{T}.bib", f"outputs/{T}.md"):
        (ROOT / f).unlink(missing_ok=True)


if __name__ == "__main__":
    build()
