# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf"]
# ///
"""Fetch the full text of papers into a topic's cache, for verification.

Usage:
  uv run tools/fulltext.py <topic> <paper-id> [<paper-id> ...] [--refresh]
  uv run tools/fulltext.py <topic> --abstract [--refresh]

Writes graphs/<topic>/fulltext/<id>.txt: the paper's text, verbatim, with a
two-line provenance header. `--abstract` fetches every coreset row whose
`source` is still `abstract`, which is what verification needs when snippet
search has no body text for a paper (see docs/verification.md).

The text comes from arXiv's HTML rendering, which keeps section headings,
figure and table captions, and equations (as their LaTeX source). Papers whose
LaTeX did not convert to HTML fall back to the PDF's extracted text, with page
markers; that text is noisier, and equations in it are unreliable. The
bibliography is dropped. A paper without an arXiv ID (CorpusId:<n>) is fetched
from the open-access PDF that Semantic Scholar lists for it, if there is one;
otherwise it cannot be fetched, and its row stays uncheckable.

No model is involved, so nothing is paraphrased: an agent searches the file
with Grep, reads the matching sections, and quotes them. Requests are spaced
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import ARXIV_ONLY, ID, ROOT, row_id, sections, table_rows  # noqa: E402
from net import get_json, request  # noqa: E402

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
    return f"https://arxiv.org/html/{aid}{version.group(1) if version else ''}", "html", parser.text()


def from_pdf(aid):
    from pypdf import PdfReader

    status, url, body = get(f"https://arxiv.org/pdf/{aid}")
    if status != 200:
        return None
    pages = PdfReader(io.BytesIO(body)).pages
    text = "\n\n".join(f"[page {i}]\n{p.extract_text() or ''}" for i, p in enumerate(pages, 1))
    return url, "pdf", text.strip() + "\n"


def from_open_access(pid):
    """A paper without an arXiv ID: the open-access PDF Semantic Scholar lists for it, if any."""
    from pypdf import PdfReader

    rec = get_json("https://api.semanticscholar.org/graph/v1/paper/batch?fields=openAccessPdf", {"ids": [pid]})[0]
    url = ((rec or {}).get("openAccessPdf") or {}).get("url") or ""
    if not url.startswith(("https://", "http://")):
        return None
    try:
        status, final, body = get(url)
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        # A publisher's server refusing or failing is a fact about this paper, not a failure of the run.
        return None
    if status != 200 or not body.startswith(b"%PDF"):
        return None
    pages = PdfReader(io.BytesIO(body)).pages
    text = "\n\n".join(f"[page {i}]\n{p.extract_text() or ''}" for i, p in enumerate(pages, 1))
    return final, "pdf, open access", text.strip() + "\n"


def abstract_rows(topic):
    secs = sections((ROOT / "surveys" / f"{topic}.md").read_text())
    ids = []
    for h, c, _, line in table_rows(secs["Coreset"]):
        if h and h[0] == "paper" and c and c[-1] == "abstract" and row_id(line):
            ids.append(row_id(line))
    return list(dict.fromkeys(ids))


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    topic, ids = args[0], args[1:]
    if "--abstract" in argv:
        ids += abstract_rows(topic)
    bad = [i for i in ids if not ID.match(i)]
    if bad or not ids:
        print(f"error: expected paper IDs such as 2408.03314, hep-th/9901001 or CorpusId:6628106; got {bad or 'none'}")
        return 2

    out = ROOT / "graphs" / topic / "fulltext"
    out.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    failed, first = [], True
    for aid in dict.fromkeys(ids):
        # Pre-2007 IDs contain a slash (hep-th/9901001), corpus IDs a colon; keep the file name plain.
        path = out / f"{aid.replace('/', '_').replace(':', '_')}.txt"
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
        url, kind, text = got
        path.write_text(f"source: {url} ({kind})\nfetched: {today}\n\n{text}")
        heads = sum(1 for ln in text.splitlines() if ln.startswith("## "))
        print(f"{kind:<8} {aid}: {len(text):,} chars (about {len(text) // 4:,} tokens), {heads} sections")
    if failed:
        # Not an error: these rows stay uncheckable (docs/verification.md, "Outcomes"). The exit status is 0, so that
        # only a real failure, such as arXiv itself not answering, halts the pass (H3).
        print(f"note:    {len(failed)} paper(s) have no fetchable full text: {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
