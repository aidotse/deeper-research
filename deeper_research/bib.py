"""Regenerate bib/<topic>.bib from the paper IDs in surveys/<topic>.md.

Usage: uv run python -m deeper_research.bib <topic>

The survey's Coreset section is the source of truth; the pool
has no bib entries. Every coreset ID gets an entry, and entries for IDs no longer
in it are dropped, so survey and bib
cannot drift apart. Existing entries are kept verbatim, which keeps citation
keys stable across regenerations; only missing IDs are fetched: from the arXiv
API, or for a paper without an arXiv ID (CorpusId:<n>) from the Semantic Scholar Graph API. An
entry carries `eprint` for an arXiv paper and `corpusid` for any other, which is how
deeper_research/check.py matches it.
Run deeper_research/check.py afterwards.
"""

import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, cast

from deeper_research.check import ARXIV_ID, ROOT, bib_ids, link, row_id, sections, table_rows
from deeper_research.net import TRANSIENT, get_json, request

API = "https://export.arxiv.org/api/query?max_results=100&id_list="
NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
STOP = {"a", "an", "the", "on", "of", "in", "for", "to", "and", "is", "are", "do", "does", "can", "how", "when", "why"}


def survey_ids(topic: str) -> list[str]:
    """Return the IDs of the survey's coreset rows, in table order, each once; exit if there is no coreset."""
    # The bib covers the coreset only, so read the Coreset section and not
    # the pool below it. Preserve table order, so the bib reads in the
    # same order as the survey. A row's ID is its first link, as deeper_research/check.py reads it; a later link in
    # the row, say to a paper it cites, is not a coreset paper.
    path = ROOT / "surveys" / f"{topic}.md"
    if not path.exists():
        sys.exit(f"surveys/{topic}.md does not exist; there is no coreset to write a bib for")
    secs = sections(path.read_text())
    if "Coreset" not in secs:
        sys.exit(
            f"surveys/{topic}.md has no `## Coreset` section; add the five section headings first (docs/formats.md)"
        )
    # The filter drops rows without an ID, so every ID listed is a str.
    return cast(
        "list[str]",
        list(
            dict.fromkeys(
                row_id(line) for h, _, _, line in table_rows(secs["Coreset"]) if h and h[0] == "paper" and row_id(line)
            )
        ),
    )


def existing_entries(path: Path) -> dict[str, str]:
    """Return the bib file's entries, keyed by the paper ID each carries, verbatim; empty if there is no file."""
    if not path.exists():
        return {}
    entries = {}
    for chunk in re.split(r"\n(?=@)", path.read_text()):
        found = bib_ids(chunk)
        if chunk.startswith("@") and found:
            entries[found[0]] = chunk.strip()
    return entries


def fetch(ids: list[str]) -> dict[str, dict[str, Any]]:
    """Return metadata for arXiv papers from the arXiv API, keyed by arXiv ID."""
    # arXiv throttles bursts with transient 406/429/503 responses, so retry
    # with backoff before treating a batch as failed.
    _, _, body = request(
        API + urllib.parse.quote(",".join(ids), safe=",/."),
        headers={"User-Agent": "deeper-research bib tool"},
        attempts=4,
        wait=lambda a: 5 * 2**a,
        transient=TRANSIENT | {406},
        timeout=60,
    )
    # The XML is the arXiv API's answer to a fixed https query.
    root = ET.fromstring(body)  # noqa: S314
    out: dict[str, dict[str, Any]] = {}
    for e in root.findall("a:entry", NS):
        # The casts are for mypy alone: the code takes every field below to be present in each entry.
        aid = cast(
            "re.Match[str]", re.search(rf"abs/({ARXIV_ID})", cast("str", cast("ET.Element", e.find("a:id", NS)).text))
        ).group(1)
        out[aid] = {
            "title": " ".join(cast("str", cast("ET.Element", e.find("a:title", NS)).text).split()),
            "authors": [cast("ET.Element", a.find("a:name", NS)).text for a in e.findall("a:author", NS)],
            "published": cast("ET.Element", e.find("a:published", NS)).text,
            "category": cast("ET.Element", e.find("x:primary_category", NS)).attrib["term"],
            "journal_ref": (
                cast("ET.Element", e.find("x:journal_ref", NS)).text
                if e.find("x:journal_ref", NS) is not None
                else None
            ),
        }
    return out


S2_META = (
    "https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,authors,year,venue,publicationDate,externalIds"
)


def fetch_s2(ids: list[str]) -> dict[str, dict[str, Any]]:
    """Metadata for papers without an arXiv ID (CorpusId:<n>), from the Semantic Scholar Graph API."""
    out: dict[str, dict[str, Any]] = {}
    for i in range(0, len(ids), 100):
        batch = ids[i : i + 100]
        for pid, rec in zip(batch, get_json(S2_META, {"ids": batch}), strict=False):
            if not rec or not rec.get("title") or not rec.get("authors"):
                continue
            out[pid] = {
                "title": " ".join(rec["title"].split()),
                "authors": [a["name"] for a in rec["authors"]],
                "published": rec.get("publicationDate") or f"{rec.get('year') or '0000'}-00-00",
                "venue": rec.get("venue") or "",
                "doi": (rec.get("externalIds") or {}).get("DOI"),
            }
    return out


def make_key(meta: dict[str, Any], taken: set[str]) -> str:
    """Return a citation key not yet in `taken`, first author, year and first title word, and add it to `taken`."""
    last = re.sub(r"[^a-z]", "", meta["authors"][0].split()[-1].lower())
    words = [w for w in re.findall(r"[a-z0-9]+", meta["title"].lower()) if w not in STOP]
    base = f"{last}{meta['published'][:4]}{words[0] if words else ''}"
    key, n = base, 1
    while key in taken:
        n += 1
        key = f"{base}{chr(ord('a') + n - 1)}"
    taken.add(key)
    return key


def entry(aid: str, meta: dict[str, Any], key: str) -> str:
    """Return the BibTeX entry for a paper from its fetched metadata."""
    if aid.startswith("CorpusId:"):
        fields = [("title", meta["title"]), ("author", " and ".join(meta["authors"])), ("year", meta["published"][:4])]
        if meta["published"][5:7] not in ("", "00"):
            fields.append(("month", meta["published"][5:7]))
        if meta["venue"]:
            fields.append(("note", meta["venue"]))
        if meta["doi"]:
            fields.append(("doi", meta["doi"]))
        fields += [("url", link(aid)), ("corpusid", aid.split(":")[1])]
        body = ",\n".join(f"  {k:<13} = {{{v}}}" for k, v in fields)
        return f"@misc{{{key},\n{body}\n}}"
    fields = [
        ("title", meta["title"]),
        ("author", " and ".join(meta["authors"])),
        ("year", meta["published"][:4]),
        ("month", meta["published"][5:7]),
        ("eprint", aid),
        ("archivePrefix", "arXiv"),
        ("primaryClass", meta["category"]),
        ("url", f"https://arxiv.org/abs/{aid}"),
    ]
    if meta["journal_ref"]:
        fields.append(("note", " ".join(meta["journal_ref"].split())))
    body = ",\n".join(f"  {k:<13} = {{{v}}}" for k, v in fields)
    return f"@misc{{{key},\n{body}\n}}"


def main(topic: str) -> int:
    """Write the topic's bib file, fetching only the entries it lacks; return 1 if any had no metadata, else 0."""
    path = ROOT / "bib" / f"{topic}.bib"
    ids = survey_ids(topic)
    have = existing_entries(path)
    missing = [i for i in ids if i not in have]
    taken = {m.group(1) for c in have.values() for m in [re.match(r"@\w+\{([^,]+),", c)] if m}

    fetched: dict[str, dict[str, Any]] = {}
    on_arxiv = [i for i in missing if not i.startswith("CorpusId:")]
    for i in range(0, len(on_arxiv), 50):
        fetched.update(fetch(on_arxiv[i : i + 50]))
        time.sleep(3)  # arXiv API etiquette: one request every 3 seconds
    fetched.update(fetch_s2([i for i in missing if i.startswith("CorpusId:")]))
    unresolved = [i for i in missing if i not in fetched]
    for pid in missing:
        if pid in fetched:
            have[pid] = entry(pid, fetched[pid], make_key(fetched[pid], taken))

    dropped = sorted(set(have) - set(ids))
    header = (
        f"% BibTeX for surveys/{topic}.md\n"
        f"% Generated by deeper_research/bib.py from the arXiv API, and from Semantic Scholar for papers\n"
        f"% without an arXiv ID; regenerated {time.strftime('%Y-%m-%d')}.\n"
        "% `note` carries the arXiv journal-ref where the authors supplied one; the survey\n"
        "% table records peer-reviewed venues as reported by Semantic Scholar.\n"
    )
    path.write_text(header + "\n" + "\n\n".join(have[i] for i in ids if i in have) + "\n")
    print(
        f"bib: {len(ids) - len(unresolved)} entries ({len(missing) - len(unresolved)} fetched, {len(dropped)} dropped)"
    )
    if unresolved:
        print(f"FAIL  no metadata returned for: {unresolved}")
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip())
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
