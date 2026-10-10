"""Behaviours of the gates beyond single requirements: waivers, pending halts, progress inference, history, reject.

Usage: python3 tests/gates/behaviour.py (from anywhere). Exit status 1 if any behaviour is not as expected.
"""
import re, subprocess, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from build import build, clean, autoclean, ROOT, T
from faults import sub, resub, S, G, O, I, first_row, run, no_declared_dimensions, PROPOSED

def fails(out): return sorted(set(re.findall(r"FAIL  G\d (g\d\.[a-z0-9-]+)", out)))
def head(out): return next(l for l in out.splitlines() if l.startswith("gates:"))
res = []
autoclean()
def check(name, cond, out=""):
    res.append(cond); print(f"{'ok ' if cond else 'BAD'} {name}" + ("" if cond else "\n" + out[-800:]))

# 1 waiver: drop a fringe row (and its bib entry, for parity), then waive the quota
import check as chk
f = build()
gone = next(l for l in S.read_text().splitlines()
            if l.startswith("| [") and "| fringe |" in l and chk.row_id(l) != f["changed"])
S.write_text(S.read_text().replace(gone + "\n", "", 1))
gone_id = chk.row_id(gone)
O.write_text(O.read_text().replace(gone_id, chk.row_id(first_row("anchor"))))   # the output cites the dropped row
bib = ROOT / f"bib/{T}.bib"
bib.write_text("".join(e for e in re.split(r"(?=@misc\{)", bib.read_text()) if f"{{{gone_id.split(':')[-1]}}}" not in e))
sub(S, "- **Halts:** none", "- **Waivers:** g3.fringe-quota — only four distinct ideas — user agreed, 2026-10-09\n- **Halts:** none")
sub(S, "Coreset:** 19 rows", "Coreset:** 18 rows")
code, out = run("--gate", "G5")
check("waived requirement does not fail, is reported, and the gate passes",
      code == 0 and "g3.fringe-quota" not in fails(out) and "waived" in out, out)

# 2 pending halt holds later gates and fails --gate
f = build(); sub(S, "- **Halts:** none", "- **Halts:** H5 — no stable level after expansion — pending")
code, out = run("--gate", "G5")
check("pending halt: --gate fails with the halt named", code == 1 and "cannot pass while a halt is pending" in out, out)

# 3 inference mid-pass: strip everything after step 2 (no clusters rows, no coreset, no output, no later lines)
f = build()
t = S.read_text()
for lab in ["Clustering", "Clustering rationale", "Clusters", "Dissent searches", "Coreset",
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
def fake(path):
    return committed_text if path.name == f"{T}.md" and "surveys" in str(path) else None
gates.committed = fake
now = old.replace("- **Pool:** 10 papers in scope", "- **Pool:** 11 papers in scope")
now = now.replace(first_row("anchor") + "\n", "", 1)
now = re.sub(r"\| full-text \|$", "| abstract |", now, count=1, flags=re.M)
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

# 6a history: a verified row edited needs a logged correction; a draft (`abstract`) row does not
def history_of(text):
    S.write_text(text)
    secs = chk.sections(text)
    rows, ids, ab = chk.check_coreset(secs["Coreset"], dims, "coreset", [], [])
    st = chk.check_structure(T, secs, rows, ids, [], [])
    return gates.history(gates.Ctx(T, secs, st, rows, ids, ab, O.read_text(), dims, steer, read_targets(T)[0]))[0]
f = build()
committed_text = S.read_text()
vrow = next(l for l in committed_text.splitlines() if l.startswith("| [") and l.endswith("| full-text |"))
arow = next(l for l in committed_text.splitlines() if l.startswith("| [") and l.endswith("| abstract |"))
vid = chk.row_id(vrow)
edited = committed_text.replace(vrow, vrow.replace("| does a thing |", "| does another thing |"), 1)
hf = history_of(edited)
check("history: verified cell changed without Corrections", any("verified rows changed" in x for x in hf), str(hf))
hf = history_of(edited.replace("- **Corrections to existing rows:** none",
                               f"- **Corrections to existing rows:** {vid} — does a thing -> does another thing, per the full text"))
check("history: verified cell changed with a Corrections entry passes", not any("verified rows changed" in x for x in hf), str(hf))
hf = history_of(committed_text.replace(arow, arow.replace("| does a thing |", "| does another thing |"), 1))
check("history: an abstract-sourced row may be rewritten", not any("verified rows changed" in x for x in hf), str(hf))

# 6b evidence: full text absent -> a note in the plain check, a failure under --gate (a fresh clone has no full texts)
f = build(); import shutil; shutil.rmtree(G / "fulltext")
code, out = run()
check("evidence: missing full text is a note in the plain check", code == 0 and "not checked verbatim" in out, out)
code, out = run("--gate", "G4")
check("evidence: missing full text fails --gate G4", code == 1 and "g4.evidence" in fails(out), out)

# 6c a `snippet` source is not allowed in the coreset layout (it remains valid in legacy surveys, case 8)
f = build(); S.write_text(re.sub(r"\| full-text \|$", "| snippet |", S.read_text(), count=1, flags=re.M))
code, out = run()
check("a `snippet` source fails in the coreset layout", code == 1 and "which is not a source" in out, out)

# 6d --gate never says "passed" while failing, whatever the failure (here: integrity, a bib entry gone)
f = build(); bib = ROOT / f"bib/{T}.bib"; bib.write_text(re.split(r"(?=@misc\{)", bib.read_text(), maxsplit=2)[-1])
code, out = run("--gate", "G4")
check("--gate with an integrity failure: exit 1, no `passed` note", code == 1 and "G4 passed" not in out, out)

# 6e a pending halt keeps the safety net: an empty cell still fails the plain check
f = build(); sub(S, "- **Halts:** none", "- **Halts:** H2 — a query failed twice — pending"); sub(S, "| accuracy |", "|  |")
code, out = run()
check("pending halt: the safety net still requires what was reached", code == 1 and "g3.cells" in fails(out), out)

# 6f a survey with no pass yet: --gate G0 fails on the missing entry, --status reports
f = build(); S.write_text(f"# Survey: {T}\n\n" + "".join(f"## {s}\n\n" for s in chk.SURVEY_SECTIONS))
O.unlink(); (ROOT / f"bib/{T}.bib").unlink()
code, out = run("--gate", "G0")
check("no log entry: --gate G0 fails on g0.entry", code == 1 and "g0.entry" in fails(out), out)
code, out = run("--status")
check("no log entry: --status prints the gates", "G0 ready" in out, out)

# 6g a pass the user ended at a halt needs only the gates it declared, once closed
def halted_at_step_3(tokens=True):
    f = build(); t = S.read_text()
    for lab in ["Clustering", "Clustering rationale", "Clusters", "Dissent searches", "Coreset", "Demotions",
                "Late papers", "Coverage test", "Probes", "Corrections to existing rows", "Tokens", "Halts", "Ended"]:
        t = re.sub(rf"^- \*\*{re.escape(lab)}:\*\*.*\n(?:  .*\n)*", "", t, flags=re.M)
    t = re.sub(r"(## Clusters\n\n)(?:\|.*\n)+", r"\1", t); t = re.sub(r"(## Coreset\n\n)(?:.*\n)*?(?=## Pool)", r"\1", t)
    t = re.sub(r"(\| [^\n]*\]\([^)]*\) \| [^|]* \| )[a-z]+( \|)", r"\1\2", t)
    end = (("- **Tokens:** step 1: 80k, step 2: 250k\n" if tokens else "")
           + "- **Halts:** H4 — no structure in the pool — user decided to stop, 2026-10-09\n- **Ended:** halted (H4)\n")
    t = t.replace("- **Gates:** G0 2026-10-09", "- **Gates:** G0 2026-10-09, G1 2026-10-09")
    S.write_text(t.replace("\n## Clusters", end + "\n## Clusters", 1)); O.unlink(); (ROOT / f"bib/{T}.bib").unlink()
halted_at_step_3()
code, out = run()
check("halted pass with the user's decision: only the declared gates", code == 0 and "ended at H4" in out, out)
halted_at_step_3(tokens=False)
code, out = run()
check("halted pass without its `Tokens` line is not closed", code == 1 and "not closed" in out, out)

# 6h an explicit "no rejections" record replaces rejected.md
f = build(); (G / "rejected.md").unlink(); sub(S, 'queries "test-time compute"', 'queries "test-time compute"; rejected: none')
code, out = run("--gate", "G5")
check("`rejected: none` in `Expansion` satisfies g1.rejected", code == 0, out)

# 6i a proposed cluster the recluster overruled does not block convergence
f = build(); sub(S, "new\n  clusters: none", "new\n  clusters: none (proposed agent memory, not formed)")
code, out = run("--gate", "G5")
check("an overruled cluster proposal still converges", code == 0, out)

# 6j dimensions proposed in the log are read like declared ones: checked values and evidence
f = build(); no_declared_dimensions(f, PROPOSED + "; `pressure` — values: `none`, `prompt-level`")
code, out = run("--gate", "G5")
check("proposed dimensions: a complete pass passes", code == 0 and "proposed in the log" in out, out)
sub(S, "| capability |", "| speed |")
code, out = run()
check("proposed dimensions: a value outside the proposed set fails", code == 1 and "not an allowed value" in out, out)

# 6k trading clusters without a bridge are noted while rows are drafts, before G3 is required
f = build(); t = S.read_text()
for lab in ["Dissent searches", "Coreset", "Coverage test", "Ended"]:
    t = re.sub(rf"^- \*\*{re.escape(lab)}:\*\*.*\n(?:  .*\n)*", "", t, flags=re.M)
t = re.sub(r"\| full-text \|$", "| abstract |", t, flags=re.M)
S.write_text(t); S.write_text(t.replace(first_row("bridge:three") + "\n", "", 1)); O.unlink()
code, out = run()
check("a trading pair without a bridge is noted before G3", "run the Bridges row" in out, out)

# 6l an [abstract-only] marker after no citation fails; one after a cited abstract-sourced paper does not
f = build(); sub(O, "That length helps", "That length helps [abstract-only]")
code, out = run()
check("a free-standing [abstract-only] marker fails", code == 1 and "follows no cited paper ID" in out, out)

# 6m a pool paper also in rejected.md is noted
f = build()
(G / "rejected.md").write_text((G / "rejected.md").read_text() + f"| [{f['rows'][0]}]({chk.link(f['rows'][0])}) | 2026-10-09 | x y |\n")
code, out = run()
check("a rejected paper in the pool is noted", "both rejected" in out, out)

# 7 assign.py reject
f = build()
r = subprocess.run(["python3", "tools/assign.py", "reject", T, "2402.00001", "about", "vision"], cwd=ROOT, capture_output=True, text=True)
check("reject records a row", r.returncode == 0 and "2402.00001" in (G / "rejected.md").read_text(), r.stdout + r.stderr)
r = subprocess.run(["python3", "tools/assign.py", "reject", T, f["rows"][0], "x"], cwd=ROOT, capture_output=True, text=True)
check("reject refuses a pool paper", r.returncode != 0 and "H12" in r.stderr, r.stdout + r.stderr)
r = subprocess.run(["python3", "tools/assign.py", "reject", T, "math.GT/0309136", "x"], cwd=ROOT, capture_output=True, text=True)
check("reject refuses a non-canonical ID", r.returncode != 0, r.stdout + r.stderr)

# 8 the legacy survey is unaffected; --gate on a legacy survey is a failure
r = subprocess.run(["python3", "tools/check.py", "reasoning-legacy"], cwd=ROOT, capture_output=True, text=True)
check("reasoning-legacy still passes", r.returncode == 0, r.stdout[-400:])
r = subprocess.run(["python3", "tools/check.py", "reasoning-legacy", "--gate", "G1"], cwd=ROOT, capture_output=True, text=True)
check("--gate on a legacy survey fails clearly", r.returncode == 1 and "coreset layout" in r.stdout, r.stdout[-300:])
r = subprocess.run(["python3", "tools/check.py", "reasoning-legacy", "--gate", "G9"], cwd=ROOT, capture_output=True, text=True)
check("bad gate is a usage error (2)", r.returncode == 2)
print(f"\n{sum(res)} of {len(res)} behaviours as expected")
sys.exit(0 if all(res) else 1)
