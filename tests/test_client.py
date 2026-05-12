"""Unit tests for `pydalec.instrument`."""

import math
from collections import deque

import pytest

from pydalec.errors import PyDalecNoPositionDataError
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


class _FakeLocation:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon


class _FakeMeasurement:
    def __init__(self, lat, lon):
        self.location = _FakeLocation(lat, lon)


class _LocationTransport:
    def __init__(self, measurement_log=None):
        self.measurement_log = deque(measurement_log or [], maxlen=40)
        self.start_calls = 0
        self.stop_calls = 0
        self._connected = True

    @property
    def connected(self):
        return self._connected

    def start_measurements(self):
        self.start_calls += 1

    def stop_measurements(self):
        self.stop_calls += 1


class _TemporaryLocationTransport(_LocationTransport):
    def start_measurements(self):
        super().start_measurements()
        self.measurement_log.clear()
        self.measurement_log.append(_FakeMeasurement(float('nan'), float('nan')))
        self.measurement_log.append(_FakeMeasurement(51.1234, 4.5678))


class _TemporaryFirstFixTransport(_LocationTransport):
    def start_measurements(self):
        super().start_measurements()
        self.measurement_log.clear()
        self.measurement_log.append(_FakeMeasurement(12.34, 56.78))


def test_get_location_uses_existing_measurements_when_already_measuring():
    transport = _LocationTransport(
        measurement_log=[_FakeMeasurement(float('nan'), float('nan')), _FakeMeasurement(10.0, 20.0)]
    )
    client = Dalec(transport)
    client.status.measuring = True

    location = client.get_location(timeout=0.1)

    assert location.lat == 10.0
    assert location.lon == 20.0
    assert transport.start_calls == 0
    assert transport.stop_calls == 0


def test_get_location_temporarily_measures_and_restores_log_state():
    original_measurement = _FakeMeasurement(1.0, 2.0)
    transport = _TemporaryLocationTransport(measurement_log=[original_measurement])
    client = Dalec(transport)
    client.status.measuring = False

    location = client.get_location(timeout=0.2)

    assert location.lat == 51.1234
    assert location.lon == 4.5678
    assert transport.start_calls == 1
    assert transport.stop_calls == 1
    assert list(transport.measurement_log) == [original_measurement]
    assert client.status.measuring is False


def test_get_location_returns_first_fix_after_temporary_start():
    original_measurement = _FakeMeasurement(float('nan'), float('nan'))
    transport = _TemporaryFirstFixTransport(measurement_log=[original_measurement])
    client = Dalec(transport)
    client.status.measuring = False

    location = client.get_location(timeout=0.2)

    assert location.lat == 12.34
    assert location.lon == 56.78


def test_get_location_timeout_raises_and_restores_state():
    original_measurement = _FakeMeasurement(float('nan'), float('nan'))
    transport = _LocationTransport(measurement_log=[original_measurement])
    client = Dalec(transport)
    client.status.measuring = False

    with pytest.raises(PyDalecNoPositionDataError):
        client.get_location(timeout=0.05)

    assert transport.start_calls == 1
    assert transport.stop_calls == 1
    assert list(transport.measurement_log) == [original_measurement]
    assert client.status.measuring is False


def test_get_location_rejects_non_positive_timeout():
    transport = _LocationTransport()
    client = Dalec(transport)

    with pytest.raises(ValueError, match='timeout'):
        client.get_location(timeout=0.0)


def test_has_valid_position_fix_rejects_nan_values():
    measurement = _FakeMeasurement(float('nan'), 10.0)

    assert Dalec._has_valid_position_fix(measurement) is False
    assert math.isnan(measurement.location.lat)
