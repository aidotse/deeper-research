"""Collect expansion's candidates by script, onto a screening sheet for agents to judge (docs/process.md, "Step 2").

Usage:
  python3 tools/expand.py collect <topic>
  python3 tools/expand.py collect <topic> [--targeted <id>[,<id> ...]] --query "<theme>" --why "<why>"
  python3 tools/expand.py judge <topic> < lines        (one `<s2><TAB>yes|no|maybe<TAB><reason>` per line)

`collect`, on a pass's first expansion, reads the seeds, the frontier candidates and the themes from the latest pass's
`Orientation` line, and calls the Semantic Scholar Graph API:

  backward   the references of every seed and frontier candidate
  forward    every citer of every seed and frontier candidate
  search     one search per theme, on the bulk search endpoint: the theme as an exact phrase in a paper's title or
             abstract (stemmed, so "model collapse" also matches "modeling collapse"), keeping the SEARCH_LIMIT (50)
             most-cited matches. The relevance search endpoint ranks by relevance, but refused every unauthenticated
             call for hours on 2026-10-13, while the bulk endpoint answered. A theme that is a description rather than
             a phrase papers use may match nothing; the `Expansion` line gives each theme's matches.

Both traversals come from the batch endpoint, up to 500 papers per call. A list shorter than the paper's own count is
paged from the paper's references or citations endpoint instead, up to that endpoint's limit (about 10,000), where the
traversal is marked `capped`. With `--query` and `--why`, for a targeted expansion in step 3, it searches the region's
theme and, with `--targeted`, traverses backward from the papers given, which are the region's. The region is named by
the first paper given, or, for an expected theme with no cluster and so no papers, by the theme.

It leaves out a candidate already in the pool, by ID or by title (a second record of a pool paper, such as its venue
version); one already in graphs/<topic>/rejected.md; one already on the sheet, by ID or by title; a second record of
another new candidate, by title, keeping the one with an arXiv ID; and one Semantic Scholar does not know. It records
every source's full result, and what it left out and why, in graphs/<topic>/expand.json, and appends the rest to the
screening sheet graphs/<topic>/expand-screen.md, one numbered row each, with title and abstract. The sheet only grows:
a row keeps its number and its verdict. Rerunning a collection in the same pass replaces its record and appends only
what is new, and any candidate of expand.json that has lost its row gets it back.

Progress is saved in expand.json after every batch and every search. If the Graph API stays busy past its retries, `collect` stops and
says so, and the same command run again resumes where it stopped.

`judge` writes screening verdicts into the sheet. It is the shared judge of tools/screen.py, which says what it refuses,
and it locks the sheet while it writes, so that agents judging disjoint rows may run at once; `collect` takes the same
lock to append. Then `python3 tools/assign.py add-expand <topic>` adds each `yes` to the pool, records each `no` in
rejected.md, and prints the log's `Expansion` line.

Calls are unauthenticated; no key or user identifier is sent.
"""

import fcntl
import http.client
import json
import re
import sys
import time
import urllib.error
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from assign import pool_ids, rejected, survey_path, topic_dir  # noqa: E402
from check import BARE_ID, ID, arxiv_of, s2_ref, sections  # noqa: E402
from net import get_json  # noqa: E402
from screen import ABSTRACT_CHARS, Papers, clean, judge, judged, pool_titles, title_key, verdicts  # noqa: E402

API = "https://api.semanticscholar.org/graph/v1"
SEARCH_LIMIT = 50   # results kept per theme search, as Asta's relevance search returns by default
PAGE = 1000         # the most the references and citations endpoints return per call
BATCH = 500         # the most IDs the batch endpoint takes per call
LISTS = "citationCount,referenceCount,references.paperId,citations.paperId"
META = "title,abstract,externalIds,openAccessPdf"
LEFT_OUT = ("in the pool", "rejected earlier", "on the sheet already", "another record", "not found")
SHEET = """# Expansion screening sheet

Candidates for `{topic}` from expansion, one numbered row each (`python3 tools/expand.py collect`). Mark `in scope` as
`yes` or `no`, with a reason of at least two words tied to the topic (`python3 tools/expand.py judge {topic}`).

| # | s2 | title | abstract | in scope | reason |
| -- | -- | -- | -- | -- | -- |
"""


def call(url, body=None):
    time.sleep(1)   # the unauthenticated endpoint shares one rate limit across all its users; net retries a 429
    return get_json(url, body)


def orientation_parts(line):
    """(seeds, frontier candidates, themes) from an `Orientation` line, each in order and without repeats."""
    seeds, frontier, themes = [], [], []
    for part in line.split(";"):
        part = part.strip()
        if part.startswith("seeds from the input:"):
            seeds = BARE_ID.findall(part)
        elif part.startswith("frontier candidates:"):
            frontier = BARE_ID.findall(part)
        elif part.startswith("themes:"):
            themes = re.findall(r'"([^"]+)"', part)
    return [list(dict.fromkeys(x)) for x in (seeds, frontier, themes)]


def latest_entry(topic):
    """(date, Orientation line) of the retrieval log's latest pass entry."""
    from gates import log_entries
    entries = log_entries(sections(survey_path(topic).read_text()).get("Retrieval log", ""))
    if not entries:
        sys.exit("the retrieval log has no pass entry; run steps 0 and 1 of docs/process.md first")
    return entries[-1]["date"], " ".join(entries[-1]["lines"].get("Orientation", []))


def paged(pid, direction):
    """Every entry of one paper's references or citations list, from its own endpoint: (entries, capped)."""
    endpoint = "references" if direction == "backward" else "citations"
    out, offset = [], 0
    while True:
        try:
            d = call(f"{API}/paper/{urllib.parse.quote(s2_ref(pid), safe=':')}/{endpoint}?fields=paperId&limit={PAGE}"
                     f"&offset={offset}")
        except urllib.error.HTTPError as e:
            if e.code == 400 and offset:
                return out, True   # past the endpoint's limit on offset plus limit
            raise
        out += d.get("data") or []
        if d.get("next") is None:
            return out, False
        offset = d["next"]


def traversal(pid, direction, rec):
    """A source record for one traversal, from the paper's batch record."""
    src = {"kind": direction, "from": pid, "ids": [], "unresolved": 0}
    key, count, inner = (("references", "referenceCount", "citedPaper") if direction == "backward"
                         else ("citations", "citationCount", "citingPaper"))
    if not rec:
        src["error"] = "not found"
        print(f"  WARNING: Semantic Scholar does not know {pid}; nothing to traverse")
    else:
        items = [{inner: x} for x in rec.get(key) or []]
        if len(items) < (rec.get(count) or 0):
            items, capped = paged(pid, direction)
            if capped:
                src["capped"] = True
        for item in items:
            x = (item.get(inner) or {}).get("paperId")
            if x:
                src["ids"].append(x)
            else:
                src["unresolved"] += 1
    src["ids"] = list(dict.fromkeys(src["ids"]))
    src["returned"] = len(src["ids"])
    return src


def phrase(query):
    """A theme as the phrase searched: quotes dropped, whitespace collapsed; hyphens kept, which the endpoint matches."""
    return " ".join(query.replace('"', " ").split())


def search(query):
    """One theme's search: the theme as an exact phrase in title or abstract, its SEARCH_LIMIT most-cited matches."""
    q = urllib.parse.quote('"' + phrase(query) + '"')
    d = call(f"{API}/paper/search/bulk?query={q}&fields=paperId&sort=citationCount:desc")
    ids = list(dict.fromkeys(p["paperId"] for p in (d.get("data") or [])[:SEARCH_LIMIT] if p.get("paperId")))
    return {"kind": "search", "endpoint": "search/bulk", "query": query, "ids": ids, "unresolved": 0,
            "returned": len(ids), "matched": d.get("total") or 0}


def lite(rec):
    """What a candidate keeps of its batch record: title, abstract and canonical IDs; None for a paper not found."""
    if not rec or not rec.get("title"):
        return None
    ext = rec.get("externalIds") or {}
    return {"title": clean(rec["title"]), "abstract": clean(rec.get("abstract")), "arxiv": arxiv_of(rec),
            "corpus": f"CorpusId:{ext['CorpusId']}" if ext.get("CorpusId") else None}


def canonical(c):
    """A candidate's canonical ID (docs/formats.md, "Paper IDs"): its arXiv ID, or failing that its corpus ID."""
    return c.get("arxiv") or c.get("corpus")


def pass_rounds(data, since):
    """The indices of the rounds collected in the pass begun on `since`."""
    return [i for i, r in enumerate(data["rounds"]) if r["collected"] >= since]


def pass_candidates(data, since):
    """The candidates first put on the sheet by a round of this pass."""
    rounds = set(pass_rounds(data, since))
    return {x for x, c in data["candidates"].items() if c.get("round") in rounds}


def append_rows(topic, data):
    """Append a numbered row for every candidate in expand.json without one, under the sheet's lock."""
    sheet = topic_dir(topic) / "expand-screen.md"
    if not sheet.exists():
        sheet.write_text(SHEET.format(topic=topic))
    with open(sheet, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)   # released when the file closes
        text = f.read()
        have = verdicts(text)
        missing = [x for x in data["candidates"] if x not in have]
        first = len(have) + 1
        c = data["candidates"]
        f.seek(0)
        f.write(text.rstrip("\n") + "\n" + "".join(
            f"| {n} | {x} | {c[x]['title']} | {c[x]['abstract'] or '(no abstract)'} |  |  |\n"
            for n, x in enumerate(missing, first)))
        f.truncate()
    return first, len(missing), {**have, **{x: ("", "") for x in missing}}


def collect(topic, targeted=None, query=None, why=None):
    d = topic_dir(topic)
    since, line = latest_entry(topic)
    seeds, frontier, themes = orientation_parts(line)
    if query:
        starts, directions, queries, kind = targeted, ("backward",), [query], "targeted"
    else:
        starts = list(dict.fromkeys(seeds + frontier))
        if not starts:
            sys.exit("STOP: H14 — the latest `Orientation` line names neither seeds nor frontier candidates, so "
                     "there is nothing to traverse from (docs/process.md, \"When a pass ends\")")
        if any(not phrase(x) for x in themes):
            sys.exit("the latest `Orientation` line has an empty theme; each theme is a phrase to search")
        if not themes:
            sys.exit("the latest `Orientation` line names no themes (`themes: \"<phrase>\", ...`), so there is nothing "
                     "to search")
        directions, queries, kind = ("backward", "forward"), themes, "first"
    region = (targeted[0] if targeted else f'"{query}"') if query else None
    key = [kind, region, query]
    d.mkdir(parents=True, exist_ok=True)
    path = d / "expand.json"
    data = json.loads(path.read_text()) if path.exists() else {"rounds": [], "candidates": {}}
    rounds, cands = data["rounds"], data["candidates"]
    part = data.get("partial")
    if not (part and part["key"] == key and part["since"] == since):
        part = data["partial"] = {"key": key, "since": since, "sources": {}, "meta": {}}
    elif part["sources"] or part["meta"]:
        print(f"resuming: {len(part['sources'])} source(s) and {len(part['meta'])} record(s) already fetched")
    save = lambda: path.write_text(json.dumps(data, indent=1))
    labels = [f"{k} {p}" for k in directions for p in starts] + [f"search {q}" for q in queries]
    # The same collection rerun in the same pass replaces its record; its candidates on the sheet stay its own.
    idx = next((i for i in pass_rounds(data, since) if [rounds[i]["kind"], rounds[i].get("region"),
                                                        rounds[i].get("query")] == key), len(rounds))
    try:
        todo = [p for p in starts if any(f"{k} {p}" not in part["sources"] for k in directions)]
        for i in range(0, len(todo), BATCH):
            batch = todo[i:i + BATCH]
            for p, rec in zip(batch, call(f"{API}/paper/batch?fields={LISTS}", {"ids": [s2_ref(x) for x in batch]})):
                for k in directions:
                    part["sources"][f"{k} {p}"] = traversal(p, k, rec)
                    print(f"{k} from {p}: {part['sources'][f'{k} {p}']['returned']}")
            save()
        for q in queries:
            # A search saved before the move to the bulk endpoint has no `endpoint`, and is run again.
            if "endpoint" not in part["sources"].get(f"search {q}", {}):
                part["sources"][f"search {q}"] = search(q)
                s = part["sources"][f"search {q}"]
                print(f'query "{q}": {s["returned"]} of {s["matched"]} matched')
                save()
        sources = [part["sources"][label] for label in labels]

        own = {x for x, c in cands.items() if c.get("round") == idx}
        on_sheet = {x for x in cands if x not in own}
        pool_json = d / "pool.json"
        in_pool_s2 = ({r["s2"] for r in json.loads(pool_json.read_text())["papers"].values()} if pool_json.exists()
                      else set())
        left = {k: [] for k in LEFT_OUT}
        todo = []
        for x in dict.fromkeys(x for s in sources for x in s["ids"]):
            if x in own:
                continue
            elif x in in_pool_s2:
                left["in the pool"].append(x)
            elif x in on_sheet:
                left["on the sheet already"].append(x)
            else:
                todo.append(x)
        need = [x for x in todo if x not in part["meta"]]
        if need:
            print(f"fetching titles and abstracts of {len(need)} candidate(s)...")
        for i in range(0, len(need), BATCH):
            batch = need[i:i + BATCH]
            part["meta"].update(zip(batch, map(lite, call(f"{API}/paper/batch?fields={META}", {"ids": batch}))))
            save()
    except (urllib.error.URLError, http.client.HTTPException, TimeoutError, ConnectionError) as e:
        save()
        sys.exit(f"the Graph API failed after its retries ({e}). What was fetched is saved in {path.relative_to(ROOT)}: "
                 "run the same command again to resume. If it fails again, the pass halts (H3).")

    # Records of one paper (screen.Papers: a shared ID, or the same title by check.same_title) count as one candidate.
    pool, rej = Papers(pool_ids(topic), pool_titles(topic)), set(rejected(topic))
    sheet, seen = Papers(), Papers()   # earlier rounds' rows; this round's papers, a rerun's own rows among them
    for x, c in cands.items():
        (sheet if x in on_sheet else seen).add(x, (c.get("arxiv"), c.get("corpus")), c["title"])
    paper, keep = {}, {}   # candidate -> the paper it is a record of; paper -> the record kept: the first with an
    for x in todo:         # arXiv ID, else the first. A rerun's own row is kept already, so a match to it is left out.
        m = part["meta"].get(x)
        if m:
            found, paper[x] = seen.find((m["arxiv"], m["corpus"]), m["title"])
            if not found:
                seen.add(x, (m["arxiv"], m["corpus"]), m["title"])
                paper[x] = keep[x] = x
            elif paper[x] in keep and m["arxiv"] and not part["meta"][keep[paper[x]]]["arxiv"]:
                keep[paper[x]] = x
    new = []
    for x in todo:
        m = part["meta"].get(x)
        ids = (m["arxiv"], m["corpus"]) if m else ()
        if not m:
            left["not found"].append(x)
        elif pool.find(ids, m["title"])[0]:
            left["in the pool"].append(x)
        elif set(ids) & rej:
            left["rejected earlier"].append(x)
        elif sheet.find(ids, m["title"])[0]:
            left["on the sheet already"].append(x)
        elif keep.get(paper[x]) != x:
            left["another record"].append(x)
        else:
            cands[x] = dict(m, round=idx)
            new.append(x)
    record = {"collected": time.strftime("%Y-%m-%d"), "kind": kind, "region": region, "query": query, "why": why,
              "sources": sources, "left out": left}
    if idx < len(rounds):
        rounds[idx] = record
    else:
        rounds.append(record)
    del data["partial"]
    save()
    first, added, v = append_rows(topic, data)
    print("left out: " + ", ".join(f"{k} {len(x)}" for k, x in left.items()))
    print(f"wrote {path.relative_to(ROOT)}; {len(new)} new candidate(s); appended {added} row(s) to "
          f"graphs/{topic}/expand-screen.md" + (f", numbered {first} to {first + added - 1}" if added else ""))
    print(f"unjudged on the sheet: {sum(1 for a, r in v.values() if not judged(a, r))} of {len(v)}; next, have them "
          f"screened in blocks of at most 100 rows (docs/dispatch.md, \"Screening\"), then run "
          f"`python3 tools/assign.py add-expand {topic}`")
    return 0


def expansion_line(data, verdict_of, since):
    """The log's `Expansion` line, from expand.json and the sheet's verdicts, over the rounds of the pass begun on
    `since`. Each round is one part; a targeted round opens with `targeted, <region> (<why>):`."""
    parts = []
    for i, r in enumerate(data["rounds"]):
        if r["collected"] < since:
            continue
        src = r["sources"]
        bits = []
        for kind in ("backward", "forward"):
            items = [s for s in src if s["kind"] == kind]
            if items:
                bits.append(f"{kind} from " + ", ".join(
                    f"{s['from']} ({s['returned']}" + (f", {s['error']}" if s.get("error") else "")
                    + (", capped" if s.get("capped") else "") + ")" for s in items))
        items = [s for s in src if s["kind"] == "search"]
        if items:
            bits.append("queries " + ", ".join(
                f'"{s["query"]}" ({s["returned"]}' + (f' of {s["matched"]}' if "matched" in s else "") + ")"
                for s in items))
        mine = [x for x, c in data["candidates"].items() if c.get("round") == i]
        said = [verdict_of.get(x, ("", ""))[0] for x in mine]
        unique = len({x for s in src for x in s["ids"]})
        bits.append(f"{unique} unique, left out: " + ", ".join(f"{k} {len(r['left out'][k])}" for k in LEFT_OUT)
                    + f"; {sum(s.get('unresolved', 0) for s in src)} without a paper ID")
        bits.append(f"screened {len(mine)}: in scope {sum(v.startswith('yes') for v in said)}, rejected "
                    f"{sum(v.startswith('no') for v in said)}")
        text = "; ".join(bits)
        parts.append(f"targeted, {r['region']} ({r.get('why') or 'no reason given'}): {text}" if r["kind"] == "targeted"
                     else text)
    return "- **Expansion:** " + "; ".join(parts)


def main(argv):
    if len(argv) < 2 or argv[0] not in ("collect", "judge"):
        print(__doc__.strip())
        return 2
    topic = argv[1]
    if not survey_path(topic).exists():
        sys.exit(f"surveys/{topic}.md does not exist; run steps 0 and 1 of docs/process.md first")
    if argv[0] == "judge":
        if len(argv) != 2 or sys.stdin.isatty():
            print(__doc__.strip())
            return 2
        return judge(topic_dir(topic) / "expand-screen.md", f"`python3 tools/expand.py collect {topic}`")
    try:
        opts = {argv[i]: argv[i + 1] for i in range(2, len(argv), 2)}
    except IndexError:
        opts = None
    if (opts is None or set(opts) - {"--targeted", "--query", "--why"}
            or (opts and not {"--query", "--why"} <= set(opts)) or not all(opts.values())):
        print(__doc__.strip())
        return 2
    if opts:
        ids = [x.strip() for x in opts.get("--targeted", "").split(",") if x.strip()]
        bad = [x for x in ids if not ID.match(x)]
        if bad or ("--targeted" in opts and not ids):
            sys.exit(f"--targeted takes canonical paper IDs, comma-separated; got {bad or 'none'}")
        if not phrase(opts["--query"]):
            sys.exit("--query takes a theme to search as a phrase; got an empty one")
        return collect(topic, ids, opts["--query"], opts["--why"])
    return collect(topic)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
