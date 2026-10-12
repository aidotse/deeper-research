"""Print the Expansion line from screening files and /tmp/mc-expand/queries.tsv (query<TAB>file)."""
import glob, os, sys
T = "/tmp/mc-expand/trav/"
def n(f): return sum(1 for l in open(T + f) if l.strip())
order = ["2608.21366","CorpusId:292022319","2609.12353","2606.13732","2605.04127","2608.04268","2609.18878","2610.09415","2609.09572","2609.40295","2606.05168","2607.17043","2605.07724","2606.28438","2605.23054","2605.20151","CorpusId:289342525"]
fn = lambda p: p.replace(":", "")
back = ", ".join(f"{p} ({n('b_'+fn(p)+'.tsv')})" for p in order)
seeds = []
s1 = sum(n(f) for f in ["f_2305.17493_2026.tsv", "f_2305.17493_2025.tsv", "f_2305.17493_pre2025.tsv"])
seeds.append(f"2305.17493 ({s1})")
seeds.append(f"2404.01413 ({n('f_2404.01413.tsv')})")
fwd = ", ".join(seeds + [f"{p} ({n('f_'+fn(p)+'.tsv')})" for p in order])
qs = []
if os.path.exists("/tmp/mc-expand/queries.tsv"):
    for l in open("/tmp/mc-expand/queries.tsv"):
        if l.strip():
            q, f = l.rstrip("\n").split("\t")
            qs.append(f'"{q}" ({n(f)})')
stop = sys.argv[1] if len(sys.argv) > 1 else "in progress"
line = f"- **Expansion:** backward from {back}; forward from {fwd}"
if qs: line += "; queries " + ", ".join(qs)
line += f"; stopped: {stop}"
print(line)
