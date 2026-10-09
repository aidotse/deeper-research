"""Behaviours of the gates beyond single requirements: waivers, pending halts, progress inference, history, reject.

Usage: python3 tests/gates/behaviour.py (from anywhere). Exit status 1 if any behaviour is not as expected.
"""
import re, subprocess, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from build import build, clean, ROOT, T
from faults import sub, resub, S, G, O, I, first_row, run

def fails(out): return sorted(set(re.findall(r"FAIL  G\d (g\d\.[a-z0-9-]+)", out)))
def head(out): return next(l for l in out.splitlines() if l.startswith("gates:"))
res = []
def check(name, cond, out=""):
    res.append(cond); print(f"{'ok ' if cond else 'BAD'} {name}" + ("" if cond else "\n" + out[-800:]))

# 1 waiver
f = build(); S.write_text(S.read_text().replace(first_row("fringe") + "\n", "", 1))
sub(S, "- **Halts:** none", "- **Waivers:** g3.fringe-quota — only four distinct ideas — user agreed, 2026-10-09\n- **Halts:** none")
sub(S, "Coreset:** 19 rows", "Coreset:** 18 rows")
sub(ROOT / f"bib/{T}.bib", "", "")  # bib parity handled below
code, out = run("--gate", "G5")
check("waived requirement does not fail, and is reported", "g3.fringe-quota" not in fails(out) and "waived" in out, out)

# 2 pending halt holds later gates and fails --gate
f = build(); sub(S, "- **Halts:** none", "- **Halts:** H5 — no stable level after expansion — pending")
code, out = run("--gate", "G5")
check("pending halt: --gate fails with the halt named", code == 1 and "cannot pass while a halt is pending" in out, out)

# 3 inference mid-pass: strip everything after step 2 (no clusters rows, no coreset, no output, no later lines)
f = build()
t = S.read_text()
for lab in ["Clustering", "Temporal stability", "Clustering rationale", "Clusters", "Dissent searches", "Coreset",
            "Demotions", "Late papers", "Coverage test", "Probes", "Corrections to existing rows", "Tokens", "Halts", "Ended"]:
    t = re.sub(rf"^- \*\*{re.escape(lab)}:\*\*.*\n(?:  .*\n)*", "", t, flags=re.M)
t = re.sub(r"(## Clusters\n\n)(?:\|.*\n)+", r"\1", t); t = re.sub(r"(## Coreset\n\n)(?:.*\n)*?(?=## Pool)", r"\1", t)
t = re.sub(r"(\| [^\n]*\]\([^)]*\) \| [^|]* \| )[a-z]+( \|)", r"\1\2", t)
S.write_text(t); O.unlink(); (ROOT / f"bib/{T}.bib").unlink()
code, out = run()
check("mid-pass (after step 2, Gates G0): only G0 required, passes", code == 0 and "required G0–G0" in head(out), out)
code, out = run("--gate", "G1")
check("mid-pass: --gate G1 passes on a complete step 2", code == 0 and "G1 passed" in out, out)
code, out = run("--status")
check("mid-pass --status: next gate is G2", "next G2" in head(out) and "G2 clusters named" in out, out)

# 4 safety net: first pass with Coreset rows but Gates line only G0 -> G2 required (inferred)
f = build(); resub(S, r"^- \*\*Clustering rationale:\*\*.*\n", ""); resub(S, r"^- \*\*Ended:\*\*.*\n", "")
resub(S, r"^- \*\*Coverage test:\*\*.*\n.*\n", ""); O.unlink()
code, out = run()
check("safety net: coreset rows without a Gates entry still require G2 (missing rationale caught)",
      "g2.lines" in fails(out), out)

# 5 H13 recorded satisfies review
f = build(); I.write_text(I.read_text() + "\n## Clustering\n\n- `review`: before coreset\n")
sub(S, "- **Halts:** none", "- **Halts:** H13 — review before coreset — user reviewed, continued, 2026-10-09")
code, out = run("--gate", "G5")
check("H13 with a decision satisfies g2.review", code == 0, out)

# 6 history via a fake HEAD
import gates
f = build()
old = S.read_text()
old = old.replace("### Pass 2026-10-09", "### Pass 2026-09-01\n\n- **Pool:** 10 papers in scope\n\n### Pass 2026-10-09", 1)
S.write_text(old)
committed_text = old
import check as chk
def fake(path):
    return committed_text if path.name == f"{T}.md" and "surveys" in str(path) else None
gates.committed = fake
now = old.replace("- **Pool:** 10 papers in scope", "- **Pool:** 11 papers in scope")
now = now.replace(first_row("anchor") + "\n", "", 1)
now = re.sub(r"\| snippet \|$", "| abstract |", now, count=1, flags=re.M)
S.write_text(now)
secs = chk.sections(now)
from inputs import read_input, read_targets
dims, steer, _ = read_input(T)
rows, ids, ab = chk.check_coreset(secs["Coreset"], dims, "coreset", [], [])
st = chk.check_structure(T, secs, rows, ids, [], [])
c = gates.Ctx(T, secs, st, rows, ids, ab, O.read_text(), dims, steer, read_targets(T)[0])
hf, hn = gates.history(c)
check("history: earlier entry edited", any("log entry of 2026-09-01" in x for x in hf), str(hf))
check("history: coreset row removed without Demotions", any("coreset rows removed" in x for x in hf), str(hf))
check("history: source lowered", any("lowered" in x for x in hf), str(hf))

# 6b evidence: full text absent -> note, not failure
f = build(); import shutil; shutil.rmtree(G / "fulltext")
code, out = run("--gate", "G5")
check("evidence: missing full text is a note, not a failure", code == 0 and "not checked verbatim" in out, out)

# 7 assign.py reject
f = build()
r = subprocess.run(["python3", "tools/assign.py", "reject", T, "2402.00001", "about", "vision"], cwd=ROOT, capture_output=True, text=True)
check("reject records a row", r.returncode == 0 and "2402.00001" in (G / "rejected.md").read_text(), r.stdout + r.stderr)
r = subprocess.run(["python3", "tools/assign.py", "reject", T, f["rows"][0], "x"], cwd=ROOT, capture_output=True, text=True)
check("reject refuses a pool paper", r.returncode != 0 and "H12" in r.stderr, r.stdout + r.stderr)
r = subprocess.run(["python3", "tools/assign.py", "reject", T, "math.GT/0309136", "x"], cwd=ROOT, capture_output=True, text=True)
check("reject refuses a non-canonical ID", r.returncode != 0, r.stdout + r.stderr)

# 8 reasoning (legacy) unaffected; --gate on legacy is a failure
r = subprocess.run(["python3", "tools/check.py", "reasoning"], cwd=ROOT, capture_output=True, text=True)
check("reasoning still passes", r.returncode == 0, r.stdout[-400:])
r = subprocess.run(["python3", "tools/check.py", "reasoning", "--gate", "G1"], cwd=ROOT, capture_output=True, text=True)
check("--gate on a legacy survey fails clearly", r.returncode == 1 and "coreset layout" in r.stdout, r.stdout[-300:])
r = subprocess.run(["python3", "tools/check.py", "reasoning", "--gate", "G9"], cwd=ROOT, capture_output=True, text=True)
check("bad gate is a usage error (2)", r.returncode == 2)
print(f"\n{sum(res)} of {len(res)} behaviours as expected")
clean()
sys.exit(0 if all(res) else 1)
