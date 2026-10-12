"""Build a screening TSV from a raw Asta JSON and a decisions file.
Usage: mk.py raw.json decisions.txt out.tsv
decisions.txt lines: '<id> <code-or-in-or-?> [free reason]'. Every NEW id must have a decision."""
import json, re, sys, glob
raw, decf, out = sys.argv[1:4]
root = "/tmp/deeper-research-sim"
pool = set(re.findall(r'\]\(https://(?:arxiv\.org/abs/|api\.semanticscholar\.org/)([^)]+)\)', open(f"{root}/surveys/model-collapse.md").read()))
rej = set(re.findall(r'^\| \[([^\]]+)\]', open(f"{root}/graphs/model-collapse/rejected.md").read(), re.M))
dec = {}
import glob as _g
for _f in _g.glob("/tmp/mc-expand/trav/*.tsv"):
    for _l in open(_f):
        _r=_l.rstrip("\n").split("\t")
        if len(_r)>1 and _r[1]=="merge": dec[_r[0]]=["merge","same paper as a pool record (see earlier screening)"]
for l in open(decf):
    if not l.strip(): continue
    parts = l.strip().split(" ", 2)
    dec[parts[0]] = parts[1:]
d = json.load(open(raw)); items = d["result"] if isinstance(d, dict) else d
rows, missing = [], []
for it in items:
    p = it.get("citingPaper") or it.get("citedPaper") or it
    ext = p.get("externalIds") or {}
    pid = ext.get("ArXiv") or (f"CorpusId:{ext['CorpusId']}" if ext.get("CorpusId") else "null")
    if pid == "null": rows.append("null\tnull"); continue
    if pid in pool: rows.append(f"{pid}\tpool"); continue
    if pid in dec:
        x = dec[pid]
        if x[0] in ("in", "?", "merge"): rows.append("\t".join([pid, x[0]] + x[1:]))
        else: rows.append(f"{pid}\tout\t{' '.join(x)}")
        continue
    if pid in rej: rows.append(f"{pid}\tout\tpreviously rejected"); continue
    if len(sys.argv) > 4: rows.append(f"{pid}\tout\t{sys.argv[4]}"); continue
    missing.append(pid)
if missing: sys.exit("no decision for: " + " ".join(missing))
open(out, "w").write("\n".join(rows) + "\n")
print(out, len(rows))
