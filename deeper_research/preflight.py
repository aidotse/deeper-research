"""Run the preflight checks a pass needs before it starts, other than the ones only an agent can run.

The preflight checks that need no agent: the Semantic Scholar Graph API, the arXiv API and HTML, `uv`, and the
Asta key (docs/external_services.md, "Preflight").

Usage: uv run python -m deeper_research.preflight

Prints one line per check and the matching part of the retrieval log's `Preflight` line, and exits 1 if any check
fails, which halts the pass (H1). An unreachable service is tried twice, 90 s each, before it counts as failed. A
Graph API 429 counts as reachable: it means busy, and the scripts retry. The Graph API check says whether the
Semantic Scholar key (S2_API_KEY) is in use; the key is optional, but one that is set and refused (401 or 403) fails the
check. The Asta tools and WebSearch are checked by the `survey-pass` agent, since only an agent can call them.

Each request is one small GET or POST for a public paper. The Graph API request carries the Semantic Scholar key, if
set, and waits its turn as the scripts' requests do (deeper_research/net.py); no other key and no user identifier is
sent.
"""

import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from typing import cast

from deeper_research import asta_config, net

PAPER = "2106.15928"
HEADERS = {"User-Agent": "deeper-research preflight"}
S2_URL = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=title"


# BUG?: with tries < 1 the loop never runs and the function returns None
def status(url: str, data: bytes | None = None, tries: int = 2) -> int | str:  # type: ignore[return]
    """The HTTP status, or why the service could not be reached.

    A slow service gets a second try: the arXiv API
    has been seen to take over 60 s to answer and still answer 200.
    """
    # Callers pass the fixed https URLs of the services checked.
    req = urllib.request.Request(  # noqa: S310
        url,
        data=data,
        headers=dict(HEADERS, **({"Content-Type": "application/json"} if data else {}), **net.s2_headers(url)),
    )
    for attempt in range(tries):
        if net.is_s2(url):
            net.s2_turn()
        try:
            with net.OPENER.open(req, timeout=90) as r:
                return cast("int", r.status)
        except urllib.error.HTTPError as e:
            return e.code
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt == tries - 1:
                return f"unreachable ({type(e).__name__}, {tries} tries)"


def main() -> int:
    """Run the checks, print one line each and the log's summary, and return 1 if any failed, else 0."""
    checks = []
    s2 = status(S2_URL, f'{{"ids":["ARXIV:{PAPER}"]}}'.encode())
    keyed = bool(net.s2_headers(S2_URL))
    mode = "key" if keyed else "no key"
    if s2 == 200:
        graph = f"ok ({mode})"
    elif s2 == 429:
        graph = f"ok ({mode}; 429, busy)"
    elif keyed and s2 in (401, 403):
        graph = f"failed ({s2}: the S2_API_KEY key was refused)"
    else:
        graph = f"failed ({mode}; {s2})"
    checks.append(("Graph API", s2 in (200, 429), graph))
    api = status(f"https://export.arxiv.org/api/query?id_list={PAPER}")
    html = status(f"https://arxiv.org/html/{PAPER}")
    ok = api == 200 and html in (200, 404)  # 404: no HTML for this paper, but the site answers
    checks.append(("arXiv", ok, "ok" if ok else f"failed (API {api}, HTML {html})"))
    uv = shutil.which("uv")
    # A fixed argument list: the `uv` found on PATH, asked for its version.
    version = (
        subprocess.run([uv, "--version"], capture_output=True, text=True, check=False).stdout.strip()  # noqa: S603
        if uv
        else ""
    )
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
