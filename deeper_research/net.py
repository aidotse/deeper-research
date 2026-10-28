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

TRANSIENT = {429, 500, 502, 503, 504}


def request(url, body=None, headers=None, attempts=8, wait=lambda a: 5 * (a + 1), transient=TRANSIENT, timeout=120):
    """Return (status, final URL, body bytes). `body`, if given, is sent as JSON. `wait(a)` is the pause after attempt a."""
    data = json.dumps(body).encode() if body is not None else None
    hdrs = dict(headers or {})
    if data is not None:
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=hdrs)
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
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


def get_json(url, body=None, **kw):
    return json.loads(request(url, body, **kw)[2])
