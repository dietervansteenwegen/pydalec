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


def test_dalec_connect_mock(monkeypatch):
    """Verify connect_mock constructs a client with a mock transport."""
    recorded = {}

    class FakeMockTransport:
        def __init__(self, delay, error_rate):
            recorded['delay'] = delay
            recorded['error_rate'] = error_rate

    monkeypatch.setattr('pydalec.client.MockTransport', FakeMockTransport)

    client = DALEC.connect_mock(delay=0.25, error_rate=0.1)

    assert isinstance(client.transport, FakeMockTransport)
    assert recorded == {'delay': 0.25, 'error_rate': 0.1}


def test_dalec_measurement_log_returns_copy_not_original_list():
    """Verify measurment_log returns a shallow copy of transport log."""

    class _LogTransport:
        def __init__(self):
            self.measurement_log = ['m1', 'm2']

    transport = _LogTransport()
    client = DALEC(transport)

    exported = client.measurment_log
    exported.append('m3')

    assert exported == ['m1', 'm2', 'm3']
    assert transport.measurement_log == ['m1', 'm2']


def test_dalec_str_includes_transport_string():
    """Verify __str__ delegates to transport string representation."""

    class _StringyTransport:
        def __str__(self):
            return 'tcp://127.0.0.1:23'

    client = DALEC(_StringyTransport())

    assert str(client) == 'DALEC at tcp://127.0.0.1:23'


def test_dalec_get_temperature_sends_and_parses_float():
    """Verify get_temperature sends command and parses numeric response."""
    transport = _DummyTransport(response='24.50')
    client = DALEC(transport)

    temperature = client.get_temperature()

    assert temperature == 24.5
    assert transport.commands == ['READ:TEMP?']
