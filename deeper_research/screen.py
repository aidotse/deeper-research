"""Screening sheets: the tables on which a `survey-pass` agent marks candidates in or out of scope.

No command line of its own. Two scripts write a sheet and judge it through this module:

  deeper_research/expand.py   graphs/<topic>/expand-screen.md   expansion's candidates (docs/process.md,
                                                                "Step 2: expand")
  deeper_research/fringe.py   graphs/<topic>/fringe-screen.md   the fringe routes' candidates ("Fringe routes")

A sheet is a markdown table with, among its columns, `s2` (the Semantic Scholar paper ID), `title`, `abstract`,
`in scope` and `reason`. `judge` writes verdicts into it from stdin, one `<s2><TAB>yes|no|maybe<TAB><reason>` per
line. It refuses the whole batch if any line names an s2 ID not on the sheet, gives a verdict other than yes, no or
maybe, judges a row twice differently, or gives a `yes` or `no` a reason of fewer than two words. It holds a lock on
the sheet while it reads and writes, so that agents judging disjoint rows may run at once. A `maybe` parks a row: it
counts as unjudged, for the add step and for the G1 gate alike, until it becomes `yes` or `no`.
"""

import fcntl
import re
import sys
from collections.abc import Iterable
from pathlib import Path

from deeper_research.check import ROOT, cells_of, same_title, sections, table_rows, words

VERDICTS = ("yes", "no", "maybe")
S2_ID = re.compile(r"[0-9a-f]{40}")
ABSTRACT_CHARS = 700  # the most of an abstract a sheet shows; the opening states what the paper is about


def title_key(title: str) -> str:
    """A title reduced to its lower-case words, for matching two records of one paper."""
    return " ".join(words(title))


class Papers:
    """An index of papers, by their IDs and titles.

    Records of papers, to tell whether another record is one of them: it shares an arXiv or corpus ID with one, or
    its title is the same by `check.same_title`. Semantic Scholar can keep a preprint and its venue version as two
    records, under titles a word apart.
    """

    ids: dict[str, str | None]
    flat: dict[str, str | None]
    by_first: dict[str, list[tuple[list[str], str | None]]]

    def __init__(self, ids: Iterable[str | None] = (), titles: Iterable[str | None] = ()) -> None:
        """Index papers by `ids` and `titles`, all under the label None."""
        self.ids, self.flat, self.by_first = {}, {}, {}
        self.add(None, ids, *titles)

    def add(self, label: str | None, ids: Iterable[str | None], *titles: str | None) -> None:
        """Index a paper under `label` (returned by `find`), by its IDs and any number of titles."""
        for x in ids:
            if x:
                self.ids.setdefault(x, label)
        for t in titles:
            w = words(t or "")
            if w:
                self.flat.setdefault("".join(w), label)
                self.by_first.setdefault(w[0], []).append((w, label))

    def find(self, ids: Iterable[str | None], title: str | None) -> tuple[bool, str | None]:
        """(True, label) for the first indexed paper this record matches, else (False, None)."""
        for x in ids:
            if x and x in self.ids:
                return True, self.ids[x]
        w = words(title or "")
        if not w:
            return False, None
        if "".join(w) in self.flat:
            return True, self.flat["".join(w)]
        for v, label in self.by_first.get(w[0], []):
            if same_title(w, v):
                return True, label
        return False, None


def pool_titles(topic: str) -> set[str]:
    """The pool's titles, as title keys, from the survey's Pool table.

    A collector leaves out a candidate whose title
    matches one: it is most likely a second Semantic Scholar record of a pool paper, such as its venue version.
    """
    text = (ROOT / "surveys" / f"{topic}.md").read_text()
    return {title_key(c[0]) for h, c, _, _ in table_rows(sections(text).get("Pool", "")) if h and h[0] == "paper"}


def clean(s: str | None) -> str:
    """Text as one line for a sheet's cell: whitespace runs as one space, `|` as `/`, None as empty."""
    return re.sub(r"\s+", " ", s or "").replace("|", "/").strip()


def sheet_rows(text: str) -> list[tuple[int, list[str], list[str]]]:
    """(line index, header, cells) for each candidate row of a screening sheet, its columns located by name."""
    header: list[str] | None
    out: list[tuple[int, list[str], list[str]]]
    header, out = None, []
    for i, line in enumerate(text.splitlines()):
        if not line.startswith("|"):
            header = None
        elif header is None:
            header = cells_of(line)
        elif not line.startswith("| --"):
            cells = cells_of(line)
            if "s2" in header and len(cells) >= len(header) and S2_ID.fullmatch(cells[header.index("s2")]):
                out.append((i, header, cells))
    return out


def verdicts(text: str | None) -> dict[str, tuple[str, str]]:
    """{s2: (verdict, reason)} for every candidate row of a sheet, the verdict lower-cased."""
    return {
        cells[h.index("s2")]: (cells[h.index("in scope")].strip().lower(), cells[h.index("reason")].strip())
        for _, h, cells in sheet_rows(text or "")
    }


def judged(verdict: str, reason: str) -> bool:
    """Whether a screening row is judged: `yes` or `no` (not `maybe`), with a reason of at least two words.

    The add
    steps (deeper_research/assign.py) and the G1 gate use the same test.
    """
    return verdict.startswith(("yes", "no")) and len(words(reason)) >= 2


def judge(path: Path, hint: str) -> int:  # noqa: C901
    """Write the verdicts on stdin into the sheet at `path`. `hint` names the command that writes the sheet."""
    if not path.exists():
        sys.exit(f"no {path.relative_to(ROOT)}; run {hint} first")
    given: dict[str, tuple[str, str]]
    problems: list[str]
    given, problems = {}, []
    lines_in = list(sys.stdin)
    with open(path, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)  # released when the file closes
        lines = f.read().splitlines()
        rows = {cells[h.index("s2")]: (i, h, cells) for i, h, cells in sheet_rows("\n".join(lines))}
        # Check every line before writing any, so that a batch is written whole or not at all.
        for n, line in enumerate(lines_in, 1):
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("\t", 2)
            if len(parts) < 3:
                problems.append(f"line {n}: expected `<s2><TAB>yes|no|maybe<TAB><reason>`")
                continue
            s, v, reason = parts[0].strip(), parts[1].strip().lower(), clean(parts[2])
            if s not in rows:
                problems.append(f"line {n}: {s!r} is not an s2 ID on the sheet")
            elif v not in VERDICTS:
                problems.append(f"line {n}: verdict {parts[1].strip()!r} is not one of {', '.join(VERDICTS)}")
            elif not reason:
                problems.append(f"line {n}: {s} has no reason")
            elif v != "maybe" and len(words(reason)) < 2:
                problems.append(f"line {n}: {s} needs a reason of at least two words, tied to the topic")
            elif given.get(s, (v, reason)) != (v, reason):
                problems.append(f"line {n}: {s} is judged twice, differently")
            else:
                given[s] = (v, reason)
        if problems:
            sys.exit("\n".join(problems) + f"\nnothing written: {len(problems)} line(s) wrong")
        if not given:
            sys.exit("no `<s2><TAB>yes|no|maybe<TAB><reason>` lines on stdin; nothing written")
        written, replaced = 0, 0
        for s, (v, reason) in given.items():
            i, h, cells = rows[s]
            before = (cells[h.index("in scope")].strip().lower(), cells[h.index("reason")].strip())
            if before == (v, reason):
                continue
            replaced += bool(before[0])
            cells[h.index("in scope")], cells[h.index("reason")] = v, reason
            lines[i] = "| " + " | ".join(c.replace("\0", "\\|") for c in cells) + " |"
            written += 1
        if written:
            f.seek(0)
            f.write("\n".join(lines) + "\n")
            f.truncate()
    counts = {x: sum(1 for v, _ in given.values() if v == x) for x in VERDICTS}
    now = verdicts("\n".join(lines)).values()
    final = [v for v, _ in now]
    open_ = sum(1 for v, r in now if not judged(v, r))
    print(
        f"{path.relative_to(ROOT)}: {len(given)} verdict(s) read ({', '.join(f'{x} {k}' for x, k in counts.items())}); "
        f"{written} row(s) written, of which {replaced} replaced an earlier verdict; {len(given) - written} unchanged"
    )
    print(
        f"still unjudged: {open_} of {len(final)} candidate(s)"
        + (f", including {final.count('maybe')} `maybe`: resolve each to yes or no" if "maybe" in final else "")
    )
    return 0
