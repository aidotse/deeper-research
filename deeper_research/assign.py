"""Write pool papers and their clusters into the survey's Pool table, by script rather than by hand.

Usage:
  uv run python -m deeper_research.assign add <topic> <paper-id> [<paper-id> ...]
  uv run python -m deeper_research.assign add-expand <topic>
  uv run python -m deeper_research.assign add-fringe <topic>
  uv run python -m deeper_research.assign clusters <topic>
  uv run python -m deeper_research.assign late <topic>
  uv run python -m deeper_research.assign remap <topic>
  uv run python -m deeper_research.assign reject <topic> <paper-id> <reason ...>
  uv run python -m deeper_research.assign reject <topic> < lines          (one `<paper-id><TAB><reason>` per line)

add         Adds papers to the Pool table by canonical ID (docs/formats.md, "Paper IDs"): an arXiv ID, or CorpusId:<n>
            for a paper without one. Each row is a title linked by its ID, with the other cells empty. Titles come
            from Semantic Scholar; a paper it does not know, or one without a SPECTER2 embedding, which clustering
            needs, cannot enter the pool yet, and is listed for Open work. A
            CorpusId whose paper has an arXiv ID is refused, with the arXiv ID to use instead. A paper already in
            graphs/<topic>/rejected.md is added, with a warning that names the rejection. Afterwards the main session
            runs deeper_research/pool.py (before step 3) or `assign.py late` (after it), for `year`, `citations` and
            `cites`, and pastes the `Pool` line it prints.
add-expand  Adds the candidates marked `yes` in graphs/<topic>/expand-screen.md (step 2, and each targeted expansion),
            each by its arXiv ID or, failing that, its CorpusId, and records each `no` in rejected.md with the
            sheet's reason. Prints the log's `Expansion` line. It refuses while any row is unjudged. A `no` for a
            paper now in the pool is listed as a conflict, not recorded. Rerun after more rows are judged, it adds
            only what is new.
add-fringe  Adds the candidates marked `yes` in graphs/<topic>/fringe-screen.md (end of step 2), each by its arXiv ID
            or, failing that, its CorpusId, and prints the log's `Fringe` line. It refuses while any candidate is
            still unjudged, that is, marked neither `yes` nor `no`. It warns, as `add` does, on a rejected paper.
clusters    Writes each pool paper's computed cluster (graphs/<topic>/clusters.json) into the Pool `cluster` column,
            under the name the Clusters table's `computed` column gives it. Run after naming (step 3), and after any
            recluster and remap. Membership is never written by hand.
late        Processes the late papers as one batch (docs/process.md, "Late papers"): pool papers added after the last
            full clustering. Fetches their data (deeper_research/pool.py), assigns each to the cluster its k nearest
            clustered papers favour under the `combined` measure, each voting with its similarity (by text, for a paper
            with no positive similarity under that measure), records the assignment in clusters.json, writes the Pool
            column, and prints the log's `Late papers` line. Each paper is assigned against the clustering as it
            stood, never against other late papers, so the result does not depend on order. If late papers would
            exceed 10% of the pool, it assigns nothing and exits 3: rerun deeper_research/cluster.py instead.
remap       After a recluster, moves each named cluster's `computed` id to the new cluster it matched (clusters.json,
            `previous`), clears the ids of clusters that did not match, and lists new clusters still to be named.
            Until it has run, `clusters` refuses, so that old names cannot land on new clusters.
reject      Records a candidate screened out of scope, with a one-line reason, in graphs/<topic>/rejected.md: the trace
            of a judgement that would otherwise leave none (docs/gates.md). Used in orientation (step 1); expansion
            judges on its sheet, and add-expand copies its rejections here; the fringe routes keep theirs on their own
            sheet. Refuses a paper already in the pool.
            Without a paper ID, it reads one `<paper-id><TAB><reason>` per line from stdin, and records them all or,
            if any line is wrong, none.

Calls to Semantic Scholar are unauthenticated; no key or user identifier is sent.
"""

import json
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from deeper_research.check import ID, arxiv_of, cells_of, link, row_id, s2_ref, sections, table_rows
from deeper_research.screen import judged, pool_titles, title_key, verdicts

ROOT = Path(__file__).resolve().parent.parent

LATE_SHARE = 0.1  # late papers since the last full clustering, as a share of the pool, above which to recluster
POOL_HEADER = "| paper | year | cluster | citations | cites |\n| -- | -- | -- | -- | -- |\n"
S2_TITLES = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,externalIds,openAccessPdf"
S2_ADD = S2_TITLES + ",embedding.specter_v2"


def survey_path(topic: str) -> Path:
    """The topic's survey, surveys/<topic>.md."""
    return ROOT / "surveys" / f"{topic}.md"


def topic_dir(topic: str) -> Path:
    """The topic's directory of derived data, graphs/<topic>."""
    return ROOT / "graphs" / topic


def section_span(lines: list[str], name: str) -> tuple[int, int]:
    """The (start, end) line indices of a `## name` section's body."""
    start = next((i + 1 for i, line in enumerate(lines) if line.rstrip("\n") == f"## {name}"), None)
    if start is None:
        sys.exit(f"the survey has no `## {name}` section")
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start, end


def rewrite_column(topic: str, section: str, key_col: str | None, column: str, values: dict[str, str]) -> int:
    """Set `column` in a section's table to values[key] for each row, keyed by `key_col` (or the row's arXiv ID)."""
    path = survey_path(topic)
    lines = path.read_text().splitlines(keepends=True)
    start, end = section_span(lines, section)
    header: list[str] | None
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
        if line.startswith(("| --", "|--")):
            continue
        cells = cells_of(line.rstrip("\n"))
        # A row without a paper link has no key: None, which is in no `values`.
        key = cast("str", row_id(line)) if key_col is None else cells[header.index(key_col)]
        if key in values and cells[header.index(column)] != values[key]:
            cells[header.index(column)] = values[key]
            lines[i] = "| " + " | ".join(c.replace("\0", "\\|") for c in cells) + " |\n"
            changed += 1
    if changed:
        path.write_text("".join(lines))
    return changed


def pool_ids(topic: str) -> list[str]:
    """The IDs of the papers in the survey's Pool table, in table order."""
    secs = sections(survey_path(topic).read_text())
    return cast(
        "list[str]",
        [row_id(line) for h, _, _, line in table_rows(secs.get("Pool", "")) if h and h[0] == "paper" and row_id(line)],
    )


def name_map(topic: str) -> dict[str, str]:
    """{computed id: named id}, from the Clusters table's `computed` column."""
    secs = sections(survey_path(topic).read_text())
    out = {}
    for h, c, _, _ in table_rows(secs.get("Clusters", "")):
        if h and h[0] == "id" and "computed" in h and c[h.index("computed")]:
            out[c[h.index("computed")]] = c[0]
    return out


def load_report(topic: str) -> tuple[Path, dict[str, Any]]:
    """(path, contents) of graphs/<topic>/clusters.json; exits if there is none yet."""
    path = topic_dir(topic) / "clusters.json"
    if not path.exists():
        sys.exit(f"no {path.relative_to(ROOT)}; run `uv run python -m deeper_research.cluster {topic}` first")
    return path, json.loads(path.read_text())


def rejected(topic: str) -> dict[str, tuple[str, str]]:
    """{paper id: (date, reason)} from graphs/<topic>/rejected.md, the latest rejection of each paper."""
    path = topic_dir(topic) / "rejected.md"
    if not path.exists():
        return {}
    return {
        cast("str", row_id(line)): (c[1], c[2])
        for h, c, _, line in table_rows(path.read_text())
        if h and h[0] == "paper" and row_id(line) and len(c) >= 3
    }


def warn_rejected(topic: str, added: list[str]) -> None:
    """Name each added paper that an earlier screening rejected: two opposite verdicts on record need reconciling."""
    rej = rejected(topic)
    hit = [a for a in added if a in rej]
    if hit:
        print(
            f"WARNING: {len(hit)} added paper(s) were rejected earlier (graphs/{topic}/rejected.md), so the record "
            "now holds two opposite verdicts; say in the log which one stands and why: "
            + "; ".join(f"{a} (rejected {rej[a][0]}: {rej[a][1]})" for a in hit)
        )


def next_step(topic: str) -> str:
    """What the main session runs next, after papers were added: the line to print."""
    return (
        f"next, for the main session: `uv run python -m deeper_research.pool {topic}` before clustering (step 3), or "
        f"`uv run python -m deeper_research.assign late {topic}` after it; paste the `Pool` line it prints into the log"
    )


# --- add ------------------------------------------------------------------------------------------


def append_pool_rows(topic: str, titled: dict[str, str]) -> list[str]:
    """Append rows for {arxiv id: title} not already in the Pool table. Returns the IDs added."""
    have = set(pool_ids(topic))
    new = [(a, t) for a, t in titled.items() if a not in have]
    if not new:
        return []
    path = survey_path(topic)
    lines = path.read_text().splitlines(keepends=True)
    start, end = section_span(lines, "Pool")
    rows = "".join(
        f"| [{t.replace('|', '/').replace('[', '(').replace(']', ')')}]({link(a)}) |  |  |  |  |\n" for a, t in new
    )
    if not any(line.startswith("|") for line in lines[start:end]):
        lines[start:start] = ["\n", POOL_HEADER, rows]
    else:
        last = max(i for i in range(start, end) if lines[i].startswith("|"))
        lines[last + 1 : last + 1] = [rows]
    path.write_text("".join(lines))
    return [a for a, _ in new]


def add(topic: str, ids: list[str]) -> int:  # noqa: C901
    """Add papers to the Pool table by canonical ID, titled from Semantic Scholar; returns the exit status."""
    # local: looked up at call time, so that a replacement of net.get_json (the behaviour tests' fake) is used
    from deeper_research.net import get_json  # noqa: PLC0415

    bad = [a for a in ids if not ID.match(a)]
    if bad or not ids:
        print(
            f"expected paper IDs such as 2408.03314, hep-th/9901001 or CorpusId:6628106; got {bad or 'none'}",
            file=sys.stderr,
        )
        return 2
    titled: dict[str, str]
    unknown: list[str]
    has_arxiv: dict[str, str | None]
    no_embedding: list[str]
    titled, unknown, has_arxiv, no_embedding = {}, [], {}, []
    for i in range(0, len(ids), 100):
        batch = ids[i : i + 100]
        for a, rec in zip(batch, get_json(S2_ADD, {"ids": [s2_ref(x) for x in batch]}), strict=False):
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
        print(
            f"no SPECTER2 embedding, so they cannot be clustered and were not added; record them in Open work: "
            f"{no_embedding}"
        )
    if has_arxiv:
        print(
            "these have an arXiv ID, which is their canonical ID; add them by it instead: "
            + ", ".join(f"{a} -> {x}" for a, x in has_arxiv.items())
        )
    warn_rejected(topic, added)
    if added:
        print(next_step(topic))
    return 0


def add_expand(topic: str) -> int:
    """Add the expansion sheet's `yes` candidates to the pool and record its `no`s; returns the exit status."""
    # local: import cycle with expand
    from deeper_research.expand import canonical, expansion_line, latest_entry, pass_candidates  # noqa: PLC0415

    d = topic_dir(topic)
    for name in ("expand.json", "expand-screen.md"):
        if not (d / name).exists():
            sys.exit(
                f"no graphs/{topic}/{name}; run `uv run python -m deeper_research.expand collect {topic}` first, then "
                "have the candidates screened"
            )
    data = json.loads((d / "expand.json").read_text())
    since = latest_entry(topic)[0]
    cands, said = data["candidates"], verdicts((d / "expand-screen.md").read_text())
    unknown = [s for s in said if s not in cands]
    if unknown:
        sys.exit(f"{len(unknown)} row(s) of expand-screen.md are not in expand.json: {unknown[:3]}")
    # Only this pass's candidates: an earlier pass's verdicts were acted on then, and the user may since have changed
    # the pool (H12).
    mine = pass_candidates(data, since)
    absent = [s for s in mine if s not in said]
    if absent:
        sys.exit(
            f"{len(absent)} candidate(s) in expand.json have no row in expand-screen.md: {absent[:3]}; rerun "
            f"`uv run python -m deeper_research.expand collect {topic}` with the same arguments, which restores "
            "missing rows"
        )
    blank = [s for s in mine if not judged(*said[s])]
    if blank:
        sys.exit(
            f"{len(blank)} row(s) of expand-screen.md have no `yes` or `no` judgement with a reason of at least two "
            "words yet"
        )
    pool, titles = set(pool_ids(topic)), pool_titles(topic)
    yes = [s for s in mine if said[s][0].startswith("yes")]
    no = [s for s in mine if said[s][0].startswith("no")]
    there = [s for s in yes if canonical(cands[s]) in pool or title_key(cands[s]["title"]) in titles]
    no_id = [s for s in yes if not canonical(cands[s])]
    ids = cast("list[str]", [canonical(cands[s]) for s in yes if s not in there and canonical(cands[s])])
    if ids:
        add(topic, ids)  # fetches each paper's record, and refuses one without a SPECTER2 embedding
    print(f"{len(there)} in-scope candidate(s) already in the pool")
    if no_id:
        print(f"in scope but without an arXiv or corpus ID, so not added; record them in Open work: {no_id}")
    pool, rej = set(pool_ids(topic)), rejected(topic)
    conflict = [canonical(cands[s]) for s in no if canonical(cands[s]) in pool]
    _, recorded, _ = write_rejections(
        topic,
        cast(
            "list[tuple[str, str]]",
            [
                (canonical(cands[s]), said[s][1])
                for s in no
                if canonical(cands[s]) and canonical(cands[s]) not in pool | set(rej)
            ],
        ),
    )
    print(f"recorded {len(recorded)} rejection(s) in graphs/{topic}/rejected.md")
    if conflict:
        print(
            f"judged `no` on the sheet but in the pool, so not recorded as rejected: {conflict}; one verdict is wrong: "
            f"re-judge the row with `uv run python -m deeper_research.expand judge {topic}`, or ask the user to take "
            "the paper out of the pool (H12)"
        )
    print("\nlog line, in place of any earlier `Expansion` line of this pass:")
    print(expansion_line(data, said, since))
    return 0


def add_fringe(topic: str) -> int:  # noqa: C901
    """Add the fringe sheet's `yes` candidates to the Pool table; returns the exit status."""
    d = topic_dir(topic)
    for name in ("fringe.json", "fringe-screen.md"):
        if not (d / name).exists():
            sys.exit(
                f"no graphs/{topic}/{name}; run `uv run python -m deeper_research.fringe collect {topic}` first, then "
                "have the candidates screened"
            )
    data = json.loads((d / "fringe.json").read_text())
    cands = data["candidates"]

    rows = verdicts((d / "fringe-screen.md").read_text())
    screened = {s: v for s, (v, _) in rows.items()}
    # The gate's own test (G1, fringe-screened): `yes` or `no` with a reason; blank or `maybe` is unjudged.
    blank = [s for s, (v, r) in rows.items() if not judged(v, r)]
    if blank:
        sys.exit(f"{len(blank)} candidate(s) in fringe-screen.md have no `yes` or `no` judgement with a reason yet")
    absent = [s for s in cands if s not in rows]
    if absent:
        sys.exit(f"{len(absent)} candidate(s) in fringe.json have no row in fringe-screen.md: {absent[:3]}")
    unknown = [s for s in screened if s not in cands]
    if unknown:
        sys.exit(
            f"{len(unknown)} row(s) of fringe-screen.md are not in fringe.json: {unknown[:3]}; rerun "
            f"`uv run python -m deeper_research.fringe collect {topic}`, which keeps the judgements already on the "
            "sheet"
        )
    yes = [s for s, v in screened.items() if v.startswith("yes")]
    # The canonical ID: the arXiv ID where there is one, otherwise the corpus ID (docs/formats.md).
    missing = [s for s in yes if not cands[s].get("arxiv")]
    if missing:
        # local: looked up at call time, so that a replacement of net.get_json (the behaviour tests' fake) is used
        from deeper_research.net import get_json  # noqa: PLC0415

        for s, rec in zip(missing, get_json(S2_TITLES, {"ids": missing}), strict=False):
            if arxiv_of(rec):
                cands[s]["arxiv"] = arxiv_of(rec)
            elif rec and (rec.get("externalIds") or {}).get("CorpusId"):
                cands[s]["corpus"] = f"CorpusId:{rec['externalIds']['CorpusId']}"
        # Keep the resolved IDs, so that deeper_research/check.py can find every in-scope candidate in the pool.
        (d / "fringe.json").write_text(json.dumps(data, separators=(",", ":")))
    titled = {
        cands[s].get("arxiv") or cands[s].get("corpus"): cands[s]["title"]
        for s in yes
        if cands[s].get("arxiv") or cands[s].get("corpus")
    }
    no_id = [s for s in yes if not (cands[s].get("arxiv") or cands[s].get("corpus"))]
    added = append_pool_rows(topic, titled)
    routes = {r: sum(1 for x in cands.values() if r in x["routes"]) for r in ("hidden", "new")}
    print(f"added {len(added)} candidate(s) to the Pool table")
    if no_id:
        print(f"in scope but without an arXiv or corpus ID, so not added; record them in Open work: {no_id}")
    print("\nlog line:")
    print(
        f"- **Fringe:** collected {data['collected']}: hidden {routes['hidden']}, new {routes['new']} candidates "
        f"({len(cands)} unique); in scope {len(yes)}; added to the pool {len(added)}, of which "
        f"{sum(1 for a in added if a.startswith('CorpusId:'))} without an arXiv ID; left out {len(no_id)}"
    )
    warn_rejected(topic, added)
    if added:
        print(f"\n{next_step(topic)}")
    return 0


# --- clusters, late, remap ------------------------------------------------------------------------


def write_clusters(topic: str) -> int:
    """Write each pool paper's computed cluster, by name, into the Pool `cluster` column; returns the exit status."""
    _, report = load_report(topic)
    if report.get("previous") and not report["previous"].get("remapped") and name_map(topic):
        print(
            f"FAIL  clusters.json is a new clustering whose names have not been carried over; run "
            f"`uv run python -m deeper_research.assign remap {topic}` first, or the old names would land on the new "
            "clusters"
        )
        return 1
    names = name_map(topic)
    assigned = dict(report["assignment"])
    assigned.update({p: x["cluster"] for p, x in report.get("late", {}).items()})
    unnamed = sorted(set(assigned.values()) - set(names))
    if unnamed:
        print(
            f"FAIL  computed cluster(s) {unnamed} have no row in the Clusters table (`computed` column); name them "
            "first (docs/process.md, step 3)"
        )
        return 1
    values = {p: names[c] for p, c in assigned.items()}
    changed = rewrite_column(topic, "Pool", None, "cluster", values)
    waiting = sorted(set(pool_ids(topic)) - set(assigned))
    print(f"Pool table: {changed} `cluster` cell(s) written")
    if waiting:
        print(
            f"late papers awaiting assignment ({len(waiting)}): {waiting}; run "
            f"`uv run python -m deeper_research.assign late {topic}`"
        )
    return 0


def late(topic: str) -> int:
    """Assign the late papers to their nearest clusters, as one batch; returns the exit status."""
    # local: keeps numpy out of the commands that do not assign late papers
    import numpy as np  # noqa: PLC0415

    # local: a top-level import would load pool, binding its net.get_json, before a test could replace it
    from deeper_research import pool  # noqa: PLC0415

    # local: keeps numpy, igraph, leidenalg and scikit-learn out of the commands that do not assign late papers
    from deeper_research.cluster import combined_sim, refs_sim, text_sim  # noqa: PLC0415

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
    n_late = len(report.get("late", {})) + len(queue)
    if n_late / len(members) > LATE_SHARE:
        # One decimal: in whole percents, 10.3% would read "10% of the pool, above 10%".
        print(
            f"RECLUSTER: late papers since the last full clustering would be {n_late} of {len(members)} "
            f"({n_late / len(members):.1%}), above {LATE_SHARE:.0%} of the pool: rerun "
            f"`uv run python -m deeper_research.cluster {topic}` instead, then "
            f"`uv run python -m deeper_research.assign remap {topic}`"
        )
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
    shown: list[str] = []
    for j, a in enumerate(queue):
        row = S[n + j, :n]
        if not np.any(row > 0):  # e.g. no shared references at all under `refs`: fall back on text
            row = T[n + j, :n]
        votes: dict[str, float] = {}
        for i in np.argsort(row)[::-1][:k]:
            votes[labels[i]] = votes.get(labels[i], 0.0) + float(max(row[i], 0.0))
        best = sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        late_rec[a] = {"cluster": best, "assigned": today, "votes": {x: round(v, 3) for x, v in votes.items()}}
        shown.append(f"{a} -> {names.get(best, best)}")
    path.write_text(json.dumps(report, indent=1))
    status = write_clusters(topic)
    print("\nlog line:")
    print(
        f"- **Late papers:** {today}: {len(queue)} assigned to their nearest cluster ({', '.join(shown)}); late "
        f"since the last full clustering: {len(late_rec)} of {len(members)} ({len(late_rec) / len(members):.0%})"
    )
    return status


def remap(topic: str) -> int:
    """Carry each named cluster's `computed` id over to the new cluster it matched after a recluster."""
    path, report = load_report(topic)
    prev = report.get("previous")
    if not prev:
        sys.exit("clusters.json has no `previous` clustering to match against; nothing to remap")
    if prev.get("remapped"):
        sys.exit("already remapped after this clustering")
    names = name_map(topic)
    carry: dict[str, str] = {}
    for b, x in prev["new"].items():
        if x["case"] == "matched":
            carry[x["from"][0]] = b
    values: dict[str, str]
    lost: list[str]
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
        print(
            "did not match a new cluster, so their `computed` is cleared; retire, merge or rename them, and log it: "
            + "; ".join(lost)
        )
    if unnamed:
        print(
            "new clusters to name (add a Clusters row with their `computed` id): "
            + ", ".join(f"{b} ({prev['new'][b]['case']})" for b in unnamed)
        )
    print(f"then: `uv run python -m deeper_research.assign clusters {topic}`")
    return 0


REJECTED_HEADER = """# Rejected candidates: {topic}

Candidates screened out of scope, one row per judgement: in orientation, by `deeper_research/assign.py reject`; in \
expansion and
targeted expansions, copied from `expand-screen.md` by `deeper_research/assign.py add-expand`. The fringe routes' \
judgements are in
`fringe-screen.md`. See docs/gates.md.

| paper | date | reason |
| -- | -- | -- |
"""


def write_rejections(
    topic: str, todo: list[tuple[str, str]]
) -> tuple[Path, list[tuple[str, str]], list[tuple[str, str]]]:
    """Append [(paper id, reason)] to rejected.md, dated today, skipping a paper already recorded today.

    Returns (path, recorded, skipped).
    """
    path = topic_dir(topic) / "rejected.md"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(REJECTED_HEADER.format(topic=topic))
    today = time.strftime("%Y-%m-%d")
    text = path.read_text()
    done = {
        row_id(line) for h, c, _, line in table_rows(text) if h and h[0] == "paper" and len(c) > 1 and c[1] == today
    }
    new: list[tuple[str, str]]
    again: list[tuple[str, str]]
    new, again = [], []
    for pid, reason in todo:
        (again if pid in done else new).append((pid, reason))
        done.add(pid)
    if new:
        path.write_text(text.rstrip("\n") + "\n" + "".join(f"| [{p}]({link(p)}) | {today} | {r} |\n" for p, r in new))
    return path, new, again


def reject(topic: str, args: list[str]) -> int:  # noqa: C901
    """args: a paper ID and its reason; or none, to read `<paper-id><TAB><reason>` lines from stdin."""
    if args:
        items = [(1, args[0], " ".join(args[1:]))]
    else:
        items = []
        for n, line in enumerate(sys.stdin, 1):
            if line.strip():
                pid, _, reason = line.rstrip("\n").partition("\t")
                items.append((n, pid.strip(), reason))
        if not items:
            sys.exit("no `<paper-id><TAB><reason>` lines on stdin; nothing recorded")
    pool = {
        row_id(row)
        for h, _, _, row in table_rows(sections(survey_path(topic).read_text()).get("Pool", ""))
        if h and h[0] == "paper"
    }
    # Check every line before writing any, so that a batch is recorded whole or not at all.
    todo: list[tuple[str, str]]
    problems: list[str]
    todo, problems = [], []
    for n, pid, given in items:
        reason = " ".join(given.replace("|", "/").split())
        where = "" if args else f"line {n}: "
        if not ID.match(pid):
            problems.append(f'{where}{pid!r} is not a canonical paper ID (docs/formats.md, "Paper IDs")')
        elif not reason:
            problems.append(f"{where}give {pid} a one-line reason" + ("" if args else ", after a tab"))
        elif pid in pool:
            problems.append(
                f"{where}{pid} is in the pool; a paper leaves the pool only with the user's permission (H12)"
            )
        else:
            todo.append((pid, reason))
    if problems:
        sys.exit(
            "\n".join(problems) + ("" if args else f"\nnothing recorded: {len(problems)} of {len(items)} line(s) wrong")
        )
    path, new, again = write_rejections(topic, todo)
    if args:
        print(
            f"{args[0]} is already recorded as rejected today"
            if again
            else f"recorded {args[0]} as out of scope in {path.relative_to(ROOT)}"
        )
    else:
        print(
            f"recorded {len(new)} paper(s) as out of scope in {path.relative_to(ROOT)}"
            + (f"; {len(again)} already recorded today, skipped: {[p for p, _ in again]}" if again else "")
        )
    return 0


def main(argv: list[str]) -> int:
    """Run the command line; returns the exit status."""
    commands: dict[str, Callable[[str], int]] = {
        "add": lambda t: add(t, argv[2:]),
        "add-expand": add_expand,
        "add-fringe": add_fringe,
        "clusters": write_clusters,
        "late": late,
        "remap": remap,
        "reject": lambda t: reject(t, argv[2:]),
    }
    # `reject` takes an ID and a reason, or neither and lines on stdin, which must then not be a terminal.
    if argv and argv[0] == "reject" and (len(argv) == 3 or (len(argv) == 2 and sys.stdin.isatty())):
        print(__doc__.strip())
        return 2
    if len(argv) < 2 or argv[0] not in commands or (argv[0] not in ("add", "reject") and len(argv) != 2):
        print(__doc__.strip())
        return 2
    if not survey_path(argv[1]).exists():
        sys.exit(
            f"surveys/{argv[1]}.md does not exist; write it first, with its five section headings "
            "(docs/process.md, step 0; docs/formats.md)"
        )
    return commands[argv[0]](argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
