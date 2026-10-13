"""Build the gate fixture: a complete, passing coreset-layout pass from reasoning-legacy's data.

Used by faults.py and behaviour.py; `clean()` removes every file it writes, and `autoclean()` makes that happen when the
process exits, even after a crash. The topic is `zz-gate-<pid>`, so two runs never share files; set ZZ_GATE_TOPIC to
choose the name. `python3 tests/gates/build.py` builds the fixture and keeps it, for inspection. Needs
graphs/reasoning-legacy/.
"""
import atexit, contextlib, io, json, os, re, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from graph import parse
from check import link

T, DATE = os.environ.get("ZZ_GATE_TOPIC") or f"zz-gate-{os.getpid()}", "2026-10-09"
# The claims the two dissent rows quote; their full texts contain them, and their evidence quotes them.
DISSENT = ["accuracy falls when the chain is truncated early in our experiments",
           "we find no gain from longer reasoning on these tasks"]
SOURCE = "reasoning-legacy"   # the legacy survey; its pool, clustering and fringe data seed the fixture
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
    yes_map, out, k, n = {}, [], 0, 0
    for line in sheet:
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if c and c[0] == "s2":   # the legacy sheet has no row numbers; the fixture's sheet has them, as collect writes
            line = "| # " + line
        elif c and c[0].startswith("--"):
            line = "| -- " + line
        if len(c) >= 6 and re.fullmatch(r"[0-9a-f]{40}", c[0]):
            if k < 3:
                pid = pids[k * 7]; k += 1
                fr["candidates"][c[0]].update(arxiv=pid if not pid.startswith("CorpusId") else None,
                                              corpus=pid if pid.startswith("CorpusId") else None, title=titles[pid])
                c[4], c[5] = "yes", "in scope"
            else:
                c[4], c[5] = "no", "out of scope"
            n += 1
            line = f"| {n} | " + " | ".join(c[:6]) + " |"
        out.append(line)
    (dst / "fringe-screen.md").write_text("\n".join(out) + "\n")
    (dst / "fringe.json").write_text(json.dumps(fr))
    (dst / "rejected.md").write_text(f"# Rejected candidates: {T}\n\n| paper | date | reason |\n| -- | -- | -- |\n"
                                     f"| [2401.00001](https://arxiv.org/abs/2401.00001) | {DATE} | about image classification |\n")
    unique = len(fr["candidates"])

    names = {f"c{i}": n for i, n in enumerate(["one", "two", "three", "four", "five", "six"], 1)}
    align = {"c1": "high", "c2": "high", "c3": "medium", "c4": "medium", "c5": "low", "c6": "low"}
    members = {c: sorted(p for p, x in a.items() if x == c) for c in names}
    used, rows = set(), {c: [] for c in names}

    def take(c, role, why="highest in-degree in the cluster", src_="full-text"):
        p = next(p for p in members[c] if p not in used); used.add(p); rows[c].append((p, role, why, src_))
        return p

    fringe_ids = []
    for f in rep["fringe"]:
        if len(fringe_ids) == 5:
            break
        if f["id"] in a:
            used.add(f["id"]); fringe_ids.append(f["id"])
            rows[a[f["id"]]].append((f["id"], "fringe", "carries an idea no other row has", "full-text"))
    take("c1", "anchor"); take("c1", "frontier", src_="abstract"); take("c1", "frontier")
    d1 = take("c1", "dissent", f'reports "{DISSENT[0]}" against the cluster')
    take("c2", "anchor"); take("c2", "frontier", src_="abstract")
    d2 = take("c2", "dissent", f'finds "{DISSENT[1]}" against the cluster')
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
    claim = lambda c: " It holds that longer reasoning helps." if align[c] == "high" else ""
    cl_rows = "\n".join(f"| {n} | Cluster {n} | Papers about {n}.{claim(c)} | {align[c]} | bears on the input | {c} |"
                        for c, n in names.items())
    pool_rows = "\n".join(f"| [{titles[p].replace('|', '/')}]({link(p)}) | {pool['papers'][p].get('year') or ''} | {names[a[p]]} | 1 |  |"
                          for p in sorted(a))
    fetched = sorted({pool["papers"][p].get("fetched") for p in a} - {None})
    when = ("unknown" if not fetched else fetched[0] if len(fetched) == 1
            else f"{fetched[0]} to {fetched[-1]}")   # as tools/pool.py prints it
    fr1, fr2 = rows["c1"][-4][0], rows["c2"][-4][0]   # two anchors as frontier candidates
    changed = rows["c3"][0][0]
    # expansion: one collection from the two frontier candidates and one theme; its sheet has three rows, two `yes`
    # that are pool papers and one `no`, the paper rejected.md records
    import expand, screen
    s2s, pids_x = [f"{k + 1:040x}" for k in range(3)], [pids[3], pids[10], "2401.00001"]
    cands = {x: {"title": titles.get(p, "A study of image classifiers"), "abstract": "An abstract of the paper.",
                 "arxiv": None if p.startswith("CorpusId") else p, "corpus": p if p.startswith("CorpusId") else None,
                 "round": 0} for x, p in zip(s2s, pids_x)}
    xsrc = [dict(kind="backward", **{"from": fr1}, ids=s2s[:2], unresolved=1, returned=2),
           dict(kind="backward", **{"from": fr2}, ids=s2s[2:], unresolved=0, returned=1),
           dict(kind="forward", **{"from": fr1}, ids=[], unresolved=0, returned=0),
           dict(kind="forward", **{"from": fr2}, ids=[], unresolved=0, returned=0),
           dict(kind="search", query="test-time compute", ids=s2s, unresolved=0, returned=3)]
    exp = {"rounds": [{"collected": DATE, "kind": "first", "region": None, "why": None, "sources": xsrc,
                       "left out": {k: [] for k in expand.LEFT_OUT}}], "candidates": cands}
    said = [("yes", "studies test-time compute"), ("yes", "studies reasoning length"), ("no", "about image classification")]
    sheet = expand.SHEET.format(topic=T) + "".join(f"| {n} | {x} | {cands[x]['title'].replace('|', '/')} | An abstract of "
                                                   f"the paper. | {v} | {r} |\n" for n, (x, (v, r)) in enumerate(zip(s2s, said), 1))
    (dst / "expand.json").write_text(json.dumps(exp))
    (dst / "expand-screen.md").write_text(sheet)
    expansion = expand.expansion_line(exp, screen.verdicts(sheet), DATE)
    survey = f"""# Survey: {T}

## Retrieval log

### Pass {DATE}

- **Gates:** G0 {DATE}
- **Preflight:** snippet_search ok | search_papers_by_relevance ok | get_paper ok | get_citations ok | WebSearch ok |
  Graph API ok | arXiv ok | uv ok | Asta key set
- **Orientation (WebSearch):** "reasoning models"; themes: "test-time compute"; seeds from the input: none;
  frontier candidates: {fr1}, {fr2}
{expansion}
- **Errored queries:** none
- **Recency window:** 2026-04-09 to {DATE}, applied to the recency queries only
- **Fringe:** collected {DATE}: hidden 60, new 60 candidates ({unique} unique); in scope 3; added to the pool 3, of
  which 0 without an arXiv ID; left out 0
- **Pool:** {len(a)} papers in scope; metadata fetched {when}
- **Clustering:** measure {rep['measure']}; level {len(rep['clusters'])} clusters by rule tau, stability 0.79; next finer
  level 8 clusters at 0.67; diagnostics: thin cluster: six -> expanded; manual overrides: none
- **Clustering rationale:** The level is stable and the two high clusters are long-standing.
- **Clusters:** 6 (2 high, 2 medium, 2 low); halted for review: no; not yet reviewed
- **Dimensions:** declared in the input
- **Dissent searches:** one: "fails to" -> found: {d1} | two: "does not" -> found: {d2}
- **Coreset:** {len(all_rows)} rows
- **Demotions:** none
- **Late papers:** none
- **Coverage test:** round 1: 1 of 12 sampled candidates changed the output ({changed}: Gaps: it adds a gap the
  output lacks); new clusters: none
- **Judgement audit:** JUDGEMENT_AUDIT
- **Probes:** none
- **Corrections to existing rows:** none
- **Tokens:** step 1: 80k
- **Halts:** none
- **Waivers:** none
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
    claim = {d1: DISSENT[0], d2: DISSENT[1]}
    for i, p in enumerate(verified):
        name = p.replace("/", "_").replace(":", "_")
        # Every verified row quotes its fetched full text. In the first, hyphenation and wrapping differ from the quote.
        hyphen = i == 0
        (ft / f"{name}.txt").write_text(
            "# 3 Method\n\nWe propose a method that does a thing, and we assume a fixed compute budget.\n\n"
            "# 4 Results\n\nOn GSM8K the method " + ("im-\nproves" if hyphen else "improves") + " accuracy by two points "
            "over the baseline at equal compute, and the gain holds across all model sizes we tested.\n"
            + (f"\n# 5 Analysis\n\nUnlike earlier work, {claim[p]}.\n" if p in claim else ""))
        body = ('- `method name`, `method summary`, `evidence`, `measures`, `elicitation`, `pressure` — full-text, 3 Method — "We propose '
                'a method that does a thing, and we assume a fixed compute budget"\n'
                '- `result`, `datasets / models`, `metric` — full-text, 4 Results — "the method improves accuracy by two points ... the gain holds '
                'across all model sizes"\n'
                + (f'- `selected because` — full-text, 5 Analysis — "{claim[p]}"\n' if p in claim else ""))
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
    # The coverage sheet of round 1: the paper the line counts, and eleven pool papers outside the coreset.
    import coverage, audit
    others = [p for p in sorted(a) if p not in all_rows][:11]
    cov = [dict(paper=f"[{titles[changed]}]({link(changed)})", **{"drawn as": "worst-covered", "distance": "0.300",
                "nearest row": all_rows[0], "verdict": "changes Gaps", "reason": "it adds a gap the output lacks"})]
    cov += [dict(paper=f"[{titles[p].replace('|', '/')}]({link(p)})", **{"drawn as": "worst-covered", "distance": "0.200",
                 "nearest row": all_rows[0], "verdict": "no change", "reason": "its nearest row already makes the claim"})
            for p in others]
    coverage.write_sheet(dst / "coverage-1.md", T, 1, f"Drawn {DATE} by `tools/coverage.py draw`, seed 1.\n\n"
                         f'Recency query: "reasoning models" ({DATE}): 0 result(s).', cov)
    # The judgement audits, run through tools/audit.py as the order of operations runs them.
    def call(fn, *args, stdin=""):
        with contextlib.redirect_stdout(io.StringIO()):
            old, sys.stdin = sys.stdin, io.StringIO(stdin)
            try:
                assert fn(T, *args) == 0, fn.__name__
            finally:
                sys.stdin = old
    cells = dict(zip(cols[4:-1], ["M", "does a thing", "GSM8K", "accuracy", "+2"] + list(dims.values())))
    call(audit.reverify, 1)
    picked = [l.split("abs/")[1].split(")")[0] for l in (dst / "reverify.md").read_text().splitlines() if "arxiv.org/abs/" in l]
    call(audit.fill, stdin="".join(f"{p}\t{k}\t{v}\n" for p in picked for k, v in cells.items()))
    call(audit.compare)
    call(audit.judge, "reverify", stdin="".join(f"{p}\t{k}\tagree\tthe same claim\n" for p in picked for k in cells))
    call(audit.trace, 15, 1)
    n = (dst / "faithfulness.md").read_text().count("| S")
    call(audit.judge, "faithfulness", stdin="".join(f"S{i}\tsupported\tthe row says so\n" for i in range(1, n + 1)))
    s = (ROOT / f"surveys/{T}.md").read_text().replace("JUDGEMENT_AUDIT", audit.summary(T)[0])
    (ROOT / f"surveys/{T}.md").write_text(s)
    return dict(verified=verified, dissent=[d1, d2], abstract=abstract, rows=all_rows, changed=changed, fr1=fr1, fr2=fr2, names=names, a=a,
                s2s=s2s, expanded=pids_x)


def clean():
    shutil.rmtree(dst, ignore_errors=True)
    for f in (f"surveys/{T}.md", f"inputs/{T}.md", f"bib/{T}.bib", f"outputs/{T}.md"):
        (ROOT / f).unlink(missing_ok=True)


def autoclean():
    atexit.register(clean)


if __name__ == "__main__":
    build()
    print(f"built {T}; remove it with: ZZ_GATE_TOPIC={T} python3 -c 'import sys; sys.path.insert(0, \"tests/gates\"); "
          f"import build; build.clean()'")
