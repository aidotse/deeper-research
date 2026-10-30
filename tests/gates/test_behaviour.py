"""Behaviours of the gates beyond single requirements: waivers, pending halts, progress inference, history, reject.

Run with `uv run pytest tests/gates/test_behaviour.py`. Each behaviour is a subtest, named by what it expects. The
scenario runs in order; each test function below is one stretch of it that starts from a freshly built fixture and
shares no state with the others, so the functions may run apart (for example on different xdist workers).
"""

import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
import urllib.error
from collections.abc import Callable
from pathlib import Path
from typing import IO, Any, cast

import pytest

from deeper_research import assign, fringe, gates, net, screen
from deeper_research import check as chk
from deeper_research import expand as ex
from deeper_research.inputs import read_input, read_targets
from deeper_research.screen import verdicts as screen_verdicts
from tests.gates import (
    INP,
    OUT,
    PROPOSED,
    ROOT,
    G,
    S,
    T,
    build,
    first_row,
    no_declared_dimensions,
    resub,
    run,
    sub,
)

Check = Callable[..., None]


def fails(out: str) -> list[str]:
    """The gate requirements the check's output reports as failing, sorted."""
    return sorted(set(re.findall(r"FAIL  G\d (g\d\.[a-z0-9-]+)", out)))


def head(out: str) -> str:
    """The check's `gates:` summary line."""
    return next(ln for ln in out.splitlines() if ln.startswith("gates:"))


@pytest.fixture
def check(subtests: pytest.Subtests) -> Check:
    """`check(name, cond, out)`: one behaviour, as a subtest named `name` that passes when `cond` holds."""

    def check_(name: str, cond: object, out: str = "") -> None:
        with subtests.test(msg=name):
            assert cond, out[-800:]

    return check_


def tool(*a: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run a Python command line from the repository root, with `stdin` as its input; capture its output."""
    return subprocess.run([sys.executable, *a], cwd=ROOT, capture_output=True, text=True, input=stdin, check=False)


def test_waiver_and_pending_halts(check: Check) -> None:
    """Steps 1 to 2b: a waived requirement, and a pending halt."""
    # 1 waiver: drop a fringe row (and its bib entry, for parity), then waive the quota
    f = build()
    gone = next(
        ln
        for ln in S.read_text().splitlines()
        if ln.startswith("| [") and "| fringe |" in ln and chk.row_id(ln) != f["changed"]
    )
    S.write_text(S.read_text().replace(gone + "\n", "", 1))
    gone_id = cast("str", chk.row_id(gone))
    OUT.write_text(
        OUT.read_text().replace(gone_id, cast("str", chk.row_id(first_row("anchor"))))
    )  # the output cites the dropped row
    bib = ROOT / f"bib/{T}.bib"
    bib.write_text(
        "".join(e for e in re.split(r"(?=@misc\{)", bib.read_text()) if f"{{{gone_id.split(':')[-1]}}}" not in e)
    )
    sub(S, "- **Waivers:** none", "- **Waivers:** g3.fringe-quota — only four distinct ideas — user agreed, 2026-10-09")
    sub(S, "Coreset:** 19 rows", "Coreset:** 18 rows")
    code, out = run("--gate", "G5")
    check(
        "waived requirement does not fail, is reported, and the gate passes",
        code == 0 and "g3.fringe-quota" not in fails(out) and "waived" in out,
        out,
    )

    # 2 pending halt holds later gates and fails --gate
    f = build()
    sub(S, "- **Halts:** none", "- **Halts:** H5 — no stable level after expansion — pending")
    code, out = run("--gate", "G5")
    check(
        "pending halt: --gate fails with the halt named",
        code == 1 and "cannot pass while a halt is pending" in out,
        out,
    )

    # 2b a pending halt whose description contains a dash is still pending: the decision follows the entry's last dash
    f = build()
    sub(S, "- **Halts:** none", '- **Halts:** H2 — query "prm survey" — 429 after 3 retries — pending')
    code, out = run("--gate", "G5")
    check(
        "pending halt with a dash in what happened: --gate still fails",
        code == 1 and "cannot pass while a halt is pending" in out,
        out,
    )


def test_progress_inference_and_recorded_halts(check: Check) -> None:
    """Steps 3 to 5b: progress inferred mid-pass and by the safety net, and recorded halts."""
    # 3 inference mid-pass: strip everything after step 2 (no clusters rows, no coreset, no output, no later lines)
    build()
    t = S.read_text()
    for lab in [
        "Clustering",
        "Clustering rationale",
        "Clusters",
        "Dissent searches",
        "Coreset",
        "Demotions",
        "Late papers",
        "Coverage test",
        "Judgement audit",
        "Probes",
        "Corrections to existing rows",
        "Tokens",
        "Ended",
    ]:  # Halts and Waivers stay: they are written at step 0
        t = re.sub(rf"^- \*\*{re.escape(lab)}:\*\*.*\n(?:  .*\n)*", "", t, flags=re.M)
    t = re.sub(r"(## Clusters\n\n)(?:\|.*\n)+", r"\1", t)
    t = re.sub(r"(## Coreset\n\n)(?:.*\n)*?(?=## Pool)", r"\1", t)
    t = re.sub(r"(\| [^\n]*\]\([^)]*\) \| [^|]* \| )[a-z]+( \|)", r"\1\2", t)
    S.write_text(t)
    OUT.unlink()
    (ROOT / f"bib/{T}.bib").unlink()
    code, out = run()
    check(
        "mid-pass (after step 2, Gates G0): only G0 required, passes", code == 0 and "required G0–G0" in head(out), out
    )
    code, out = run("--gate", "G1")
    check("mid-pass: --gate G1 passes on a complete step 2", code == 0 and "G1 passed" in out, out)
    code, out = run("--status")
    check("mid-pass --status: next gate is G2", "next G2" in head(out) and "G2 clusters named" in out, out)

    # 4 safety net: first pass with Coreset rows but Gates line only G0 -> G2 required (inferred)
    build()
    resub(S, r"^- \*\*Clustering rationale:\*\*.*\n", "")
    resub(S, r"^- \*\*Ended:\*\*.*\n", "")
    resub(S, r"^- \*\*Coverage test:\*\*.*\n.*\n", "")
    OUT.unlink()
    code, out = run()
    check(
        "safety net: coreset rows without a Gates entry still require G2 (missing rationale caught)",
        "g2.lines" in fails(out),
        out,
    )

    # 5 H13 recorded satisfies review
    build()
    INP.write_text(INP.read_text() + "\n## Clustering\n\n- `review`: before coreset\n")
    sub(S, "- **Halts:** none", "- **Halts:** H13 — review before coreset — user reviewed, continued, 2026-10-09")
    code, out = run("--gate", "G5")
    check("H13 with a decision satisfies g2.review", code == 0, out)

    # 5b H1 recorded does not stand in for the preflight: a continued pass still needs the line, or a waiver
    build()
    resub(S, r"^- \*\*Preflight:\*\*.*\n", "")
    sub(S, "- **Halts:** none", "- **Halts:** H1 — arXiv API unreachable — user continued, 2026-10-12")
    code, out = run("--gate", "G0")
    check("H1 with a decision does not satisfy g0.preflight", code == 1 and "g0.preflight" in fails(out), out)


def test_history(check: Check, monkeypatch: pytest.MonkeyPatch) -> None:
    """Steps 6 and 6a: the history checks against the committed survey, faked."""
    # 6 history via a fake HEAD
    build()
    old = S.read_text()
    old = old.replace(
        "### Pass 2026-10-09", "### Pass 2026-09-01\n\n- **Pool:** 10 papers in scope\n\n### Pass 2026-10-09", 1
    )
    S.write_text(old)
    committed_text = old

    def fake(path: Path) -> str | None:
        return committed_text if path.name == f"{T}.md" and "surveys" in str(path) else None

    monkeypatch.setattr(gates, "committed", fake)
    now = old.replace("- **Pool:** 10 papers in scope", "- **Pool:** 11 papers in scope")
    now = now.replace(first_row("anchor") + "\n", "", 1)
    now = re.sub(r"\| full-text \|$", "| abstract |", now, count=1, flags=re.M)
    S.write_text(now)
    secs = chk.sections(now)

    dims_read, steer, _ = read_input(T)
    dims = cast("dict[str, set[str]]", dims_read)  # the fixture declares dimensions
    rows, ids, ab = chk.check_coreset(secs["Coreset"], dims, "coreset", [], [])
    st = chk.check_structure(T, secs, rows, ids, [], [])
    c = gates.Ctx(T, secs, st, rows, ids, ab, OUT.read_text(), dims, steer, read_targets(T)[0])
    hf, _ = gates.history(c)
    check("history: earlier entry edited", any("log entry of 2026-09-01" in x for x in hf), str(hf))
    check("history: coreset row removed without Demotions", any("coreset rows removed" in x for x in hf), str(hf))
    check("history: source lowered", any("lowered" in x for x in hf), str(hf))

    # 6a history: a verified row edited needs a logged correction; a draft (`abstract`) row does not
    def history_of(text: str) -> list[str]:
        S.write_text(text)
        secs = chk.sections(text)
        rows, ids, ab = chk.check_coreset(secs["Coreset"], dims, "coreset", [], [])
        st = chk.check_structure(T, secs, rows, ids, [], [])
        return gates.history(gates.Ctx(T, secs, st, rows, ids, ab, OUT.read_text(), dims, steer, read_targets(T)[0]))[0]

    build()
    committed_text = S.read_text()
    vrow = next(ln for ln in committed_text.splitlines() if ln.startswith("| [") and ln.endswith("| full-text |"))
    arow = next(ln for ln in committed_text.splitlines() if ln.startswith("| [") and ln.endswith("| abstract |"))
    vid = chk.row_id(vrow)
    edited = committed_text.replace(vrow, vrow.replace("| does a thing |", "| does another thing |"), 1)
    hf = history_of(edited)
    check("history: verified cell changed without Corrections", any("verified rows changed" in x for x in hf), str(hf))
    hf = history_of(
        edited.replace(
            "- **Corrections to existing rows:** none",
            f"- **Corrections to existing rows:** {vid} — does a thing -> does another thing, per the full text",
        )
    )
    check(
        "history: verified cell changed with a Corrections entry passes",
        not any("verified rows changed" in x for x in hf),
        str(hf),
    )
    hf = history_of(committed_text.replace(arow, arow.replace("| does a thing |", "| does another thing |"), 1))
    check(
        "history: an abstract-sourced row may be rewritten", not any("verified rows changed" in x for x in hf), str(hf)
    )


def test_evidence_sources_and_closing(check: Check) -> None:
    """Steps 6b to 6g: missing full text, sources, integrity under --gate, the safety net, an empty survey, halts."""
    # 6b evidence: full text absent -> a note in the plain check, a failure under --gate (a fresh clone has no full
    # texts)
    build()

    shutil.rmtree(G / "fulltext")
    code, out = run()
    check("evidence: missing full text is a note in the plain check", code == 0 and "not checked verbatim" in out, out)
    code, out = run("--gate", "G4")
    check("evidence: missing full text fails --gate G4", code == 1 and "g4.evidence" in fails(out), out)

    # 6c a `snippet` source is not allowed in the coreset layout (it remains valid in legacy surveys, case 8)
    build()
    S.write_text(re.sub(r"\| full-text \|$", "| snippet |", S.read_text(), count=1, flags=re.M))
    code, out = run()
    check("a `snippet` source fails in the coreset layout", code == 1 and "which is not a source" in out, out)

    # 6d --gate never says "passed" while failing, whatever the failure (here: integrity, a bib entry gone)
    build()
    bib = ROOT / f"bib/{T}.bib"
    bib.write_text(re.split(r"(?=@misc\{)", bib.read_text(), maxsplit=2)[-1])
    code, out = run("--gate", "G4")
    check("--gate with an integrity failure: exit 1, no `passed` note", code == 1 and "G4 passed" not in out, out)

    # 6e a pending halt keeps the safety net: an empty cell still fails the plain check
    build()
    sub(S, "- **Halts:** none", "- **Halts:** H2 — a query failed twice — pending")
    sub(S, "| accuracy |", "|  |")
    code, out = run()
    check("pending halt: the safety net still requires what was reached", code == 1 and "g3.cells" in fails(out), out)

    # 6f a survey with no pass yet: --gate G0 fails on the missing entry, --status reports
    build()
    S.write_text(f"# Survey: {T}\n\n" + "".join(f"## {s}\n\n" for s in chk.SURVEY_SECTIONS))
    OUT.unlink()
    (ROOT / f"bib/{T}.bib").unlink()
    code, out = run("--gate", "G0")
    check("no log entry: --gate G0 fails on g0.entry", code == 1 and "g0.entry" in fails(out), out)
    code, out = run("--status")
    check("no log entry: --status prints the gates", "G0 ready" in out, out)

    # 6g a pass the user ended at a halt needs only the gates it declared, once closed
    def halted_at_step_3(tokens: bool = True) -> None:
        build()
        t = S.read_text()
        for lab in [
            "Clustering",
            "Clustering rationale",
            "Clusters",
            "Dissent searches",
            "Coreset",
            "Demotions",
            "Late papers",
            "Coverage test",
            "Probes",
            "Corrections to existing rows",
            "Tokens",
            "Halts",
            "Ended",
        ]:
            t = re.sub(rf"^- \*\*{re.escape(lab)}:\*\*.*\n(?:  .*\n)*", "", t, flags=re.M)
        t = re.sub(r"(## Clusters\n\n)(?:\|.*\n)+", r"\1", t)
        t = re.sub(r"(## Coreset\n\n)(?:.*\n)*?(?=## Pool)", r"\1", t)
        t = re.sub(r"(\| [^\n]*\]\([^)]*\) \| [^|]* \| )[a-z]+( \|)", r"\1\2", t)
        end = (
            "- **Tokens:** step 1: 80k, step 2: 250k\n" if tokens else ""
        ) + "- **Halts:** H4 — no structure in the pool — user decided to stop, 2026-10-09\n- **Ended:** halted (H4)\n"
        t = t.replace("- **Gates:** G0 2026-10-09", "- **Gates:** G0 2026-10-09, G1 2026-10-09")
        S.write_text(t.replace("\n## Clusters", end + "\n## Clusters", 1))
        OUT.unlink()
        (ROOT / f"bib/{T}.bib").unlink()

    halted_at_step_3()
    code, out = run()
    check("halted pass with the user's decision: only the declared gates", code == 0 and "ended at H4" in out, out)
    halted_at_step_3(tokens=False)
    code, out = run()
    check("halted pass without its `Tokens` line is not closed", code == 1 and "not closed" in out, out)


def test_expansion_sheets(check: Check) -> None:
    """Steps 6h to 6h4: add-expand, the judges' one-word refusal, and two judges at once."""
    # 6h expansion: add-expand refuses while a row is unjudged, then records each `no` and prints the logged line
    f = build()
    resub(G / "expand-screen.md", r"\| no \| about image classification \|$", "| maybe | images, perhaps |")
    r = tool("-m", "deeper_research.assign", "add-expand", T)
    check(
        "add-expand refuses while a row is `maybe`", r.returncode == 1 and "1 row(s)" in r.stderr, r.stdout + r.stderr
    )
    f = build()
    (G / "rejected.md").unlink()
    r = tool("-m", "deeper_research.assign", "add-expand", T)
    line = next((ln for ln in r.stdout.splitlines() if ln.startswith("- **Expansion:**")), "")
    check(
        "add-expand records the `no` in rejected.md and prints the logged line",
        r.returncode == 0
        and "2401.00001" in (G / "rejected.md").read_text()
        and line
        and " ".join(line.split()) in " ".join(S.read_text().split()),
        r.stdout + r.stderr,
    )
    code, out = run("--gate", "G5")
    check("after add-expand the pass passes G5 again", code == 0, out)
    r = tool("-m", "deeper_research.assign", "add-expand", T)
    check(
        "add-expand rerun records nothing twice",
        r.returncode == 0 and (G / "rejected.md").read_text().count("| [2401.00001]") == 1,
        r.stdout + r.stderr,
    )

    # 6h2 a `no` for a paper in the pool is a conflict, listed and not recorded
    f = build()
    resub(G / "expand-screen.md", r"\| yes \| studies test-time compute \|$", "| no | about something else |")
    r = tool("-m", "deeper_research.assign", "add-expand", T)
    pid = f["expanded"][0]
    check(
        "add-expand lists a `no` for a pool paper as a conflict, and does not record it",
        r.returncode == 0 and "in the pool, so not recorded" in r.stdout and pid not in (G / "rejected.md").read_text(),
        r.stdout + r.stderr,
    )

    # 6h3 judge refuses a one-word reason, on both sheets, writing nothing (the gate's own two-word test)
    f = build()
    before = (G / "expand-screen.md").read_text()
    r = tool("-m", "deeper_research.expand", "judge", T, stdin=f"{f['s2s'][2]}\tno\timages\n")
    check(
        "expand judge refuses a one-word reason",
        r.returncode == 1 and "two words" in r.stderr and (G / "expand-screen.md").read_text() == before,
        r.stdout + r.stderr,
    )
    fr_row = next(
        ln for ln in (G / "fringe-screen.md").read_text().splitlines() if ln.endswith("| no | out of scope |")
    )
    r = tool("-m", "deeper_research.fringe", "judge", T, stdin=f"{fr_row.split('|')[2].strip()}\tno\timages\n")
    check("fringe judge refuses a one-word reason", r.returncode == 1 and "two words" in r.stderr, r.stdout + r.stderr)

    # 6h4 two judges at once on disjoint rows both land: judge locks the sheet
    f = build()
    lost = 0
    for k in range(8):
        procs = [
            subprocess.Popen(
                [sys.executable, "-m", "deeper_research.expand", "judge", T],
                cwd=ROOT,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            for _ in range(2)
        ]
        for n, pr in enumerate(procs):
            stdin = cast("IO[str]", pr.stdin)
            stdin.write(f"{f['s2s'][n]}\tyes\tround {k} by judge {n}\n")
            stdin.close()
        for pr in procs:
            pr.wait()
        text = (G / "expand-screen.md").read_text()
        lost += not all(f"round {k} by judge {n}" in text for n in range(2))
    check("parallel judges on disjoint rows lose no verdict", lost == 0, f"{lost} of 8 rounds lost a verdict")


def test_collect_and_add(check: Check, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: C901
    """Steps 6h5 to 6h8: collect against a fake Graph API, the fringe routes' title match, add-expand by CorpusId."""
    # 6h5 collect, against a fake Graph API: what it leaves out and why, paging, a resumed run, a rerun, a targeted
    # round
    f = build()
    ex_data = json.loads((G / "expand.json").read_text())
    ex_data["rounds"][0].update(
        kind="targeted", region=f["fr1"], query="earlier", why="a thin cluster"
    )  # a new first round appends
    (G / "expand.json").write_text(json.dumps(ex_data))
    pool_s2 = json.loads((G / "pool.json").read_text())["papers"][sorted(f["a"])[0]]["s2"]
    pool_title = cast("re.Match[str]", re.search(r"^\| \[([^\]]+)\]", S.read_text().split("## Pool")[1], re.M)).group(1)
    A, C, D, E, G1, H = (f"{k:040x}".replace("0", "a", 1) for k in range(1, 7))
    recs = {
        A: {
            "title": "A new paper on reasoning",
            "abstract": "We study it.",
            "externalIds": {"ArXiv": "2402.11111", "CorpusId": 1},
        },
        C: {"title": pool_title.upper(), "abstract": "", "externalIds": {"CorpusId": 2}},
        D: {"title": "Vision", "abstract": "", "externalIds": {"ArXiv": "2401.00001", "CorpusId": 3}},
        G1: {"title": "Paged citer", "abstract": "Found on page two.", "externalIds": {"CorpusId": 5}},
        H: {"title": "A new paper on reasoning.", "abstract": "", "externalIds": {"CorpusId": 6}},
    }  # E: not found
    calls: list[str] = []
    fail = {"meta": 0}

    def fake(url: str, body: dict[str, Any] | None = None) -> object:
        calls.append(url)
        if "fields=citationCount" in url:
            out = {
                chk.s2_ref(f["fr1"]): {
                    "referenceCount": 5,
                    "citationCount": 1,
                    "references": [{"paperId": x} for x in (A, pool_s2, C, D)] + [{"paperId": None}],
                    "citations": [{"paperId": E}],
                },
                chk.s2_ref(f["fr2"]): {"referenceCount": 0, "citationCount": 3, "references": [], "citations": []},
            }
            return [out.get(x) for x in cast("dict[str, Any]", body)["ids"]]
        if "/paper/batch" in url:
            if fail["meta"]:
                fail["meta"] -= 1
                raise urllib.error.URLError("busy")
            return [recs.get(x) for x in cast("dict[str, Any]", body)["ids"]]
        if "/citations" in url and "offset=0" in url:
            return {"data": [{"citingPaper": {"paperId": G1}}], "next": 1}
        if "/citations" in url:
            return {"data": [{"citingPaper": {"paperId": H}}]}
        if "/paper/search/bulk" in url:
            return {"total": 7, "data": [{"paperId": A}, {"paperId": f["s2s"][0]}]}
        return {"data": []}

    calls_all: list[str] = []

    def fake_call(url: str, body: dict[str, Any] | None = None) -> object:
        calls_all.append(url)
        return fake(url, body)

    monkeypatch.setattr(ex, "call", fake_call)
    fail["meta"] = 1
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try:
            ex.collect(T)
            stopped = False
        except SystemExit as e:
            stopped = "run the same command again" in str(e)
    part = json.loads((G / "expand.json").read_text()).get("partial", {})
    check(
        "a busy API stops collect with its progress saved",
        stopped and len(part.get("sources", {})) == 5,
        str(part)[:300],
    )
    calls.clear()
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        ex.collect(T)
    check(
        "the rerun resumes: no traversal or search fetched again",
        not any("fields=citationCount" in u or "/search" in u for u in calls),
        str(calls),
    )
    d2 = json.loads((G / "expand.json").read_text())
    left = {k: len(v) for k, v in d2["rounds"][1]["left out"].items()}
    check(
        "collect leaves out pool papers (by s2 and title), rejected, on-sheet, second records and unknown papers",
        left
        == {"in the pool": 2, "rejected earlier": 1, "on the sheet already": 1, "another record": 1, "not found": 1}
        and "partial" not in d2,
        str(left),
    )
    fwd = next(x for x in d2["rounds"][1]["sources"] if x["kind"] == "forward" and x["from"] == f["fr2"])
    check("a citer list shorter than its count is paged to the end", fwd["ids"] == [G1, H], str(fwd))
    rows = {c[1]: c for h, c, _, _ in chk.table_rows((G / "expand-screen.md").read_text()) if h and "s2" in h}
    check(
        "collect appends the new candidates as rows 4 and 5, with their abstracts",
        rows.get(A, [""])[0] == "4" and rows.get(G1, [""])[0] == "5" and rows[A][3] == "We study it.",
        buf.getvalue()[-600:],
    )
    with contextlib.redirect_stdout(io.StringIO()):
        ex.collect(T)
    d3 = json.loads((G / "expand.json").read_text())
    check(
        "a rerun replaces its round and appends nothing",
        len(d3["rounds"]) == 2 and (G / "expand-screen.md").read_text().count(A) == 1,
        str(len(d3["rounds"])),
    )
    sheet = (G / "expand-screen.md").read_text()
    (G / "expand-screen.md").write_text("\n".join(ln for ln in sheet.splitlines() if A not in ln) + "\n")
    with contextlib.redirect_stdout(io.StringIO()):
        ex.collect(T)
    check("a rerun restores a candidate's lost row", A in (G / "expand-screen.md").read_text(), "")
    line = ex.expansion_line(d3, screen.verdicts((G / "expand-screen.md").read_text()), "2026-10-09")
    check(
        "the line counts the new round",
        "1 without a paper ID" in line and "screened 2: in scope 0, rejected 0" in line,
        line,
    )
    check(
        "a theme is searched as an exact phrase, by citations, and the line gives its matches",
        any("/paper/search/bulk?query=%22" in u and "sort=citationCount:desc" in u for u in calls_all)
        and "(2 of 7)" in line,
        line,
    )
    check(
        "a theme keeps its hyphens and loses stray quotes and spaces, and an older search record prints its count "
        "alone",
        ex.phrase(' "self-consuming   generative\tmodels" ') == "self-consuming generative models"
        and 'queries "q" (1);'
        in ex.expansion_line(
            {
                "rounds": [
                    {
                        "collected": "2026-10-09",
                        "kind": "first",
                        "sources": [{"kind": "search", "query": "q", "ids": ["x"], "returned": 1, "unresolved": 0}],
                        "left out": {k: [] for k in ex.LEFT_OUT},
                    }
                ],
                "candidates": {},
            },
            {},
            "2026-10-09",
        ),
        "",
    )
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try:
            ex.main(["collect", T, "--query", ' " ', "--why", "empty"])
            empty = None
        except SystemExit as e:
            empty = str(e)
    check("collect refuses an empty theme", empty and "empty" in empty, str(empty))
    with contextlib.redirect_stdout(io.StringIO()):
        code = ex.main(["collect", T, "--targeted", f["fr1"]])
    check("collect --targeted without --query and --why is a usage error", code == 2, str(code))
    with contextlib.redirect_stdout(io.StringIO()):
        ex.main(["collect", T, "--query", "agent memory", "--why", "an expected theme with no cluster"])
    d_t = json.loads((G / "expand.json").read_text())
    check(
        "a targeted round with a theme and no papers only searches, and is named by its theme",
        d_t["rounds"][-1]["region"] == '"agent memory"'
        and [x["kind"] for x in d_t["rounds"][-1]["sources"]] == ["search"],
        str(d_t["rounds"][-1])[:300],
    )
    with contextlib.redirect_stdout(io.StringIO()):
        ex.main(["collect", T, "--targeted", f["fr1"], "--query", "chain of thought", "--why", "thin cluster"])
        ex.main(["collect", T, "--targeted", f["fr1"], "--query", "other theme", "--why", "thin cluster"])
    d4 = json.loads((G / "expand.json").read_text())
    line = ex.expansion_line(d4, screen.verdicts((G / "expand-screen.md").read_text()), "2026-10-09")
    check(
        "a targeted round is its own part, and another query on the same region is another round",
        len(d4["rounds"]) == 5
        and f"targeted, {f['fr1']} (thin cluster): backward from {f['fr1']}" in line
        and not any(x["kind"] == "forward" for x in d4["rounds"][3]["sources"]),
        line[-400:],
    )

    # 6h6 a start paper Semantic Scholar does not know passes G1 only once Open work records it
    f = build()

    def unknown_fr2(d: dict[str, Any]) -> None:
        for x in d["rounds"][0]["sources"]:
            if x.get("from") == f["fr2"]:
                x.update(error="not found", ids=[], returned=0)

    def jset_(fn: Callable[[dict[str, Any]], None]) -> None:
        d = json.loads((G / "expand.json").read_text())
        fn(d)
        (G / "expand.json").write_text(json.dumps(d))

    jset_(unknown_fr2)

    code, out = run()
    check("an untraversed start paper fails g1.expansion-collected", "g1.expansion-collected" in fails(out), out[-500:])

    # 6h7 the fringe routes leave out a second record of a pool paper, by title (M2)
    f = build()
    pool = json.loads((G / "pool.json").read_text())["papers"]
    counts: dict[str, int] = {}
    for r in pool.values():
        for x in r["refs"]:
            counts[x] = counts.get(x, 0) + 1
    multi = [x for x, n in counts.items() if n >= 2 and x not in {r["s2"] for r in pool.values()}][:2]

    def fake_fetch(ids: list[str]) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for k, x in enumerate(ids):
            if x in multi:
                out[x] = {
                    "s2": x,
                    "title": pool_title if x == multi[0] else "An older theory paper",
                    "abstract": "Old.",
                    "arxiv": None,
                    "corpus": f"CorpusId:{900 + k}",
                    "date": "2015-01-01",
                    "year": 2015,
                    "citations": 1,
                    "refs": [],
                    "embedding": [0.1],
                }
        return out

    def fake_fringe_call(url: str, body: dict[str, Any] | None = None) -> dict[str, list[str]]:
        return {"recommendedPapers": []}

    monkeypatch.setattr(fringe, "fetch_s2", fake_fetch)
    monkeypatch.setattr(fringe, "call", fake_fringe_call)
    with contextlib.redirect_stdout(io.StringIO()):
        fringe.collect(T, 60)
    got = json.loads((G / "fringe.json").read_text())["candidates"]
    check(
        "fringe collect leaves out a candidate titled as a pool paper",
        len(multi) == 2 and multi[0] not in got and multi[1] in got,
        str(list(got)),
    )
    # The sheet numbers its rows, for handing them over as ranges, and the shared parser still finds them.
    fr_lines = [
        ln for ln in (G / "fringe-screen.md").read_text().splitlines() if ln.startswith("| ") and "--" not in ln[:5]
    ]
    check(
        "fringe sheet rows are numbered from 1",
        fr_lines[0].startswith("| # | s2 |")
        and [ln.split("|")[1].strip() for ln in fr_lines[1:]] == [str(n) for n in range(1, len(got) + 1)]
        and set(screen_verdicts((G / "fringe-screen.md").read_text())) == set(got),
        "\n".join(fr_lines[:3]),
    )

    # 6h8 a `yes` with only a CorpusId enters the pool by it; a `yes` titled as a pool paper is not added again
    f = build()
    X, Y = "f" * 40, "e" * 40
    d = json.loads((G / "expand.json").read_text())
    d["candidates"][X] = {
        "title": "A paper with no arXiv ID",
        "abstract": "Text.",
        "arxiv": None,
        "corpus": "CorpusId:999",
        "round": 0,
    }
    d["candidates"][Y] = {"title": pool_title, "abstract": "Text.", "arxiv": None, "corpus": "CorpusId:998", "round": 0}
    (G / "expand.json").write_text(json.dumps(d))
    (G / "expand-screen.md").write_text(
        (G / "expand-screen.md").read_text()
        + f"| 4 | {X} | A paper with no arXiv ID | Text. | yes | studies reasoning length |\n"
        f"| 5 | {Y} | {pool_title} | Text. | yes | studies reasoning length |\n"
    )
    sent: list[Any] = []

    def fake_get_json(url: str, body: dict[str, Any] | None = None, **kw: object) -> list[dict[str, Any]]:
        sent.append(body)
        return [
            {"title": "A paper with no arXiv ID", "externalIds": {"CorpusId": 999}, "embedding": {"vector": [0.1]}}
            for _ in cast("dict[str, Any]", body)["ids"]
        ]

    monkeypatch.setattr(net, "get_json", fake_get_json)
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        assign.add_expand(T)
    check(
        "add-expand adds a CorpusId-only candidate, and skips one already in the pool by title",
        "CorpusId:999" in S.read_text()
        and "CorpusId:998" not in S.read_text()
        and sent
        and sent[0]["ids"] == ["CorpusId:999"],
        buf.getvalue()[-500:],
    )


def test_proposals_dimensions_and_notes(check: Check) -> None:
    """Steps 6i to 6m: an overruled cluster proposal, proposed dimensions, and the notes of the plain check."""
    # 6i a proposed cluster the recluster overruled does not block convergence
    f = build()
    sub(S, "lacks); new clusters: none", "lacks); new clusters: none (proposed agent memory, not formed)")
    code, out = run("--gate", "G5")
    check("an overruled cluster proposal still converges", code == 0, out)

    # 6j dimensions proposed in the log are read like declared ones: checked values and evidence
    f = build()
    no_declared_dimensions(f, PROPOSED + "; `pressure` — values: `none`, `prompt-level`")
    code, out = run("--gate", "G5")
    check("proposed dimensions: a complete pass passes", code == 0 and "proposed in the log" in out, out)
    sub(S, "| capability |", "| speed |")
    code, out = run()
    check(
        "proposed dimensions: a value outside the proposed set fails", code == 1 and "not an allowed value" in out, out
    )

    # 6k trading clusters without a bridge are noted while rows are drafts, before G3 is required
    f = build()
    t = S.read_text()
    for lab in ["Dissent searches", "Coreset", "Coverage test", "Ended"]:
        t = re.sub(rf"^- \*\*{re.escape(lab)}:\*\*.*\n(?:  .*\n)*", "", t, flags=re.M)
    t = re.sub(r"\| full-text \|$", "| abstract |", t, flags=re.M)
    S.write_text(t)
    S.write_text(t.replace(first_row("bridge:three") + "\n", "", 1))
    OUT.unlink()
    code, out = run()
    check("a trading pair without a bridge is noted before G3", "run the Bridges row" in out, out)

    # 6l an [abstract-only] marker after no citation fails; one after a cited abstract-sourced paper does not
    f = build()
    sub(OUT, "That length helps", "That length helps [abstract-only]")
    code, out = run()
    check("a free-standing [abstract-only] marker fails", code == 1 and "follows no cited paper ID" in out, out)

    # 6m a pool paper also in rejected.md is noted
    f = build()
    (G / "rejected.md").write_text(
        (G / "rejected.md").read_text() + f"| [{f['rows'][0]}]({chk.link(f['rows'][0])}) | 2026-10-09 | x y |\n"
    )
    code, out = run()
    check("a rejected paper in the pool is noted", "both rejected" in out, out)


def test_reject_legacy_and_print(check: Check) -> None:
    """Steps 7 to 9: assign.py reject, the legacy survey, and check.py --print."""
    # 7 assign.py reject
    f = build()
    r = subprocess.run(
        [sys.executable, "-m", "deeper_research.assign", "reject", T, "2402.00001", "about", "vision"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    check(
        "reject records a row",
        r.returncode == 0 and "2402.00001" in (G / "rejected.md").read_text(),
        r.stdout + r.stderr,
    )
    r = subprocess.run(
        [sys.executable, "-m", "deeper_research.assign", "reject", T, f["rows"][0], "x"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    check("reject refuses a pool paper", r.returncode != 0 and "H12" in r.stderr, r.stdout + r.stderr)
    r = subprocess.run(
        [sys.executable, "-m", "deeper_research.assign", "reject", T, "math.GT/0309136", "x"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    check("reject refuses a non-canonical ID", r.returncode != 0, r.stdout + r.stderr)

    # 8 the legacy survey is unaffected; --gate on a legacy survey is a failure
    r = subprocess.run(
        [sys.executable, "-m", "deeper_research.check", "reasoning-legacy"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    check("reasoning-legacy still passes", r.returncode == 0, r.stdout[-400:])
    r = subprocess.run(
        [sys.executable, "-m", "deeper_research.check", "reasoning-legacy", "--gate", "G1"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    check(
        "--gate on a legacy survey fails clearly", r.returncode == 1 and "coreset layout" in r.stdout, r.stdout[-300:]
    )
    r = subprocess.run(
        [sys.executable, "-m", "deeper_research.check", "reasoning-legacy", "--gate", "G9"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    check("bad gate is a usage error (2)", r.returncode == 2)

    # 9 check.py --print: one section, or one cluster's block, with its line span; a wrong name is a usage error
    f = build()
    r = subprocess.run(
        [sys.executable, "-m", "deeper_research.check", T, "--print", "Coreset:two"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    check(
        "--print prints one cluster's block",
        r.returncode == 0
        and r.stdout.splitlines()[2].startswith("### two")
        and "### three" not in r.stdout
        and "lines " in r.stdout.splitlines()[0],
        r.stdout[-400:],
    )
    r = subprocess.run(
        [sys.executable, "-m", "deeper_research.check", T, "--print", "open-work"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    check("--print finds a section by a loose name", r.returncode == 0 and "## Open work" in r.stdout, r.stdout[-300:])
    r = subprocess.run(
        [sys.executable, "-m", "deeper_research.check", T, "--print", "Coreset:nine"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    check("--print of an unknown block is a usage error (2)", r.returncode == 2 and "one, two" in r.stderr, r.stderr)


def test_second_coverage_round(check: Check) -> None:
    """Step 10: a second coverage round through deeper_research/coverage.py, from draw to the pasted line."""
    # 10 a second coverage round through deeper_research/coverage.py: drawn by seed, judged, its line pasted; G5 still
    # holds
    f = build()

    def uv(*a: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "deeper_research.coverage", *a],
            cwd=ROOT,
            capture_output=True,
            text=True,
            input=stdin,
            check=False,
        )

    r = uv("draw", T, "2", "--seed", "7")
    drawn = re.findall(r"arxiv\.org/abs/([0-9.]+)\)", (G / "coverage-2.md").read_text()) if r.returncode == 0 else []
    first = set(re.findall(r"arxiv\.org/abs/([0-9.]+)\)", (G / "coverage-1.md").read_text()))
    check(
        "draw writes ten candidates, none from round 1 or the coreset",
        len(drawn) == 10 and not (set(drawn) & first) and not (set(drawn) & set(f["rows"])),
        r.stdout + r.stderr,
    )
    again = subprocess.run(
        [sys.executable, "-m", "deeper_research.coverage", "draw", T, "2"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    check("draw refuses to redraw a round", again.returncode == 1 and "drawn once" in again.stderr, again.stderr)
    r = uv("judge", T, "2", stdin="".join(f"{p}\tno change\tits nearest row already says it\n" for p in drawn))

    def cov(*a: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "deeper_research.coverage", *a],
            cwd=ROOT,
            capture_output=True,
            text=True,
            input=stdin,
            check=False,
        )

    r = cov("line", T, "2")
    check(
        "line refuses until the recency query is recorded", r.returncode == 1 and "recency query" in r.stderr, r.stderr
    )
    cov("query", T, "2", "reasoning models", "2026-04-09 to 2026-10-10", "0")
    line = cov("line", T, "2").stdout
    check(
        "line counts the sheet",
        "round 2: 0 of 10 sampled candidates changed the output; new clusters: none" in line and "at most 26%" in line,
        line,
    )
    sub(S, "lacks); new clusters: none\n", "lacks); new clusters: none\n" + line.splitlines()[0] + "\n")
    code, out = run("--gate", "G5")
    check("a round pasted from its sheet passes G5", code == 0, out)
    r = subprocess.run(
        [sys.executable, "-m", "deeper_research.coverage", "judge", T, "2"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        input="2401.00001\tchanges Landscape\tnot on the sheet at all\n",
        check=False,
    )
    check(
        "judge refuses a paper not on the sheet, writing nothing",
        r.returncode == 1 and "nothing written" in r.stderr,
        r.stderr,
    )
    r = cov("judge", T, "2", stdin=f"{drawn[0]}\tchanges Gaps\tit opens a gap on monitoring the output lacks\n")
    check(
        "judge says when it replaces a verdict",
        r.returncode == 0 and "replaced an earlier verdict" in r.stdout,
        r.stdout,
    )
    code, out = run("--gate", "G5")
    check(
        "G5 fails until the pasted line matches the sheet again",
        code == 1 and "differs from its sheet" in out,
        out[-600:],
    )
    r = cov("judge", T, "2", "--recency", stdin="2609.31121\tno change\tit restates what the output says\n")
    check("a recency candidate needs its title", r.returncode == 1 and "title" in r.stderr, r.stderr)
