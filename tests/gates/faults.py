"""At least one injected fault per gate requirement; each must be caught by its own requirement.

Usage: python3 tests/gates/faults.py (from anywhere). Exit status 1 if any fault is missed.
"""
import json, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import build, clean, autoclean, ROOT, T, DISSENT
from check import link
S, G, O, I = ROOT / f"surveys/{T}.md", ROOT / f"graphs/{T}", ROOT / f"outputs/{T}.md", ROOT / f"inputs/{T}.md"

def sub(path, a, b, count=1):
    t = path.read_text(); assert a in t, (path.name, a[:60]); path.write_text(t.replace(a, b, count))

def resub(path, pat, b):
    t = path.read_text(); n = re.subn(pat, b, t, count=1, flags=re.M); assert n[1], pat; path.write_text(n[0])

def jset(name, fn):
    d = json.loads((G / name).read_text()); fn(d); (G / name).write_text(json.dumps(d))

def first_row(role):
    return next(l for l in S.read_text().splitlines() if l.startswith("| [") and f"| {role} |" in l)

def blank_pool_cluster(f, pid):
    """Empty a pool row's `cluster` cell and drop the paper from the computed assignment: an unassigned late paper."""
    resub(S, rf"(^\| \[[^\n]*\]\({re.escape(link(pid))}\) \| [^|]* \| ){f['names'][f['a'][pid]]}( \|)", r"\1\2")
    jset("clusters.json", lambda d: d["assignment"].pop(pid))

PROPOSED = ("proposed: `evidence` — values: `empirical`, `proven`; `measures` — values: `capability`, `other`; "
            "`elicitation` — values: `elicited`, `observational`")

def no_declared_dimensions(f, line=PROPOSED):
    """An input without dimensions; the `Dimensions` line proposes them (by default only three of the four columns)."""
    I.write_text(I.read_text().split("## Dimensions")[0])
    sub(S, "declared in the input", line)

def ev(f, which):
    """The evidence file of a verified row."""
    return G / "evidence" / (which.replace("/", "_").replace(":", "_") + ".md")

RESULT_QUOTE = '"the method improves accuracy by two points ... the gain holds across all model sizes"'

F = {
 "g0.entry": lambda f: sub(S, "### Pass 2026-10-09\n", ""),
 "g0.preflight": lambda f: sub(S, "uv ok", "uv failed"),
 "g0.placeholders": lambda f: sub(S, "step 1: 80k", "<step>: <tokens>"),
 "g0.labels": lambda f: sub(S, "- **Demotions:** none", "- **Demotions:** none\n- **Pool:** 195 papers in scope; metadata fetched x"),
 "g0.dimensions": lambda f: sub(S, "declared in the input", "as before"),
 "g0.dimensions ": lambda f: no_declared_dimensions(f, "proposed and adopted provisionally: TBD"),
 "g0.dimensions  ": lambda f: no_declared_dimensions(f, PROPOSED.replace("`capability`, `other`", "`capability`")),
 "g1.orientation": lambda f: sub(S, f"frontier candidates: {f['fr1']}", "frontier candidates: 2401.99999"),
 "g1.expansion": lambda f: sub(S, f", {f['fr2']} (35)", ""),
 "g1.expansion ": lambda f: sub(S, "backward from", "we did NOT traverse"),
 "g1.errored": lambda f: sub(S, "**Errored queries:** none", '**Errored queries:** "q" (429, failed after 3 retries; retried at the end of the step: failed)'),
 "g1.errored ": lambda f: sub(S, "**Errored queries:** none", '**Errored queries:** none; "q" (429, failed after 3 retries; retried at the end of the step: failed)'),
 "g1.rejected": lambda f: (G / "rejected.md").unlink(),
 "g1.fetched": lambda f: jset("pool.json", lambda d: d["papers"].pop(f["rows"][0])),
 "g1.fringe-collected": lambda f: jset("fringe.json", lambda d: d.update(collected="2026-09-01")),
 "g1.fringe-screened": lambda f: resub(G / "fringe-screen.md", r"\| no \| out of scope \|$", "|  |  |"),
 "g1.fringe-screened ": lambda f: (G / "fringe-screen.md").write_text("\n".join(
     l for l in (G / "fringe-screen.md").read_text().splitlines() if not l.endswith("| no | out of scope |")) + "\n"),
 "g1.fringe-screened  ": lambda f: resub(G / "fringe-screen.md", r"\| no \| out of scope \|$", "| no | x |"),
 "g1.fringe-added": lambda f: resub(G / "fringe-screen.md", r"\| no \| out of scope \|$", "| yes | in scope |"),
 "g1.fringe-line": lambda f: sub(S, "in scope 3;", "in scope 4;"),
 "g1.pool-line": lambda f: sub(S, "195 papers in scope", "190 papers in scope"),
 "g1.pool-line ": lambda f: sub(S, "metadata fetched 2026-09-29", "metadata fetched 2026-10-09"),
 "g2.clustered": lambda f: jset("clusters.json", lambda d: d.update(generated="2026-10-01")),
 "g2.named": lambda f: sub(S, "| papers about one |", "|  |"),
 "g2.written": lambda f: resub(S, r"(^\| \[[^\n]*\]\([^)]*\) \| [^|]* \| )five( \|)", r"\1\2"),
 "g2.lines": lambda f: resub(S, r"^- \*\*Clustering rationale:\*\*.*\n", ""),
 "g2.lines ": lambda f: resub(S, r"^(- \*\*Clustering rationale:\*\*).*\n", r"\1\n"),
 "g2.clustering-line": lambda f: sub(S, "measure combined", "measure text"),
 "g2.clustering-line ": lambda f: jset("clusters.json", lambda d: d.update(rule="tau, moved by user override (8)")),
 "g2.clusters-line": lambda f: sub(S, "6 (2 high", "6 (3 high"),
 "g2.diagnosis-halts": lambda f: jset("clusters.json", lambda d: d["diagnostics"].append({"case": "no structure", "detail": "x"})),
 "g2.review": lambda f: I.write_text(I.read_text() + "\n## Clustering\n\n- `review`: before coreset\n"),
 "g3.roles": lambda f: S.write_text(S.read_text().replace(first_row("anchor") + "\n", "", 1)),
 "g3.dissent-searched": lambda f: resub(S, r' \| two: "does not" -> found: \S+', ""),
 "g3.dissent-searched ": lambda f: sub(S, f"found: {f['dissent'][0]}", f"found: {f['fr1']}"),
 "g3.dissent-searched  ": lambda f: resub(S, r"^(- \*\*Dissent searches:\*\*).*\n", r"\1 one two\n"),
 "g3.dissent-quoted": lambda f: sub(S, f'reports "{DISSENT[0]}"', "reports a fall"),
 "g3.bridges": lambda f: S.write_text(S.read_text().replace(first_row("bridge:three") + "\n", "", 1)),
 "g3.divided": lambda f: S.write_text(S.read_text().replace([l for l in S.read_text().splitlines() if "| frontier |" in l and l.endswith("| full-text |")][0] + "\n", "", 1)),
 "g3.fringe-quota": lambda f: S.write_text(S.read_text().replace(first_row("fringe") + "\n", "", 1)),
 "g3.cells": lambda f: sub(S, "| accuracy |", "|  |"),
 "g3.assigned": lambda f: blank_pool_cluster(f, f["rows"][0]),
 "g3.dimension-columns": no_declared_dimensions,
 "g4.evidence": lambda f: (G / "evidence" / (f["verified"][3].replace("/", "_").replace(":", "_") + ".md")).unlink(),
 "g4.evidence ": lambda f: sub(G / "evidence" / (f["verified"][1].replace("/", "_").replace(":", "_") + ".md"), "- `result`, ", "- "),
 "g4.evidence           ": lambda f: sub(ev(f, f["verified"][1]), "`datasets / models`, `metric` —", "`datasets / models` —"),
 "g4.evidence  ": lambda f: sub(G / "evidence" / (f["verified"][0].replace("/", "_").replace(":", "_") + ".md"), "improves accuracy by two points", "raises accuracy by two points"),
 "g4.evidence   ": lambda f: sub(G / "evidence" / (f["verified"][2].replace("/", "_").replace(":", "_") + ".md"), " — full-text, 4 Results — ", " from the results: "),
 "g4.evidence    ": lambda f: sub(G / "evidence" / (f["verified"][2].replace("/", "_").replace(":", "_") + ".md"), " — full-text, 4 Results — ", " — snippet — "),
 "g4.evidence     ": lambda f: sub(ev(f, f["verified"][2]), RESULT_QUOTE, '"pro ... ves ... all model sizes"'),
 "g4.evidence      ": lambda f: sub(ev(f, f["verified"][2]), RESULT_QUOTE, '""'),
 "g4.evidence       ": lambda f: sub(ev(f, f["verified"][2]), RESULT_QUOTE, '"On GSM8K the"'),
 "g4.evidence        ": lambda f: sub(ev(f, f["verified"][2]), RESULT_QUOTE,
                                      '"the gain holds across all model sizes ... the method improves accuracy by two points"'),
 "g4.evidence         ": lambda f: sub(ev(f, f["verified"][2]), f"# Evidence: {f['verified'][2]}", f"# Evidence: {f['verified'][3]}"),
 "g4.evidence          ": lambda f: sub(ev(f, f["verified"][2]), "— full-text, 3 Method —", "— abstract —"),
 "g4.dissent-evidence": lambda f: resub(ev(f, f["dissent"][0]), r"^- `selected because`.*\n", ""),
 "g4.abstract-listed": lambda f: resub(S, r"^- \*\*Rows needing verification:\*\*.*\n", ""),
 "g4.h10": lambda f: S.write_text(re.sub(r"\| full-text \|$", "| abstract |", S.read_text(), count=8, flags=re.M)),
 "g4.coreset-line": lambda f: resub(S, r"Coreset:\*\* \d+ rows", "Coreset:** 3 rows"),
 "g5.output": lambda f: O.unlink(),
 "g5.cite-entries": lambda f: sub(O, "- Does it hold? Builds on", "- Does it hold?\n\n- Another"),
 "g5.coverage": lambda f: sub(S, "round 1: 1 of 12 sampled", "round 1: one of twelve sampled"),
 "g5.coverage ": lambda f: sub(S, "round 1: 1 of 12 sampled", "round 1: 1 of 8 sampled"),
 "g5.coverage  ": lambda f: sub(S, f"({f['changed']}: gap: a new gap)", "(gap: a new gap)"),
 "g5.converged": lambda f: sub(S, "round 1: 1 of 12", "round 1: 3 of 12"),
 "g5.converged ": lambda f: sub(S, "**Ended:** finished (F1)", "**Ended:** done"),
 "g5.changed-in-coreset": lambda f: sub(S, f"({f['changed']}: gap", "(2401.99999: gap"),
 "g5.late-empty": lambda f: jset("clusters.json", lambda d: d["assignment"].pop(sorted(set(f["a"]) - set(f["rows"]))[0])),
 "g5.end-lines": lambda f: resub(S, r"^- \*\*Tokens:\*\*.*\n", ""),
 "g5.end-lines ": lambda f: sub(S, "**Tokens:** step 1: 80k", "**Tokens:** lots"),
 "g5.end-lines  ": lambda f: resub(S, r"^(- \*\*Ended:\*\*).*\n", r"\1\n"),
 "g5.end-lines   ": lambda f: resub(S, r"^(- \*\*Halts:\*\*).*\n", r"\1   \n"),
}

def run(*extra):
    r = subprocess.run(["python3", "tools/check.py", T, *extra], cwd=ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr

def main():
    autoclean()
    build()
    code, out = run("--gate", "G5")
    if code != 0:   # a fault is only "caught" if the unmodified fixture passes
        print("MISS baseline: the unmodified fixture fails --gate G5, so no fault result means anything\n" + out[-1500:])
        return 1
    print("ok  baseline                 the unmodified fixture passes --gate G5")
    bad = 0
    for rid, fn in F.items():
        f = build(); fn(f)
        code, out = run("--gate", "G5")
        hit = re.findall(r"FAIL  G\d (g\d\.[a-z0-9-]+)", out)
        other = [l[6:90] for l in out.splitlines() if l.startswith("FAIL") and not re.match(r"FAIL  G\d g", l)]
        ok = code == 1 and rid.strip() in hit
        bad += not ok
        print(f"{'ok ' if ok else 'MISS'} {rid:24} gates failing: {sorted(set(hit))}" + (f"  integrity: {other}" if other else ""))
        if not ok and "Traceback" in out:
            print(out[-1500:])
    print(f"\n{len(F) - bad} of {len(F)} faults caught")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
