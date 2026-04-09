"""Unit tests for `pydalec.transport.mock`."""

from pydalec.transport.mock import MockTransport


def test_mock_transport_init_sets_defaults():
    """Verify default constructor values for the mock transport."""
    transport = MockTransport()
    assert transport.delay == 0.0
    assert transport.error_rate == 0.0


def test_mock_transport_send_strips_command():
    """Verify send strips whitespace around the command."""
    transport = MockTransport()
    transport.send('  READ:TEMP?  ')
    assert transport._last_cmd == 'READ:TEMP?'


def test_mock_transport_disconnect_is_noop():
    """Verify close can be called without changing mock behavior."""
    transport = MockTransport()

    assert transport.disconnect() is None
