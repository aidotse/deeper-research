"""Print title+year+abstract for given IDs from a raw Asta JSON file. Usage: abs.py raw.json id..."""
import json, sys
d = json.load(open(sys.argv[1])); items = d["result"] if isinstance(d, dict) else d
want = set(sys.argv[2:])
for it in items:
    p = it.get("citingPaper") or it.get("citedPaper") or it
    ext = p.get("externalIds") or {}
    pid = ext.get("ArXiv") or (f"CorpusId:{ext['CorpusId']}" if ext.get("CorpusId") else "null")
    if pid in want:
        print(f"== {pid} ({p.get('year')}) {p.get('title')}\n{(p.get('abstract') or 'NO ABSTRACT')[:1200]}\n")
