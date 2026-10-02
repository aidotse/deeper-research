#!/usr/bin/env python3
"""Fetch the metadata a topic's clustering needs, straight from the Semantic Scholar API.

Usage: python3 tools/pool.py <topic> [--refresh]

For every paper in surveys/<topic>.md (coreset and pool), fetches its publication date, citation count, full
reference list (as Semantic Scholar paper IDs, not only arXiv IDs within the set) and its SPECTER2 embedding. Writes
them to the pool sidecar graphs/<topic>/pool.json. Later runs fetch only papers missing from the file; --refresh
refetches all.

For a coreset survey, it then fills the Pool table's `year`, `citations` and `cites` columns from that data, so they
are never filled by hand. `cites` lists the other pool papers each paper cites. A legacy survey has no Pool table and
is left untouched.

This runs outside any model's context, so it costs no tokens.

Calls are unauthenticated. No API key or user identifier is sent.
"""

import json
import sys
import time
import urllib.error
import urllib.request

from check import ARXIV, ROOT, cells_of
from graph import parse, topic_dir

FIELDS = "externalIds,publicationDate,year,citationCount,referenceCount,references.paperId,embedding.specter_v2"
S2_BATCH = f"https://api.semanticscholar.org/graph/v1/paper/batch?fields={FIELDS}"


def fetch(ids):
    out = {}
    for i in range(0, len(ids), 100):
        batch = ids[i : i + 100]
        body = json.dumps({"ids": [f"ARXIV:{a}" for a in batch]}).encode()
        req = urllib.request.Request(S2_BATCH, data=body, headers={"Content-Type": "application/json"})
        # The unauthenticated endpoint shares one rate limit across all users and answers 429 freely.
        for attempt in range(8):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or attempt == 7:
                    raise
                time.sleep(5 * (attempt + 1))
        for aid, rec in zip(batch, data):
            if rec is None:
                continue
            emb = rec.get("embedding") or {}
            out[aid] = {
                "s2": rec.get("paperId"),
                "date": rec.get("publicationDate"),
                "year": rec.get("year"),
                "citations": rec.get("citationCount"),
                "reference_count": rec.get("referenceCount"),
                "refs": sorted({x["paperId"] for x in rec.get("references") or [] if x.get("paperId")}),
                "embedding_model": emb.get("model"),
                "embedding": [round(v, 5) for v in emb.get("vector") or []],
            }
        print(f"  {min(i + 100, len(ids))}/{len(ids)}")
    return out


def fill_pool(topic, records):
    """Rewrite the Pool table's year, citations and cites cells in place. Returns the number of rows changed."""
    path = ROOT / "surveys" / f"{topic}.md"
    lines = path.read_text().splitlines(keepends=True)
    s2_to_arxiv = {r["s2"]: a for a, r in records.items() if r.get("s2")}
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
        m = ARXIV.search(line)
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
        new["cites"] = " ".join(sorted({s2_to_arxiv[x] for x in rec["refs"] if s2_to_arxiv.get(x) in pool_ids} - {aid}))
        out = [new.get(h, c) for h, c in zip(header, cells)]
        if out != cells:
            lines[i] = "| " + " | ".join(c.replace("\0", "\\|") for c in out) + " |\n"
            changed += 1
    if changed:
        path.write_text("".join(lines))
    return changed if rows else None


def main(argv):
    if not argv or argv[0].startswith("-"):
        sys.exit(__doc__)
    topic, refresh = argv[0], "--refresh" in argv
    papers = parse(topic)[4]
    path = topic_dir(topic) / "pool.json"
    cache = {} if refresh or not path.exists() else json.loads(path.read_text())
    records = cache.get("papers", {})
    missing = sorted(a for a in papers if a not in records)
    if missing:
        print(f"fetching {len(missing)} paper(s) from Semantic Scholar...")
        records.update(fetch(missing))
        cache = {"fetched": time.strftime("%Y-%m-%d"), "papers": records}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cache, separators=(",", ":"), sort_keys=True))
    unresolved = sorted(a for a in papers if a not in records)
    no_emb = sorted(a for a in papers if a in records and not records[a]["embedding"])
    short = sum(1 for a in papers if a in records and len(records[a]["refs"]) < 10)
    print(f"{path.relative_to(ROOT)}: {len(records)} papers, fetched {cache.get('fetched')}")
    print(f"unresolved: {len(unresolved)} {unresolved}")
    print(f"no embedding: {len(no_emb)} {no_emb}")
    print(f"fewer than 10 resolved references: {short}")
    filled = fill_pool(topic, records)
    print("no Pool table (legacy survey); survey left untouched" if filled is None
          else f"Pool table: {filled} row(s) updated (citations as of {cache.get('fetched')})")


if __name__ == "__main__":
    main(sys.argv[1:])
