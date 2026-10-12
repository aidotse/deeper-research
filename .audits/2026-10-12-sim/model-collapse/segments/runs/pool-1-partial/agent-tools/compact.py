"""Compact an Asta citations/references JSON file: prints 'n<TAB>status<TAB>id<TAB>title', status POOL/REJ/SEEN/NEW.
SEEN = already decided in another screening file. Prints total count at the end."""
import json, re, sys, glob
root = "/tmp/deeper-research-sim"
pool = set(re.findall(r'\]\(https://(?:arxiv\.org/abs/|api\.semanticscholar\.org/)([^)]+)\)', open(f"{root}/surveys/model-collapse.md").read()))
rej = set(re.findall(r'^\| \[([^\]]+)\]', open(f"{root}/graphs/model-collapse/rejected.md").read(), re.M))
seen = {}
for f in glob.glob("/tmp/mc-expand/trav/*.tsv"):
    for l in open(f):
        r = l.rstrip("\n").split("\t")
        if r[0] != "null": seen[r[0]] = r[1]
d = json.load(open(sys.argv[1]))
items = d["result"] if isinstance(d, dict) else d
if isinstance(items, dict) and "references" in items: items = items["references"]
n = 0
for it in items:
    p = it.get("citingPaper") or it.get("citedPaper") or it
    ext = p.get("externalIds") or {}
    pid = ext.get("ArXiv") or (f"CorpusId:{ext['CorpusId']}" if ext.get("CorpusId") else "null")
    st = "POOL" if pid in pool else "REJ" if pid in rej else ("SEEN:" + seen[pid]) if pid in seen else "NEW"
    n += 1
    if len(sys.argv) > 2 and sys.argv[2] == "new" and st != "NEW": continue
    print(f"{n}\t{st}\t{pid}\t{(p.get('title') or '').strip()}")
print("TOTAL", n, file=sys.stderr)
