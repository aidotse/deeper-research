"""At least one injected fault per gate requirement; each must be caught by its own requirement.

Each fault is one pytest item, named by the requirement that must catch it: `uv run pytest tests/gates/test_faults.py`.
A requirement with several faults has one item per variant, numbered from its second (`g4.evidence`,
`g4.evidence-2`, ...). Every item fails unless the unmodified fixture passes `--gate G5`, since a fault is only caught
if the baseline passes.
"""

import re
from collections.abc import Callable
from pathlib import Path

import pytest

from deeper_research.check import link
from tests.gates import (
    DISSENT,
    INP,
    OUT,
    PROPOSED,
    Built,
    G,
    S,
    build,
    first_row,
    jset,
    no_declared_dimensions,
    resub,
    run,
    sub,
)


def blank_pool_cluster(f: Built, pid: str) -> None:
    """Empty a pool row's `cluster` cell and drop the paper from the computed assignment: an unassigned late paper."""
    resub(S, rf"(^\| \[[^\n]*\]\({re.escape(link(pid))}\) \| [^|]* \| ){f['names'][f['a'][pid]]}( \|)", r"\1\2")
    jset("clusters.json", lambda d: d["assignment"].pop(pid))


def ev(f: Built, which: str) -> Path:
    """The evidence file of a verified row."""
    return G / "evidence" / (which.replace("/", "_").replace(":", "_") + ".md")


RESULT_QUOTE = '"the method improves accuracy by two points ... the gain holds across all model sizes"'

F: dict[str, Callable[[Built], object]] = {
    "g0.entry": lambda f: sub(S, "### Pass 2026-10-09\n", ""),
    "g0.preflight": lambda f: sub(S, "uv ok", "uv failed"),
    "g0.placeholders": lambda f: sub(S, "step 1: 80k", "<step>: <tokens>"),
    "g0.labels": lambda f: sub(
        S, "- **Demotions:** none", "- **Demotions:** none\n- **Pool:** 195 papers in scope; metadata fetched x"
    ),
    "g0.dimensions": lambda f: sub(S, "declared in the input", "as before"),
    "g0.dimensions ": lambda f: no_declared_dimensions(f, "proposed and adopted provisionally: TBD"),
    "g0.dimensions  ": lambda f: no_declared_dimensions(f, PROPOSED.replace("`capability`, `other`", "`capability`")),
    "g1.orientation": lambda f: sub(S, f"frontier candidates: {f['fr1']}", "frontier candidates: 2401.99999"),
    "g1.orientation ": lambda f: sub(S, 'themes: "test-time compute"; ', ""),
    "g1.orientation  ": lambda f: sub(S, f"frontier candidates: {f['fr1']}, {f['fr2']}", "frontier candidates: none"),
    "g1.expansion-collected": lambda f: jset("expand.json", lambda d: d["rounds"][0]["sources"].pop()),
    "g1.expansion-collected ": lambda f: jset("expand.json", lambda d: d["rounds"][0].update(collected="2026-09-01")),
    "g1.expansion-collected  ": lambda f: jset("expand.json", lambda d: d["rounds"][0]["sources"].pop(0)),
    "g1.expansion-screened": lambda f: resub(
        G / "expand-screen.md", r"\| no \| about image classification \|$", "|  |  |"
    ),
    "g1.expansion-screened ": lambda f: resub(G / "expand-screen.md", r"^\| 3 \|.*\n", ""),
    "g1.expansion-screened  ": lambda f: resub(
        G / "expand-screen.md", r"\| no \| about image classification \|$", "| no | images |"
    ),
    "g1.expansion-added": lambda f: (G / "rejected.md").unlink(),
    "g1.expansion-added ": lambda f: resub(
        G / "expand-screen.md", r"\| no \| about image classification \|$", "| yes | about image classification |"
    ),
    "g1.expansion-line": lambda f: sub(S, "screened 3:", "screened 4:"),
    "g1.errored": lambda f: sub(
        S,
        "**Errored queries:** none",
        '**Errored queries:** "q" (429, failed after 3 retries; retried at the end of the step: failed)',
    ),
    "g1.errored ": lambda f: sub(
        S,
        "**Errored queries:** none",
        '**Errored queries:** none; "q" (429, failed after 3 retries; retried at the end of the step: failed)',
    ),
    "g1.fetched": lambda f: jset("pool.json", lambda d: d["papers"].pop(f["rows"][0])),
    "g1.fringe-collected": lambda f: jset("fringe.json", lambda d: d.update(collected="2026-09-01")),
    "g1.fringe-screened": lambda f: resub(G / "fringe-screen.md", r"\| no \| out of scope \|$", "|  |  |"),
    "g1.fringe-screened ": lambda f: (G / "fringe-screen.md").write_text(
        "\n".join(
            ln for ln in (G / "fringe-screen.md").read_text().splitlines() if not ln.endswith("| no | out of scope |")
        )
        + "\n"
    ),
    "g1.fringe-screened  ": lambda f: resub(G / "fringe-screen.md", r"\| no \| out of scope \|$", "| no | x |"),
    "g1.fringe-added": lambda f: resub(G / "fringe-screen.md", r"\| no \| out of scope \|$", "| yes | in scope |"),
    "g1.fringe-line": lambda f: sub(S, "in scope 3;", "in scope 4;"),
    "g1.pool-line": lambda f: sub(S, "195 papers in scope", "190 papers in scope"),
    "g1.pool-line ": lambda f: sub(S, "metadata fetched 2026-09-29", "metadata fetched 2026-10-09"),
    "g2.clustered": lambda f: jset("clusters.json", lambda d: d.update(generated="2026-10-01")),
    "g2.named": lambda f: resub(S, r"^(\| one \| Cluster one \| )[^|]*( \|)", r"\1\2"),
    "g2.written": lambda f: resub(S, r"(^\| \[[^\n]*\]\([^)]*\) \| [^|]* \| )five( \|)", r"\1\2"),
    "g2.lines": lambda f: resub(S, r"^- \*\*Clustering rationale:\*\*.*\n", ""),
    "g2.lines ": lambda f: resub(S, r"^(- \*\*Clustering rationale:\*\*).*\n", r"\1\n"),
    "g2.clustering-line": lambda f: sub(S, "measure combined", "measure text"),
    "g2.clustering-line ": lambda f: jset("clusters.json", lambda d: d.update(rule="tau, moved by user override (8)")),
    "g2.clusters-line": lambda f: sub(S, "6 (2 high", "6 (3 high"),
    "g2.diagnosis-halts": lambda f: jset(
        "clusters.json", lambda d: d["diagnostics"].append({"case": "no structure", "detail": "x"})
    ),
    "g2.review": lambda f: INP.write_text(INP.read_text() + "\n## Clustering\n\n- `review`: before coreset\n"),
    "g3.roles": lambda f: S.write_text(S.read_text().replace(first_row("anchor") + "\n", "", 1)),
    "g3.dissent-searched": lambda f: resub(S, r' \| two: "does not" -> found: \S+', ""),
    "g3.dissent-searched ": lambda f: sub(S, f"found: {f['dissent'][0]}", f"found: {f['fr1']}"),
    "g3.dissent-searched  ": lambda f: resub(S, r"^(- \*\*Dissent searches:\*\*).*\n", r"\1 one two\n"),
    "g3.dissent-quoted": lambda f: sub(S, f'reports "{DISSENT[0]}"', "reports a fall"),
    "g3.bridges": lambda f: S.write_text(S.read_text().replace(first_row("bridge:three") + "\n", "", 1)),
    "g3.divided": lambda f: S.write_text(
        S.read_text().replace(
            [ln for ln in S.read_text().splitlines() if "| frontier |" in ln and ln.endswith("| full-text |")][0]
            + "\n",
            "",
            1,
        )
    ),
    "g3.fringe-quota": lambda f: S.write_text(S.read_text().replace(first_row("fringe") + "\n", "", 1)),
    "g3.cells": lambda f: sub(S, "| accuracy |", "|  |"),
    "g3.assigned": lambda f: blank_pool_cluster(f, f["rows"][0]),
    "g3.dimension-columns": no_declared_dimensions,
    "g4.evidence": lambda f: (G / "evidence" / (f["verified"][3].replace("/", "_").replace(":", "_") + ".md")).unlink(),
    "g4.evidence ": lambda f: sub(
        G / "evidence" / (f["verified"][1].replace("/", "_").replace(":", "_") + ".md"), "- `result`, ", "- "
    ),
    "g4.evidence           ": lambda f: sub(
        ev(f, f["verified"][1]), "`datasets / models`, `metric` —", "`datasets / models` —"
    ),
    "g4.evidence  ": lambda f: sub(
        G / "evidence" / (f["verified"][0].replace("/", "_").replace(":", "_") + ".md"),
        "improves accuracy by two points",
        "raises accuracy by two points",
    ),
    "g4.evidence   ": lambda f: sub(
        G / "evidence" / (f["verified"][2].replace("/", "_").replace(":", "_") + ".md"),
        " — full-text, 4 Results — ",
        " from the results: ",
    ),
    "g4.evidence    ": lambda f: sub(
        G / "evidence" / (f["verified"][2].replace("/", "_").replace(":", "_") + ".md"),
        " — full-text, 4 Results — ",
        " — snippet — ",
    ),
    "g4.evidence     ": lambda f: sub(ev(f, f["verified"][2]), RESULT_QUOTE, '"pro ... ves ... all model sizes"'),
    "g4.evidence      ": lambda f: sub(ev(f, f["verified"][2]), RESULT_QUOTE, '""'),
    "g4.evidence       ": lambda f: sub(ev(f, f["verified"][2]), RESULT_QUOTE, '"On GSM8K the"'),
    "g4.evidence        ": lambda f: sub(
        ev(f, f["verified"][2]),
        RESULT_QUOTE,
        '"the gain holds across all model sizes ... the method improves accuracy by two points"',
    ),
    "g4.evidence         ": lambda f: sub(
        ev(f, f["verified"][2]), f"# Evidence: {f['verified'][2]}", f"# Evidence: {f['verified'][3]}"
    ),
    "g4.evidence          ": lambda f: sub(ev(f, f["verified"][2]), "— full-text, 3 Method —", "— abstract —"),
    "g4.dissent-evidence": lambda f: resub(ev(f, f["dissent"][0]), r"^- `selected because`.*\n", ""),
    "g4.abstract-listed": lambda f: resub(S, r"^- \*\*Rows needing verification:\*\*.*\n", ""),
    "g4.h10": lambda f: S.write_text(re.sub(r"\| full-text \|$", "| abstract |", S.read_text(), count=8, flags=re.M)),
    "g4.coreset-line": lambda f: resub(S, r"Coreset:\*\* \d+ rows", "Coreset:** 3 rows"),
    "g5.output": lambda f: OUT.unlink(),
    "g5.cite-entries": lambda f: sub(OUT, "- Does it hold? Builds on", "- Does it hold?\n\n- Another"),
    "g5.coverage": lambda f: sub(S, "round 1: 1 of 12 sampled", "round 1: one of twelve sampled"),
    "g5.coverage ": lambda f: sub(S, "round 1: 1 of 12 sampled", "round 1: 1 of 8 sampled"),
    "g5.coverage  ": lambda f: sub(S, f"({f['changed']}: Gaps:", "(Gaps:"),
    "g5.coverage-sheets": lambda f: (G / "coverage-1.md").unlink(),
    "g5.coverage-sheets ": lambda f: sub(
        G / "coverage-1.md", "| no change | its nearest row already makes the claim |", "|  |  |"
    ),
    "g5.coverage-sheets  ": lambda f: sub(G / "coverage-1.md", "| changes Gaps |", "| no change |"),
    "g5.coverage-sheets   ": lambda f: sub(G / "coverage-1.md", "| no change |", "| new cluster |"),
    "g5.converged": lambda f: sub(S, "round 1: 1 of 12", "round 1: 3 of 12"),
    "g5.converged ": lambda f: sub(S, "**Ended:** finished (F1)", "**Ended:** done"),
    "g4.counted-rows": lambda f: sub(S, f"({f['changed']}: Gaps", "(2401.99999: Gaps"),
    "g4.counted-rows ": lambda f: resub(
        S, rf"^(\| \[[^\n]*{re.escape(link(f['changed']))}[^\n]*\| )full-text( \|)$", r"\1abstract\2"
    ),
    "g0.halts-waivers": lambda f: sub(S, "- **Waivers:** none\n", ""),
    "g2.central-claim": lambda f: sub(S, " It holds that longer reasoning helps.", ""),
    "g5.coverage-sheets    ": lambda f: sub(S, "it adds a gap the", "it adds a large gap the"),
    "g5.coverage-sheets     ": lambda f: resub(G / "coverage-1.md", r"^Recency query: .*\n", ""),
    "g5.late-empty": lambda f: jset(
        "clusters.json", lambda d: d["assignment"].pop(sorted(set(f["a"]) - set(f["rows"]))[0])
    ),
    "g5.judgement-audit": lambda f: resub(S, r"^- \*\*Judgement audit:\*\*.*\n", ""),
    "g5.judgement-audit ": lambda f: sub(
        G / "reverify-compare.md", "| agree | the same claim |", "| differ | the same claim |"
    ),
    "g5.judgement-audit  ": lambda f: (G / "faithfulness.md").unlink(),
    "g5.end-lines": lambda f: resub(S, r"^- \*\*Tokens:\*\*.*\n", ""),
    "g5.end-lines ": lambda f: sub(S, "**Tokens:** step 1: 80k", "**Tokens:** lots"),
    "g5.end-lines  ": lambda f: resub(S, r"^(- \*\*Ended:\*\*).*\n", r"\1\n"),
    "g5.end-lines   ": lambda f: resub(S, r"^(- \*\*Halts:\*\*).*\n", r"\1   \n"),
}


def fault_id(rid: str) -> str:
    """The item's id: the requirement's name, with the variant's number after the first (the key's trailing spaces)."""
    name = rid.strip()
    return name if rid == name else f"{name}-{len(rid) - len(name) + 1}"


@pytest.fixture(scope="module")
def baseline() -> None:
    """The unmodified fixture must pass `--gate G5`; otherwise no fault result means anything."""
    build()
    code, out = run("--gate", "G5")
    assert code == 0, (
        "MISS baseline: the unmodified fixture fails --gate G5, so no fault result means anything\n" + (out[-1500:])
    )


@pytest.mark.parametrize("rid", list(F), ids=[fault_id(rid) for rid in F])
@pytest.mark.usefixtures("baseline")
def test_fault_is_caught(rid: str) -> None:
    """The fault fails `--gate G5` (exit 1), and its own requirement is among the failing ones."""
    f = build()
    F[rid](f)
    code, out = run("--gate", "G5")
    hit = re.findall(r"FAIL  G\d (g\d\.[a-z0-9-]+)", out)
    other = [ln[6:90] for ln in out.splitlines() if ln.startswith("FAIL") and not re.match(r"FAIL  G\d g", ln)]
    assert code == 1 and rid.strip() in hit, (
        f"gates failing: {sorted(set(hit))}"
        + (f"  integrity: {other}" if other else "")
        + ("\n" + out[-1500:] if "Traceback" in out else "")
    )
