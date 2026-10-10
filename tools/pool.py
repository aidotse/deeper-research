#!/usr/bin/env python3
"""Fetch the metadata a topic's clustering needs, straight from the Semantic Scholar API.

Usage: python3 tools/pool.py <topic> [--refresh]

For every paper in surveys/<topic>.md (coreset and pool), by arXiv ID or CorpusId, fetches its publication date, citation count, full
reference list (as Semantic Scholar paper IDs, not only arXiv IDs within the set) and its SPECTER2 embedding. Writes
them to the pool sidecar graphs/<topic>/pool.json, saving after every batch of 100, so a failed run keeps what it
fetched. Each record carries the date it was fetched. Later runs fetch only papers missing from the file; --refresh
refetches all.

For a coreset survey, it then fills the Pool table's `year`, `citations` and `cites` columns from that data, so they
are never filled by hand. `cites` lists the other pool papers each paper cites. A legacy survey has no Pool table and
is left untouched.

Each record also keeps the paper's arXiv ID where Semantic Scholar knows it, from `externalIds` or an open-access PDF
on arXiv, which tools/check.py uses to catch a CorpusId row for a paper that has an arXiv ID. A record fetched before
it kept the arXiv ID has no `arxiv` key; each run backfills that key and `corpus` for such records, by one light call
per 100 papers, and leaves the rest of the record, and its fetch date, as it was. It ends by printing the retrieval
log's `Pool` line: the papers in scope, how many of them have an arXiv ID, and the fetch dates.

This runs outside any model's context, so it costs no tokens.

Calls are unauthenticated. No API key or user identifier is sent.
"""

import json
import sys
import time

from check import ARXIV_ONLY, LINK, ROOT, arxiv_of, cells_of, s2_ref, sections
from graph import parse, topic_dir
from net import get_json

FIELDS = "externalIds,openAccessPdf,publicationDate,year,citationCount,referenceCount,references.paperId,embedding.specter_v2"
S2_BATCH = f"https://api.semanticscholar.org/graph/v1/paper/batch?fields={FIELDS}"
S2_IDS = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=externalIds,openAccessPdf"


def fetch(ids, save):
    """Fetch in batches of 100, passing each batch's records to `save` as soon as it arrives."""
    for i in range(0, len(ids), 100):
        batch = ids[i : i + 100]
        # The unauthenticated endpoint shares one rate limit across all users and answers 429 freely; net retries.
        data = get_json(S2_BATCH, {"ids": [s2_ref(a) for a in batch]})
        today, out = time.strftime("%Y-%m-%d"), {}
        for aid, rec in zip(batch, data):
            if rec is None:
                continue
            emb = rec.get("embedding") or {}
            ext = rec.get("externalIds") or {}
            out[aid] = {
                "s2": rec.get("paperId"),
                "arxiv": arxiv_of(rec),
                "corpus": f"CorpusId:{ext['CorpusId']}" if ext.get("CorpusId") else None,
                "date": rec.get("publicationDate"),
                "year": rec.get("year"),
                "citations": rec.get("citationCount"),
                "reference_count": rec.get("referenceCount"),
                "refs": sorted({x["paperId"] for x in rec.get("references") or [] if x.get("paperId")}),
                "embedding_model": emb.get("model"),
                "embedding": [round(v, 5) for v in emb.get("vector") or []],
                "fetched": today,
            }
        save(out)
        print(f"  {min(i + 100, len(ids))}/{len(ids)}")


def backfill(ids, records, save):
    """Add `arxiv` and `corpus` to records fetched before they were kept, changing nothing else: the citations,
    references and embedding stay those the clustering was computed from. A paper Semantic Scholar does not return is
    left without the key, to be tried again on the next run."""
    for i in range(0, len(ids), 100):
        batch = ids[i : i + 100]
        out = {}
        for aid, rec in zip(batch, get_json(S2_IDS, {"ids": [s2_ref(a) for a in batch]})):
            if rec is None:
                continue
            ext = rec.get("externalIds") or {}
            corpus = f"CorpusId:{ext['CorpusId']}" if ext.get("CorpusId") else None
            out[aid] = dict(records[aid], arxiv=arxiv_of(rec), corpus=records[aid].get("corpus") or corpus)
        save(out)
        print(f"  {min(i + 100, len(ids))}/{len(ids)}")


def fetched_range(records, ids):
    dates = sorted({records[a].get("fetched") for a in ids if a in records} - {None})
    return "unknown" if not dates else dates[0] if len(dates) == 1 else f"{dates[0]} to {dates[-1]}"


def fill_pool(topic, records):
    """Rewrite the Pool table's year, citations and cites cells in place. Returns the number of rows changed."""
    path = ROOT / "surveys" / f"{topic}.md"
    lines = path.read_text().splitlines(keepends=True)
    s2_to_id = {r["s2"]: a for a, r in records.items() if r.get("s2")}
    in_pool, header, changed, rows = False, None, 0, []
    for i, line in enumerate(lines):
        if line.startswith("## "):
            in_pool, header = line[3:].strip() == "Pool", None
            continue
        if not in_pool or not line.startswith("|"):
            header = None if in_pool and not line.startswith("|") else header
            continue
        if header is None:
            header = cells_of(line.rstrip("\n"))
            continue
        if line.startswith("| --") or line.startswith("|--"):
            continue
        m = LINK.search(line)
        if m:
            rows.append((i, m.group(1), header))
    pool_ids = {aid for _, aid, _ in rows}
    for i, aid, header in rows:
        rec = records.get(aid)
        if rec is None:
            continue
        cells = cells_of(lines[i].rstrip("\n"))
        new = dict(zip(header, cells))
        if rec.get("year"):
            new["year"] = str(rec["year"])
        if rec.get("citations") is not None:
            new["citations"] = str(rec["citations"])
        new["cites"] = " ".join(sorted({s2_to_id[x] for x in rec["refs"] if s2_to_id.get(x) in pool_ids} - {aid}))
        out = [new.get(h, c) for h, c in zip(header, cells)]
        if out != cells:
            lines[i] = "| " + " | ".join(c.replace("\0", "\\|") for c in out) + " |\n"
            changed += 1
    if changed:
        path.write_text("".join(lines))
    return changed if rows else None


def main(argv):
    if not argv or argv[0].startswith("-") or any(a != "--refresh" for a in argv[1:]):
        print(__doc__.strip())
        return 2
    topic, refresh = argv[0], "--refresh" in argv
    survey = ROOT / "surveys" / f"{topic}.md"
    if not survey.exists():
        sys.exit(f"surveys/{topic}.md does not exist; write it first, with its five section headings (docs/process.md, "
                 "step 0), and add the pool's papers with `python3 tools/assign.py add`")
    if "Coreset" not in sections(survey.read_text()):
        sys.exit(f"surveys/{topic}.md has no `## Coreset` section; add the five section headings first (docs/formats.md)")
    papers = parse(topic)[4]
    path = topic_dir(topic) / "pool.json"
    cache = {} if refresh or not path.exists() else json.loads(path.read_text())
    records = cache.get("papers", {})
    # Files written before records carried their own date had one date for the whole file.
    old = cache.pop("fetched", None)
    for r in records.values():
        r.setdefault("fetched", old)

    def save(batch):
        records.update(batch)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"papers": records}, separators=(",", ":"), sort_keys=True))

    missing = sorted(a for a in papers if a not in records)
    if missing:
        print(f"fetching {len(missing)} paper(s) from Semantic Scholar...")
        fetch(missing, save)
    elif old:
        save({})
    stale = sorted(a for a in papers if a in records and "arxiv" not in records[a])
    if stale:
        print(f"backfilling the arXiv ID of {len(stale)} record(s) fetched before it was kept...")
        backfill(stale, records, save)
    unresolved = sorted(a for a in papers if a not in records)
    no_emb = sorted(a for a in papers if a in records and not records[a]["embedding"])
    short = sum(1 for a in papers if a in records and len(records[a]["refs"]) < 10)
    when = fetched_range(records, papers)
    print(f"{path.relative_to(ROOT)}: {len(records)} papers, fetched {when}")
    print(f"unresolved: {len(unresolved)} {unresolved}")
    print(f"no embedding: {len(no_emb)} {no_emb}")
    print(f"fewer than 10 resolved references: {short}")
    filled = fill_pool(topic, records)
    print("no Pool table (legacy survey); survey left untouched" if filled is None
          else f"Pool table: {filled} row(s) updated (citations as of {when})")
    # A paper has an arXiv ID if its canonical ID is one, or, for a CorpusId row, if its record knows one.
    on_arxiv = sum(1 for a in papers if ARXIV_ONLY.match(a) or (records.get(a) or {}).get("arxiv"))
    print("\nlog line:")
    print(f"- **Pool:** {len(papers)} papers in scope, {on_arxiv} with an arXiv ID; metadata fetched {when}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
