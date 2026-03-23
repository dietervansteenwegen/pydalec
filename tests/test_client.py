"""Unit tests for `pydalec.client`."""

from pydalec.client import DALEC


class _DummyTransport:
    """Small fake transport for client unit tests."""

    def __init__(self, response='25.00'):
        self.commands = []
        self.response = response

    def send(self, data):
        self.commands.append(data)

    def receive(self):
        return self.response


def test_dalec_init_sets_transport():
    """Verify constructor stores the provided transport object."""
    transport = _DummyTransport()
    client = DALEC(transport)
    assert client.transport is transport


def test_dalec_connect_tcp(monkeypatch):
    """Verify connect_tcp constructs a client with a TCP transport."""
    recorded = {}

    class FakeTCPTransport:
        def __init__(self, host, port):
            recorded['host'] = host
            recorded['port'] = port

    monkeypatch.setattr('pydalec.client.TCPTransport', FakeTCPTransport)

    client = DALEC.connect_tcp('10.0.0.5', 9999)

    assert isinstance(client.transport, FakeTCPTransport)
    assert recorded == {'host': '10.0.0.5', 'port': 9999}


def test_dalec_get_temperature_sends_and_parses_float():
    """Verify get_temperature sends command and parses numeric response."""
    transport = _DummyTransport(response='24.50')
    client = DALEC(transport)

    temperature = client.get_temperature()

    assert temperature == 24.5
    assert transport.commands == ['READ:TEMP?']
