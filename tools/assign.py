# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scikit-learn", "igraph", "leidenalg"]
# ///
"""Write pool papers and their clusters into the survey's Pool table, by script rather than by hand.

Usage:
  python3 tools/assign.py add <topic> <paper-id> [<paper-id> ...]
  python3 tools/assign.py add-fringe <topic>
  python3 tools/assign.py clusters <topic>
  uv run tools/assign.py late <topic>
  python3 tools/assign.py remap <topic>
  python3 tools/assign.py reject <topic> <paper-id> <reason ...>

add         Adds papers to the Pool table by canonical ID (docs/formats.md, "Paper IDs"): an arXiv ID, or CorpusId:<n>
            for a paper without one. Each row is a title linked by its ID, with the other cells empty. Titles come
            from Semantic Scholar; a paper it does not know, or one without a SPECTER2 embedding, which clustering
            needs, cannot enter the pool yet, and is listed for Open work. A
            CorpusId whose paper has an arXiv ID is refused, with the arXiv ID to use instead. Run tools/pool.py
            afterwards for `year`, `citations` and `cites`.
add-fringe  Adds the candidates marked `yes` in graphs/<topic>/fringe-screen.md (end of step 2), each by its arXiv ID
            or, failing that, its CorpusId, and prints the log's `Fringe` line. It refuses while any candidate is
            still unjudged.
clusters    Writes each pool paper's computed cluster (graphs/<topic>/clusters.json) into the Pool `cluster` column,
            under the name the Clusters table's `computed` column gives it. Run after naming (step 3), and after any
            recluster and remap. Membership is never written by hand.
late        Processes the late papers as one batch (docs/process.md, "Late papers"): pool papers added after the last
            full clustering. Fetches their data (tools/pool.py), assigns each to the cluster most common among its k
            nearest clustered papers under the chosen measure, records the assignment in clusters.json, writes the Pool
            column, and prints the log's `Late papers` line. Each paper is assigned against the clustering as it
            stood, never against other late papers, so the result does not depend on order. If late papers would
            exceed 10% of the pool, it assigns nothing and exits 3: rerun tools/cluster.py instead.
remap       After a recluster, moves each named cluster's `computed` id to the new cluster it matched (clusters.json,
            `previous`), clears the ids of clusters that did not match, and lists new clusters still to be named.
            Until it has run, `clusters` refuses, so that old names cannot land on new clusters.
reject      Records a candidate screened out of scope, with a one-line reason, in graphs/<topic>/rejected.md: the trace
            of a judgement that would otherwise leave none (docs/gates.md). Used in steps 1 and 2 and in targeted
            expansions; the fringe routes record theirs on their own sheet. Refuses a paper already in the pool.

Calls to Semantic Scholar are unauthenticated; no key or user identifier is sent.
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from check import ID, arxiv_of, cells_of, link, row_id, s2_ref, sections, table_rows  # noqa: E402

LATE_SHARE = 0.1  # late papers since the last full clustering, as a share of the pool, above which to recluster
POOL_HEADER = "| paper | year | cluster | citations | cites |\n| -- | -- | -- | -- | -- |\n"
S2_TITLES = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,externalIds,openAccessPdf"
S2_ADD = S2_TITLES + ",embedding.specter_v2"


def survey_path(topic):
    return ROOT / "surveys" / f"{topic}.md"


def topic_dir(topic):
    return ROOT / "graphs" / topic


def section_span(lines, name):
    """The (start, end) line indices of a `## name` section's body."""
    start = next((i + 1 for i, l in enumerate(lines) if l.rstrip("\n") == f"## {name}"), None)
    if start is None:
        sys.exit(f"the survey has no `## {name}` section")
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start, end


def rewrite_column(topic, section, key_col, column, values):
    """Set `column` in a section's table to values[key] for each row, keyed by `key_col` (or the row's arXiv ID)."""
    path = survey_path(topic)
    lines = path.read_text().splitlines(keepends=True)
    start, end = section_span(lines, section)
    header, changed = None, 0
    for i in range(start, end):
        line = lines[i]
        if not line.startswith("|"):
            header = None
            continue
        if header is None:
            header = cells_of(line.rstrip("\n"))
            if column not in header:
                sys.exit(f"the {section} table has no `{column}` column")
            continue
        if line.startswith("| --") or line.startswith("|--"):
            continue
        cells = cells_of(line.rstrip("\n"))
        key = row_id(line) if key_col is None else cells[header.index(key_col)]
        if key in values and cells[header.index(column)] != values[key]:
            cells[header.index(column)] = values[key]
            lines[i] = "| " + " | ".join(c.replace("\0", "\\|") for c in cells) + " |\n"
            changed += 1
    if changed:
        path.write_text("".join(lines))
    return changed


def pool_ids(topic):
    secs = sections(survey_path(topic).read_text())
    return [row_id(l) for h, _, _, l in table_rows(secs.get("Pool", "")) if h and h[0] == "paper" and row_id(l)]


def name_map(topic):
    """{computed id: named id}, from the Clusters table's `computed` column."""
    secs = sections(survey_path(topic).read_text())
    out = {}
    for h, c, _, _ in table_rows(secs.get("Clusters", "")):
        if h and h[0] == "id" and "computed" in h and c[h.index("computed")]:
            out[c[h.index("computed")]] = c[0]
    return out


def load_report(topic):
    path = topic_dir(topic) / "clusters.json"
    if not path.exists():
        sys.exit(f"no {path.relative_to(ROOT)}; run `uv run tools/cluster.py {topic}` first")
    return path, json.loads(path.read_text())


# --- add ------------------------------------------------------------------------------------------


def append_pool_rows(topic, titled):
    """Append rows for {arxiv id: title} not already in the Pool table. Returns the IDs added."""
    have = set(pool_ids(topic))
    new = [(a, t) for a, t in titled.items() if a not in have]
    if not new:
        return []
    path = survey_path(topic)
    lines = path.read_text().splitlines(keepends=True)
    start, end = section_span(lines, "Pool")
    rows = "".join(
        f"| [{t.replace('|', '/').replace('[', '(').replace(']', ')')}]({link(a)}) |  |  |  |  |\n"
        for a, t in new)
    if not any(l.startswith("|") for l in lines[start:end]):
        lines[start:start] = ["\n", POOL_HEADER, rows]
    else:
        last = max(i for i in range(start, end) if lines[i].startswith("|"))
        lines[last + 1:last + 1] = [rows]
    path.write_text("".join(lines))
    return [a for a, _ in new]


def add(topic, ids):
    from net import get_json
    bad = [a for a in ids if not ID.match(a)]
    if bad or not ids:
        sys.exit(f"expected paper IDs such as 2408.03314, hep-th/9901001 or CorpusId:6628106; got {bad or 'none'}")
    titled, unknown, has_arxiv, no_embedding = {}, [], {}, []
    for i in range(0, len(ids), 100):
        batch = ids[i:i + 100]
        for a, rec in zip(batch, get_json(S2_ADD, {"ids": [s2_ref(x) for x in batch]})):
            if not (rec and rec.get("title")):
                unknown.append(a)
            elif not (rec.get("embedding") or {}).get("vector"):
                no_embedding.append(a)
            elif a.startswith("CorpusId:") and arxiv_of(rec):
                has_arxiv[a] = arxiv_of(rec)
            else:
                titled[a] = " ".join(rec["title"].split())
    added = append_pool_rows(topic, titled)
    print(f"added {len(added)} paper(s) to the Pool table; {len(titled) - len(added)} already there")
    if unknown:
        print(f"not in Semantic Scholar, so not added; record them in Open work: {unknown}")
    if no_embedding:
        print(f"no SPECTER2 embedding, so they cannot be clustered and were not added; record them in Open work: "
              f"{no_embedding}")
    if has_arxiv:
        print("these have an arXiv ID, which is their canonical ID; add them by it instead: "
              + ", ".join(f"{a} -> {x}" for a, x in has_arxiv.items()))
    if added:
        print(f"next: `python3 tools/pool.py {topic}`")
    return 0


def add_fringe(topic):
    d = topic_dir(topic)
    data = json.loads((d / "fringe.json").read_text())
    cands = data["candidates"]
    screened = {}
    for h, c, _, _ in table_rows((d / "fringe-screen.md").read_text()):
        if h and h[0] == "s2":
            screened[c[0]] = c[h.index("in scope")].strip().lower()
    blank = [s for s, v in screened.items() if not v]
    if blank:
        sys.exit(f"{len(blank)} candidate(s) in fringe-screen.md have no `in scope` judgement yet")
    yes = [s for s, v in screened.items() if v.startswith("yes")]
    # The canonical ID: the arXiv ID where there is one, otherwise the corpus ID (docs/formats.md).
    missing = [s for s in yes if not cands[s].get("arxiv")]
    if missing:
        from net import get_json
        for s, rec in zip(missing, get_json(S2_TITLES, {"ids": missing})):
            if arxiv_of(rec):
                cands[s]["arxiv"] = arxiv_of(rec)
            elif rec and (rec.get("externalIds") or {}).get("CorpusId"):
                cands[s]["corpus"] = f"CorpusId:{rec['externalIds']['CorpusId']}"
        # Keep the resolved IDs, so that tools/check.py can find every in-scope candidate in the pool.
        (d / "fringe.json").write_text(json.dumps(data, separators=(",", ":")))
    titled = {cands[s].get("arxiv") or cands[s].get("corpus"): cands[s]["title"] for s in yes
              if cands[s].get("arxiv") or cands[s].get("corpus")}
    no_id = [s for s in yes if not (cands[s].get("arxiv") or cands[s].get("corpus"))]
    added = append_pool_rows(topic, titled)
    routes = {r: sum(1 for x in cands.values() if r in x["routes"]) for r in ("hidden", "new")}
    print(f"added {len(added)} candidate(s) to the Pool table")
    if no_id:
        print(f"in scope but without an arXiv or corpus ID, so not added; record them in Open work: {no_id}")
    print("\nlog line:")
    print(f"- **Fringe:** collected {data['collected']}: hidden {routes['hidden']}, new {routes['new']} candidates "
          f"({len(cands)} unique); in scope {len(yes)}; added to the pool {len(added)}, of which "
          f"{sum(1 for a in added if a.startswith('CorpusId:'))} without an arXiv ID; left out {len(no_id)}")
    if added:
        print(f"\nnext: `python3 tools/pool.py {topic}`")
    return 0


# --- clusters, late, remap ------------------------------------------------------------------------


def write_clusters(topic):
    _, report = load_report(topic)
    if report.get("previous") and not report["previous"].get("remapped") and name_map(topic):
        print(f"FAIL  clusters.json is a new clustering whose names have not been carried over; run "
              f"`python3 tools/assign.py remap {topic}` first, or the old names would land on the new clusters")
        return 1
    names = name_map(topic)
    assigned = dict(report["assignment"])
    assigned.update({p: x["cluster"] for p, x in report.get("late", {}).items()})
    unnamed = sorted(set(assigned.values()) - set(names))
    if unnamed:
        print(f"FAIL  computed cluster(s) {unnamed} have no row in the Clusters table (`computed` column); name them "
              "first (docs/process.md, step 3)")
        return 1
    values = {p: names[c] for p, c in assigned.items()}
    changed = rewrite_column(topic, "Pool", None, "cluster", values)
    waiting = sorted(set(pool_ids(topic)) - set(assigned))
    print(f"Pool table: {changed} `cluster` cell(s) written")
    if waiting:
        print(f"late papers awaiting assignment ({len(waiting)}): {waiting}; run `uv run tools/assign.py late {topic}`")
    return 0


def late(topic):
    import numpy as np
    import pool
    from cluster import combined_sim, refs_sim, text_sim

    pool.main([topic])
    path, report = load_report(topic)
    cache = json.loads((topic_dir(topic) / "pool.json").read_text())["papers"]
    done = set(report["assignment"]) | set(report.get("late", {}))
    members = pool_ids(topic)
    queue = [p for p in members if p not in done]
    missing = [p for p in queue if not (cache.get(p) or {}).get("embedding")]
    queue = [p for p in queue if p not in missing]
    if missing:
        print(f"no Semantic Scholar data for {missing}; they stay unassigned (record them in Open work)")
    if not queue:
        print("no late papers to assign")
        return 0
    share = (len(report.get("late", {})) + len(queue)) / len(members)
    if share > LATE_SHARE:
        print(f"RECLUSTER: late papers since the last full clustering would be {share:.0%} of the pool, above "
              f"{LATE_SHARE:.0%}: rerun `uv run tools/cluster.py {topic}` instead, then "
              f"`python3 tools/assign.py remap {topic}`")
        return 3

    base = report["ids"]
    recs = [cache[a] for a in base] + [cache[a] for a in queue]
    k, c, measure = report["params"]["k"], report["params"]["c"], report["measure"]
    T = text_sim(recs)
    S = T if measure == "text" else refs_sim(recs) if measure == "refs" else combined_sim(T, refs_sim(recs), recs, c)
    n = len(base)
    labels = [report["assignment"][a] for a in base]
    late_rec, today = report.setdefault("late", {}), time.strftime("%Y-%m-%d")
    names = name_map(topic)
    shown = []
    for j, a in enumerate(queue):
        row = S[n + j, :n]
        if not np.any(row > 0):  # e.g. no shared references at all under `refs`: fall back on text
            row = T[n + j, :n]
        votes = {}
        for i in np.argsort(row)[::-1][:k]:
            votes[labels[i]] = votes.get(labels[i], 0.0) + float(max(row[i], 0.0))
        best = sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        late_rec[a] = {"cluster": best, "assigned": today, "votes": {x: round(v, 3) for x, v in votes.items()}}
        shown.append(f"{a} -> {names.get(best, best)}")
    path.write_text(json.dumps(report, indent=1))
    status = write_clusters(topic)
    print("\nlog line:")
    print(f"- **Late papers:** {today}: {len(queue)} assigned to their nearest cluster ({', '.join(shown)}); late "
          f"since the last full clustering: {len(late_rec)} of {len(members)} ({len(late_rec) / len(members):.0%})")
    return status


def remap(topic):
    path, report = load_report(topic)
    prev = report.get("previous")
    if not prev:
        sys.exit("clusters.json has no `previous` clustering to match against; nothing to remap")
    if prev.get("remapped"):
        sys.exit("already remapped after this clustering")
    names = name_map(topic)
    carry = {}
    for b, x in prev["new"].items():
        if x["case"] == "matched":
            carry[x["from"][0]] = b
    values, lost = {}, []
    for old, named in names.items():
        if old in carry:
            values[named] = carry[old]
        else:
            values[named] = ""
            lost.append(f"{named} (was {old}: {prev['old'].get(old, {}).get('case', 'unknown')})")
    changed = rewrite_column(topic, "Clusters", "id", "computed", values)
    prev["remapped"] = True
    path.write_text(json.dumps(report, indent=1))
    unnamed = sorted(set(report["assignment"].values()) - set(carry.values()), key=lambda x: int(x[1:]))
    print(f"Clusters table: {changed} `computed` id(s) updated")
    if lost:
        print("did not match a new cluster, so their `computed` is cleared; retire, merge or rename them, and log it: "
              + "; ".join(lost))
    if unnamed:
        print("new clusters to name (add a Clusters row with their `computed` id): "
              + ", ".join(f"{b} ({prev['new'][b]['case']})" for b in unnamed))
    print(f"then: `python3 tools/assign.py clusters {topic}`")
    return 0


REJECTED_HEADER = """# Rejected candidates: {topic}

Candidates screened out of scope in orientation, expansion and targeted expansions, one row per judgement, written by
`tools/assign.py reject`. The fringe routes' judgements are in `fringe-screen.md`. See docs/gates.md.

| paper | date | reason |
| -- | -- | -- |
"""


def reject(topic, pid, reason):
    if not ID.match(pid):
        sys.exit(f"{pid!r} is not a canonical paper ID (docs/formats.md, \"Paper IDs\")")
    reason = " ".join(reason).replace("|", "/").strip()
    if not reason:
        sys.exit("give a one-line reason")
    pool = {row_id(l) for h, _, _, l in table_rows(sections(survey_path(topic).read_text()).get("Pool", ""))
            if h and h[0] == "paper"}
    if pid in pool:
        sys.exit(f"{pid} is in the pool; a paper leaves the pool only with the user's permission (H12)")
    path = topic_dir(topic) / "rejected.md"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(REJECTED_HEADER.format(topic=topic))
    today = time.strftime("%Y-%m-%d")
    text = path.read_text()
    if any(c[0].startswith(f"[{pid}]") and c[1] == today for h, c, _, _ in table_rows(text) if h and h[0] == "paper"):
        print(f"{pid} is already recorded as rejected today")
        return 0
    path.write_text(text.rstrip("\n") + f"\n| [{pid}]({link(pid)}) | {today} | {reason} |\n")
    print(f"recorded {pid} as out of scope in {path.relative_to(ROOT)}")
    return 0


def main(argv):
    commands = {"add": lambda t: add(t, argv[2:]), "add-fringe": add_fringe, "clusters": write_clusters,
                "late": late, "remap": remap, "reject": lambda t: reject(t, argv[2], argv[3:])}
    if argv and argv[0] == "reject" and len(argv) < 4:
        print(__doc__.strip())
        return 2
    if len(argv) < 2 or argv[0] not in commands or (argv[0] not in ("add", "reject") and len(argv) != 2):
        print(__doc__.strip())
        return 2
    return commands[argv[0]](argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
