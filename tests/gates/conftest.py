"""Fixtures of the gate suites: the fixture topic is removed when a process's tests end, pass or fail."""

from collections.abc import Iterator

import pytest

from tests.gates import autoclean, clean


@pytest.fixture(scope="session", autouse=True)
def gate_topic() -> Iterator[None]:
    """Remove this process's fixture topic at the end of the session, and at exit should the process crash first.

    Each process (the plain pytest run, or each xdist worker) has its own topic, `zz-gate-<pid>`, so one worker's
    cleanup never touches another's files.
    """
    autoclean()
    try:
        yield
    finally:
        clean()
