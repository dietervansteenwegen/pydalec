"""Unit tests for `pydalec.instrument`."""

from pydalec.instrument import Dalec


class _DummyTransport:
    """Small fake transport for client unit tests."""

    def __init__(self, response='25.00'):
        self.commands = []
        self.response = response
        self._connected = True

    @property
    def connected(self):
        return self._connected

    def send(self, data):
        self.commands.append(data)

    def receive(self):
        return self.response


def test_dalec_init_sets_transport():
    """Verify constructor stores the provided transport object."""
    transport = _DummyTransport()
    client = Dalec(transport)
    assert client.transport is transport


def test_dalec_connect_tcp(monkeypatch):
    """Verify connect_tcp constructs a client with a TCP transport."""
    recorded = {}

    class FakeTCPTransport:
        def __init__(self, host, port):
            recorded['host'] = host
            recorded['port'] = port

    monkeypatch.setattr('pydalec.instrument.TCPTransport', FakeTCPTransport)

    client = Dalec.connect_tcp('10.0.0.5', 9999)

    assert isinstance(client.transport, FakeTCPTransport)
    assert recorded == {'host': '10.0.0.5', 'port': 9999}


def test_dalec_connect_mock(monkeypatch):
    """Verify connect_mock constructs a client with a mock transport."""
    recorded = {}

    class FakeMockTransport:
        def __init__(self, delay, error_rate):
            recorded['delay'] = delay
            recorded['error_rate'] = error_rate

    monkeypatch.setattr('pydalec.instrument.MockTransport', FakeMockTransport)

    client = Dalec.connect_mock(delay=0.25, error_rate=0.1)

    assert isinstance(client.transport, FakeMockTransport)
    assert recorded == {'delay': 0.25, 'error_rate': 0.1}


def test_dalec_measurement_log_returns_copy_not_original_list():
    """Verify measurment_log returns a shallow copy of transport log."""

    class _LogTransport:
        def __init__(self):
            self.measurement_log = ['m1', 'm2']

    transport = _LogTransport()
    client = Dalec(transport)

    exported = client.measurement_log
    exported.append('m3')

    assert exported == ['m1', 'm2', 'm3']
    assert transport.measurement_log == ['m1', 'm2']


def test_dalec_str_includes_transport_string():
    """Verify __str__ delegates to transport string representation."""

    class _StringyTransport:
        def __str__(self):
            return 'tcp://127.0.0.1:23'

    client = Dalec(_StringyTransport())

    assert str(client) == 'DALEC at tcp://127.0.0.1:23'


class _ConnectableTransport:
    """Minimal fake transport that supports connect/disconnect state changes."""

    def __init__(self, initially_connected=True):
        self._connected = initially_connected
        self.connect_calls = 0
        self.disconnect_calls = 0

    @property
    def connected(self):
        return self._connected

    def connect(self):
        self._connected = True
        self.connect_calls += 1

    def disconnect(self):
        self._connected = False
        self.disconnect_calls += 1


def test_dalec_connected_reads_from_transport():
    """Verify connected property reflects transport state, not a cached copy."""
    transport = _ConnectableTransport(initially_connected=False)
    client = Dalec(transport)
    assert client.connected is False

    transport._connected = True
    assert client.connected is True


def test_dalec_disconnect_delegates_to_transport():
    """Verify disconnect() calls through to the transport and connected becomes False."""
    transport = _ConnectableTransport(initially_connected=True)
    client = Dalec(transport)

    client.disconnect()

    assert transport.disconnect_calls == 1
    assert client.connected is False


def test_dalec_connect_when_disconnected_calls_transport():
    """Verify connect() calls transport.connect() when currently disconnected."""
    transport = _ConnectableTransport(initially_connected=False)
    client = Dalec(transport)

    client.connect()

    assert transport.connect_calls == 1
    assert client.connected is True


def test_dalec_connect_when_already_connected_is_noop():
    """Verify connect() does not call transport.connect() when already connected."""
    transport = _ConnectableTransport(initially_connected=True)
    client = Dalec(transport)

    client.connect()

    assert transport.connect_calls == 0
    assert client.connected is True
