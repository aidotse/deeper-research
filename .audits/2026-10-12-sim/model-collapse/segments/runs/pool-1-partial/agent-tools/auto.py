"""Write a screening TSV from ordered lines '<id> [decision...]'; ids without a decision get pool/out(previously rejected) automatically, else error."""
import re, sys
root = "/tmp/deeper-research-sim"
pool = set(re.findall(r'\]\(https://(?:arxiv\.org/abs/|api\.semanticscholar\.org/)([^)]+)\)', open(f"{root}/surveys/model-collapse.md").read()))
rej = set(re.findall(r'^\| \[([^\]]+)\]', open(f"{root}/graphs/model-collapse/rejected.md").read(), re.M))
rows, bad = [], []
for l in open(sys.argv[1]):
    l = l.strip()
    if not l: continue
    p = l.split(" ", 2)
    pid = p[0]
    if len(p) == 1:
        if pid == "null": rows.append("null\tnull")
        elif pid in pool: rows.append(f"{pid}\tpool")
        elif pid in rej: rows.append(f"{pid}\tout\tpreviously rejected")
        else: bad.append(pid)
        continue
    if pid in pool and p[1] != "merge": rows.append(f"{pid}\tpool"); continue
    if p[1] in ("in", "?", "merge"): rows.append("\t".join([pid] + p[1:]))
    else: rows.append(f"{pid}\tout\t{' '.join(p[1:])}")
if bad: sys.exit("undecided: " + " ".join(bad))
open(sys.argv[2], "w").write("\n".join(rows) + "\n"); print(sys.argv[2], len(rows))
