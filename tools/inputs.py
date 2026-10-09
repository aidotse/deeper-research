#!/usr/bin/env python3
"""Read and check a topic's input file, inputs/<topic>.md.

Usage: python3 tools/inputs.py <topic>

Prints what the tools take from the input — the declared dimensions with their allowed values, and the `Clustering`
steering — and exits 1 if the input breaks the format in docs/formats.md: an unknown section, a missing `Topic`, a
dimension without values, or an unknown `Clustering` field or value. A typo such as `review: before-coreset` would
otherwise silently skip the halt it asks for.

`tools/check.py` and `tools/graph.py` import `read_input` for the dimensions, and `tools/cluster.py` for the
`granularity` steering.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = {"Topic", "Context", "Coreset Spec", "Dimensions", "Clustering"}
CLUSTERING = {"granularity", "expect", "exclude", "alignment", "review"}
ALIGNMENTS = {"high", "medium", "low"}

# A dimension: a top-level bullet `- **`name`** — values: `a`, `b` or `c`. Any prose after.`
DIM = re.compile(r"^- \*\*`([a-z0-9][a-z0-9-]*)`\*\*")
VALUES = re.compile(r"values:\s*((?:`[^`]+`(?:\s*,\s*|\s+or\s+|\s+and\s+|,\s*or\s+)?)+)")
# A Clustering field: a top-level bullet `- `key`: value`.
FIELD = re.compile(r"^- `([^`]+)`:\s*(.*)$")


def sections(text):
    out, name, buf = {}, None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if name is not None:
                out[name] = buf
            name, buf = line[3:].strip(), []
        elif name is not None:
            buf.append(line)
    if name is not None:
        out[name] = buf
    return out


def bullets(lines):
    """Top-level bullets, each joined with its wrapped continuation lines (but not its nested bullets)."""
    out, cur = [], None
    for line in lines:
        if line.startswith("- "):
            cur = [line]
            out.append(cur)
        elif cur is not None and line.startswith("  ") and not line.lstrip().startswith("- ") and line.strip():
            cur.append(line.strip())
        elif not line.strip():
            cur = None
    return [" ".join(b) for b in out]


def read_input(topic):
    """Return (dimensions, clustering, problems). dimensions: {name: set of values}; clustering: {field: value}."""
    path = ROOT / "inputs" / f"{topic}.md"
    if not path.exists():
        return None, None, [f"inputs/{topic}.md does not exist"]
    secs, problems = sections(path.read_text()), []
    for name in secs:
        if name not in SECTIONS:
            problems.append(f"input: unknown section `## {name}`; known: {', '.join(sorted(SECTIONS))}")
    if "Topic" not in secs:
        problems.append("input: no `## Topic` section")

    dims = {}
    for b in bullets(secs.get("Dimensions", [])):
        m = DIM.match(b)
        if not m:
            if b.startswith("- **"):
                problems.append(f"input: dimension not in the form ``- **`name`** — values: `a`, `b``` (a lowercase "
                                f"name in backticks): {b[:60]!r}")
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
        if key == "granularity" and not (plain in ("coarser", "finer") or plain.isdigit()):
            problems.append(f"input: `granularity` is `coarser`, `finer` or a number of clusters, not {plain!r}")
        if key == "review" and plain != "before coreset":
            problems.append(f"input: `review` can only be `before coreset`, not {plain!r}")
        if key == "alignment":
            for part in filter(None, (p.strip() for p in value.split(";"))):
                rating = re.findall(r"`([a-z]+)`\s*$", part)
                if not rating or rating[0] not in ALIGNMENTS:
                    problems.append(f"input: `alignment` entry must end in `high`, `medium` or `low`: {part[:60]!r}")
        steering[key] = value
    return dims, steering, problems


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
    for p in problems:
        print(f"FAIL  {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
