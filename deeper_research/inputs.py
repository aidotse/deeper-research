#!/usr/bin/env python3
"""Read and check a topic's input file, inputs/<topic>.md.

Usage: uv run python -m deeper_research.inputs <topic>

Prints what the tools take from the input — the declared dimensions with their allowed values, the `Clustering`
steering, and the coreset's targets — and exits 1 if the input breaks the format in docs/formats.md: an unknown,
repeated or wrongly levelled section (sections are `##` headings), a missing or empty `Topic`, a dimension without
values, an unknown `Clustering` field or value, a `Coreset Spec` bullet that is neither a target nor a `drop`, or no
targets left after the drops. A typo such as `review: before-coreset` would otherwise silently skip the halt it asks
for.

A bullet is any list item: `-`, `*`, `+` or numbered (`1.`, `1)`). mdformat rewrites `*` and `+` as `-`, so the input
must read the same before and after it; a numbered item is a list item too, and mdformat keeps it numbered.

`deeper_research/check.py` and `deeper_research/graph.py` import `read_input` for the dimensions, and `deeper_research/cluster.py` for the
`granularity` steering; `deeper_research/check.py` imports `read_targets` for the output's sections.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = {"Topic", "Context", "Coreset Spec", "Dimensions", "Clustering"}
CLUSTERING = {"granularity", "expect", "exclude", "alignment", "review"}
ALIGNMENTS = {"high", "medium", "low"}
DEFAULT_TARGETS = ["Landscape", "Assumptions", "Gaps"]
DERIVED = ["Questions", "Reading"]  # always in the output, never targets

# A dimension: a top-level bullet `- **`name`** — values: `a`, `b` or `c`. Any prose after.`
DIM = re.compile(r"^- \*\*`([a-z0-9][a-z0-9-]*)`\*\*")
# The separators include the Oxford comma: "`a`, `b`, or `c`" is {a, b, c}.
VALUES = re.compile(r"values:\s*((?:`[^`]+`(?:\s*,\s*(?:(?:or|and)\s+)?|\s+(?:or|and)\s+)?)+)")
# A Clustering field: a top-level bullet `- `key`: value`.
FIELD = re.compile(r"^- `([^`]+)`:\s*(.*)$")
# An added target: a top-level bullet `- **`Name`** — what the output must say about it`.
TARGET = re.compile(r"^- \*\*`([^`]+)`\*\*")
# A list item's marker: `-`, `*`, `+`, or a number with `.` or `)`. Bullets are read as if marked `-`.
ITEM = re.compile(r"^(?:[-*+]|\d{1,9}[.)])\s+")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def sections(text):
    """Return ({name: lines}, problems). A repeated section is a problem; its lines are kept, after the first's."""
    out, problems, name = {}, [], None
    for line in text.splitlines():
        h = HEADING.match(line)
        if h and len(h.group(1)) == 2:
            name = h.group(2)
            if name in out:
                problems.append(f"input: section `## {name}` appears more than once; merge them into one")
            out.setdefault(name, [])
            continue
        if h and h.group(2) in SECTIONS:
            # A known section at the wrong level would otherwise be read as prose in the section before it.
            problems.append(f"input: `{line.strip()}` is a level-{len(h.group(1))} heading; sections are `##` "
                            f"headings, as in `## {h.group(2)}`")
        if name is not None:
            out[name].append(line)
    return out, problems


def bullets(lines):
    """Top-level bullets, each joined with its wrapped continuation lines (but not its nested bullets)."""
    out, cur = [], None
    for line in lines:
        m = ITEM.match(line)
        if m:
            cur = ["- " + line[m.end():]]
            out.append(cur)
        elif not line.strip():
            cur = None
        elif cur is not None and not ITEM.match(line.lstrip()):
            # An indented continuation, or a lazy one at column 0: mdformat indents both, so both must read the same.
            cur.append(line.strip())
    return [" ".join(b) for b in out]


def read_input(topic):
    """Return (dimensions, clustering, problems). dimensions: {name: set of values}; clustering: {field: value}."""
    path = ROOT / "inputs" / f"{topic}.md"
    if not path.exists():
        return None, None, [f"inputs/{topic}.md does not exist"]
    secs, problems = sections(path.read_text())
    for name in secs:
        if name not in SECTIONS:
            problems.append(f"input: unknown section `## {name}`; known: {', '.join(sorted(SECTIONS))}")
    if "Topic" not in secs:
        problems.append("input: no `## Topic` section (sections are `##` headings)")
    elif not any(line.strip() for line in secs["Topic"]):
        problems.append("input: the `## Topic` section is empty")

    dims = {}
    for b in bullets(secs.get("Dimensions", [])):
        m = DIM.match(b)
        if not m:
            # Every top-level bullet here declares a dimension (docs/formats.md); one in another form would otherwise
            # be dropped silently, and its values never checked.
            problems.append(f"input: dimension not in the form ``- **`name`** — values: `a`, `b``` (a lowercase "
                            f"name in bold backticks): {b[:60]!r}")
            continue
        v = VALUES.search(b)
        if not v:
            problems.append(f"input: dimension `{m.group(1)}` declares no values (`values: `a`, `b``)")
            continue
        dims[m.group(1)] = set(re.findall(r"`([^`]+)`", v.group(1)))

    steering = {}
    for b in bullets(secs.get("Clustering", [])):
        m = FIELD.match(b)
        if not m:
            problems.append(f"input: `Clustering` line not in the form `- `field`: value`: {b[:60]!r}")
            continue
        key, value = m.group(1), m.group(2).strip()
        if key not in CLUSTERING:
            problems.append(f"input: unknown `Clustering` field `{key}`; known: {', '.join(sorted(CLUSTERING))}")
            continue
        plain = value.replace("`", "").strip()
        if key == "granularity" and not (plain in ("coarser", "finer") or (plain.isdigit() and int(plain) > 0)):
            problems.append(f"input: `granularity` is `coarser`, `finer` or a number of clusters above 0, "
                            f"not {plain!r}")
        if key == "review" and plain != "before coreset":
            problems.append(f"input: `review` can only be `before coreset`, not {plain!r}")
        if key == "alignment":
            for part in filter(None, (p.strip() for p in value.split(";"))):
                rating = re.findall(r"`([a-z]+)`\s*$", part)
                if not rating or rating[0] not in ALIGNMENTS:
                    problems.append(f"input: `alignment` entry must end in `high`, `medium` or `low`: {part[:60]!r}")
        steering[key] = value
    return dims, steering, problems


def read_targets(topic):
    """Return (targets, problems): the output sections the coreset must stay stable against (docs/formats.md, `Coreset
    Spec`). The defaults apply unless dropped with `- `drop`: `Name``; each `- **`Name`** — ...` bullet adds one."""
    path = ROOT / "inputs" / f"{topic}.md"
    if not path.exists():
        return list(DEFAULT_TARGETS), []
    targets, problems = list(DEFAULT_TARGETS), []
    # Section problems are read_input's to report; reporting them here too would print them twice.
    for b in bullets(sections(path.read_text())[0].get("Coreset Spec", [])):
        m, f = TARGET.match(b), FIELD.match(b)
        if m:
            name = m.group(1).strip()
            if name in DERIVED:
                problems.append(f"input: `{name}` is always in the output and is never a target")
            elif name not in targets:
                targets.append(name)
        elif f and f.group(1) == "drop":
            for name in re.findall(r"`([^`]+)`", f.group(2)):
                if name in DEFAULT_TARGETS and name in targets:
                    targets.remove(name)
                else:
                    problems.append(f"input: `drop` names {name!r}, which is not a default target")
        else:
            # Prose is allowed as a paragraph, or nested under a target; a top-level bullet that is neither form
            # is more likely a mistyped target than prose, so it fails rather than being dropped.
            problems.append(f"input: `Coreset Spec` bullet is neither a target (``- **`Name`** — ...``) nor a "
                            f"`drop`; write prose as a paragraph or nested under a target: {b[:60]!r}")
    if not targets:
        problems.append("input: `Coreset Spec` drops every target and adds none, so the coverage test would check "
                        "nothing")
    return targets, problems


def main(argv):
    if len(argv) != 1:
        print(__doc__.strip())
        return 2
    dims, steering, problems = read_input(argv[0])
    if dims is not None:
        print(f"dimensions: {len(dims)}")
        for name, values in dims.items():
            print(f"  {name}: {', '.join(sorted(values))}")
        print("clustering steering: " + ("none" if not steering else ""))
        for key, value in steering.items():
            print(f"  {key}: {value}")
    targets, more = read_targets(argv[0])
    problems = problems + more
    print(f"targets: {', '.join(targets)}; then {', '.join(DERIVED)}")
    for p in problems:
        print(f"FAIL  {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
