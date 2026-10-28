"""Fetch the full text of papers into a topic's cache, for verification, and read it by section.

Usage:
  uv run python -m deeper_research.fulltext <topic> <paper-id> [<paper-id> ...] [--refresh]
  uv run python -m deeper_research.fulltext <topic> --abstract [--refresh]
  uv run python -m deeper_research.fulltext show <topic> <paper-id> [<pattern>] [--section <name>]... [--max <tokens>]

Writes graphs/<topic>/fulltext/<id>.txt: the paper's text, verbatim, with a
two-line provenance header. `--abstract` fetches every coreset row whose
`source` is still `abstract`: the rows verification has yet to do. Every
verified row quotes this text (see docs/verification.md).

The text comes from arXiv's HTML rendering, which keeps section headings,
figure and table captions, and equations (as their LaTeX source). Papers whose
LaTeX did not convert to HTML fall back to the PDF's extracted text, with page
markers; that text is noisier, and equations in it are unreliable. A paper
without an arXiv ID (CorpusId:<n>) is fetched from the open-access PDF that
Semantic Scholar lists for it, if there is one; otherwise it cannot be fetched,
and its row stays uncheckable.

The bibliography is dropped, so that a search for a claim's terms cannot hit a
reference title. In HTML it is its own element. In PDF text it is cut from the
last `References` or `Bibliography` heading that a list of references follows,
up to an `Appendix` or `Supplementary material` heading if one comes after it;
an appendix headed otherwise ("A Proofs") is cut with the bibliography. A line
`[bibliography removed]` marks the cut, and the page markers inside it are kept.

`show` reads a fetched file by section, so that an agent reads only the parts it
needs. With no pattern it prints the outline: every heading with the size of its
section, subsections included, in tokens estimated as characters / 4. With a
pattern, a case-insensitive regular expression, it prints each matching passage
(its paragraph, or a few lines around the match) under its section heading. With
`--section`, it prints whole sections whose heading starts with the name (case
ignored, section numbers optional); with a pattern too, it searches only those.
Output is capped at --max tokens (default 6000), with a note when cut. Passages
are printed verbatim, so they can be quoted, and with the file's line numbers,
to read on from. PDF text has no markup: its sections are its pages (`page 3`)
and the lines that look like headings.

No model is involved, so nothing is paraphrased: an agent reads the outline, the
sections and passages a claim turns on, and quotes them. Requests are spaced
three seconds apart, following arXiv's etiquette, and carry no key or user
identifier. Existing files are kept unless --refresh is passed. A paper with no fetchable
full text is listed in a note, and the exit status stays 0; a failure of arXiv itself, after
retries, exits non-zero.
"""

import datetime
import io
import re
import sys
import time
import urllib.error
from html.parser import HTMLParser
from pathlib import Path

from deeper_research.check import ARXIV_ONLY, ID, ROOT, row_id, sections, table_rows  # noqa: E402
from deeper_research.net import get_json, request  # noqa: E402

HEADERS = {"User-Agent": "deeper-research fulltext tool"}
PAUSE = 3

# Elements whose content is navigation, styling or bibliography, not the paper.
SKIP_TAGS = {"script", "style", "nav", "header", "footer", "button", "svg", "noscript"}
SKIP_CLASSES = {"ltx_bibliography", "ltx_TOC", "ltx_page_footer", "ltx_page_header"}
BLOCK_TAGS = {"p", "div", "section", "article", "figure", "table", "tr", "li", "ul", "ol", "blockquote", "br"}
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
HEADING_LEVEL = {
    "ltx_title_document": 1,
    "ltx_title_abstract": 2,
    "ltx_title_part": 2,
    "ltx_title_section": 2,
    "ltx_title_appendix": 2,
    "ltx_title_subsection": 3,
    "ltx_title_subsubsection": 4,
    "ltx_title_paragraph": 4,
}

# PDF text has no markup. A references heading is a line of its own, perhaps numbered ("7 References", "VII.
# REFERENCES") or letter-spaced by the extraction ("R EFERENCES").
REFS_HEAD = re.compile(r"^(?:(?:\d{1,2}|[IVX]{1,4})\.?\s+)?(?:r\s?eferences(?: and notes)?|bibliography|literature cited|"
                       r"works cited)\s*:?$", re.I)
# What a list of references looks like: numbered entries such as [12], a year that ends a sentence ("2022." or
# "(2022)."), as in an entry and seldom in a body sentence, which cites as "(Wei et al., 2022)", and venue words.
REF_MARK = re.compile(r"^\[\d{1,3}\]|\b(?:19|20)\d\d[a-z]?\)?\.|arXiv preprint|In Proceedings|\bdoi\b", re.M)
APPENDIX_HEAD = re.compile(r"^(?:[A-Z]\.?\s+)?(?:appendix|appendices|a\s?ppendix|supplementary materials?|"
                           r"supplemental materials?)\b[^.]{0,80}$", re.I)
PAGE = re.compile(r"^\[page (\d+)\]$")
# A section heading in PDF text, a guess: a short numbered title on its own line ("3 Method", "4.2 Ablations"), or one
# of the unnumbered headings most papers share.
PDF_HEAD = re.compile(r"^(?:\d{1,2}(?:\.\d{1,2}){0,2}\.?\s+[A-Z][A-Za-z\-]+(?:\s+[A-Za-z][A-Za-z\-:]*){0,7}|"
                      r"(?i:abstract|introduction|related work|background|methods?|experiments|results|discussion|"
                      r"conclusions?|limitations|broader impacts?|acknowledge?ments|appendix(?:\s+[A-Z])?\b[^.]{0,60}|"
                      r"appendices))$")
CAP = 6000  # tokens `show` prints by default


class Text(HTMLParser):
    """Flatten arXiv's LaTeXML HTML into plain text with markdown headings.

    Tables come out one row per line, cells separated by ` | `. LaTeXML writes
    rows either as <tr> or as nested spans of class `ltx_tr`, so the parser
    keeps a stack of open elements to find where a row ends.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.in_math = [], [], 0
        self.open, self.rows = [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        if self.skip:
            if tag == self.skip[-1]:
                self.skip.append(tag)
            return
        if tag in SKIP_TAGS or classes & SKIP_CLASSES:
            self.skip.append(tag)
            return
        if self.in_math:
            return
        if tag == "math":
            # An equation is kept as its LaTeX source, which is what a claim
            # about it can be checked against.
            self.out.append(f" ${a.get('alttext', '').strip()}$ ")
            self.in_math = 1
            return
        row = tag == "tr" or "ltx_tr" in classes
        if tag not in VOID_TAGS:
            self.open.append((tag, row))
        level = next((HEADING_LEVEL[c] for c in classes if c in HEADING_LEVEL), None)
        if row:
            self.rows += 1
            self.out.append("\n")
        elif tag in ("td", "th") or "ltx_td" in classes:
            self.out.append(" " if "ltx_eqn_cell" in classes else " | ")
        elif level:
            self.out.append("\n\n" + "#" * level + " ")
        elif tag == "figcaption":
            self.out.append("\n[caption] ")
        elif tag in BLOCK_TAGS:
            # Inside a table row, a paragraph in a cell must not break the row.
            self.out.append(" " if self.rows else "\n")

    def handle_endtag(self, tag):
        if self.skip:
            if tag == self.skip[-1]:
                self.skip.pop()
            return
        if self.in_math:
            if tag == "math":
                self.in_math = 0
            return
        while self.open:
            name, row = self.open.pop()
            if row:
                self.rows -= 1
                self.out.append("\n")
            if name == tag:
                break
        if not self.rows and (tag in BLOCK_TAGS or tag in HEADINGS or tag == "figcaption"):
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip and not self.in_math:
            # Line breaks in the HTML source are spaces; structure comes from
            # the tags alone.
            self.out.append(re.sub(r"\s+", " ", data))

    def text(self):
        lines = (re.sub(r"[ \t\u00a0]+", " ", ln).strip() for ln in "".join(self.out).splitlines())
        text = "\n".join(lines)
        # The site's own chrome (banners, a feedback dialog) precedes the
        # paper; start at the document title.
        start = text.find("\n# ")
        text = text[start:] if start >= 0 else text
        return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def get(url):
    try:
        return request(url, headers=HEADERS, attempts=4, wait=lambda a: 5 * 2**a)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 404, url, b""
        raise


def from_html(aid):
    status, url, body = get(f"https://arxiv.org/html/{aid}")
    page = body.decode("utf-8", "replace")
    if status != 200 or "ltx_document" not in page:
        return None
    version = re.search(rf"{re.escape(aid)}(v\d+)", page)
    parser = Text()
    parser.feed(page)
    return f"https://arxiv.org/html/{aid}{version.group(1) if version else ''}", "html", parser.text(), None


def pdf_text(body):
    """A PDF's extracted text, with page markers and without its bibliography, and a note on what was cut; or None
    for a file pypdf cannot read, which leaves the paper unfetched rather than halting the run."""
    from pypdf import PdfReader
    from pypdf.errors import PyPdfError

    try:
        pages = PdfReader(io.BytesIO(body)).pages
        raw = "\n\n".join(f"[page {i}]\n{p.extract_text() or ''}" for i, p in enumerate(pages, 1))
    except PyPdfError:
        return None
    text, note = drop_bibliography(raw)
    return text.strip() + "\n", note


def drop_bibliography(text):
    """Cut the bibliography out of PDF text. Returns the text and a note on what was cut.

    The cut starts at the last references heading that a list of references follows, so that a line that merely
    reads "References" in the body does not count. It ends at the first appendix heading after it, or else at the end
    of the text. Page markers inside the cut are kept, so that the pages after it keep their numbers.
    """
    lines = text.split("\n")
    heads = [i for i, ln in enumerate(lines) if REFS_HEAD.match(ln.strip())
             and len(REF_MARK.findall("\n".join(lines[i + 1:i + 40]))) >= 8]
    if not heads:
        return text, "no bibliography heading found, nothing cut"
    start = heads[-1]
    end = next((j for j in range(start + 1, len(lines)) if APPENDIX_HEAD.match(lines[j].strip())), len(lines))
    pages = [ln for ln in lines[start:end] if PAGE.match(ln.strip())]
    note = (f"bibliography cut, lines {start + 1}-{end}; kept from {lines[end].strip()!r}" if end < len(lines)
            else f"bibliography cut, lines {start + 1}-{end}, with everything after it: no appendix heading follows")
    return "\n".join(lines[:start] + ["[bibliography removed]"] + pages + lines[end:]), note


def from_pdf(aid):
    status, url, body = get(f"https://arxiv.org/pdf/{aid}")
    if status != 200 or not body.startswith(b"%PDF") or not (got := pdf_text(body)):
        return None
    return url, "pdf", *got


def from_open_access(pid):
    """A paper without an arXiv ID: the open-access PDF Semantic Scholar lists for it, if any."""
    rec = get_json("https://api.semanticscholar.org/graph/v1/paper/batch?fields=openAccessPdf", {"ids": [pid]})[0]
    url = ((rec or {}).get("openAccessPdf") or {}).get("url") or ""
    if not url.startswith(("https://", "http://")):
        return None
    try:
        status, final, body = get(url)
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        # A publisher's server refusing or failing is a fact about this paper, not a failure of the run.
        return None
    if status != 200 or not body.startswith(b"%PDF") or not (got := pdf_text(body)):
        return None
    return final, "pdf, open access", *got


def file_of(topic, pid):
    # Pre-2007 IDs contain a slash (hep-th/9901001), corpus IDs a colon; keep the file name plain.
    return ROOT / "graphs" / topic / "fulltext" / f"{pid.replace('/', '_').replace(':', '_')}.txt"


def abstract_rows(topic):
    """The coreset rows still `abstract`-sourced, or None, with a message, where the survey has no coreset to read."""
    path = ROOT / "surveys" / f"{topic}.md"
    secs = sections(path.read_text()) if path.exists() else {}
    if "Coreset" not in secs:
        print(f"error: --abstract fetches the coreset rows of surveys/{topic}.md, which "
              + ("has no `## Coreset` section" if path.exists() else "does not exist")
              + "; name the papers to fetch instead")
        return None
    ids = []
    for h, c, _, line in table_rows(secs["Coreset"]):
        if h and h[0] == "paper" and c and c[-1] == "abstract" and row_id(line):
            ids.append(row_id(line))
    return list(dict.fromkeys(ids))


# --- reading a fetched file by section ------------------------------------------------------------


def headings(lines, pdf):
    """A full text's headings, as (line index, level, label, kind).

    HTML text marks its headings in markdown. PDF text has none, so its sections come in two kinds, each running to
    the next heading of its own kind: pages, from the page markers, and lines that look like headings.
    """
    out = []
    for i, ln in enumerate(lines):
        if m := re.match(r"(#{1,6}) (\S.*)$", ln):
            out.append((i, len(m.group(1)), m.group(2).strip(), "head"))
        elif pdf and (m := PAGE.match(ln.strip())):
            out.append((i, 1, f"page {m.group(1)}", "page"))
        elif pdf and PDF_HEAD.match(ln.strip()):
            number = re.match(r"\d+(?:\.\d+)*", ln.strip())
            out.append((i, 2 + (number.group().count(".") if number else 0), ln.strip(), "head"))
    return out


def section_end(heads, k, n):
    """Where the k-th heading's section ends: at the next heading of its kind at the same level or above."""
    _, level, _, kind = heads[k]
    return next((h[0] for h in heads[k + 1:] if h[3] == kind and h[1] <= level), n)


def answers(label, name):
    """Whether a heading answers to a section name: the name starts the heading, case ignored, with or without the
    heading's number ("3.2", "A", "Appendix B"). Returns 2 where the name ends at a word boundary, 1 for a bare
    prefix, 0 for no match."""
    label, name = label.lower(), name.lower().strip()
    bare = re.sub(r"^(?:appendix\s+)?(?:[a-z]|\d+)(?:\.\d+)*\.?\s+", "", label)
    if any(re.match(re.escape(name) + r"(?!\w)", x) for x in (label, bare)):
        return 2
    return 1 if label.startswith(name) or bare.startswith(name) else 0


def passages(lines, lo, hi, rx, pdf):
    """The passages in lines lo to hi that match: a whole paragraph where it is short; in a table, the matching rows
    and the table's first row, which usually names the columns; otherwise, as in a long block or anywhere in PDF text,
    whose blocks are pages, the lines around each match. Returns (start, end, first matching line)."""
    out, i = [], lo
    while i < hi:
        if not lines[i].strip():
            i += 1
            continue
        j = i
        while j < hi and lines[j].strip():
            j += 1
        table = lines[i].startswith("| ")
        while table and j + 1 < hi and not lines[j].strip() and lines[j + 1].startswith("| "):
            # HTML tables come one row per line with blank lines between: the rows of one table are one block.
            j += 2
            while j < hi and lines[j].strip():
                j += 1
        hits = [k for k in range(i, j) if rx.search(lines[k])]
        if hits and not pdf and j - i <= 12 and sum(len(ln) for ln in lines[i:j]) <= 4000:
            out.append((i, j, hits[0]))
            hits = []
        elif hits and table:
            out += [(k, k + 1, k) for k in dict.fromkeys([i] + hits)]
            hits = []
        for k in hits:
            a, b = max(i, k - 2), min(j, k + 3)
            if out and out[-1][0] >= i and out[-1][1] >= a:
                out[-1] = (out[-1][0], b, out[-1][2])
            else:
                out.append((a, b, k))
        i = j
    return out


def show(topic, pid, pattern, names, cap):
    path = file_of(topic, pid)
    if not path.exists():
        print(f"error: no full text for {pid} in graphs/{topic}/fulltext; fetch it first with "
              f"`uv run python -m deeper_research.fulltext {topic} {pid}`")
        return 1
    try:
        rx = re.compile(pattern, re.I) if pattern else None
    except re.error as e:
        print(f"error: the pattern {pattern!r} is not a regular expression: {e}")
        return 2
    lines = path.read_text().split("\n")
    pdf = "(pdf" in lines[0]
    body = lines.index("", 0) + 1 if lines[0].startswith("source:") and "" in lines else 0
    heads = headings(lines, pdf)
    ends = [section_end(heads, k, len(lines)) for k in range(len(heads))]
    size = lambda a, b: sum(len(ln) + 1 for ln in lines[a:b]) // 4  # noqa: E731

    def where(i):
        """The heading a line sits under; in PDF text, its page too."""
        found = [lines[h[0]].strip() for h in heads if h[0] <= i and h[3] == "head"][-1:]
        page = [lines[h[0]].strip() for h in heads if h[0] <= i and h[3] == "page"][-1:]
        return " ".join(page + found) or "(before the first heading)"

    if not pattern and not names:
        listed = [k for k, h in enumerate(heads) if h[3] == "head"]
        if pdf and len(listed) < 3:
            listed = [k for k, h in enumerate(heads) if h[3] == "page"]
        print(f"{pid}: {lines[0].removeprefix('source: ')}, about {size(body, len(lines)):,} tokens")
        print("tokens: estimated as characters / 4, for the section with its subsections"
              + ("; headings in PDF text are guessed from short numbered lines" if pdf else ""))
        print(f"{'line':>6} {'tokens':>7}  heading")
        for k in listed:
            i, level, label, kind = heads[k]
            page = [h[2] for h in heads if h[0] <= i and h[3] == "page"][-1:] if pdf and kind == "head" else []
            print(f"{i + 1:>6} {size(i, ends[k]):>7,}  {'  ' * (level - 1)}{label}" + "".join(f"  ({p})" for p in page))
        print("next: `--section <name>` prints a section, a pattern prints the passages that match it")
        return 0

    # Sections by name: the best-matching headings, each section printed once even where a subsection matches too.
    spans = [(body, len(lines))]
    if names:
        spans = []
        for name in names:
            score = [answers(h[2], name) for h in heads]
            best = max(score, default=0)
            if not best:
                print(f"error: no heading starts with {name!r}; run `uv run python -m deeper_research.fulltext show {topic} {pid}` "
                      f"for the outline")
                return 1
            spans += [(heads[k][0], ends[k]) for k, s in enumerate(score) if s == best]
        spans = sorted(set(spans), key=lambda s: (s[0], -s[1]))
        spans = [s for j, s in enumerate(spans) if not any(a <= s[0] and s[1] <= b for a, b in spans[:j])]

    budget, printed = cap * 4, 0
    if not rx:
        for a, b in spans:
            print(f"[lines {a + 1}-{b}, about {size(a, b):,} tokens]")
            for i in range(a, b):
                if printed and printed + len(lines[i]) > budget:
                    print(f"\nnote: cut at about {cap:,} tokens; the section runs on from line {i + 1} to {b}. Raise "
                          f"--max, name a subsection, or read the file from that line.")
                    return 0
                print(lines[i])
                printed += len(lines[i]) + 1
        return 0

    found = [p for a, b in spans for p in passages(lines, a, b, rx, pdf)]
    print(f"{len(found)} passage(s) in {pid} match /{pattern}/" + (f" in {', '.join(names)}" if names else "")
          + "; each printed under its heading, with its first line number")
    shown, rest = None, []
    for a, b, hit in found:
        chunk = "\n".join(lines[a:b])
        if rest or (printed and printed + len(chunk) > budget):
            rest.append(where(hit))
            continue
        if where(hit) != shown:
            shown = where(hit)
            print(f"\n{shown}")
        print(f"[line {a + 1}]\n{chunk}")
        printed += len(chunk) + 1
    if rest:
        print(f"\nnote: cut at about {cap:,} tokens; {len(rest)} more passage(s), under: "
              f"{'; '.join(dict.fromkeys(rest))}. Narrow the pattern, name a --section, or raise --max.")
    return 0


def show_main(argv):
    names, cap, pos, it = [], str(CAP), [], iter(argv)
    for a in it:
        key, eq, value = a.partition("=")
        if key in ("--section", "--max"):
            value = value if eq else next(it, "")
            if key == "--section":
                names.append(value)
            else:
                cap = value
        elif a.startswith("--"):
            print(f"error: unknown option {a}")
            return 2
        else:
            pos.append(a)
    if len(pos) not in (2, 3) or not all(n.strip() for n in names) or not cap.isdigit() or int(cap) < 1:
        print("usage: uv run python -m deeper_research.fulltext show <topic> <paper-id> [<pattern>] [--section <name>]... "
              "[--max <tokens>]")
        return 2
    if not ID.match(pos[1]):
        print(f"error: expected a paper ID such as 2408.03314 or CorpusId:6628106; got {pos[1]!r}")
        return 2
    return show(pos[0], pos[1], pos[2] if len(pos) == 3 else None, names, int(cap))


# --- fetching -------------------------------------------------------------------------------------


def main(argv):
    # `show <topic> <id>` reads a fetched file. A topic named `show` can still fetch: there, an ID follows it.
    rest = [a for a in argv[1:] if not a.startswith("--")]
    if argv[:1] == ["show"] and rest and not ID.match(rest[0]):
        return show_main(argv[1:])
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    topic, ids = args[0], args[1:]
    if "--abstract" in argv:
        rows = abstract_rows(topic)
        if rows is None:
            return 2
        ids += rows
    bad = [i for i in ids if not ID.match(i)]
    if bad or not ids:
        print(f"error: expected paper IDs such as 2408.03314, hep-th/9901001 or CorpusId:6628106; got {bad or 'none'}")
        return 2

    out = ROOT / "graphs" / topic / "fulltext"
    out.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    failed, first = [], True
    for aid in dict.fromkeys(ids):
        path = file_of(topic, aid)
        if path.exists() and "--refresh" not in argv:
            print(f"cached   {aid}")
            continue
        if not first:
            time.sleep(PAUSE)
        first = False
        if ARXIV_ONLY.match(aid):
            got = from_html(aid)
            if got is None:
                time.sleep(PAUSE)
                got = from_pdf(aid)
        else:
            got = from_open_access(aid)
        if got is None:
            failed.append(aid)
            print(f"missing  {aid}: " + ("no HTML or PDF on arXiv" if ARXIV_ONLY.match(aid) else "no open-access PDF"))
            continue
        url, kind, text, note = got
        path.write_text(f"source: {url} ({kind})\nfetched: {today}\n\n{text}")
        heads = sum(1 for ln in text.splitlines() if ln.startswith("## "))
        print(f"{kind:<8} {aid}: {len(text):,} chars (about {len(text) // 4:,} tokens), "
              + (note if note else f"{heads} sections"))
    if failed:
        # Not an error: these rows stay uncheckable (docs/verification.md, "Outcomes"). The exit status is 0, so that
        # only a real failure, such as arXiv itself not answering, halts the pass (H3).
        print(f"note:    {len(failed)} paper(s) have no fetchable full text: {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
