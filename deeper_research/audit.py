"""The judgement audits of a pass: how often verification and the output are right, measured on a sample
(docs/process.md, "Auditing the judgements").

Usage:
  uv run python -m deeper_research.audit reverify <topic> [--seed 1]
  uv run python -m deeper_research.audit fill <topic> < lines           (one `<id><TAB><column><TAB><text>` per line)
  uv run python -m deeper_research.audit compare <topic>
  uv run python -m deeper_research.audit trace <topic> [--n 15] [--seed 1]
  uv run python -m deeper_research.audit judge <topic> reverify|faithfulness < lines
  uv run python -m deeper_research.audit line <topic>

Re-verification measures verification. `reverify` draws a random 10% of the coreset rows verified from the full text
(source `full-text`), at least five, or all of them if there are fewer, and writes graphs/<topic>/reverify.md: one row
per paper, with its ID and empty claim cells (`method name` to `result`, then the dimensions). A fresh agent fills them
from the paper's full text alone, with `fill`, never seeing the survey's rows or their evidence. `compare` then writes
graphs/<topic>/reverify-compare.md: per paper and cell, the survey's text beside the re-verified text, with empty
`agrees` and `reason` cells. It refuses while a cell of reverify.md is empty: `n/a` is written out.

Faithfulness measures the output. `trace` splits the output after its legend into sentences, keeps those that cite a
coreset paper outside `Questions` and `Reading` (which recommend rather than claim), draws --n (15) of them at random,
or all if there are fewer, and writes graphs/<topic>/faithfulness.md: each sentence with its
section, line and cited IDs, empty `verdict` and `reason` cells, and after the table each cited row's cells and its
evidence quotes, once per paper.

`judge` writes verdicts from stdin, refusing the whole batch on any bad line:

  reverify      `<id><TAB><column><TAB>agree|partly|differ<TAB><reason>`
  faithfulness  `S<n><TAB>supported|partly|unsupported<TAB><reason>`

`line` prints the log's `Judgement audit` line from the two judged sheets, ready to paste. It refuses while either is
missing or has a row without a verdict. deeper_research/gates.py (`g5.judgement-audit`) recomputes the line the same way.

Standard library only; nothing is fetched. Usage errors exit with status 2.
"""

import math
import random
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
from deeper_research.check import BARE_ID, LINK, cells_of, link, row_id, sections, table_rows  # noqa: E402

SHARE, LEAST = 0.10, 5  # re-verify this share of the verified rows, and at least this many
N_TRACE = 15  # output sentences drawn for the faithfulness sample
CLAIMS = ["method name", "method summary", "datasets / models", "metric", "result"]
AGREES = ("agree", "partly", "differ")
SKIP = {"Questions", "Reading"}  # output sections that recommend reading rather than claim something of a paper
SUPPORT = ("supported", "partly", "unsupported")
ABBREV = re.compile(r"(?:\b(?:al|e\.g|i\.e|cf|vs|Fig|Sec|Eq|Tab|approx|resp)|\b[A-Z])\.$")


def usage(msg):
    print(f"usage error: {msg}", file=sys.stderr)
    sys.exit(2)


def paths(topic):
    d = ROOT / "graphs" / topic
    return d / "reverify.md", d / "reverify-compare.md", d / "faithfulness.md"


def cell(text):
    return re.sub(r"\s+", " ", text or "").replace("|", "/").strip()


def table(text, first):
    """[{column: cell}] for the rows of the table whose header starts with `first`, with `id` from the row's link."""
    out = []
    for h, cs, _, line in table_rows(text or ""):
        if h and h[0] == first:
            row = dict(zip(h, cs))
            row["id"] = row_id(line) or cs[0]
            out.append(row)
    return out


def write(path, title, header, columns, rows, tail=""):
    lines = [
        f"# {title}",
        "",
        header,
        "",
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("--" for _ in columns) + " |",
    ]
    lines += ["| " + " | ".join(cell(row.get(c, "")) for c in columns) + " |" for row in rows]
    path.write_text("\n".join(lines) + "\n" + (f"\n{tail.strip()}\n" if tail.strip() else ""))


def header_of(text):
    """The paragraph between a sheet's title and its table."""
    return "\n".join(text.split("\n| ")[0].strip().splitlines()[2:]).strip()


def survey(topic):
    path = ROOT / "surveys" / f"{topic}.md"
    if not path.exists():
        sys.exit(f"no surveys/{topic}.md")
    return sections(path.read_text())


def coreset(topic):
    """{id: {column: cell}} for the coreset rows, and the claim columns: CLAIMS and the dimension columns."""
    rows, cols = {}, list(CLAIMS)
    for h, cs, _, line in table_rows(survey(topic).get("Coreset", "")):
        if h and h[0] == "paper" and row_id(line):
            rows[row_id(line)] = dict(zip(h, cs))
            extra = [x for x in h[h.index("result") + 1 : -1]] if "result" in h else []
            cols += [x for x in extra if x not in cols]
    return rows, cols


def seed_of(text):
    m = re.search(r"seed (\d+)", text or "")
    return int(m.group(1)) if m else None


def evidence(topic, pid):
    path = ROOT / "graphs" / topic / "evidence" / (pid.replace("/", "_").replace(":", "_") + ".md")
    return path.read_text().split("\n", 1)[-1].strip() if path.exists() else "(no evidence file)"


# --- re-verification -------------------------------------------------------------------------------


def reverify(topic, seed):
    path = paths(topic)[0]
    if path.exists():
        sys.exit(f"{path.relative_to(ROOT)} exists; the sample is drawn once a pass")
    rows, cols = coreset(topic)
    verified = sorted(p for p, r in rows.items() if r.get("source") == "full-text")
    if not verified:
        sys.exit(f"surveys/{topic}.md has no row verified from the full text yet")
    n = min(len(verified), max(LEAST, math.ceil(SHARE * len(rows))))
    picked = sorted(random.Random(seed).sample(verified, n))
    header = (
        f"Drawn {date.today().isoformat()} by `deeper_research/audit.py reverify`, seed {seed}: {n} of the {len(verified)} "
        f"coreset rows verified from the full text, at random. Fill every cell from the paper's full text alone, "
        f"with `uv run python -m deeper_research.audit fill {topic}`, without reading the survey's rows or their evidence; write "
        f"`n/a` where the column's definition allows it."
    )
    write(
        path,
        f"Blind re-verification: {topic}",
        header,
        ["paper"] + cols,
        [{"paper": f"[{p}]({link(p)})"} for p in picked],
    )
    print(f"wrote {path.relative_to(ROOT)}: {n} rows, seed {seed}: {', '.join(picked)}")
    print(f"columns: {', '.join(cols)}")
    return 0


def fill(topic):
    path = paths(topic)[0]
    if not path.exists():
        sys.exit(f"no {path.relative_to(ROOT)}; run `uv run python -m deeper_research.audit reverify {topic}` first")
    text = path.read_text()
    rows = table(text, "paper")
    cols = [c for c in cells_of(next(l for l in text.splitlines() if l.startswith("| paper")))][1:]
    by_id = {r["id"]: r for r in rows}
    given, problems = [], []
    for k, line in enumerate(sys.stdin, 1):
        if not line.strip():
            continue
        parts = line.rstrip("\n").split("\t", 2)
        if len(parts) < 3:
            problems.append(f"line {k}: expected `<id><TAB><column><TAB><text>`")
        elif parts[0].strip() not in by_id:
            problems.append(f"line {k}: {parts[0].strip()!r} is not a paper on the sheet")
        elif parts[1].strip() not in cols:
            problems.append(f"line {k}: {parts[1].strip()!r} is not a column; the columns are {', '.join(cols)}")
        elif not cell(parts[2]):
            problems.append(f"line {k}: the text is empty; write `n/a` where the definition allows it")
        else:
            given.append((parts[0].strip(), parts[1].strip(), cell(parts[2])))
    if problems:
        sys.exit("\n".join(problems) + f"\nnothing written: {len(problems)} line(s) wrong")
    if not given:
        sys.exit("no `<id><TAB><column><TAB><text>` lines on stdin; nothing written")
    for pid, col, val in given:
        by_id[pid][col] = val
    write(path, f"Blind re-verification: {topic}", header_of(text), ["paper"] + cols, rows)
    left = sum(1 for r in rows for c in cols if not r.get(c))
    print(f"{path.relative_to(ROOT)}: {len(given)} cell(s) written; {left} still empty")
    return 0


def compare(topic):
    src, path, _ = paths(topic)
    if not src.exists():
        sys.exit(f"no {src.relative_to(ROOT)}; run `uv run python -m deeper_research.audit reverify {topic}` first")
    text = src.read_text()
    cols = cells_of(next(l for l in text.splitlines() if l.startswith("| paper")))[1:]
    rows = table(text, "paper")
    empty = [f"{r['id']} {c}" for r in rows for c in cols if not r.get(c)]
    if empty:
        sys.exit(f"{src.relative_to(ROOT)} has {len(empty)} empty cell(s), e.g. {empty[:4]}; fill them first")
    if path.exists() and any(r.get("agrees") for r in table(path.read_text(), "paper")):
        sys.exit(f"{path.relative_to(ROOT)} already has verdicts; it is written once")
    current, _ = coreset(topic)
    out = [
        {
            "paper": r["id"],
            "cell": c,
            "in the survey": current.get(r["id"], {}).get(c, "(row no longer in the coreset)"),
            "re-verified": r[c],
        }
        for r in rows
        for c in cols
    ]
    header = (
        f"From {src.name} (seed {seed_of(text)}): {len(rows)} rows, {len(out)} cells. For each cell, judge whether "
        f'the two say the same thing (docs/process.md, "Auditing the judgements"), with '
        f"`uv run python -m deeper_research.audit judge {topic} reverify`."
    )
    write(
        path,
        f"Re-verification compared: {topic}",
        header,
        ["paper", "cell", "in the survey", "re-verified", "agrees", "reason"],
        out,
    )
    print(f"wrote {path.relative_to(ROOT)}: {len(out)} cells of {len(rows)} rows to judge")
    return 0


# --- faithfulness ----------------------------------------------------------------------------------


def sentences(output):
    """(section, line number, sentence) for every sentence of the output after its legend."""
    lines = output.splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("## ")), len(lines))
    section, block, out = "", [], []

    def flush():
        if not block:
            return
        text = " ".join(l.strip() for _, l in block)
        text = re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", text)
        first = block[0][0]
        pos = 0
        for m in re.finditer(r"[.!?][*_)\]”\"]*\s+(?=[A-Z\[(“\"*`])", text):
            if ABBREV.search(text[: m.start() + 1]):
                continue
            out.append((section, first, text[pos : m.end()].strip()))
            pos = m.end()
        if text[pos:].strip():
            out.append((section, first, text[pos:].strip()))
        block.clear()

    for i in range(start, len(lines)):
        l = lines[i]
        if l.startswith("#"):
            flush()
            section = l.lstrip("#").strip() if l.startswith("## ") else section
        elif not l.strip() or re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", l) or l.startswith("|"):
            flush()
            if l.strip() and not l.startswith("|"):
                block.append((i + 1, l))
        else:
            block.append((i + 1, l))
    flush()
    return out


def cited(text):
    return sorted(set(LINK.findall(text)) | set(BARE_ID.findall(text)))


def trace(topic, n, seed):
    path = paths(topic)[2]
    if path.exists():
        sys.exit(f"{path.relative_to(ROOT)} exists; the sample is drawn once a pass")
    out_path = ROOT / "outputs" / f"{topic}.md"
    if not out_path.exists():
        sys.exit(f"no outputs/{topic}.md; write the output first (docs/process.md, step 6)")
    rows, cols = coreset(topic)
    cand = [
        (s, ln, t, ids)
        for s, ln, t in sentences(out_path.read_text())
        if s not in SKIP and (ids := [i for i in cited(t) if i in rows])
    ]
    if not cand:
        sys.exit(f"outputs/{topic}.md has no sentence citing a coreset paper")
    k = min(n, len(cand))
    picked = sorted(random.Random(seed).sample(range(len(cand)), k))
    table_rows_ = [
        {
            "sentence": f"S{j}: {cand[i][2]}",
            "section": cand[i][0],
            "line": str(cand[i][1]),
            "cites": ", ".join(cand[i][3]),
        }
        for j, i in enumerate(picked, 1)
    ]
    papers = sorted({p for i in picked for p in cand[i][3]})
    tail = ["## Rows and evidence", ""]
    for p in papers:
        r = rows[p]
        tail += [f"### {p}", "", f"- role: {r.get('role', '')}; source: {r.get('source', '')}"]
        tail += [f"- {c}: {r.get(c, '')}" for c in cols]
        tail += ["", "Evidence:", "", evidence(topic, p), ""]
    header = (
        f"Drawn {date.today().isoformat()} by `deeper_research/audit.py trace`, seed {seed}: {k} of the {len(cand)} "
        f"sentences of outputs/{topic}.md that cite a coreset paper, at random. Judge each against the rows and "
        f'evidence below alone (docs/process.md, "Auditing the judgements"), with '
        f"`uv run python -m deeper_research.audit judge {topic} faithfulness`."
    )
    write(
        path,
        f"Faithfulness sample: {topic}",
        header,
        ["sentence", "section", "line", "cites", "verdict", "reason"],
        table_rows_,
        "\n".join(tail),
    )
    print(f"wrote {path.relative_to(ROOT)}: {k} of {len(cand)} citing sentences, seed {seed}; {len(papers)} rows")
    return 0


# --- judging and the line --------------------------------------------------------------------------


def judge(topic, which):
    _, cmp_path, faith_path = paths(topic)
    path = cmp_path if which == "reverify" else faith_path
    if not path.exists():
        then = "compare" if which == "reverify" else "trace"
        sys.exit(f"no {path.relative_to(ROOT)}; run `uv run python -m deeper_research.audit {then} {topic}` first")
    text = path.read_text()
    head, _, tail = text.partition("\n## Rows and evidence")
    if which == "reverify":
        cols, rows, verdicts, vcol = (
            ["paper", "cell", "in the survey", "re-verified", "agrees", "reason"],
            table(head, "paper"),
            AGREES,
            "agrees",
        )
        key = {(r["paper"], r["cell"]): r for r in rows}
        form = "`<id><TAB><column><TAB>agree|partly|differ<TAB><reason>`"
    else:
        cols, rows, verdicts, vcol = (
            ["sentence", "section", "line", "cites", "verdict", "reason"],
            table(head, "sentence"),
            SUPPORT,
            "verdict",
        )
        key = {r["sentence"].split(":")[0]: r for r in rows}
        form = "`S<n><TAB>supported|partly|unsupported<TAB><reason>`"
    given, problems = {}, []
    for k, line in enumerate(sys.stdin, 1):
        if not line.strip():
            continue
        parts = line.rstrip("\n").split("\t")
        need = 4 if which == "reverify" else 3
        if len(parts) < need:
            problems.append(f"line {k}: expected {form}")
            continue
        parts = parts[: need - 1] + ["\t".join(parts[need - 1 :])]
        kk = (parts[0].strip(), parts[1].strip()) if which == "reverify" else parts[0].strip()
        v, reason = parts[-2].strip().lower(), cell(parts[-1])
        if kk not in key:
            problems.append(f"line {k}: {kk!r} is not on the sheet")
        elif v not in verdicts:
            problems.append(f"line {k}: verdict {v!r} is not one of {', '.join(verdicts)}")
        elif len(reason.split()) < 2:
            problems.append(f"line {k}: a reason of a few words is needed")
        elif given.get(kk, (v, reason)) != (v, reason):
            problems.append(f"line {k}: {kk} is judged twice, differently")
        else:
            given[kk] = (v, reason)
    if problems:
        sys.exit("\n".join(problems) + f"\nnothing written: {len(problems)} line(s) wrong")
    if not given:
        sys.exit(f"no {form} lines on stdin; nothing written")
    for kk, (v, reason) in given.items():
        key[kk][vcol], key[kk]["reason"] = v, reason
    title = head.splitlines()[0][2:]
    write(path, title, header_of(head), cols, rows, ("## Rows and evidence" + tail) if tail else "")
    left = sum(1 for r in rows if not r.get(vcol))
    print(f"{path.relative_to(ROOT)}: {len(given)} verdict(s) written; {left} of {len(rows)} still unjudged")
    return 0


def summary(topic):
    """(the `Judgement audit` line's value, None), or (None, what is missing)."""
    src, cmp_path, faith_path = paths(topic)
    for p, then in ((src, "reverify"), (cmp_path, "compare"), (faith_path, "trace")):
        if not p.exists():
            return None, f"no {p.relative_to(ROOT)} (`uv run python -m deeper_research.audit {then} {topic}`)"
    cmp_rows = table(cmp_path.read_text(), "paper")
    faith_text = faith_path.read_text().partition("\n## Rows and evidence")[0]
    faith_rows = table(faith_text, "sentence")
    open_ = [
        f"{cmp_path.name}: {sum(1 for r in cmp_rows if r.get('agrees') not in AGREES)}",
        f"{faith_path.name}: {sum(1 for r in faith_rows if r.get('verdict') not in SUPPORT)}",
    ]
    if any(not x.endswith(": 0") for x in open_) or not cmp_rows or not faith_rows:
        return None, f"rows without a verdict: {'; '.join(open_)}"
    a = {v: sum(1 for r in cmp_rows if r["agrees"] == v) for v in AGREES}
    f = {v: sum(1 for r in faith_rows if r["verdict"] == v) for v in SUPPORT}
    n_rows = len({r["paper"] for r in cmp_rows})
    value = (
        f"re-verification: {a['agree']} of {len(cmp_rows)} cells agree, {a['partly']} partly, {a['differ']} "
        f"differ, over {n_rows} rows (seed {seed_of(src.read_text())}); faithfulness: {f['supported']} of "
        f"{len(faith_rows)} sentences supported, {f['partly']} partly, {f['unsupported']} unsupported (seed "
        f"{seed_of(faith_path.read_text())})"
    )
    return value, None


def line(topic):
    value, missing = summary(topic)
    if missing:
        sys.exit(missing)
    print(f"- **Judgement audit:** {value}")
    return 0


def main(argv):
    cmds = ("reverify", "fill", "compare", "trace", "judge", "line")
    if len(argv) < 2 or argv[0] not in cmds:
        print(__doc__.strip())
        return 2
    cmd, topic, rest = argv[0], argv[1], argv[2:]
    if cmd in ("reverify", "trace"):
        opts = dict(zip(rest[::2], rest[1::2]))
        allowed = {"--seed"} | ({"--n"} if cmd == "trace" else set())
        if len(rest) % 2 or set(opts) - allowed:
            usage(f"unknown option(s) {rest}")
        try:
            seed, n = int(opts.get("--seed", 1)), int(opts.get("--n", N_TRACE))
        except ValueError:
            usage("--seed and --n take whole numbers")
        return reverify(topic, seed) if cmd == "reverify" else trace(topic, n, seed)
    if cmd == "judge":
        if len(rest) != 1 or rest[0] not in ("reverify", "faithfulness") or sys.stdin.isatty():
            print(__doc__.strip())
            return 2
        return judge(topic, rest[0])
    if rest or (cmd == "fill" and sys.stdin.isatty()):
        print(__doc__.strip())
        return 2
    return {"fill": fill, "compare": compare, "line": line}[cmd](topic)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
