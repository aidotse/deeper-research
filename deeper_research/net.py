"""HTTP with retries, for the scripts that call outside services.

A transient failure is retried: a 429 (rate limited), a 5xx, a dropped connection or a timeout. Anything else, such as a
404, is raised at once, for the caller to handle. After the last attempt the error is raised too; a script that fails
this way halts the pass (docs/process.md, "When a pass ends", H3).

A request to the Semantic Scholar API waits its turn first: requests from every process on the machine are spaced
S2_INTERVAL apart, since the key's rate limit counts every endpoint together. It carries the key in S2_KEY_ENV, if set,
and only such a request does: the key is never sent to another host. No other key and no user identifier is sent from
here (docs/external_services.md, "Credentials and privacy").
"""

import fcntl
import http.client
import json
import os
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Container, Mapping
from pathlib import Path
from typing import Any, TypedDict, Unpack

TRANSIENT = {429, 500, 502, 503, 504}

S2_HOST = "api.semanticscholar.org"
S2_KEY_ENV = "S2_API_KEY"
# The key's limit is 1 request per second; the margin keeps clock jitter from breaking it.
S2_INTERVAL = 1.1
# When the last Semantic Scholar request was sent, shared by every process of this user on the machine.
S2_CLOCK = Path(tempfile.gettempdir()) / f"deeper-research-s2-{os.getuid()}.clock"


def is_s2(url: str) -> bool:
    """Whether the URL is on the Semantic Scholar API's host."""
    return urllib.parse.urlsplit(url).hostname == S2_HOST


def s2_headers(url: str) -> dict[str, str]:
    """The key header for a Semantic Scholar API URL when S2_KEY_ENV is set; empty for any other URL, or no key."""
    key = os.environ.get(S2_KEY_ENV, "").strip()
    return {"x-api-key": key} if key and is_s2(url) else {}


class KeepKeyHome(urllib.request.HTTPRedirectHandler):
    """Follows redirects as urllib does, but drops the key header when one leaves the Semantic Scholar API's host.

    urllib copies a request's headers onto the redirected request, wherever it points.
    """

    def redirect_request(  # noqa: PLR0913
        self,
        req: urllib.request.Request,
        fp: Any,  # noqa: ANN401
        code: int,
        msg: str,
        headers: Any,  # noqa: ANN401
        newurl: str,
    ) -> urllib.request.Request | None:
        """The redirect urllib builds, minus the key header unless `newurl` is on the Semantic Scholar API."""
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and not is_s2(newurl):
            for name in [h for h in new.headers if h.lower() == "x-api-key"]:
                del new.headers[name]
        return new


OPENER = urllib.request.build_opener(KeepKeyHome)


def s2_turn() -> None:
    """Wait until S2_INTERVAL has passed since the last Semantic Scholar request from any process, then stamp the clock.

    The lock is held while waiting, so concurrent scripts take turns rather than sending together.
    """
    with S2_CLOCK.open("a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        try:
            last = float(f.read() or 0)
        except ValueError:
            last = 0.0
        pause = last + S2_INTERVAL - time.time()
        if pause > 0:
            time.sleep(pause)
        f.seek(0)
        f.truncate()
        f.write(repr(time.time()))


class RequestOptions(TypedDict, total=False):
    """The keyword arguments `get_json` passes on to `request`."""

    headers: Mapping[str, str] | None
    attempts: int
    wait: Callable[[int], float]
    transient: Container[int]
    timeout: float


# BUG?: with attempts < 1 the loop never runs and the function returns None
def request(  # type: ignore[return]
    url: str,
    body: dict[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    attempts: int = 8,
    wait: Callable[[int], float] = lambda a: 5 * (a + 1),
    transient: Container[int] = TRANSIENT,
    timeout: float = 120,
) -> tuple[int, str, bytes]:
    """Return (status, final URL, body bytes).

    `body`, if given, is sent as JSON. `wait(a)` is the pause after attempt a.
    """
    data = json.dumps(body).encode() if body is not None else None
    hdrs = dict(headers or {}, **s2_headers(url))
    if data is not None:
        hdrs.setdefault("Content-Type", "application/json")
    # Callers pass the fixed https URLs of the services they call.
    req = urllib.request.Request(url, data=data, headers=hdrs)  # noqa: S310
    for attempt in range(attempts):
        if is_s2(url):
            s2_turn()
        try:
            # The request carries a caller's fixed https URL (see above).
            with OPENER.open(req, timeout=timeout) as r:
                return r.status, r.geturl(), r.read()
        except urllib.error.HTTPError as e:
            if e.code not in transient or attempt == attempts - 1:
                raise
            reason = f"HTTP {e.code}"
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException) as e:
            if attempt == attempts - 1:
                raise
            reason = type(e).__name__
        pause = wait(attempt)
        print(f"  {reason}; retrying in {pause}s ({attempt + 1}/{attempts - 1})")
        time.sleep(pause)


# Parsed JSON is as loose as the service's answer: a list from the batch endpoints, an object from the others.
def get_json(url: str, body: dict[str, Any] | None = None, **kw: Unpack[RequestOptions]) -> Any:  # noqa: ANN401
    """`request` the URL and return its body parsed as JSON."""
    return json.loads(request(url, body, **kw)[2])
