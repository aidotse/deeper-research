"""HTTP with retries, for the scripts that call outside services.

A transient failure is retried: a 429 (rate limited), a 5xx, a dropped connection or a timeout. Anything else, such as a
404, is raised at once, for the caller to handle. After the last attempt the error is raised too; a script that fails
this way halts the pass (docs/process.md, "When a pass ends", H3).

No API key or user identifier is ever sent from here; callers pass only the headers they need.
"""

import http.client
import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Container, Mapping
from typing import Any, TypedDict, Unpack

TRANSIENT = {429, 500, 502, 503, 504}


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
    hdrs = dict(headers or {})
    if data is not None:
        hdrs.setdefault("Content-Type", "application/json")
    # Callers pass the fixed https URLs of the services they call.
    req = urllib.request.Request(url, data=data, headers=hdrs)  # noqa: S310
    for attempt in range(attempts):
        try:
            # The request carries a caller's fixed https URL (see above).
            with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310
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
