#!/usr/bin/env python3
"""Consistency check for one topic's pipeline artifacts.

Usage: python3 tools/check.py <topic>

Verifies, for surveys/<topic>.md, bib/<topic>.bib and outputs/<topic>.md:
  - the Coreset section has one row per unique arXiv ID, with a
    parsable `source` cell last and a consistent column count
  - declared dimension values are within their allowed sets
  - clusters, roles and the pool agree with each other (coreset surveys only)
  - coreset and bib contain the same IDs, in both directions
  - every arXiv ID cited in the output is in the coreset

It also prints notes that are not failures: per-cluster role coverage, anchors
that are not their cluster's in-degree leader, the `source` tally, and which
papers the output cites that are still `abstract`-sourced.

Surveys written before the coreset structure (no `## Clusters` section) get
only the checks that apply to them.

Exit status is 1 if any check fails, so it can gate a pass.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARXIV = re.compile(r"arxiv\.org/abs/(\d{4}\.\d{5})")
# Outputs cite papers as bare IDs inline (e.g. "(2504.13837)") rather than as
# links, so that prose stays readable. Match those too, or the output/survey
# cross-reference check silently passes by matching nothing.
BARE_ARXIV = re.compile(r"(?<![\w.])(\d{4}\.\d{5})(?:v\d+)?(?!\w|\.\d)")
EPRINT = re.compile(r"eprint\s*=\s*\{([0-9.]+)\}")
CLUSTER_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

DIMS = {
    "evidence": {"proven", "derived", "empirical", "fitted", "position"},
    "measures": {"capability", "faithfulness", "monitorability", "control-protocol", "n/a"},
    "elicitation": {"elicited", "observational", "spontaneous", "n/a"},
    "pressure": {"monitor-in-reward", "training-incidental", "prompt-level", "none", "n/a"},
}
ALIGNMENTS = {"high", "medium", "low"}
ROLES = {"anchor", "frontier", "dissent", "fringe"}
FRINGE_QUOTA = (5, 10)  # per topic, not per cluster
SOURCES = {"abstract", "snippet", "full-text"}


def read(path):
    return path.read_text() if path.exists() else None


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


def table_rows(text):
    """Yield (header_cells, row_cells, block_heading) for every table row."""
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
    m = ARXIV.search(line)
    return m.group(1) if m else None


def check_coreset(table, failures):
    """Checks that apply to any Coreset section, legacy or current."""
    rows = [(h, c, b, l) for h, c, b, l in table_rows(table) if h and h[0] == "paper"]
    ids = [row_id(l) for _, _, _, l in rows]
    unique = {i for i in ids if i}
    print(f"coreset: {len(rows)} rows, {len(unique)} unique arXiv IDs")
    if len(rows) != len(unique) or None in ids:
        failures.append(
            f"row count {len(rows)} != unique IDs {len(unique)} "
            "(duplicate row, or a row whose link is malformed)"
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
    bad = [row_id(l) for (_, c, _, l) in rows if c[-1] not in SOURCES]
    if bad or (rows and rows[0][0][-1] != "source"):
        failures.append(f"rows without a parsable `source` last column: {bad}")
    tally = {k: sources.count(k) for k in sorted(set(sources) & SOURCES)}
    print(f"source:  {tally}")

    header = rows[0][0] if rows else []
    present = [(i, n) for i, n in enumerate(header) if n in DIMS]
    for i, n in present:
        counts = {}
        for _, c, _, l in rows:
            v = c[i] if i < len(c) else ""
            counts[v] = counts.get(v, 0) + 1
            if v not in DIMS[n]:
                failures.append(f"row {row_id(l)}: {n}={v!r} is not an allowed value")
        shown = ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda t: -t[1]))
        print(f"{n + ':':13}{shown}")

    abstract = {row_id(l) for _, c, _, l in rows if c[-1] == "abstract"}
    return rows, unique, abstract


def check_structure(secs, rows, coreset_ids, failures, notes):
    """Checks for surveys using clusters, roles and a pool."""
    clusters = {}
    for h, c, _, _ in table_rows(secs["Clusters"]):
        if not h or h[0] != "id":
            continue
        cid, alignment = c[0], c[h.index("alignment")] if "alignment" in h else ""
        if not CLUSTER_ID.match(cid):
            failures.append(f"cluster id {cid!r} is not kebab-case")
        if cid in clusters:
            failures.append(f"cluster id {cid!r} is defined twice")
        if alignment not in ALIGNMENTS:
            failures.append(f"cluster {cid}: alignment {alignment!r} is not one of {sorted(ALIGNMENTS)}")
        clusters[cid] = alignment
    print(f"clusters: {len(clusters)} ({', '.join(f'{a} {list(clusters.values()).count(a)}' for a in ['high', 'medium', 'low'])})")

    header = rows[0][0] if rows else []
    if "role" not in header:
        failures.append("Coreset section has no `role` column")
        return
    ri = header.index("role")
    roles = {cid: {} for cid in clusters}
    anchors = {cid: set() for cid in clusters}
    for _, c, block, l in rows:
        cid = (block or "").split(" — ")[0].strip()
        if cid not in clusters:
            failures.append(f"block {block!r} is not headed by a known cluster id")
            continue
        role = c[ri]
        base, _, target = role.partition(":")
        if base == "bridge":
            if target not in clusters:
                failures.append(f"row {row_id(l)}: bridge target {target!r} is not a known cluster")
        elif role not in ROLES:
            failures.append(f"row {row_id(l)}: role {role!r} is not valid")
        roles[cid][base] = roles[cid].get(base, 0) + 1
        if role == "anchor":
            anchors[cid].add(row_id(l))

    pool, pool_cluster, cites = set(), {}, {}
    for h, c, _, l in table_rows(secs["Pool"]):
        if not h or h[0] != "paper":
            continue
        pid = row_id(l)
        if pid is None:
            failures.append(f"pool row with no arXiv link: {c[0][:60]!r}")
            continue
        if pid in pool:
            failures.append(f"pool lists {pid} twice")
        pool.add(pid)
        cl = c[h.index("cluster")] if "cluster" in h else ""
        if cl not in clusters:
            failures.append(f"pool {pid}: cluster {cl!r} is not a known cluster")
        pool_cluster[pid] = cl
        cites[pid] = set(BARE_ARXIV.findall(c[h.index("cites")])) if "cites" in h else set()
    print(f"pool:    {len(pool)} papers")
    missing = sorted(coreset_ids - pool)
    if missing:
        failures.append(f"coreset papers missing from the pool: {missing}")

    indeg = {p: 0 for p in pool}
    for p, cs in cites.items():
        for q in cs & pool:
            if q != p:
                indeg[q] += 1

    n_fringe = sum(r.get("fringe", 0) for r in roles.values())
    if not FRINGE_QUOTA[0] <= n_fringe <= FRINGE_QUOTA[1]:
        notes.append(f"{n_fringe} fringe row(s); the quota is {FRINGE_QUOTA[0]}-{FRINGE_QUOTA[1]} per topic")
    for cid, alignment in clusters.items():
        members = [p for p in pool if pool_cluster.get(p) == cid]
        r = roles[cid]
        shown = ", ".join(f"{k} {v}" for k, v in sorted(r.items())) or "empty"
        print(f"  {cid} [{alignment}]: pool {len(members)}; coreset {shown}")
        if alignment == "high":
            gaps = [k for k in ("anchor", "frontier", "dissent") if not r.get(k)]
            if gaps:
                notes.append(f"{cid} is high-alignment but has no {', '.join(gaps)}")
        if members and anchors[cid]:
            top = max(indeg[p] for p in members)
            leaders = {p for p in members if indeg[p] == top}
            if top > 0 and not anchors[cid] & leaders:
                notes.append(
                    f"{cid}: anchor {sorted(anchors[cid])} is not the in-degree leader "
                    f"{sorted(leaders)} ({top}); fine if deliberate"
                )


def main(topic):
    survey = read(ROOT / "surveys" / f"{topic}.md")
    if survey is None:
        print(f"FAIL  surveys/{topic}.md does not exist")
        return 1
    bib = read(ROOT / "bib" / f"{topic}.bib")
    output = read(ROOT / "outputs" / f"{topic}.md")

    failures, notes = [], []
    secs = sections(survey)
    if "Coreset" not in secs:
        print(f"FAIL  surveys/{topic}.md has no `## Coreset` section")
        return 1

    rows, coreset_ids, abstract = check_coreset(secs["Coreset"], failures)

    if "Clusters" in secs:
        for needed in ("Pool", "Open work"):
            if needed not in secs:
                failures.append(f"coreset survey has no `## {needed}` section")
        if "Pool" in secs:
            check_structure(secs, rows, coreset_ids, failures, notes)
    else:
        print("layout:  legacy (no Clusters section); cluster, role and pool checks skipped")

    if bib is None:
        failures.append(f"bib/{topic}.bib does not exist")
    else:
        bib_ids = set(EPRINT.findall(bib))
        print(f"bib:     {len(bib_ids)} entries")
        if coreset_ids - bib_ids:
            failures.append(f"in coreset but not bib: {sorted(coreset_ids - bib_ids)}")
        if bib_ids - coreset_ids:
            failures.append(f"in bib but not coreset: {sorted(bib_ids - coreset_ids)}")

    if output is None:
        print("output:  not written yet")
    else:
        out_ids = set(ARXIV.findall(output)) | set(BARE_ARXIV.findall(output))
        print(f"output:  {len(out_ids)} cited IDs")
        if out_ids - coreset_ids:
            failures.append(f"cited in output but not in the coreset: {sorted(out_ids - coreset_ids)}")
        # Load-bearing claims must not rest on abstract-only rows. We cannot
        # tell which claims are load-bearing, so surface the overlap for a
        # human to judge.
        risky = sorted(out_ids & abstract)
        if risky:
            notes.append(
                f"{len(risky)} paper(s) cited in the output are still abstract-sourced: {risky}; "
                "each needs an explicit provisional marker"
            )

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
    if len(sys.argv) != 2:
        print(__doc__.strip())
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
