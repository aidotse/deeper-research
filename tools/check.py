#!/usr/bin/env python3
"""Consistency check for one topic's pipeline artifacts, and the gates of a pass.

Usage: python3 tools/check.py <topic> [--gate G<n>] [--status]

Two kinds of check, both failing with exit status 1:

  integrity  whatever exists must be well formed. The input's format; the survey's sections and their order; the
             Clusters table; the Pool table (columns, paper links, unique IDs, known clusters; no paper twice, whether
             under two IDs, as two records with one title, or as a CorpusId row for a paper that has an arXiv ID); every
             pool paper's `cluster` its computed cluster, through the Clusters table's `computed` column; once the
             Coreset has rows, one row per unique paper ID, the required columns, `source` last, declared dimension
             values, blocks headed by known clusters in the Clusters table's order, valid roles and bridges, every
             coreset paper in the pool and in the block of its computed cluster, and coreset/bib parity; once the
             output exists, every cited paper ID in the coreset, every citation of an `abstract`-sourced paper marked
             [abstract-only] with a legend before the first section, no marker after the legend that follows no
             citation, and a section per target plus Questions and Reading.
  gates      what each step must have left behind, G0 to G5 (tools/gates.py, docs/gates.md). The gates the pass has
             reached are worked out from the files; `--gate G<n>` also requires every gate up to G<n>, which is how the
             main session checks a gate before starting the next step. `--status` prints every gate's open
             requirements: what the run has done, and what remains.

When the input declares no dimensions, the ones proposed in the current log entry's `Dimensions` line
(`proposed: `<name>` — values: `<a>`, `<b>`; ...`) are checked in their place.

It also prints, without failing: each cluster's in-degree leaders within the pool and role coverage, anchors that are
not an in-degree leader, the `source` tally, how many coreset and pool papers have an arXiv ID, and pool papers still
waiting for a cluster. Notes also flag clusters that trade papers with no bridge yet, while G3 is not yet required, and
papers both rejected and in the pool.

Surveys written before the coreset structure (no `## Clusters` section) get only the integrity checks that apply to
them, and no gates. Exit status 2 is a usage error.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
# A paper's canonical ID (docs/formats.md): its arXiv ID where it has one, otherwise its Semantic Scholar corpus ID,
# `CorpusId:<n>`. These are the one definition every tool uses.
#
# Every form of arXiv identifier: YYMM.NNNNN since 2015, YYMM.NNNN from 2007 to
# 2014, and archive/YYMMNNN before that (hep-th/9901001). The canonical old form
# has no subject class: math/0309136, not math.GT/0309136, which Semantic
# Scholar does not resolve.
ARXIV_ID = r"(?:\d{2}(?:0[1-9]|1[0-2])\.\d{4,5}|[a-z]+(?:-[a-z]+)?/\d{7})"
CORPUS_ID = r"CorpusId:\d+"
PAPER_ID = rf"(?:{ARXIV_ID}|{CORPUS_ID})"
ID = re.compile(rf"^{PAPER_ID}$")
ARXIV_ONLY = re.compile(rf"^{ARXIV_ID}$")
# A survey row links its paper to arxiv.org/abs/<id>, or, without an arXiv ID, to
# api.semanticscholar.org/CorpusId:<n>, which redirects to the paper's page.
LINK = re.compile(rf"(?:arxiv\.org/abs/|api\.semanticscholar\.org/)({PAPER_ID})")
# Outputs cite papers as bare IDs inline (e.g. "(2504.13837)") rather than as
# links, so that prose stays readable. Match those too, or the output/survey
# cross-reference check silently passes by matching nothing.
BARE_ID = re.compile(rf"(?<![\w./-])({PAPER_ID})(?:v\d+)?(?![\w/]|\.\d)")
# A bib entry carries `eprint` for an arXiv paper, `corpusid` for any other.
BIB_ID = re.compile(rf"(?:eprint\s*=\s*\{{({ARXIV_ID})\}}|corpusid\s*=\s*\{{(\d+)\}})")
# What may sit between a cited ID and its [abstract-only] marker: a version,
# whitespace (including a line break), bold markers and punctuation, but no
# other ID.
MARKED = re.compile(r"(?:v\d+)?[\s*,;:()\]]*\[abstract-only\]")
CLUSTER_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

SURVEY_SECTIONS = ["Retrieval log", "Clusters", "Coreset", "Pool", "Open work"]
POOL_COLUMNS = ["paper", "year", "cluster", "citations", "cites"]
CORESET_COLUMNS = ["paper", "venue+year", "role", "selected because", "method name", "method summary",
                   "datasets / models", "metric", "result"]
ALIGNMENTS = {"high", "medium", "low"}
ROLES = {"anchor", "frontier", "dissent", "fringe"}
NEEDED = {"high": ("anchor", "frontier", "dissent"), "medium": ("anchor", "frontier"), "low": ("anchor",)}
FRINGE_QUOTA = (5, 10)  # per topic, not per cluster
ABSTRACT_SHARE = 0.2  # above this share of abstract-sourced rows after step 5, the pass halts (H10)
SOURCES = {"abstract", "full-text"}
# Legacy surveys were verified against snippets, before quotes had to come from the fetched full text.
LEGACY_SOURCES = SOURCES | {"snippet"}
# Phrases that claim absence, which only a probe may support (docs/verification.md, "Probes").
ABSENCE = re.compile(r"\b(?:has not been (?:studied|explored|addressed)|no (?:prior )?work (?:on|has)|nobody has|"
                     r"no one has|has never been)\b", re.I)


def read(path):
    return path.read_text() if path.exists() else None


def s2_ref(pid):
    """How the Semantic Scholar API and Asta name a paper: ARXIV:<id>, or CorpusId:<n> as it is."""
    return pid if pid.startswith("CorpusId:") else f"ARXIV:{pid}"


def link(pid):
    return f"https://api.semanticscholar.org/{pid}" if pid.startswith("CorpusId:") else f"https://arxiv.org/abs/{pid}"


def arxiv_of(rec):
    """The arXiv ID of a Semantic Scholar API record. Some records omit it from `externalIds` though their open-access
    PDF is on arXiv: often a preprint whose venue version is a separate record."""
    ext = (rec or {}).get("externalIds") or {}
    if ext.get("ArXiv"):
        return ext["ArXiv"]
    m = re.search(rf"arxiv\.org/(?:pdf|abs)/({ARXIV_ID})", ((rec or {}).get("openAccessPdf") or {}).get("url") or "")
    return m.group(1) if m else None


def bib_ids(text):
    return [a or f"CorpusId:{n}" for a, n in BIB_ID.findall(text)]


def cells_of(line):
    """Split a markdown table row into cells.

    Escaped pipes (`\\|`) appear inside cell text — formulae like `q(y\\|x)` —
    and are not separators, so they must be masked before splitting or the row
    looks wider than it is.
    """
    return [c.strip() for c in line.replace(r"\|", "\0").strip("|").split("|")]


def sections(text):
    """Map each `## ` heading to the text under it, up to the next one."""
    out, name, buf = {}, None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if name is not None:
                out[name] = "\n".join(buf)
            name, buf = line[3:].strip(), []
        else:
            buf.append(line)
    if name is not None:
        out[name] = "\n".join(buf)
    return out


def section_order(text):
    return [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]


def table_rows(text):
    """Yield (header_cells, row_cells, block_heading, line) for every table row."""
    block, header = None, None
    for line in text.splitlines():
        if line.startswith("### "):
            block, header = line[4:].strip(), None
        elif line.startswith("|") and header is None:
            header = cells_of(line)
        elif line.startswith("| --") or line.startswith("|--"):
            continue
        elif line.startswith("|"):
            yield header, cells_of(line), block, line
        else:
            # Tables are contiguous; any non-table line ends the current one.
            header = None


def row_id(line):
    m = LINK.search(line)
    return m.group(1) if m else None


# --- the coreset table ----------------------------------------------------------------------------


def check_coreset(table, dims, layout, failures, notes):
    """Checks that apply to any Coreset section, legacy or current."""
    rows = [(h, c, b, l) for h, c, b, l in table_rows(table) if h and h[0] == "paper"]
    ids = [row_id(l) for _, _, _, l in rows]
    unique = {i for i in ids if i}
    print(f"coreset: {len(rows)} rows, {len(unique)} unique paper IDs")
    if len(rows) != len(unique) or None in ids:
        failures.append(
            f"row count {len(rows)} != unique IDs {len(unique)} "
            "(duplicate row, or a row whose link is neither arxiv.org/abs/<id> nor api.semanticscholar.org/CorpusId:<n>)"
        )

    widths = {}
    for h, c, b, l in rows:
        widths.setdefault(len(h), set()).add(b)
        if len(c) != len(h):
            failures.append(f"{b or '(no block)'}: row {row_id(l)} has {len(c)} cells, header has {len(h)}")
    blocks = len({b for _, _, b, _ in rows})
    print(f"columns: {', '.join(f'{w}' for w in sorted(widths))} across {blocks} block(s)")
    if len(widths) > 1:
        failures.append(f"blocks disagree on column count: {sorted(widths)}")

    sources = [c[-1] for _, c, _, _ in rows]
    allowed = SOURCES if layout == "coreset" else LEGACY_SOURCES
    bad = [row_id(l) for (_, c, _, l) in rows if c[-1] not in allowed]
    if bad or (rows and rows[0][0][-1] != "source"):
        failures.append(f"rows without a parsable `source` last column: {bad}")
    snip = [row_id(l) for (_, c, _, l) in rows if c[-1] == "snippet" and layout == "coreset"]
    if snip:
        failures.append(f"rows with `source` `snippet`, which is not a source: verify against the fetched full text, "
                        f"or leave the row `abstract` (docs/verification.md): {snip[:8]}")
    tally = {k: sources.count(k) for k in sorted(set(sources) & allowed)}
    print(f"source:  {tally}")
    print(f"arXiv:   {sum(1 for i in unique if ARXIV_ONLY.match(i))} of {len(unique)} coreset papers have an arXiv ID")

    if layout == "coreset" and rows:
        share = sources.count("abstract") / len(rows)
        print(f"         {share:.0%} abstract-sourced; after step 5, more than {ABSTRACT_SHARE:.0%} halts the pass (H10)")
        for h in {tuple(h) for h, _, _, _ in rows}:
            missing = [c for c in CORESET_COLUMNS if c not in h]
            if missing:
                failures.append(f"Coreset table lacks required column(s): {missing}")
            extra = [c for c in h if c not in CORESET_COLUMNS and c != "source" and c not in dims]
            if extra:
                notes.append(f"Coreset column(s) {extra} are not dimensions, declared in the input or proposed in the "
                             f"log; values unchecked")

    header = rows[0][0] if rows else []
    for i, n in [(i, n) for i, n in enumerate(header) if n in dims]:
        counts = {}
        for _, c, _, l in rows:
            v = c[i] if i < len(c) else ""
            counts[v] = counts.get(v, 0) + 1
            if v not in dims[n]:
                failures.append(f"row {row_id(l)}: {n}={v!r} is not an allowed value")
        shown = ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda t: -t[1]))
        print(f"{n + ':':13}{shown}")

    abstract = {row_id(l) for _, c, _, l in rows if c[-1] == "abstract"}
    return rows, unique, abstract


# --- clusters and pool ----------------------------------------------------------------------------


def read_clusters(secs, failures):
    """The Clusters table: {id: alignment}, the `computed` column as {computed id: named id}, and the rows."""
    clusters, computed, rows = {}, {}, []
    for h, c, _, _ in table_rows(secs["Clusters"]):
        if not h or h[0] != "id":
            continue
        row = dict(zip(h, c))
        rows.append(row)
        cid, alignment = row["id"], row.get("alignment", "")
        if not CLUSTER_ID.match(cid):
            failures.append(f"cluster id {cid!r} is not kebab-case")
        if cid in clusters:
            failures.append(f"cluster id {cid!r} is defined twice")
        if alignment not in ALIGNMENTS:
            failures.append(f"cluster {cid}: alignment {alignment!r} is not one of {sorted(ALIGNMENTS)}")
        clusters[cid] = alignment
        if row.get("computed"):
            if row["computed"] in computed:
                failures.append(f"computed cluster {row['computed']} is named twice in the Clusters table")
            computed[row["computed"]] = cid
    print(f"clusters: {len(clusters)} ({', '.join(f'{a} {list(clusters.values()).count(a)}' for a in ['high', 'medium', 'low'])})")
    return clusters, computed, rows


def read_pool(secs, clusters, failures):
    """The Pool table: its IDs, each one's `cluster` cell (may be empty), and the pool papers each one cites."""
    pool_cluster, cites, titles, header_checked = {}, {}, {}, False
    for h, c, _, l in table_rows(secs["Pool"]):
        if not h or h[0] != "paper":
            continue
        if not header_checked:
            header_checked = True
            missing = [x for x in POOL_COLUMNS if x not in h]
            if missing:
                failures.append(f"Pool table lacks required column(s): {missing}")
        pid = row_id(l)
        if pid is None:
            failures.append(f"pool row whose link is neither arxiv.org/abs/<id> nor api.semanticscholar.org/CorpusId:<n>: "
                            f"{c[0][:60]!r}")
            continue
        titles[pid] = c[0]
        if pid in pool_cluster:
            failures.append(f"pool lists {pid} twice")
        cl = c[h.index("cluster")] if "cluster" in h else ""
        if cl and cl not in clusters:
            failures.append(f"pool {pid}: cluster {cl!r} is not a known cluster")
        pool_cluster[pid] = cl
        cites[pid] = set(BARE_ID.findall(c[h.index("cites")])) if "cites" in h else set()
    print(f"pool:    {len(pool_cluster)} papers, {sum(1 for p in pool_cluster if ARXIV_ONLY.match(p))} with an arXiv ID")
    return set(pool_cluster), pool_cluster, cites, titles


def words(title):
    title = re.sub(r"\]\(.*", "", title.lstrip("["))  # the link text only
    return re.findall(r"[a-z0-9]+", title.lower())


def check_duplicates(topic, titles, failures, notes):
    """A preprint and its venue version can be two Semantic Scholar records; keep the arXiv one (docs/formats.md)."""
    sidecar = read(ROOT / "graphs" / topic / "pool.json")
    records = json.loads(sidecar)["papers"] if sidecar else {}
    by_s2 = {}
    for pid in titles:
        rec = records.get(pid) or {}
        if rec.get("s2"):
            by_s2.setdefault(rec["s2"], []).append(pid)
        if pid.startswith("CorpusId:") and rec.get("arxiv"):
            failures.append(f"pool {pid} has an arXiv ID, {rec['arxiv']}: use it as the paper's ID")
    for same in by_s2.values():
        if len(same) > 1:
            failures.append(f"pool lists one Semantic Scholar paper under several IDs: {same}")
    keyed = {pid: words(t) for pid, t in titles.items()}
    exact = {}
    for pid, w in keyed.items():
        exact.setdefault(" ".join(w), []).append(pid)
    for t, same in exact.items():
        if t and len(same) > 1:
            failures.append(f"pool rows with the same title, probably one paper twice: {same}; keep the arXiv record, "
                            "merge the other into it, and log it under `Corrections to existing rows`")
    sets = sorted(((pid, set(w)) for pid, w in keyed.items() if len(w) >= 4), key=lambda x: len(x[1]))
    for i, (a, A) in enumerate(sets):
        for b, B in sets[i + 1:]:
            if len(B) > len(A) / 0.9:
                break
            if " ".join(keyed[a]) != " ".join(keyed[b]) and len(A & B) / len(A | B) >= 0.9:
                notes.append(f"pool rows with near-identical titles: {a}, {b}; one paper twice?")


def check_computed(topic, pool, pool_cluster, clusters, computed, failures, notes):
    """Every pool paper's cluster must be its computed one: membership is never changed by hand."""
    text = read(ROOT / "graphs" / topic / "clusters.json")
    unclustered = sorted(p for p in pool if not pool_cluster.get(p))
    if text is None:
        if clusters:
            failures.append(f"the Clusters table has rows but graphs/{topic}/clusters.json does not exist")
        elif unclustered:
            notes.append(f"{len(unclustered)} pool paper(s) have no cluster yet; clustering is step 3")
        return None
    report = json.loads(text)
    assigned = dict(report.get("assignment", {}))
    assigned.update({p: x["cluster"] for p, x in report.get("late", {}).items()})
    if not clusters:
        if unclustered:
            notes.append(f"{len(unclustered)} pool paper(s) have no cluster yet: name the computed clusters (step 3), "
                         f"then run `python3 tools/assign.py clusters {topic}`")
        return report
    if not computed:
        failures.append("the Clusters table has no `computed` column, so pool clusters cannot be checked against "
                        "clusters.json (docs/formats.md, Clusters)")
        return report
    if report.get("previous") and not report["previous"].get("remapped"):
        failures.append(f"clusters.json is a new clustering whose names have not been carried over; run "
                        f"`python3 tools/assign.py remap {topic}`, then `python3 tools/assign.py clusters {topic}`")
        return report
    known = set(report.get("assignment", {}).values())
    orphans = [cid for cid in clusters if cid not in computed.values()]
    if orphans:
        failures.append(f"Clusters row(s) {orphans} have no `computed` id: every named cluster is a computed one")
    for cc, cid in computed.items():
        if cc not in known:
            failures.append(f"Clusters table: {cid} names computed cluster {cc!r}, which clusters.json does not have")
    unnamed = sorted(known - set(computed), key=lambda x: int(x[1:]) if x[1:].isdigit() else 0)
    if unnamed:
        failures.append(f"computed cluster(s) {unnamed} have no row in the Clusters table")
    wrong = sorted(p for p in pool if p in assigned and pool_cluster.get(p)
                   and computed.get(assigned[p]) != pool_cluster[p])
    if wrong:
        failures.append(f"pool cluster differs from the computed assignment for {wrong[:10]}"
                        + (f" and {len(wrong) - 10} more" if len(wrong) > 10 else "")
                        + f"; run `python3 tools/assign.py clusters {topic}`, never edit by hand")
    blank = sorted(p for p in pool if p in assigned and not pool_cluster.get(p))
    if blank:
        notes.append(f"{len(blank)} pool paper(s) are assigned in clusters.json but their Pool cell is empty; run "
                     f"`python3 tools/assign.py clusters {topic}`")
    sidecar = read(ROOT / "graphs" / topic / "pool.json")
    records = json.loads(sidecar)["papers"] if sidecar else {}
    unclusterable = sorted(p for p in pool if p in records and not records[p].get("embedding"))
    if unclusterable:
        notes.append(f"pool paper(s) without a SPECTER2 embedding, which no clustering can place: {unclusterable}; "
                     "record them in Open work (docs/formats.md, \"Paper IDs\")")
    late = sorted(p for p in pool if p not in assigned and p not in unclusterable)
    if late:
        notes.append(f"late papers awaiting assignment ({len(late)}): {late}; run `uv run tools/assign.py late {topic}` "
                     "(docs/process.md, \"Late papers\")")
    return report


def leaders(cid, pool, pool_cluster, indeg):
    """Print and return a cluster's in-degree leaders within the pool."""
    members = [p for p in pool if pool_cluster.get(p) == cid]
    top = max((indeg[p] for p in members), default=0)
    lead = {p for p in members if indeg[p] == top} if top > 0 else set()
    print(f"    in-degree leader(s) within the pool: {', '.join(sorted(lead)) or 'none'}" + (f" ({top})" if top else ""))
    return lead, top


def check_structure(topic, secs, rows, coreset_ids, failures, notes):
    """Checks for surveys using clusters, roles and a pool. Returns what the gates read."""
    clusters, computed, cluster_rows = read_clusters(secs, failures)
    pool, pool_cluster, cites, titles = read_pool(secs, clusters, failures)
    check_duplicates(topic, titles, failures, notes)
    report = check_computed(topic, pool, pool_cluster, clusters, computed, failures, notes)

    sidecar = read(ROOT / "graphs" / topic / "pool.json")
    unfetched = sorted(pool - set(json.loads(sidecar)["papers"] if sidecar else ()))
    if unfetched:
        notes.append(f"{len(unfetched)} pool paper(s) are not in graphs/{topic}/pool.json; run "
                     f"`python3 tools/pool.py {topic}`")

    indeg = {p: 0 for p in pool}
    for p, cs in cites.items():
        for q in cs & pool:
            if q != p:
                indeg[q] += 1

    out = {"clusters": clusters, "computed": computed, "cluster_rows": cluster_rows, "pool": pool,
           "pool_cluster": pool_cluster, "titles": titles, "report": report, "roles": {}, "bridges": set()}
    if not rows:
        for cid, alignment in clusters.items():
            print(f"  {cid} [{alignment}]: pool {sum(1 for p in pool if pool_cluster.get(p) == cid)}")
            leaders(cid, pool, pool_cluster, indeg)
        return out

    header = rows[0][0]
    if "role" not in header:
        failures.append("Coreset section has no `role` column")
        return out
    ri = header.index("role") if rows else None
    order = [b.split(" — ")[0].strip() for b in
             (line[4:].strip() for line in secs["Coreset"].splitlines() if line.startswith("### "))]
    known_order = [b for b in order if b in clusters]
    if known_order != [cid for cid in clusters if cid in known_order]:
        failures.append(f"Coreset blocks are not in the Clusters table's order: {known_order}")

    roles = {cid: {} for cid in clusters}
    anchors = {cid: set() for cid in clusters}
    bridges = set()
    for _, c, block, l in rows:
        cid, pid = (block or "").split(" — ")[0].strip(), row_id(l)
        if cid not in clusters:
            failures.append(f"block {block!r} is not headed by a known cluster id")
            continue
        role = c[ri]
        base, _, target = role.partition(":")
        if base == "bridge":
            if target not in clusters:
                failures.append(f"row {pid}: bridge target {target!r} is not a known cluster")
            elif target == cid:
                failures.append(f"row {pid}: bridge to its own cluster {cid!r}")
            bridges.add(frozenset((cid, target)))
        elif role not in ROLES:
            failures.append(f"row {pid}: role {role!r} is not valid")
        roles[cid][base] = roles[cid].get(base, 0) + 1
        if role == "anchor":
            anchors[cid].add(pid)
        if pool_cluster.get(pid) and pool_cluster[pid] != cid:
            failures.append(f"row {pid} sits in block {cid!r} but was computed into {pool_cluster[pid]!r}; "
                            "membership is never changed by hand")

    missing = sorted(coreset_ids - pool)
    if missing:
        failures.append(f"coreset papers missing from the pool: {missing}")

    for cid, alignment in clusters.items():
        r = roles[cid]
        shown = ", ".join(f"{k} {v}" for k, v in sorted(r.items())) or "no rows"
        gaps = [k for k in NEEDED.get(alignment, ()) if not r.get(k)]
        print(f"  {cid} [{alignment}]: pool {sum(1 for p in pool if pool_cluster.get(p) == cid)}; coreset {shown}"
              + (f"; missing {', '.join(gaps)}" if gaps else ""))
        lead, top = leaders(cid, pool, pool_cluster, indeg)
        if anchors[cid] and lead and not anchors[cid] & lead:
            notes.append(f"{cid}: anchor {sorted(anchors[cid])} is not the in-degree leader {sorted(lead)} ({top}); "
                         "fine if deliberate")

    out.update(roles=roles, bridges=bridges)
    return out


# --- output ---------------------------------------------------------------------------------------


def check_output(output, coreset_ids, abstract, layout, targets, failures, notes):
    out_ids = set(LINK.findall(output)) | set(BARE_ID.findall(output))
    print(f"output:  {len(out_ids)} cited IDs")
    if out_ids - coreset_ids:
        failures.append(f"cited in output but not in the coreset: {sorted(out_ids - coreset_ids)}")
    # A claim resting on an abstract-sourced row carries the marker next to
    # the paper's ID, every time it is cited (docs/formats.md, outputs).
    risky = sorted(out_ids & abstract)
    unmarked = {}
    for m in list(LINK.finditer(output)) + list(BARE_ID.finditer(output)):
        if m.group(1) in abstract and not MARKED.match(output, m.end()):
            unmarked.setdefault(m.group(1), []).append(output.count("\n", 0, m.start()) + 1)
    for aid, lines in sorted(unmarked.items()):
        failures.append(f"output cites abstract-sourced {aid} without an [abstract-only] marker "
                        f"(line {', '.join(map(str, sorted(set(lines))))})")
    # The reverse: a marker that follows no citation marks nothing. The legend before the first section is exempt.
    covered = {mk.end() for m in list(LINK.finditer(output)) + list(BARE_ID.finditer(output))
               if (mk := MARKED.match(output, m.end()))}
    body = output.find("\n## ")
    stray = sorted({output.count("\n", 0, m.start()) + 1 for m in re.finditer(r"\[abstract-only\]", output)
                    if m.end() not in covered and 0 <= body < m.start()})
    if stray and layout == "coreset":
        failures.append(f"output has an [abstract-only] marker that follows no cited paper ID (line "
                        f"{', '.join(map(str, stray))})")
    if risky and "[abstract-only]" not in output.split("\n## ")[0]:
        failures.append("output cites abstract-sourced papers but has no legend for [abstract-only] "
                        "before its first section")
    if risky:
        notes.append(f"{len(risky)} abstract-sourced paper(s) cited in the output: {risky}")
    if layout == "coreset":
        missing = [s for s in targets + ["Questions", "Reading"] if s not in sections(output)]
        if missing:
            failures.append(f"output lacks required section(s): {missing}: one per target, then Questions and Reading "
                            "(docs/formats.md, outputs)")
        absent = sorted({output.count("\n", 0, m.start()) + 1 for m in ABSENCE.finditer(output)})
        if absent:
            notes.append(f"output claims absence (line {', '.join(map(str, absent))}); only a probe supports that, and "
                         "an unrepresented connection is \"not represented in the coreset\"")


def main(argv):
    gate = argv[argv.index("--gate") + 1] if "--gate" in argv else None
    status = "--status" in argv
    args = [a for a in argv if not a.startswith("--") and a != gate]
    if len(args) != 1 or (gate is not None and not re.fullmatch(r"G[0-5]", gate)):
        print(__doc__.strip())
        return 2
    topic = args[0]
    survey = read(ROOT / "surveys" / f"{topic}.md")
    if survey is None:
        print(f"FAIL  surveys/{topic}.md does not exist")
        return 1
    bib = read(ROOT / "bib" / f"{topic}.bib")
    output = read(ROOT / "outputs" / f"{topic}.md")

    from inputs import read_input, read_targets
    dims, steering, problems = read_input(topic)
    targets, more = read_targets(topic)
    dims = dims or {}
    failures, notes = list(problems) + more, []
    secs = sections(survey)
    layout = "coreset" if "Clusters" in secs else "legacy"
    print(f"layout:  {layout}")
    # Without declared dimensions, the pass proposes them in its `Dimensions` line, which is then read the same way.
    proposed = layout == "coreset" and not dims
    if proposed:
        import gates
        entries = gates.log_entries(secs.get("Retrieval log", ""))
        dims = gates.proposed_dimensions(" ".join(entries[-1]["lines"].get("Dimensions", []))) if entries else {}
        if dims:
            print(f"dimensions: proposed in the log: {', '.join(dims)}")

    if layout == "coreset":
        found = [s for s in section_order(survey) if s in SURVEY_SECTIONS]
        if found != SURVEY_SECTIONS:
            failures.append(f"survey sections must be {SURVEY_SECTIONS}, in that order; found {found}")
    elif "Coreset" not in secs:
        print(f"FAIL  surveys/{topic}.md has no `## Coreset` section")
        return 1

    has_rows = any(h and h[0] == "paper" for h, _, _, _ in table_rows(secs.get("Coreset", "")))
    rows, coreset_ids, abstract = [], set(), set()
    if layout == "legacy" or has_rows:
        rows, coreset_ids, abstract = check_coreset(secs.get("Coreset", ""), dims, layout, failures, notes)

    structure = None
    if layout == "coreset" and "Clusters" in secs and "Pool" in secs:
        structure = check_structure(topic, secs, rows, coreset_ids, failures, notes)
    elif layout == "legacy":
        print("layout:  legacy (no Clusters section); cluster, role, pool and gate checks skipped")

    if rows:
        if bib is None:
            failures.append(f"bib/{topic}.bib does not exist; run `python3 tools/bib.py {topic}`")
        else:
            in_bib = set(bib_ids(bib))
            print(f"bib:     {len(in_bib)} entries")
            if coreset_ids - in_bib:
                failures.append(f"in coreset but not bib: {sorted(coreset_ids - in_bib)}")
            if in_bib - coreset_ids:
                failures.append(f"in bib but not coreset: {sorted(in_bib - coreset_ids)}")

    if output is not None:
        check_output(output, coreset_ids, abstract, layout, targets, failures, notes)

    if layout == "coreset":
        import gates
        ctx = gates.Ctx(topic, secs, structure, rows, coreset_ids, abstract, output, dims, steering, targets, proposed)
        g_fail, g_notes = gates.run(ctx, int(gate[1]) if gate else None, status)
        failures += g_fail
        notes += g_notes
        # Only now is every failure known: integrity, gates and history alike.
        if gate and not failures:
            notes.append(f"{gate} passed: add `{gate} <today>` to the log's `Gates` line")
    elif gate or status:
        failures.append("gates apply only to surveys in the coreset layout")

    print()
    for n in notes:
        print(f"note  {n}")
    if failures:
        for f in failures:
            print(f"FAIL  {f}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
