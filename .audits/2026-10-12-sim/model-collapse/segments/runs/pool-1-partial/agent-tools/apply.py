"""Apply decisions to '?' rows: reads JSON {id: [decision, reason]} from argv[1]."""
import glob, json, sys
dec = json.load(open(sys.argv[1]))
for f in glob.glob("/tmp/mc-expand/trav/*.tsv"):
    out=[]
    for l in open(f):
        r=l.rstrip("\n").split("\t")
        if r[0] in dec and r[1]=="?":
            r=[r[0]]+dec[r[0]]
        out.append("\t".join(r))
    open(f,"w").write("\n".join(out)+("\n" if out else ""))
