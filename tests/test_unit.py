"""Unit tests for the synchronous DALEC client and mock transport."""

from pydalec.client import DALEC
from pydalec.transport.mock import MockTransport


def test_temp():
    """Verify temperature readback from the default mock transport state."""
    client = DALEC(MockTransport())
    assert client.get_temperature() == 25.0
