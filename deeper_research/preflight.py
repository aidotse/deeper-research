"""The preflight checks that need no agent: the Semantic Scholar Graph API, the arXiv API and HTML, `uv`, and the
Asta key (docs/external_services.md, "Preflight").

Usage: uv run python -m deeper_research.preflight

Prints one line per check and the matching part of the retrieval log's `Preflight` line, and exits 1 if any check
fails, which halts the pass (H1). An unreachable service is tried twice, 90 s each, before it counts as failed. A
Graph API 429 counts as reachable: it means busy, and the scripts retry. The Asta tools and WebSearch are checked by
the `survey-pass` agent, since only an agent can call them.

Each request is one small unauthenticated GET or POST for a public paper; no key or user identifier is sent.
"""

import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from deeper_research import asta_config  # noqa: E402

PAPER = "2106.15928"
HEADERS = {"User-Agent": "deeper-research preflight"}


def status(url, data=None, tries=2):
    """The HTTP status, or why the service could not be reached. A slow service gets a second try: the arXiv API
    has been seen to take over 60 s to answer and still answer 200."""
    req = urllib.request.Request(url, data=data, headers=dict(HEADERS, **({"Content-Type": "application/json"}
                                                                          if data else {})))
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status
        except urllib.error.HTTPError as e:
            return e.code
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt == tries - 1:
                return f"unreachable ({type(e).__name__}, {tries} tries)"


def main():
    checks = []
    s2 = status("https://api.semanticscholar.org/graph/v1/paper/batch?fields=title",
                f'{{"ids":["ARXIV:{PAPER}"]}}'.encode())
    checks.append(("Graph API", s2 in (200, 429), "ok" if s2 == 200 else "ok (429, busy)" if s2 == 429 else f"failed ({s2})"))
    api = status(f"https://export.arxiv.org/api/query?id_list={PAPER}")
    html = status(f"https://arxiv.org/html/{PAPER}")
    ok = api == 200 and html in (200, 404)  # 404: no HTML for this paper, but the site answers
    checks.append(("arXiv", ok, "ok" if ok else f"failed (API {api}, HTML {html})"))
    uv = shutil.which("uv")
    version = subprocess.run([uv, "--version"], capture_output=True, text=True).stdout.strip() if uv else ""
    checks.append(("uv", bool(version), "ok" if version else "failed (not installed)"))
    key = asta_config.main(["--quiet"]) == 0
    checks.append(("Asta key", key, "set" if key else "not set"))

    for name, passed, text in checks:
        print(f"{'ok  ' if passed else 'FAIL'}  {name}: {text}")
    print("\nfor the log's Preflight line, after the agent's Asta and WebSearch checks:")
    print(" | ".join(f"{name} {text}" for name, _, text in checks))
    failed = [name for name, passed, _ in checks if not passed]
    if failed:
        print(f"\nSTOP: H1 — preflight failed: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
