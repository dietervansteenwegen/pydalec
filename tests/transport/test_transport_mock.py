"""Unit tests for `pydalec.transport.mock`."""

from pydalec.transport.mock import MockTransport


def test_mock_transport_init_sets_defaults():
    """Verify default constructor values for the mock transport."""
    transport = MockTransport()
    assert transport.delay == 0.0
    assert transport.error_rate == 0.0
    assert transport.measurement_log.maxlen == 40


def test_mock_transport_default_measurement_log_size_is_40():
    """Verify default measurement_log maxlen is 40."""
    transport = MockTransport()
    assert transport.measurement_log.maxlen == 40


def test_mock_transport_resize_measurement_log_keeps_existing_records():
    """Verify growing log size keeps current records."""
    transport = MockTransport()
    transport.set_measurement_log_size(2)
    transport.measurement_log.extend(['m1', 'm2'])

    transport.set_measurement_log_size(4)

    assert transport.measurement_log.maxlen == 4
    assert list(transport.measurement_log) == ['m1', 'm2']


def test_mock_transport_resize_measurement_log_drops_oldest_on_shrink():
    """Verify shrinking log size keeps newest records only."""
    transport = MockTransport()
    transport.set_measurement_log_size(4)
    transport.measurement_log.extend(['m1', 'm2', 'm3'])

    transport.set_measurement_log_size(2)

    assert transport.measurement_log.maxlen == 2
    assert list(transport.measurement_log) == ['m2', 'm3']


def test_mock_transport_resize_measurement_log_rejects_invalid_size():
    """Verify resizing rejects non-positive sizes."""
    transport = MockTransport()

    try:
        transport.set_measurement_log_size(0)
    except ValueError as exc:
        assert 'size' in str(exc)
    else:
        err_msg = 'Expected ValueError for size=0'
        raise AssertionError(err_msg)


def test_mock_transport_send_strips_command():
    """Verify send strips whitespace around the command."""
    transport = MockTransport()
    transport.send('  READ:TEMP?  ')
    assert transport._last_cmd == 'READ:TEMP?'


def test_mock_transport_disconnect_is_noop():
    """Verify disconnect method leaves the transport in a disconnected state."""
    transport = MockTransport()
    transport.disconnect()
    assert transport.connected is False
