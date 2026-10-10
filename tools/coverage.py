# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy==2.5.3", "scikit-learn==1.9.1", "igraph==1.0.0", "leidenalg==0.12.0"]
# ///
"""How well the coreset covers the pool, and the coverage test's sample and sheet (docs/process.md, step 7).

Usage:
  uv run tools/coverage.py radius <topic> [--loo]
  uv run tools/coverage.py draw <topic> <R> [--n 10] [--seed <R>]
  python3 tools/coverage.py judge <topic> <R> [--recency] < lines   (one `<id><TAB><verdict><TAB><reason>` per line)
  python3 tools/coverage.py line <topic> <R>

A pool paper's distance from the coreset is 1 minus its similarity to the nearest coreset row, under the clustering's
`combined` measure (tools/cluster.py). That measure is built from neighbour ranks, so the distance reads as a share of
the pool: 0.05 means the nearest coreset row is, on average over the two directions, among the paper's nearest 5% of
pool papers. The coreset's radius is the largest such distance over the pool papers outside the coreset.

`radius` prints the radius (max, p90 and mean) and the ten worst-covered pool papers, each with its nearest coreset row.
With --loo, it also prints, per coreset row, how much the radius and the p90 grow when that row alone is removed: a
proxy for how much each row is needed.

`draw` writes round R's coverage sheet, graphs/<topic>/coverage-<R>.md: --n (10) pool papers drawn at random, with the
seed given (R by default), from the worst-covered quarter of the pool papers that are not coreset rows and were not
sampled in an earlier round; at least 2 x --n papers are eligible, the quarter being widened to reach that. Each row
gives the paper, how it was drawn, its distance, its nearest coreset row, and empty `verdict` and `reason` cells. The
header records the date, the seed, the eligible set and the radius. It refuses to overwrite an existing sheet.

`judge` writes verdicts into the sheet from stdin. A verdict is `no change`, `changes <target>` (a target of the input's
`Coreset Spec`, as tools/inputs.py reads them), or `new cluster`; the reason is one sentence. With --recency, each line
instead adds a candidate from the fresh recency query, as a row drawn as `recency query`; its ID must be a paper ID
(docs/formats.md, "Paper IDs"). It refuses the whole batch on any bad line.

`line` prints the round's `Coverage test` line from the sheet, ready to paste: K and N counted by script, each counted
candidate with its target and reason. It refuses while a row has no verdict. When a row is judged `new cluster`, the
line ends with a placeholder for the proposed cluster's name, which the main session replaces once the recluster has
shown whether it formed (docs/process.md, "Returning to step 3"). It also prints the round's one-sided 95% upper bound
(Clopper-Pearson) on the share of the worst-covered quarter that would change the output, from the drawn rows alone.

`radius` and `draw` need numpy and the clustering's packages (uv); `judge` and `line` are standard library only, and
tools/gates.py reads the sheets with this module's `sheet` function. Usage errors exit with status 2.
"""

import json
import math
import random
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from check import ID, cells_of, link, row_id, sections, table_rows  # noqa: E402

N_DRAW = 10          # pool papers drawn per round; the recency query adds to these (docs/process.md: 10-15 in all)
QUARTER = 0.25       # the worst-covered share of the eligible pool papers that the draw is made from
WORST = 10           # worst-covered papers listed by `radius`
COLUMNS = ["paper", "drawn as", "distance", "nearest row", "verdict", "reason"]
VERDICT = re.compile(r"^(no change|new cluster|changes (.+))$")


def usage(msg):
    print(f"usage error: {msg}", file=sys.stderr)
    sys.exit(2)


def sheet_path(topic, r):
    return ROOT / "graphs" / topic / f"coverage-{r}.md"


def sheet(text):
    """The rows of a coverage sheet: [{column: cell}], with `id` added from the paper link, in sheet order."""
    out = []
    for h, cs, _, line in table_rows(text or ""):
        if h and h[0] == "paper" and "verdict" in h:
            row = dict(zip(h, cs))
            row["id"] = row_id(line)
            out.append(row)
    return out


def counted(rows):
    """(changed, new) rows of a judged sheet: those whose verdict is `changes <target>`, and `new cluster`."""
    changed = [r for r in rows if r.get("verdict", "").startswith("changes ")]
    new = [r for r in rows if r.get("verdict", "") == "new cluster"]
    return changed, new


def upper_bound(k, n, conf=0.95):
    """One-sided Clopper-Pearson upper bound on a binomial share, by bisection on the binomial tail."""
    if n == 0:
        return 1.0
    if k >= n:
        return 1.0

    def tail(p):   # P(X <= k) for X ~ Bin(n, p)
        return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k + 1))
    lo, hi = k / n, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if tail(mid) > 1 - conf:
            lo = mid
        else:
            hi = mid
    return hi


# --- distances: numpy and the clustering's measure -----------------------------------------------


def distances(topic):
    """(pool ids, coreset ids, D) where D[i][j] is the distance of pool paper i from coreset row j. Papers without an
    embedding are left out, as they are from the clustering."""
    import numpy as np
    from cluster import C_REFS, combined_sim, refs_sim, text_sim
    from graph import parse
    survey = ROOT / "surveys" / f"{topic}.md"
    pool_path = ROOT / "graphs" / topic / "pool.json"
    for path, then in ((survey, "steps 0-5 of docs/process.md"), (pool_path, f"`python3 tools/pool.py {topic}`")):
        if not path.exists():
            sys.exit(f"no {path.relative_to(ROOT)}; run {then} first")
    secs = sections(survey.read_text())
    core = {row_id(l) for h, _, _, l in table_rows(secs.get("Coreset", "")) if h and h[0] == "paper"} - {None}
    cache = json.loads(pool_path.read_text())["papers"]
    ids = sorted(a for a in parse(topic)[4] if a in cache and cache[a].get("embedding"))
    if not core & set(ids):
        sys.exit(f"surveys/{topic}.md has no coreset row with an embedding in pool.json; nothing covers the pool yet")
    recs = [cache[a] for a in ids]
    S = combined_sim(text_sim(recs), refs_sim(recs), recs, C_REFS)
    cols = [i for i, a in enumerate(ids) if a in core]
    return ids, [ids[j] for j in cols], 1.0 - S[:, cols], np.array([a in core for a in ids])


def summary(d):
    import numpy as np
    return float(d.max()), float(np.percentile(d, 90)), float(d.mean())


def radius(topic, loo):
    import numpy as np
    ids, core, D, in_core = distances(topic)
    outside = ~in_core
    near = D[outside].min(axis=1)
    arg = D[outside].argmin(axis=1)
    mx, p90, mean = summary(near)
    out_ids = [a for a, c in zip(ids, in_core) if not c]
    print(f"{topic}: {len(core)} coreset rows cover {len(out_ids)} other pool papers (combined measure; a distance is "
          f"the nearest coreset row's rank among the paper's neighbours, as a share of the pool)")
    print(f"radius: max {mx:.3f}, p90 {p90:.3f}, mean {mean:.3f}")
    print(f"\nworst covered:")
    for i in np.argsort(-near)[:WORST]:
        print(f"  {out_ids[i]}  {near[i]:.3f}  nearest row {core[arg[i]]}")
    if loo:
        print("\nleave one out: the radius without each row (max, p90), and the growth over the full coreset")
        res = []
        for j, a in enumerate(core):
            keep = [x for x in range(len(core)) if x != j]
            # The removed row becomes a pool paper to be covered too.
            rows = outside | (np.arange(len(ids)) == ids.index(a))
            d = D[rows][:, keep].min(axis=1)
            m, p, _ = summary(d)
            res.append((m - mx, p - p90, a, m, p))
        for dm, dp, a, m, p in sorted(res, reverse=True):
            print(f"  {a}  max {m:.3f} ({dm:+.3f}), p90 {p:.3f} ({dp:+.3f})")
    return 0


def earlier(topic, r):
    """IDs on the sheets of rounds before R."""
    seen = set()
    for x in range(1, r):
        p = sheet_path(topic, x)
        if p.exists():
            seen |= {row["id"] for row in sheet(p.read_text())}
    return seen


def write_sheet(path, topic, r, header, rows):
    """Write a coverage sheet: a title, the header paragraph, and the table of `rows` ([{column: cell}])."""
    lines = [f"# Coverage test, round {r}: {topic}", "", header, "",
             "| " + " | ".join(COLUMNS) + " |", "| " + " | ".join("--" for _ in COLUMNS) + " |"]
    lines += ["| " + " | ".join(row.get(c, "") for c in COLUMNS) + " |" for row in rows]
    path.write_text("\n".join(lines) + "\n")


def titles(topic):
    from graph import parse
    return {a: v.get("title") or a for a, v in parse(topic)[4].items()}


def cell(text):
    return re.sub(r"\s+", " ", text or "").replace("|", "/").strip()


def draw(topic, r, n, seed):
    import numpy as np
    path = sheet_path(topic, r)
    if path.exists():
        sys.exit(f"{path.relative_to(ROOT)} exists; a round's sample is drawn once. Judge it with "
                 f"`python3 tools/coverage.py judge {topic} {r}`, or draw round {r + 1}")
    ids, core, D, in_core = distances(topic)
    seen = earlier(topic, r)
    near, arg = D.min(axis=1), D.argmin(axis=1)
    eligible = [i for i, a in enumerate(ids) if not in_core[i] and a not in seen]
    if len(eligible) < n:
        sys.exit(f"only {len(eligible)} pool papers outside the coreset are left to sample; a round needs {n}")
    eligible.sort(key=lambda i: (-near[i], ids[i]))
    m = min(len(eligible), max(2 * n, math.ceil(QUARTER * len(eligible))))
    worst = eligible[:m]
    picked = sorted(random.Random(seed).sample(worst, n), key=lambda i: -near[i])
    names = titles(topic)
    out_near = near[[i for i in range(len(ids)) if not in_core[i]]]
    mx, p90, mean = summary(out_near)
    header = (f"Drawn {date.today().isoformat()} by `tools/coverage.py draw`, seed {seed}: {n} pool papers at random "
              f"from the {m} worst-covered of the {len(eligible)} pool papers outside the coreset and not sampled in an "
              f"earlier round (distance at least {near[worst[-1]]:.3f}). Coverage of the pool by the coreset's "
              f"{len(core)} rows: max {mx:.3f}, p90 {p90:.3f}, mean {mean:.3f}. Judge each row with "
              f"`python3 tools/coverage.py judge {topic} {r}`; add the recency query's candidates with `--recency`.")
    rows = [{"paper": f"[{cell(names.get(ids[i], ids[i]))}]({link(ids[i])})", "drawn as": "worst-covered",
             "distance": f"{near[i]:.3f}", "nearest row": core[arg[i]]} for i in picked]
    write_sheet(path, topic, r, header, rows)
    print(f"wrote {path.relative_to(ROOT)}: {n} candidates, seed {seed}, from the {m} worst-covered of "
          f"{len(eligible)} eligible pool papers")
    print(f"radius: max {mx:.3f}, p90 {p90:.3f}, mean {mean:.3f}")
    for i in picked:
        print(f"  {ids[i]}  {near[i]:.3f}  nearest row {core[arg[i]]}")
    return 0


# --- judging and the log line: standard library only ----------------------------------------------


def read_sheet(topic, r):
    path = sheet_path(topic, r)
    if not path.exists():
        sys.exit(f"no {path.relative_to(ROOT)}; run `uv run tools/coverage.py draw {topic} {r}` first")
    return path, path.read_text()


def judge(topic, r, recency):
    from inputs import read_targets
    targets = read_targets(topic)[0]
    path, text = read_sheet(topic, r)
    rows = sheet(text)
    by_id = {row["id"]: row for row in rows}
    names = None
    given, problems = {}, []
    for k, line in enumerate(sys.stdin, 1):
        if not line.strip():
            continue
        parts = line.rstrip("\n").split("\t", 2)
        if len(parts) < 3:
            problems.append(f"line {k}: expected `<id><TAB><verdict><TAB><reason>`")
            continue
        pid, v, reason = parts[0].strip(), cell(parts[1]).lower(), cell(parts[2])
        m = VERDICT.match(v)
        if recency and not ID.match(pid):
            problems.append(f"line {k}: {pid!r} is not a paper ID (docs/formats.md, \"Paper IDs\"); a candidate "
                            "without one cannot join the pool, so draw another")
        elif recency and pid in by_id:
            problems.append(f"line {k}: {pid} is already on the sheet; judge it without --recency")
        elif not recency and pid not in by_id:
            problems.append(f"line {k}: {pid!r} is not on the sheet; a recency-query candidate is added with --recency")
        elif not m:
            problems.append(f"line {k}: verdict {parts[1].strip()!r} is not `no change`, `changes <target>` or "
                            "`new cluster`")
        elif m.group(2) and m.group(2).lower() not in {t.lower() for t in targets}:
            problems.append(f"line {k}: {m.group(2)!r} is not a target; the targets are {', '.join(targets)}")
        elif not reason or len(reason.split()) < 3:
            problems.append(f"line {k}: {pid} needs a reason of one sentence")
        elif given.get(pid, (v, reason)) != (v, reason):
            problems.append(f"line {k}: {pid} is judged twice, differently")
        else:
            if m.group(2):
                v = "changes " + next(t for t in targets if t.lower() == m.group(2).lower())
            given[pid] = (v, reason)
    if problems:
        sys.exit("\n".join(problems) + f"\nnothing written: {len(problems)} line(s) wrong")
    if not given:
        sys.exit("no `<id><TAB><verdict><TAB><reason>` lines on stdin; nothing written")
    for pid, (v, reason) in given.items():
        if recency:
            names = names if names is not None else titles(topic)
            rows.append({"paper": f"[{cell(names.get(pid, pid))}]({link(pid)})", "drawn as": "recency query",
                         "distance": "", "nearest row": "", "id": pid})
            by_id[pid] = rows[-1]
        by_id[pid]["verdict"], by_id[pid]["reason"] = v, reason
    head = text.split("\n| paper |")[0].rstrip("\n")
    header = "\n".join(head.splitlines()[2:]).strip()
    write_sheet(path, topic, r, header, rows)
    left = [row["id"] for row in rows if not row.get("verdict")]
    print(f"{path.relative_to(ROOT)}: {len(given)} verdict(s) written" + (" (recency-query rows added)" if recency else "")
          + f"; {len(rows)} row(s), {len(left)} still unjudged" + (f": {', '.join(left)}" if left else ""))
    return 0


def line(topic, r):
    path, text = read_sheet(topic, r)
    rows = sheet(text)
    left = [row["id"] for row in rows if not row.get("verdict")]
    if left:
        sys.exit(f"{path.relative_to(ROOT)}: {len(left)} row(s) without a verdict: {', '.join(left)}")
    changed, new = counted(rows)
    parts = ", ".join(f"{row['id']}: {row['verdict'][8:]}: {row['reason'].replace(';', ',')}" for row in changed)
    proposed = ", ".join(row["id"] for row in new)
    print(f"- **Coverage test:** round {r}: {len(changed)} of {len(rows)} sampled candidates changed the output"
          + (f" ({parts})" if parts else "")
          + "; new clusters: " + (f"<the proposed cluster, from {proposed}>" if new else "none"))
    drawn = [row for row in rows if row.get("drawn as") == "worst-covered"]
    k = sum(1 for row in drawn if row in changed)
    print(f"\nbound: {k} of the {len(drawn)} drawn candidates changed the output, so at 95% confidence at most "
          f"{100 * upper_bound(k, len(drawn)):.0f}% of the worst-covered papers would (one-sided Clopper-Pearson)")
    if new:
        print(f"proposed cluster: {proposed}; replace the placeholder once the recluster shows whether it formed")
    return 0


def main(argv):
    cmds = {"radius": 2, "draw": 3, "judge": 3, "line": 3}
    if not argv or argv[0] not in cmds or len([a for a in argv if not a.startswith("--")]) < cmds[argv[0]]:
        print(__doc__.strip())
        return 2
    cmd, topic = argv[0], argv[1]
    if cmd == "radius":
        if set(argv[2:]) - {"--loo"}:
            usage(f"unknown option(s) {argv[2:]}")
        return radius(topic, "--loo" in argv)
    try:
        r = int(argv[2])
        assert r >= 1
    except (ValueError, AssertionError):
        usage(f"the round must be a number from 1, not {argv[2]!r}")
    rest = argv[3:]
    if cmd == "draw":
        opts = dict(zip(rest[::2], rest[1::2]))
        if len(rest) % 2 or set(opts) - {"--n", "--seed"}:
            usage(f"unknown option(s) {rest}")
        try:
            n, seed = int(opts.get("--n", N_DRAW)), int(opts.get("--seed", r))
        except ValueError:
            usage("--n and --seed take whole numbers")
        return draw(topic, r, n, seed)
    if cmd == "judge":
        if set(rest) - {"--recency"} or sys.stdin.isatty():
            print(__doc__.strip())
            return 2
        return judge(topic, r, "--recency" in rest)
    if rest:
        usage(f"unknown option(s) {rest}")
    return line(topic, r)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
