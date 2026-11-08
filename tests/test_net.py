"""The Semantic Scholar key and pacing in `deeper_research/net.py`: the key reaches that API's host and no other."""

import urllib.request
from pathlib import Path
from typing import Any

import pytest

from deeper_research import net

S2 = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=title"
ARXIV = "https://export.arxiv.org/api/query?id_list=2106.15928"


class FakeResponse:
    """Enough of an HTTP response for `net.request`."""

    status = 200

    def __init__(self, url: str) -> None:
        """A response from `url`."""
        self.url = url

    def __enter__(self) -> "FakeResponse":
        """The response itself, as urllib's is."""
        return self

    def __exit__(self, *exc: object) -> None:
        """Nothing to close."""

    def geturl(self) -> str:
        """The URL answered."""
        return self.url

    def read(self) -> bytes:
        """An empty JSON list."""
        return b"[]"


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> list[urllib.request.Request]:
    """The requests `net.request` sends, answered without the network; the pacing is recorded as a 0 per turn."""
    out: list[urllib.request.Request] = []

    def fake_open(req: urllib.request.Request, timeout: float) -> FakeResponse:
        out.append(req)
        return FakeResponse(req.full_url)

    monkeypatch.setattr(net.OPENER, "open", fake_open)
    monkeypatch.setattr(net, "s2_turn", lambda: out.append(0))  # type: ignore[arg-type]
    return out


def key_of(req: urllib.request.Request) -> str | None:
    """The request's key header, if any."""
    return req.get_header("X-api-key")


def test_key_only_for_semantic_scholar(monkeypatch: pytest.MonkeyPatch) -> None:
    """The key header is for the Semantic Scholar API's host alone, and only when a key is set."""
    monkeypatch.setenv(net.S2_KEY_ENV, "k")
    assert net.s2_headers(S2) == {"x-api-key": "k"}
    assert net.s2_headers(ARXIV) == {}
    assert net.s2_headers("https://api.semanticscholar.org.example.com/graph/v1") == {}
    monkeypatch.setenv(net.S2_KEY_ENV, " ")
    assert net.s2_headers(S2) == {}
    monkeypatch.delenv(net.S2_KEY_ENV)
    assert net.s2_headers(S2) == {}


def test_request_sends_key_and_waits_its_turn(monkeypatch: pytest.MonkeyPatch, sent: list[Any]) -> None:
    """A Graph API request waits its turn and carries the key; a request to another host does neither."""
    monkeypatch.setenv(net.S2_KEY_ENV, "k")
    net.get_json(S2, {"ids": ["ARXIV:2106.15928"]})
    assert sent[0] == 0, "a Semantic Scholar request waits its turn first"
    assert key_of(sent[1]) == "k"
    sent.clear()
    net.request(ARXIV)
    assert len(sent) == 1, "another host's request does not wait"
    assert key_of(sent[0]) is None


def test_request_without_key(monkeypatch: pytest.MonkeyPatch, sent: list[Any]) -> None:
    """Without a key, a Graph API request goes unauthenticated, and still waits its turn."""
    monkeypatch.delenv(net.S2_KEY_ENV, raising=False)
    net.request(S2)
    assert sent[0] == 0, "an unauthenticated request is paced too"
    assert key_of(sent[1]) is None


@pytest.mark.parametrize(("to", "kept"), [(ARXIV, False), (S2 + "&x=1", True)])
def test_redirect_keeps_key_home(to: str, kept: bool) -> None:
    """A redirect keeps the key on the Semantic Scholar API's host and drops it anywhere else."""
    # A fixed https URL, and never opened.
    req = urllib.request.Request(S2, headers={"x-api-key": "k"})  # noqa: S310
    new = net.KeepKeyHome().redirect_request(req, None, 302, "Found", {}, to)
    assert new is not None
    assert (key_of(new) == "k") is kept


def test_turns_are_spaced(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A turn waits out what is left of S2_INTERVAL since the last one, and no longer."""
    now = [1000.0]
    slept: list[float] = []

    def sleep(s: float) -> None:
        slept.append(s)
        now[0] += s

    monkeypatch.setattr(net, "S2_CLOCK", tmp_path / "clock")
    monkeypatch.setattr("deeper_research.net.time.time", lambda: now[0])
    monkeypatch.setattr("deeper_research.net.time.sleep", sleep)
    net.s2_turn()
    assert slept == [], "the first turn does not wait"
    now[0] += 0.3
    net.s2_turn()
    assert slept == [pytest.approx(net.S2_INTERVAL - 0.3)]
    now[0] += 5
    net.s2_turn()
    assert len(slept) == 1, "a turn long after the last does not wait"
