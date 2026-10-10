"""The gates of a pass: what each step must have left behind in the files, checked by tools/check.py (docs/gates.md).

No command line of its own: `python3 tools/check.py <topic> [--gate G<n>] [--status]` runs it.

A gate is a point in the order of operations (docs/process.md) after which a set of requirements must hold:

  G0 ready             after step 0: the pass's log entry, its dimensions (declared, or proposed with their values),
                       a passing preflight
  G1 pool complete     after step 2: orientation and expansion recorded, rejections recorded, the pool fetched, the
                       fringe routes collected, screened and added
  G2 clusters named    after step 3: this pass's clustering, named, written into the pool, and logged
  G3 coreset selected  after step 4: every required role filled or its empty slot recorded, dissent searched and quoted,
                       bridges and the fringe quota, no empty cell
  G4 verified          after step 5: every verified row's evidence recorded under its own ID, its full-text quotes
                       found verbatim and in order, a dissent row's quoted claim among them; every row still `abstract`
                       listed as needing verification, H10 if over 20%
  G5 pass ended        after step 7: the output and its sections, a converged coverage test or a recorded halt, each
                       round's sheet backing its line, no late paper left, the judgement audits, the closing log lines

Requirements are cumulative: a gate's check also checks every earlier gate. Which gates are required is worked out from
the files: the log's `Gates` line (the gates the main session has passed), plus a safety net of evidence that a later
step has started, such as a `Clustering` line in the current entry or, on a first pass, Coreset rows. An open halt
(`Halts` entry with the decision `pending`) fails every `--gate` until the user decides; the safety net still applies. A
pass the user ended at a halt (`Ended: halted (<id>)`, with the decision recorded) needs only the gates it declared, and
its closing lines. A requirement the user has waived, in the log's `Waivers` line, is reported and does not fail.

`--gate` is passed only when nothing fails: integrity, gates and history alike. A full-text quote that cannot be checked
because the full text is not fetched is a note in the plain check, and a failure under `--gate G4` or later.

The checks are of records, not of judgement: that a screening was recorded, not that it was right (docs/gates.md).
"""

import json
import re
import subprocess
import unicodedata

from check import (ABSTRACT_SHARE, BARE_ID, CORESET_COLUMNS, FRINGE_QUOTA, NEEDED, ROOT, read, row_id, sections,
                   table_rows, words)

GATES = [("G0", "ready"), ("G1", "pool complete"), ("G2", "clusters named"), ("G3", "coreset selected"),
         ("G4", "verified"), ("G5", "pass ended")]
PREFLIGHT = ["snippet_search", "search_papers_by_relevance", "get_paper", "get_citations", "WebSearch", "Graph API",
             "arXiv", "uv", "Asta key"]
PLACEHOLDER = re.compile(r"<[a-z][^<>\n]{0,80}>")
COMPUTED_ID = re.compile(r"\bc\d+\b")
QUOTE = re.compile(r"[\"“][^\"”]{12,}[\"”]")
REPEATABLE = {"Coverage test"}
SOURCE_RANK = {"abstract": 0, "snippet": 1, "full-text": 1}   # `snippet` only in legacy surveys and old commits
QUOTE_WORDS = 6        # the fewest words in each part of an evidence quote, so that a quote cannot be vacuous
QUOTE_WINDOW = 3000    # the most characters of normalised text between two parts of an elided quote
COVERAGE_SAMPLE = 10   # the fewest sampled candidates in a coverage-test round (docs/process.md: 10-15)
TOKENS = re.compile(r"^[^:,]+:\s*~?\d[\d,.]*\s*[kKM]?$")


# --- parsing --------------------------------------------------------------------------------------


def labelled(lines):
    """Map each `- **Label:** value` bullet to its values (one per occurrence), joined with its continuation lines.
    A parenthesis after the label is dropped: `Orientation (WebSearch)` is `Orientation`."""
    out, item = {}, None
    for line in lines:
        m = re.match(r"^- \*\*([^*]+?):\*\*\s*(.*)$", line)
        if m:
            item = [m.group(2)]
            out.setdefault(re.sub(r"\s*\(.*\)$", "", m.group(1)).strip(), []).append(item)
        elif item is not None and line[:1] in (" ", "\t") and line.strip():
            item.append(line.strip())
        elif not line.strip() or line.startswith("#"):
            item = None
    return {k: [" ".join(v) for v in vs] for k, vs in out.items()}


def log_entries(log_text):
    """The retrieval log's `### Pass YYYY-MM-DD` entries, in order: {date, text, lines}."""
    entries, cur = [], None
    for line in log_text.splitlines():
        m = re.match(r"^### Pass (\d{4}-\d{2}-\d{2})", line)
        if m:
            cur = {"date": m.group(1), "raw": []}
            entries.append(cur)
        elif cur is not None:
            cur["raw"].append(line)
    for e in entries:
        e["text"] = "\n".join(e["raw"])
        e["lines"] = labelled(e["raw"])
    return entries


def halts(lines):
    """{halt id: [decision, ...]} from the `Halts` line: entries `<id> — <what happened> — <decision>`, separated by
    `;`. The decision is what follows the entry's last `—`, since what happened may itself contain one."""
    text = " ".join(lines.get("Halts", []))
    out = {}
    for entry in re.split(r";\s*(?=H\d+\s*—)", text):
        m = re.match(r"\s*(H\d+)\s*—\s*(.*)—\s*(.*?)\s*$", entry)
        if m:
            out.setdefault(m.group(1), []).append(m.group(3).strip())
    return out


def gate_line(lines):
    return {int(g) for g in re.findall(r"\bG([0-5])\b", " ".join(lines.get("Gates", [])))}


def waivers(lines):
    return set(re.findall(r"\b(g\d\.[a-z0-9-]+)\s*—", " ".join(lines.get("Waivers", []))))


def proposed_dimensions(text):
    """{name: set of values} from a `Dimensions` line that proposes them, in the input's form:
    `proposed: `name` — values: `a`, `b`; `other` — values: `c`, `d``."""
    out = {}
    for part in text.partition("proposed")[2].split(";"):
        m = re.search(r"`([a-z0-9][a-z0-9-]*)`\s*—\s*values:(.*)$", part)
        if m:
            out[m.group(1)] = set(re.findall(r"`([^`]+)`", m.group(2)))
    return out


def mentions(text, *parts):
    """Whether `text` holds the parts in order, separated by a dash: `c — dissent`."""
    return re.search(r"\s*[—-]+\s*".join(re.escape(p) for p in parts), text or "") is not None


# --- context --------------------------------------------------------------------------------------


class Ctx:
    """Everything the requirements read, gathered once by tools/check.py."""

    def __init__(self, topic, secs, structure, rows, coreset_ids, abstract, output, dims, steering, targets,
                 proposed=False):
        self.topic, self.secs, self.output = topic, secs, output
        # The dimensions: declared in the input, or, when it declares none, proposed in the `Dimensions` line.
        self.dims, self.proposed, self.steering, self.targets = dims, proposed, steering or {}, targets
        self.rows, self.coreset_ids, self.abstract = rows, coreset_ids, abstract
        s = structure or {}
        self.clusters, self.computed = s.get("clusters", {}), s.get("computed", {})
        self.cluster_rows = s.get("cluster_rows", [])
        self.pool, self.pool_cluster, self.titles = s.get("pool", set()), s.get("pool_cluster", {}), s.get("titles", {})
        self.report, self.roles, self.bridges = s.get("report"), s.get("roles", {}), s.get("bridges", set())
        self.entries = log_entries(secs.get("Retrieval log", ""))
        self.cur = self.entries[-1] if self.entries else None
        self.L = self.cur["lines"] if self.cur else {}
        # Without an entry, g0.entry fails; the empty date keeps the date comparisons of other requirements working.
        self.date = self.cur["date"] if self.cur else ""
        self.first_pass = len(self.entries) <= 1
        self.open_work = labelled(secs.get("Open work", "").splitlines())
        self.halts, self.waived, self.declared = halts(self.L), waivers(self.L), gate_line(self.L)
        d = ROOT / "graphs" / topic
        self.records = json.loads(read(d / "pool.json") or '{"papers": {}}')["papers"]
        self.fringe = json.loads(read(d / "fringe.json") or "null")
        self.screen = read(d / "fringe-screen.md")
        self.rejected = read(d / "rejected.md")

    def line(self, label):
        return " ".join(self.L.get(label, []))

    def ow(self, label):
        return " ".join(self.open_work.get(label, []))

    def pending(self):
        return sorted(h for h, ds in self.halts.items() if any(d.lower().startswith("pending") for d in ds))

    def assigned(self):
        r = self.report or {}
        a = dict(r.get("assignment", {}))
        a.update({p: x["cluster"] for p, x in r.get("late", {}).items()})
        return a


# --- requirements ---------------------------------------------------------------------------------
# Each returns None when it holds, or a string saying what is missing.


def need_lines(c, *labels):
    missing = [l for l in labels if not any(v.strip() for v in c.L.get(l, []))]   # an empty line is a missing one
    return f"the log entry of {c.date} has no `{'`, `'.join(missing)}` line" if missing else None


def r_entry(c):
    return None if c.cur else "the Retrieval log has no `### Pass YYYY-MM-DD` entry for this pass"


def r_placeholders(c):
    text = (c.cur["text"] if c.cur else "") + "\n" + c.secs.get("Open work", "")
    found = sorted(set(PLACEHOLDER.findall(text)))
    return f"template placeholders left in the log entry or Open work: {found[:6]}" if found else None


def r_labels(c):
    twice = sorted(k for k, v in c.L.items() if len(v) > 1 and k not in REPEATABLE)
    return f"log lines written twice in one entry: {twice}; update the line instead" if twice else None


def r_dimensions(c):
    if (m := need_lines(c, "Dimensions")):
        return m
    text = c.line("Dimensions")
    if not c.proposed:
        if c.dims and "declared in the input" not in text:
            return "the input declares dimensions, but the `Dimensions` line does not say `declared in the input`"
        if c.dims:
            return None
    form = "``proposed: `<name>` — values: `<a>`, `<b>`; `<name>` — values: ...``"
    if not c.dims:
        return f"the input declares no dimensions: propose them in the `Dimensions` line, in the form {form}"
    few = sorted(n for n, v in c.dims.items() if len(v) < 2)
    return f"proposed dimensions with fewer than two values: {few}; the form is {form}" if few else None


def r_preflight(c):
    if "H1" in c.halts:
        return None
    if (m := need_lines(c, "Preflight")):
        return m
    bad = []
    for name in PREFLIGHT:
        hit = next((v for v in (p.strip() for p in c.line("Preflight").split("|")) if v.startswith(name + " ")), None)
        if hit is None or not re.match(rf"{re.escape(name)} (ok|set)\b", hit):
            bad.append(name)
    return f"`Preflight` does not show these checks passing: {bad}; a failed check halts the pass (H1)" if bad else None


def frontier(c):
    m = re.search(r"frontier candidates:\s*(.*)$", c.line("Orientation"))
    return BARE_ID.findall(m.group(1)) if m else []


def r_orientation(c):
    if (m := need_lines(c, "Orientation", "Recency window")):
        return m
    ids = frontier(c)
    if not ids:
        return "`Orientation` lists no frontier candidates by ID (`; frontier candidates: <id>, ...`)"
    out = sorted(set(ids) - c.pool)
    return f"frontier candidates not in the pool: {out}; add them with `tools/assign.py add`" if out else None


def r_expansion(c):
    if (m := need_lines(c, "Expansion")):
        return m
    # A candidate counts as traversed where a part of the line that opens with a direction gives it a count:
    # `backward from <id> (40), <id> (35)`.
    traversed = set()
    for part in c.line("Expansion").split(";"):
        part = part.strip()
        if re.match(r"(backward|forward|both)\b", part) and not re.search(r"\bnot\b", part, re.I):
            traversed |= set(re.findall(rf"{BARE_ID.pattern}\s*\(\d+\)", part))
    out = [i for i in frontier(c) if i not in traversed]
    return (f"`Expansion` does not name these frontier candidates as traversed, in the form `backward from <id> (<n>), "
            f"...`: {out}") if out else None


def r_errored(c):
    if (m := need_lines(c, "Errored queries")):
        return m
    text = c.line("Errored queries")
    entries = re.findall(r"\"[^\"]*\"\s*\(([^()]*)\)", text)
    if not entries and text.strip().lower().startswith("none"):
        return None   # a `none` followed by entries is read by its entries
    if not entries:
        return "`Errored queries` is neither `none` nor in the form `\"<query>\" (...; retried at the end of the step: ok | failed)`"
    if any("retried at the end of the step:" not in e for e in entries):
        return "an errored query has no retry outcome (`retried at the end of the step: ok | failed`)"
    if any(re.search(r"retried at the end of the step:\s*failed", e) for e in entries) and "H2" not in c.halts:
        return "an errored query still failed after its retry, but `Halts` has no H2"
    return None


def r_rejected(c):
    # A pass that judged every candidate in scope says so in its `Expansion` line, rather than having nothing to show.
    if re.search(r"\brejected: none\b", c.line("Expansion")):
        return None
    if not c.rejected:
        return f"graphs/{c.topic}/rejected.md does not exist: record each out-of-scope candidate with `tools/assign.py reject`"
    dates = [cs[1] for h, cs, _, _ in table_rows(c.rejected) if h and h[0] == "paper" and len(cs) > 1]
    if not any(d >= c.date for d in dates):
        return (f"no rejection recorded since {c.date} (`tools/assign.py reject`); if none was out of scope, end the "
                f"`Expansion` line with `; rejected: none`")
    return None


def pool_step(c):
    """What fetches papers added to the pool and prints the `Pool` line: `pool.py` before this pass's clustering, and
    `assign.py late` after it, which also places them in their nearest cluster."""
    if c.report and c.report.get("generated", "") >= c.date:
        return f"`uv run tools/assign.py late {c.topic}`"
    return f"`python3 tools/pool.py {c.topic}`"


def r_fetched(c):
    out = sorted(c.pool - set(c.records))
    return (f"{len(out)} pool paper(s) not fetched: {out[:8]}; run {pool_step(c)} and paste the `Pool` line it prints"
            if out else None)


def screened(c):
    """{s2: (verdict, reason)} from the fringe screening sheet."""
    return {cs[0]: (cs[h.index("in scope")].strip().lower(), cs[h.index("reason")].strip())
            for h, cs, _, _ in table_rows(c.screen or "") if h and h[0] == "s2" and len(cs) == len(h)}


def r_fringe_collected(c):
    if not c.fringe:
        return f"graphs/{c.topic}/fringe.json does not exist: run `uv run tools/fringe.py collect {c.topic}`"
    if c.fringe.get("collected", "") < c.date:
        return f"the fringe routes were last collected on {c.fringe.get('collected')}, before this pass ({c.date})"
    return None


def judged(verdict, reason):
    """Whether a screening row is judged: `yes` or `no` (not `maybe`), with a reason of a few words. `tools/assign.py
    add-fringe` uses the same test."""
    return (verdict.startswith("yes") or verdict.startswith("no")) and len(words(reason)) >= 2


def r_fringe_screened(c):
    if not c.screen:
        return f"graphs/{c.topic}/fringe-screen.md does not exist"
    s = screened(c)
    # Every collected candidate needs its row: deleting rows must not shorten the screening.
    absent = sorted(set((c.fringe or {}).get("candidates", {})) - set(s))
    bad = [k for k, (v, r) in s.items() if not judged(v, r)]
    problems = []
    if absent:
        problems.append(f"{len(absent)} fringe candidate(s) in fringe.json have no row in the screening sheet: {absent[:4]}")
    if bad:
        problems.append(f"{len(bad)} fringe candidate(s) without an `in scope` judgement and a reason of a few words")
    return "; ".join(problems) or None


def r_fringe_added(c):
    if not (c.fringe and c.screen):
        return None  # g1.fringe-collected and g1.fringe-screened report it
    cands, missing = c.fringe.get("candidates", {}), []
    pool_titles = {" ".join(words(t)) for t in c.titles.values()}
    for s, (v, _) in screened(c).items():
        if not v.startswith("yes"):
            continue
        x = cands.get(s, {})
        pid = x.get("arxiv") or x.get("corpus")
        if pid in c.pool or " ".join(words(x.get("title", ""))) in pool_titles:
            continue
        if (x.get("title") or s) in c.ow("Papers that could not enter the pool") or (pid and pid in c.ow("Papers that could not enter the pool")):
            continue
        missing.append(pid or s)
    return (f"{len(missing)} in-scope fringe candidate(s) neither in the pool nor in Open work: {missing[:6]}; run "
            f"`python3 tools/assign.py add-fringe {c.topic}`") if missing else None


def r_fringe_line(c):
    if (m := need_lines(c, "Fringe")):
        return m
    if not c.fringe:
        return None
    text, problems = c.line("Fringe"), []
    if f"collected {c.fringe.get('collected')}" not in text:
        problems.append(f"collection date is not {c.fringe.get('collected')}")
    u = re.search(r"\((\d+) unique\)", text)
    if not u or int(u.group(1)) != len(c.fringe.get("candidates", {})):
        problems.append(f"unique candidates is not {len(c.fringe.get('candidates', {}))}")
    yes = sum(1 for v, _ in screened(c).values() if v.startswith("yes"))
    s = re.search(r"in scope (\d+)", text)
    if not s or int(s.group(1)) != yes:
        problems.append(f"in scope is not {yes}")
    return f"`Fringe` disagrees with the files: {'; '.join(problems)}; paste the line `add-fringe` prints" if problems else None


def fetched_range(c):
    """The fetch dates of the pool's records, as tools/pool.py prints them: one date, or `<first> to <last>`."""
    dates = sorted({(c.records.get(p) or {}).get("fetched") for p in c.pool | c.coreset_ids} - {None})
    return "unknown" if not dates else dates[0] if len(dates) == 1 else f"{dates[0]} to {dates[-1]}"


def r_pool_line(c):
    if (m := need_lines(c, "Pool")):
        return m
    text, problems = c.line("Pool"), []
    n = re.search(r"(\d+) papers in scope", text)
    if not (n and int(n.group(1)) == len(c.pool)):
        problems.append(f"does not say {len(c.pool)} papers in scope")
    when = fetched_range(c)
    if f"metadata fetched {when}" not in text:
        problems.append(f"does not say `metadata fetched {when}`, the fetch dates in pool.json")
    return f"`Pool` {'; '.join(problems)}; run {pool_step(c)} and paste the line it prints" if problems else None


def r_clustered(c):
    if not c.report:
        return f"graphs/{c.topic}/clusters.json does not exist"
    if c.report.get("generated", "") < c.date:
        return f"clusters.json is from {c.report.get('generated')}, before this pass: run `uv run tools/cluster.py {c.topic}`"
    return None


def r_named(c):
    if not c.cluster_rows:
        return "the Clusters table has no rows"
    cols = ["id", "name", "definition", "alignment", "alignment reason", "computed"]
    bad = sorted({r.get("id", "?") for r in c.cluster_rows for k in cols if not r.get(k) or PLACEHOLDER.search(r.get(k, ""))})
    return f"Clusters rows with an empty or placeholder cell: {bad}" if bad else None


def r_written(c):
    a = c.assigned()
    blank = sorted(p for p in c.pool if p in a and not c.pool_cluster.get(p))
    return f"{len(blank)} pool paper(s) have no cluster written: run `python3 tools/assign.py clusters {c.topic}`" if blank else None


def r_cluster_lines(c):
    if (m := need_lines(c, "Clustering", "Clustering rationale", "Clusters")):
        return m
    ids = sorted(set(COMPUTED_ID.findall(c.line("Clustering"))))
    if ids:
        return f"`Clustering` still uses computed ids {ids}: use the Clusters table's ids"
    return None


def r_clustering_matches(c):
    if not c.report or not c.L.get("Clustering"):
        return None
    text, problems = c.line("Clustering"), []
    m = re.search(r"measure (text|refs|combined)", text)
    if not m or m.group(1) != c.report.get("measure"):
        problems.append(f"measure is not {c.report.get('measure')}")
    n = re.search(r"level (\d+) clusters", text)
    if not n or int(n.group(1)) != len(c.report.get("clusters", [])):
        problems.append(f"level is not {len(c.report.get('clusters', []))} clusters")
    # The rule, with any granularity steering or --level override that moved the level, as tools/cluster.py recorded it.
    rule = c.report.get("rule", "")
    r = re.search(r"clusters by rule (.+?), stability", text)
    if not r or r.group(1).strip() != rule:
        problems.append(f"the rule is not `{rule}`")
    overrides = text.partition("manual overrides:")[2]
    if "user override" in rule and "--level" not in overrides:
        problems.append("the --level override is not logged under `manual overrides`")
    if "--level" in overrides and "user override" not in rule:
        problems.append("`manual overrides` logs a --level that clusters.json does not record")
    return f"`Clustering` disagrees with clusters.json: {'; '.join(problems)}" if problems else None


def r_clusters_line(c):
    if not c.L.get("Clusters"):
        return None
    text = c.line("Clusters")
    al = list(c.clusters.values())
    want = (len(al), al.count("high"), al.count("medium"), al.count("low"))
    m = re.search(r"(\d+) \((\d+) high, (\d+) medium, (\d+) low\)", text)
    if not m or tuple(map(int, m.groups())) != want:
        return f"`Clusters` does not read `{want[0]} ({want[1]} high, {want[2]} medium, {want[3]} low)`"
    if "not yet reviewed" in text and not c.ow("Clusters not yet reviewed by the user").strip():
        return "`Clusters` says not yet reviewed, but Open work has no `Clusters not yet reviewed by the user`"
    return None


def r_diagnosis_halts(c):
    cases = {d.get("case") for d in (c.report or {}).get("diagnostics", [])}
    need = [h for case, h in (("no structure", "H4"), ("no stable level", "H5")) if case in cases and h not in c.halts]
    return f"clusters.json diagnoses {', '.join(need)}'s condition, but `Halts` does not record it" if need else None


def r_review(c):
    if "review" in c.steering and "H13" not in c.halts:
        return "the input asks for `review: before coreset`, but `Halts` does not record H13 with the user's decision"
    return None


def empty_roles(c):
    return c.ow("Empty roles")


def r_roles(c):
    out = []
    for cid, alignment in c.clusters.items():
        for role in NEEDED.get(alignment, ()):
            if not c.roles.get(cid, {}).get(role) and not mentions(empty_roles(c), cid, role):
                out.append(f"{cid}: {role}")
    return (f"roles neither filled nor recorded under Open work's `Empty roles` (`<cluster> — <role> — <what was "
            f"searched>`): {out}") if out else None


def dissent_searches(c):
    """{cluster id: [found ids] or None for `none found`} from `Dissent searches`, whose entries read
    `<cluster id>: <what was searched> -> found: <id>, ... | none found`, separated by `|` or `;`."""
    out = {}
    for m in re.finditer(r"(?:^|[|;])\s*([a-z0-9]+(?:-[a-z0-9]+)*):\s*([^|;]*?)->\s*(found:[^|;]*|none found)",
                         c.line("Dissent searches")):
        found = None if m.group(3).startswith("none") else BARE_ID.findall(m.group(3))
        out.setdefault(m.group(1), []).append(found)
    return out


def r_dissent_searched(c):
    searches, problems = dissent_searches(c), []
    missing = [cid for cid, a in c.clusters.items() if a == "high" and cid not in searches]
    if missing:
        problems.append(f"high-alignment clusters missing from `Dissent searches` (`<cluster id>: <what was searched> "
                        f"-> found: <id> | none found`): {missing}")
    _, rows = coreset_cells(c)
    dissent = {(r["_block"], r["_id"]) for r in rows if r.get("role") == "dissent"}
    demoted = c.line("Demotions")
    for cid, results in searches.items():
        if any(found == [] for found in results):
            problems.append(f"`Dissent searches` for {cid} says found but names no paper ID")
        stray = sorted({i for found in results if found for i in found if (cid, i) not in dissent and i not in demoted})
        if stray:
            problems.append(f"`Dissent searches` for {cid} found {stray}, which are not dissent rows of {cid}")
    return "; ".join(problems) or None


def coreset_cells(c):
    header = c.rows[0][0] if c.rows else []
    return header, [dict(zip(header, cs)) | {"_id": row_id(l), "_block": (b or "").split(" — ")[0].strip()}
                    for _, cs, b, l in c.rows]


def r_dissent_quoted(c):
    _, rows = coreset_cells(c)
    out = [r["_id"] for r in rows if r.get("role") == "dissent" and not QUOTE.search(r.get("selected because", ""))]
    return f"dissent rows whose `selected because` does not quote the claim that contradicts the cluster: {out}" if out else None


def r_bridges(c):
    out = []
    for d in (c.report or {}).get("diagnostics", []):
        if d.get("case") != "clusters trade papers":
            continue
        a, b = (c.computed.get(x) for x in d.get("clusters", [None, None]))
        if None in (a, b) or frozenset((a, b)) in c.bridges:
            continue
        if not (mentions(empty_roles(c), a, f"bridge:{b}") or mentions(empty_roles(c), b, f"bridge:{a}")):
            out.append(f"{a} / {b}")
    return f"clusters that trade papers with neither a bridge row nor an `Empty roles` entry: {out}" if out else None


def r_divided(c):
    out = []
    for cl in (c.report or {}).get("clusters", []):
        cid = c.computed.get(cl["id"])
        if not cl.get("divided") or c.clusters.get(cid) != "high":
            continue
        r = c.roles.get(cid, {})
        if r.get("frontier", 0) >= 2 or r.get("bridge") or mentions(empty_roles(c), cid, "frontier") \
                or mentions(empty_roles(c), cid, "bridge"):
            continue
        out.append(cid)
    return (f"internally divided high-alignment clusters with neither a second frontier nor a bridge, nor an "
            f"`Empty roles` entry: {out}") if out else None


def r_fringe_quota(c):
    n = sum(r.get("fringe", 0) for r in c.roles.values())
    lo, hi = FRINGE_QUOTA
    return None if lo <= n <= hi else f"{n} fringe row(s); the quota is {lo}-{hi} per topic"


def r_cells(c):
    header, rows = coreset_cells(c)
    cols = [k for k in header if k in CORESET_COLUMNS or k in c.dims]
    bad = sorted({r["_id"] for r in rows for k in cols if not r.get(k, "").strip() or PLACEHOLDER.search(r.get(k, ""))})
    return f"coreset rows with an empty or placeholder cell: {bad[:10]}" if bad else None


def r_assigned(c):
    out = sorted(i for i in c.coreset_ids if not c.pool_cluster.get(i))
    return f"coreset rows for papers with no cluster yet (late papers take a role only once assigned): {out}" if out else None


def r_dimension_columns(c):
    """One Coreset column per dimension, declared or proposed, and no other extra column."""
    if not c.rows:
        return None
    header = c.rows[0][0]
    extra = sorted(k for k in header if k not in CORESET_COLUMNS and k != "source" and k not in c.dims)
    absent = sorted(d for d in c.dims if d not in header)
    problems = []
    if extra:
        problems.append(f"Coreset columns that are not dimensions (declared in the input, or proposed in the "
                        f"`Dimensions` line): {extra}")
    if absent:
        problems.append(f"dimensions without a Coreset column: {absent}")
    return "; ".join(problems) or None


def r_abstract_listed(c):
    out = sorted(i for i in c.abstract if i not in c.ow("Rows needing verification"))
    return f"`abstract` rows not listed in Open work's `Rows needing verification`: {out}" if out else None


def r_h10(c):
    if not c.rows:
        return None
    share = len(c.abstract) / len(c.rows)
    if share > ABSTRACT_SHARE and "H10" not in c.halts:
        return f"{share:.0%} of rows are `abstract`, over {ABSTRACT_SHARE:.0%}, but `Halts` does not record H10"
    return None


CLAIM_CELLS = ["method name", "method summary", "datasets / models", "metric", "result"]   # each needs evidence
EVIDENCE_LINE = re.compile(r"^((?:`[^`]+`\s*,?\s*)+)\s*—\s*(snippet|full-text|abstract)\b([^—]*)—\s*(.+)$", re.S)
ELLIPSIS = re.compile(r"\s*(?:\.\.\.|…|\[\.\.\.\])\s*")


def evidence_path(c, pid):
    return ROOT / "graphs" / c.topic / "evidence" / (pid.replace("/", "_").replace(":", "_") + ".md")


def evidence_entries(text):
    """[(cells, source, locator, quote)] from an evidence file: bullets `- `cell`, ... — source[, where] — "quote"`,
    joined with their wrapped continuation lines."""
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("- "):
            cur = [line[2:]]
            out.append(cur)
        elif cur is not None and line[:1] == " " and line.strip():
            cur.append(line.strip())
        elif not line.strip():
            cur = None
    entries = []
    for b in (" ".join(x) for x in out):
        m = EVIDENCE_LINE.match(b)
        if m:
            q = m.group(4).strip()
            q = q[1:-1] if len(q) > 1 and q[0] in "\"“" and q[-1] in "\"”" else q
            entries.append((re.findall(r"`([^`]+)`", m.group(1)), m.group(2), m.group(3).strip(" ,"), q))
        else:
            entries.append((None, None, None, b))
    return entries


def normalised(text):
    """Lower-case words, split on anything else, padded with spaces, so that a word matches only a whole word. Two
    readings of the text: with words hyphenated across a line break joined (`im-\nproves`), and without, so that a
    compound broken at its hyphen (`state-of-\nthe-art`) also matches."""
    text = unicodedata.normalize("NFKC", text).lower()
    joined = re.sub(r"([a-z0-9])-[ \t]*\n\s*([a-z0-9])", r"\1\2", text)
    return [" " + " ".join(re.findall(r"[a-z0-9]+", v)) + " " for v in (joined, text)]


def quote_parts(quote):
    """The parts of a quote elided with `...`, normalised; empty parts dropped."""
    return [p for p in (" " + " ".join(re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", x).lower())) + " "
                        for x in ELLIPSIS.split(quote)) if p.strip()]


def too_short(quote):
    parts = quote_parts(quote)
    return not parts or any(len(p.split()) < QUOTE_WORDS for p in parts)


def found_in(quote, readings):
    """Whether the quote's parts are in one reading of the text, in order, each within QUOTE_WINDOW of the last."""
    parts = quote_parts(quote)
    if not parts:
        return False
    for body in readings:
        start = body.find(parts[0])
        while start >= 0:
            end, ok = start + len(parts[0]) - 1, True
            for part in parts[1:]:
                i = body.find(part, end)
                if i < 0 or i - end > QUOTE_WINDOW:
                    ok = False
                    break
                end = i + len(part) - 1
            if ok:
                return True
            start = body.find(parts[0], start + 1)
    return False


def r_evidence(c):
    """Every row verified against the full text keeps the quotes it rests on (docs/verification.md): one for each
    claim cell and each dimension not `n/a`. Its file is headed by its own ID, and its method rests on the full text. A full-text quote must be in the fetched full text, at least QUOTE_WORDS words per part and its parts in
    order; no quote may come from a snippet, which nothing can check afterwards."""
    header, rows = coreset_cells(c)
    dims = [k for k in header if k in c.dims]
    missing, malformed, unfound, unchecked, snippets, short, foreign, no_text = [], [], [], [], [], [], [], []
    for r in rows:
        if r.get("source") in (None, "abstract"):
            continue
        path = evidence_path(c, r["_id"])
        if not path.exists():
            missing.append(r["_id"])
            continue
        raw = path.read_text()
        head = re.search(r"^# Evidence:\s*(\S+)", raw, re.M)
        if not head or head.group(1) != r["_id"]:
            foreign.append(f"{r['_id']} (headed {head.group(1) if head else 'nothing'})")
        entries = evidence_entries(raw)
        if any(e[0] is None for e in entries):
            malformed.append(r["_id"])
        if any(e[1] == "snippet" for e in entries):
            snippets.append(r["_id"])
        covered = {cell for cells, *_ in entries if cells for cell in cells}
        need = [k for k in CLAIM_CELLS + dims if r.get(k, "").strip() not in ("n/a", "")]
        if [n for n in need if n not in covered]:
            missing.append(f"{r['_id']} ({', '.join(n for n in need if n not in covered)})")
        # The abstract may carry a number, never the method (docs/verification.md).
        if r.get("source") == "full-text" and not any(s == "full-text" and "method summary" in (cells or [])
                                                      for cells, s, _, _ in entries):
            no_text.append(r["_id"])
        text = read(ROOT / "graphs" / c.topic / "fulltext" / (path.stem + ".txt"))
        readings = normalised(text) if text is not None else None
        for cells, source, _, quote in entries:
            if source != "full-text":
                continue
            if too_short(quote):
                short.append(f"{r['_id']} ({', '.join(cells)})")
            elif readings is None:
                unchecked.append(r["_id"])
            elif not found_in(quote, readings):
                unfound.append(f"{r['_id']} ({', '.join(cells)})")
    problems = []
    if missing:
        problems.append(f"verified rows without evidence for every cell not `n/a` (the claim cells and the dimensions): "
                        f"{missing[:8]}")
    if foreign:
        problems.append(f"evidence files not headed `# Evidence: <the row's ID>`: {foreign[:8]}")
    if malformed:
        problems.append(f"evidence lines not in the form ``- `cell` — source[, where] — \"quote\"``: {malformed[:8]}")
    if no_text:
        problems.append(f"`full-text` rows whose `method summary` has no full-text quote: {no_text[:8]}")
    if snippets:
        problems.append(f"evidence quoted from snippets, which nothing can check afterwards: quote the fetched full text "
                        f"instead (docs/verification.md): {snippets[:8]}")
    if short:
        problems.append(f"full-text quotes with a part shorter than {QUOTE_WORDS} words, too short to show where a claim "
                        f"comes from: {short[:8]}")
    if unfound:
        problems.append(f"full-text quotes not found in the fetched full text, in order, so not verbatim: {unfound[:8]}")
    if unchecked:
        c.unchecked = sorted(set(unchecked))
    return "; ".join(problems) or None


def r_dissent_evidence(c):
    """A verified dissent row's quoted claim is in its evidence, so that it too traces back to the full text."""
    out = []
    for r in coreset_cells(c)[1]:
        if r.get("role") != "dissent" or r.get("source") in (None, "abstract"):
            continue
        q = QUOTE.search(r.get("selected because", ""))
        ev = read(evidence_path(c, r["_id"]))
        if q and ev is not None and not any(found_in(q.group(0)[1:-1], [b]) for b in normalised(ev)):
            out.append(r["_id"])
    return (f"verified dissent rows whose quoted claim (`selected because`) is not among their evidence quotes: "
            f"{out}") if out else None


def r_coreset_line(c):
    if (m := need_lines(c, "Coreset")):
        return m
    n = re.search(r"(\d+) rows", c.line("Coreset"))
    return None if n and int(n.group(1)) == len(c.rows) else f"`Coreset` does not say {len(c.rows)} rows"


def r_output(c):
    return None if c.output is not None else f"outputs/{c.topic}.md does not exist"


def items(text):
    """Top-level list items of a section, each joined with its continuation lines."""
    out, cur = [], None
    for line in (text or "").splitlines():
        if re.match(r"^(?:[-*]|\d+\.)\s", line):
            cur = [line]
            out.append(cur)
        elif cur is not None and line[:1] == " " and line.strip():
            cur.append(line)
        elif not line.strip():
            cur = None
    return ["\n".join(i) for i in out]


def r_cite_entries(c):
    if c.output is None:
        return None
    secs, out = sections(c.output), []
    for name in ("Questions", "Reading"):
        for i, it in enumerate(items(secs.get(name)), 1):
            if not BARE_ID.search(it):
                out.append(f"{name} {i}")
    return f"output entries citing no coreset paper: {out}" if out else None


def rounds(c):
    out = []
    for text in c.L.get("Coverage test", []):
        m = re.search(r"round (\d+):\s*(\d+) of (\d+) sampled candidates changed the output(.*?)(?:;\s*new clusters:\s*(.*))?$", text)
        if m:
            # The IDs that open an entry, `(<id>: <what it changed>, <id>: ...)`, not IDs inside what it changed.
            ids = re.findall(rf"(?:\(|[,;]\s*){BARE_ID.pattern}\s*:", m.group(4) or "")
            out.append({"r": int(m.group(1)), "k": int(m.group(2)), "n": int(m.group(3)), "ids": ids,
                        "new": (m.group(5) or "").strip()})
        else:
            out.append(None)
    return out


def converged(r):
    return r["k"] <= 1 and r["new"].lower().startswith("none")


def r_coverage(c):
    if (m := need_lines(c, "Coverage test")):
        return m
    rs = rounds(c)
    if None in rs:
        return "a `Coverage test` line is not in the form `round R: K of N sampled candidates changed the output (...); new clusters: ...`"
    problems = []
    for i, r in enumerate(rs, 1):
        if r["n"] < COVERAGE_SAMPLE:
            problems.append(f"round {i} sampled {r['n']} candidates, fewer than {COVERAGE_SAMPLE}")
        if r["k"] != len(set(r["ids"])) or r["k"] > r["n"]:
            problems.append(f"round {i} says {r['k']} of {r['n']} changed the output but names {len(set(r['ids']))} paper ID(s)")
        if not r["new"]:
            problems.append(f"round {i} does not say `new clusters: none | <which>`")
    return "; ".join(problems) or None


def r_coverage_sheets(c):
    """Each round's sheet, written by tools/coverage.py, backs its `Coverage test` line: every candidate judged, N its
    rows, the IDs the line counts in K its `changes` rows, and a proposed cluster not reported as `none`."""
    from coverage import counted, sheet
    problems = []
    for r in (x for x in rounds(c) if x):
        path = ROOT / "graphs" / c.topic / f"coverage-{r['r']}.md"
        rows = sheet(read(path))
        if not rows:
            problems.append(f"round {r['r']} has no sheet {path.relative_to(ROOT)} (`uv run tools/coverage.py draw`)")
            continue
        left = [x["id"] for x in rows if not x.get("verdict")]
        changed, new = counted(rows)
        if left:
            problems.append(f"round {r['r']}'s sheet has candidates without a verdict: {left[:6]}")
        if len(rows) != r["n"]:
            problems.append(f"round {r['r']} says {r['n']} sampled candidates, but its sheet has {len(rows)}")
        if {x["id"] for x in changed} != set(r["ids"]):
            problems.append(f"round {r['r']} counts {sorted(set(r['ids']))} in K, but its sheet marks "
                            f"{sorted(x['id'] for x in changed)} as changing a target")
        if new and r["new"].strip().lower() == "none":
            problems.append(f"round {r['r']}'s sheet proposes a new cluster ({', '.join(x['id'] for x in new)}), but "
                            "the line says `new clusters: none`")
    return "; ".join(problems) or None


def r_judgement_audit(c):
    """The `Judgement audit` line, as tools/audit.py computes it from the two judged sheets."""
    from audit import summary
    if (m := need_lines(c, "Judgement audit")):
        return m + " (`python3 tools/audit.py line`)"
    value, missing = summary(c.topic)
    if missing:
        return f"the judgement audits are not done: {missing}"
    if " ".join(c.line("Judgement audit").split()) != value:
        return f"`Judgement audit` does not match its sheets; `python3 tools/audit.py line {c.topic}` prints: {value}"
    return None


def r_converged(c):
    rs = [r for r in rounds(c) if r]
    ended = c.line("Ended").strip()
    unconverged = sum(1 for r in rs if not converged(r))
    if unconverged >= 2 and "H11" not in c.halts:
        return "two coverage-test rounds without convergence, but `Halts` does not record H11"
    if not ended:
        return None  # g5.end-lines reports it
    if ended.startswith("finished") and not (rs and converged(rs[-1])):
        return "`Ended` says finished (F1), but the last coverage-test round did not converge"
    m = re.match(r"halted \((H\d+)\)", ended)
    if m and m.group(1) not in c.halts:
        return f"`Ended` says halted ({m.group(1)}), but `Halts` does not record it"
    if not (ended.startswith("finished (F1)") or m):
        return "`Ended` is neither `finished (F1)` nor `halted (<id>)`"
    return None


def r_changed_in_coreset(c):
    ids = {i for r in rounds(c) if r for i in r["ids"]}
    out = sorted(i for i in ids if i not in c.coreset_ids or not c.pool_cluster.get(i))
    return (f"coverage-test candidates that changed the output but are not assigned coreset rows: {out}; add them, "
            f"process them as late papers, and give them roles") if out else None


def r_late_empty(c):
    a = c.assigned()
    out = sorted(p for p in c.pool if p not in a and (c.records.get(p) or {}).get("embedding"))
    return f"late papers still awaiting assignment: {out[:8]}; run `uv run tools/assign.py late {c.topic}`" if out else None


def r_end_lines(c):
    if (m := need_lines(c, "Tokens", "Halts", "Ended")):
        return m
    bad = [x.strip() for x in c.line("Tokens").split(",") if not TOKENS.match(x.strip())]
    if bad:
        return f"`Tokens` is not a list of `<step>: <tokens>` (from each dispatch's reported usage): {bad[:4]}"
    return None


REQUIREMENTS = {
    0: [("g0.entry", r_entry), ("g0.placeholders", r_placeholders), ("g0.labels", r_labels),
        ("g0.dimensions", r_dimensions), ("g0.preflight", r_preflight)],
    1: [("g1.orientation", r_orientation), ("g1.expansion", r_expansion), ("g1.errored", r_errored),
        ("g1.rejected", r_rejected), ("g1.fetched", r_fetched), ("g1.fringe-collected", r_fringe_collected),
        ("g1.fringe-screened", r_fringe_screened), ("g1.fringe-added", r_fringe_added), ("g1.fringe-line", r_fringe_line),
        ("g1.pool-line", r_pool_line)],
    2: [("g2.clustered", r_clustered), ("g2.named", r_named), ("g2.written", r_written),
        ("g2.lines", r_cluster_lines), ("g2.clustering-line", r_clustering_matches), ("g2.clusters-line", r_clusters_line),
        ("g2.diagnosis-halts", r_diagnosis_halts), ("g2.review", r_review)],
    3: [("g3.roles", r_roles), ("g3.dissent-searched", r_dissent_searched), ("g3.dissent-quoted", r_dissent_quoted),
        ("g3.bridges", r_bridges), ("g3.divided", r_divided), ("g3.fringe-quota", r_fringe_quota), ("g3.cells", r_cells),
        ("g3.assigned", r_assigned), ("g3.dimension-columns", r_dimension_columns)],
    4: [("g4.evidence", r_evidence), ("g4.dissent-evidence", r_dissent_evidence), ("g4.abstract-listed", r_abstract_listed),
        ("g4.h10", r_h10), ("g4.coreset-line", r_coreset_line)],
    5: [("g5.output", r_output), ("g5.cite-entries", r_cite_entries), ("g5.coverage", r_coverage),
        ("g5.coverage-sheets", r_coverage_sheets), ("g5.converged", r_converged),
        ("g5.changed-in-coreset", r_changed_in_coreset), ("g5.late-empty", r_late_empty),
        ("g5.judgement-audit", r_judgement_audit), ("g5.end-lines", r_end_lines)],
}


# --- history: compared with the last commit -------------------------------------------------------


def committed(path):
    try:
        r = subprocess.run(["git", "show", f"HEAD:{path.relative_to(ROOT)}"], cwd=ROOT, capture_output=True, text=True)
    except OSError:
        return None
    return r.stdout if r.returncode == 0 else None


def history(c):
    """Invariants against HEAD: earlier passes' entries intact, no pool paper or coreset row gone unrecorded, no
    `source` lowered. Returns (failures, notes)."""
    failures, notes = [], []
    old = committed(ROOT / "surveys" / f"{c.topic}.md")
    if old is None:
        return failures, notes
    osecs = sections(old)
    now = "\n".join(c.secs.get("Retrieval log", "").splitlines())
    for e in log_entries(osecs.get("Retrieval log", "")):
        if e["date"] == c.date:
            continue
        gone = [l for l in e["raw"] if l.strip() and l not in now]
        if gone:
            failures.append(f"the log entry of {e['date']} was changed since the last commit (earlier entries are never "
                            f"rewritten; add a pointer instead): {gone[0][:80]!r}")
    record = " ".join(c.L.get(k, [""])[0] for k in ("Halts", "Corrections to existing rows", "Demotions"))
    old_pool = {row_id(l) for h, _, _, l in table_rows(osecs.get("Pool", "")) if h and h[0] == "paper"} - {None}
    gone = sorted(p for p in old_pool - c.pool if p not in record)
    if gone:
        failures.append(f"pool papers removed since the last commit without H12 or a logged merge: {gone[:8]}")
    old_rows = {row_id(l): dict(zip(h, cs)) for h, cs, _, l in table_rows(osecs.get("Coreset", ""))
                if h and h[0] == "paper"}
    gone = sorted(p for p in set(old_rows) - c.coreset_ids if p and p not in record)
    if gone:
        failures.append(f"coreset rows removed since the last commit without a `Demotions` or `Corrections` entry: {gone[:8]}")
    now_rows = {row_id(l): dict(zip(h, cs)) for h, cs, _, l in c.rows}
    both = sorted(p for p in set(old_rows) & set(now_rows) if p)
    lowered = [p for p in both if SOURCE_RANK.get(now_rows[p].get("source"), 0) < SOURCE_RANK.get(old_rows[p].get("source"), 0)]
    if lowered:
        failures.append(f"`source` lowered since the last commit (it only ratchets up): {lowered}")
    # A verified row is edited only as a logged correction (docs/process.md, "Rules for re-runs"). A row still
    # `abstract` is a draft, and verification may rewrite it freely.
    corrections = " ".join(c.L.get("Corrections to existing rows", []))
    edited = [p for p in both if old_rows[p].get("source") in ("snippet", "full-text") and p not in corrections
              and any(k != "source" and k in now_rows[p] and now_rows[p][k] != v for k, v in old_rows[p].items())]
    if edited:
        failures.append(f"verified rows changed since the last commit without a `Corrections to existing rows` entry "
                        f"naming them: {edited[:8]}")
    old_input = committed(ROOT / "inputs" / f"{c.topic}.md")
    if old_input is not None and old_input != read(ROOT / "inputs" / f"{c.topic}.md"):
        notes.append(f"inputs/{c.topic}.md changed since the last commit; only the user edits the input")
    return failures, notes


# --- running --------------------------------------------------------------------------------------


def inferred(c):
    """The highest gate the files show the pass has gone past, whatever the `Gates` line says."""
    L, g = c.L, -1
    if c.cur:
        g = 0
    if any(k in L for k in ("Clustering", "Clustering rationale", "Clusters")) or \
            (c.first_pass and c.cluster_rows):
        g = max(g, 1)
    if any(k in L for k in ("Dissent searches", "Demotions")) or (c.first_pass and c.rows):
        g = max(g, 2)
    if "Coreset" in L or (c.first_pass and any(cs[-1] != "abstract" for _, cs, _, _ in c.rows)):
        g = max(g, 3)
    if "Coverage test" in L or (c.first_pass and c.output is not None):
        g = max(g, 4)
    if "Ended" in L:
        g = 5
    return g


def evaluate(c):
    """{gate: [(id, problem or None, waived)]} for every gate."""
    return {g: [(rid, fn(c), rid in c.waived) for rid, fn in REQUIREMENTS[g]] for g in REQUIREMENTS}


def halted(c):
    """The halt that ended the pass, if `Ended` says halted and `Halts` records the user's decision on it."""
    m = re.match(r"halted \((H\d+)\)", c.line("Ended").strip())
    if m and any(d and not d.lower().startswith("pending") for d in c.halts.get(m.group(1), [])):
        return m.group(1)
    return None


def r_closed(c):
    """A halted pass is closed: its end lines are written, and its halt is recorded with the user's decision."""
    return need_lines(c, "Tokens", "Halts", "Ended")


def run(c, target=None, status=False):
    """Print the gate report; return (failures, notes) for tools/check.py, which says whether `--gate` passed."""
    failures, notes = [], []
    if c.cur is None and not c.rows and not c.clusters and target is None and not status:
        return failures, notes  # a survey with no pass yet
    results = evaluate(c)
    # The safety net holds whatever happens to the `Gates` line, and a pending halt does not switch it off.
    top = max([inferred(c)] + list(c.declared))
    pending = c.pending()
    if pending:
        notes.append(f"halt pending ({', '.join(pending)}): no further gate passes until the user decides")
    stop = halted(c)
    if stop:
        # A pass the user ended at a halt needs only the gates it declared, and to be closed (docs/gates.md).
        top = max(c.declared, default=0)
        if (m := r_closed(c)):
            failures.append(f"halted pass ({stop}) not closed: {m}")
    required = set(range(top + 1))
    if target is not None:
        required |= set(range(target + 1))
        if pending:
            failures.append(f"G{target} cannot pass while a halt is pending: {', '.join(pending)}")
    passed = [g for g in range(6) if all(p is None or w for _, p, w in results[g])]
    nxt = next((g for g in range(6) if g not in passed), None)

    print(f"gates:   pass of {c.date or 'none'}; declared {' '.join(f'G{g}' for g in sorted(c.declared)) or 'none'}; "
          + (f"required G0–G{max(required)}" if required else "required none") + (f"; ended at {stop}" if stop else "")
          + (f"; next G{nxt}" if nxt is not None else "; all passed"))
    for g in sorted(required):
        for rid, problem, waived in results[g]:
            if problem and waived:
                notes.append(f"{rid} waived (log `Waivers`): {problem}")
            elif problem:
                failures.append(f"G{g} {rid}: {problem}")
    if status:
        print()
        for gi, (g, name) in enumerate(GATES):
            open_ = [(rid, p) for rid, p, w in results[gi] if p and not w]
            mark = "passed" if not open_ else f"{len(open_)} open"
            print(f"  {g} {name:18} {mark}" + ("   (required)" if gi in required else ""))
            for rid, p in open_:
                print(f"      {rid}: {p}")
        print()
    # Bridges are selected before the fringe (docs/process.md), so the trading pairs show as soon as there are rows.
    if c.rows and 3 not in required and (b := r_bridges(c)):
        notes.append(f"{b}: run the Bridges row before Fringe selection")
    if getattr(c, "unchecked", None):
        missing = (f"full-text quotes not checked verbatim, since the full text is not fetched here: {c.unchecked[:8]}; "
                   f"`uv run tools/fulltext.py {c.topic} <id>` fetches it")
        if target is not None and target >= 4 and "g4.evidence" not in c.waived:
            failures.append(f"G4 g4.evidence: {missing}")   # a gate is never passed on quotes nobody checked
        else:
            notes.append(missing)
    conflict = sorted((c.pool | c.coreset_ids) & {row_id(l) for h, _, _, l in table_rows(c.rejected or "")
                                                  if h and h[0] == "paper"})
    if conflict:
        notes.append(f"papers both rejected (rejected.md) and in the pool: {conflict[:8]}; one of the two judgements is "
                     f"wrong")
    h_fail, h_notes = history(c)
    return failures + h_fail, notes + h_notes
