"""Unit tests for `pydalec.transport.mock`."""

from pydalec.transport.mock import MockTransport


def test_mock_transport_init_sets_defaults():
    """Verify default constructor values for the mock transport."""
    transport = MockTransport()
    assert transport.delay == 0.0
    assert transport.error_rate == 0.0
    assert transport.temperature == 25.0


def test_mock_transport_send_strips_command():
    """Verify send strips whitespace around the command."""
    transport = MockTransport()
    transport.send('  READ:TEMP?  ')
    assert transport._last_cmd == 'READ:TEMP?'


def test_mock_transport_receive_temperature(monkeypatch):
    """Verify receive returns formatted temperature for READ:TEMP?."""
    transport = MockTransport()
    transport.temperature = 26.789
    transport.send('READ:TEMP?')
    monkeypatch.setattr('pydalec.transport.mock.random.random', lambda: 0.99)

    assert transport.receive() == '26.79'


def test_mock_transport_receive_unknown_command(monkeypatch):
    """Verify unknown commands return ERROR."""
    transport = MockTransport()
    transport.send('READ:HUM?')
    monkeypatch.setattr('pydalec.transport.mock.random.random', lambda: 0.99)

    assert transport.receive() == 'ERROR'


def test_mock_transport_receive_error_rate(monkeypatch):
    """Verify random error path returns ERROR."""
    transport = MockTransport(error_rate=0.5)
    transport.send('READ:TEMP?')
    monkeypatch.setattr('pydalec.transport.mock.random.random', lambda: 0.1)

    assert transport.receive() == 'ERROR'


def test_mock_transport_receive_applies_delay(monkeypatch):
    """Verify receive sleeps when delay is configured."""
    sleep_calls = []
    transport = MockTransport(delay=0.25)
    transport.send('READ:TEMP?')

    monkeypatch.setattr('pydalec.transport.mock.random.random', lambda: 0.99)
    monkeypatch.setattr(
        'pydalec.transport.mock.time.sleep', lambda value: sleep_calls.append(value)
    )

    transport.receive()
    assert sleep_calls == [0.25]


def test_mock_transport_close_is_noop():
    """Verify close can be called without changing mock behavior."""
    transport = MockTransport()

    assert transport.close() is None
