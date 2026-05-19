"""Unit tests for `pydalec.transport.tcp`."""

import datetime

from pydalec.measurement import Coordinates, Measurement, StatusFlag, Telemetry
from pydalec.transport.tcp import TCPTransport

UTC = datetime.timezone.utc


def _measurement_payload(serial_number: str) -> str:
    measurement = Measurement(
        device_id='DALEC',
        serial_number=serial_number,
        channel_type='Ed',
        utc_time=datetime.datetime(2024, 6, 1, 12, 0, 0, tzinfo=UTC),
        location=Coordinates(lat=51.5, lon=4.3),
        sat_compass_heading=180.0,
        solar_azimuth_deg=90.0,
        solar_zenith_deg=45.0,
        gear_position_deg=0.0,
        azimuth_deg=270.0,
        relative_azimuth_deg=-90.0,
        pitch_start_measurement_deg=0.0,
        roll_start_measurement_deg=0.0,
        telemetry=Telemetry(
            voltage_volts=12.1,
            humidity_mm_hg=55.3,
            temperature_diode_celsius=23.456,
            status_flag=StatusFlag.STATIONARY,
        ),
        int_time=100,
        signal_percentage=75.0,
        dark_counts=100,
        max_counts=60000,
        spectrum=[1000] * 190,
    )
    fields = [
        measurement.device_id,
        str(int(measurement.serial_number)),
        measurement.channel_type,
        measurement.utc_time.isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
        str(measurement.location.lat),
        str(measurement.location.lon),
        str(measurement.sat_compass_heading),
        str(measurement.solar_azimuth_deg),
        str(measurement.solar_zenith_deg),
        str(measurement.gear_position_deg),
        str(measurement.azimuth_deg),
        str(measurement.relative_azimuth_deg),
        str(measurement.pitch_start_measurement_deg),
        str(measurement.roll_start_measurement_deg),
        str(measurement.telemetry.voltage_volts),
        str(measurement.telemetry.humidity_mm_hg),
        str(measurement.telemetry.temperature_diode_celsius),
        f'{measurement.telemetry.status_flag:04b}',
        str(measurement.int_time),
        str(measurement.signal_percentage),
        str(measurement.dark_counts),
        str(measurement.max_counts),
        *[str(value) for value in measurement.spectrum],
    ]
    return ','.join(fields) + '\n'


class _FakeTelnetConnection:
    """Fake telnet connection used to isolate TCPTransport tests."""

    def __init__(self, lines=None):
        self.written: list[str] = []
        self.lines = list(lines or [])
        self._connected = False
        self.flush_calls = 0

    def connect(self):
        self._connected = True

    def write(self, data):
        self.written.append(data)

    def flush(self, timeout=None):
        del timeout
        self.flush_calls += 1

    def readline(self, timeout=None):
        del timeout
        if self.lines:
            item = self.lines.pop(0)
            if isinstance(item, BaseException):
                raise item
            return item
        raise EOFError

    def close(self):
        self._connected = False


def test_tcp_transport_init_uses_telnet_connection(monkeypatch):
    """Verify TCPTransport creates a telnet connection with host and port."""
    fake_connection = _FakeTelnetConnection()
    recorded = {}

    def fake_telnet_connection(host, port, **kwargs):
        recorded['host'] = host
        recorded['port'] = port
        recorded['kwargs'] = kwargs
        return fake_connection

    monkeypatch.setattr('pydalec.transport.tcp.TelnetConnection', fake_telnet_connection)

    transport = TCPTransport('localhost', 9999)

    assert transport._connection is fake_connection
    assert fake_connection._connected is True
    assert recorded['host'] == 'localhost'
    assert recorded['port'] == 9999
    assert recorded['kwargs'] == {'connect_minwait': 0.0, 'encoding': 'utf8'}
    assert transport.measurement_log.maxlen == 40


def test_tcp_transport_send_appends_newline_and_encodes(monkeypatch):
    """Verify send writes newline-terminated text."""
    fake_connection = _FakeTelnetConnection()
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )
    transport = TCPTransport('localhost', 9999)

    transport.send('START')

    assert fake_connection.written == ['START\r\n']
    assert fake_connection.flush_calls == 1


def test_tcp_transport_receive_decodes_and_strips(monkeypatch):
    """Verify receive strips trailing whitespace."""
    fake_connection = _FakeTelnetConnection(lines=['  VALUE  \n'])
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )
    transport = TCPTransport('localhost', 9999)

    assert transport._get_reply() == 'VALUE'


def test_tcp_transport_receive_returns_empty_string_after_eof_on_all_calls(monkeypatch):
    """Verify receive keeps returning empty string after the reader reaches EOF."""
    fake_connection = _FakeTelnetConnection()
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )
    transport = TCPTransport('localhost', 9999)
    assert transport._get_reply() is None
    assert transport._get_reply() is None


def test_tcp_transport_reader_stops_on_empty_raw_message(monkeypatch):
    """Verify an empty line from readline() is treated as end-of-stream."""
    fake_connection = _FakeTelnetConnection(lines=[''])
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )
    transport = TCPTransport('localhost', 9999)

    assert transport._get_reply() is None
    assert transport._get_reply() is None


def test_tcp_transport_reader_decodes_bytes_messages(monkeypatch):
    """Verify bytes returned by readline() are decoded before parsing."""
    fake_connection = _FakeTelnetConnection(lines=[b'  VALUE  \n'])
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )
    transport = TCPTransport('localhost', 9999)

    assert transport._get_reply() == 'VALUE'


def test_tcp_transport_logs_unsolicited_measurements(monkeypatch):
    """Verify unsolicited measurements are stored without breaking normal responses."""
    fake_connection = _FakeTelnetConnection(lines=[_measurement_payload('0001'), 'OK\n'])
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )

    transport = TCPTransport('localhost', 9999)

    assert transport._get_reply() == 'OK'
    assert len(transport.measurement_log) == 1
    assert transport.measurement_log[0].serial_number == '0001'


def test_tcp_transport_keeps_only_last_measurement_records(monkeypatch):
    """Verify the measurement log keeps only the configured number of records."""
    fake_connection = _FakeTelnetConnection(
        lines=[
            _measurement_payload('0001'),
            _measurement_payload('0002'),
            _measurement_payload('0003'),
        ]
    )
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )

    transport = TCPTransport('localhost', 9999)
    transport._reader_thread.join(timeout=1)
    transport.set_measurement_log_size(2)

    assert [measurement.serial_number for measurement in transport.measurement_log] == [
        '0002',
        '0003',
    ]


def test_tcp_transport_close_shuts_down_socket(monkeypatch):
    """Verify close shuts down the telnet connection and is safe to call twice."""
    fake_connection = _FakeTelnetConnection()
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )

    transport = TCPTransport('localhost', 9999)

    transport.disconnect()
    transport.disconnect()

    assert fake_connection._connected is False
    assert transport._reader_thread.is_alive() is False


def test_tcp_transport_reconnect_restarts_background_reader(monkeypatch):
    """Verify reconnect restarts the reader thread and resumes processing replies."""
    fake_connection = _FakeTelnetConnection()
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )

    transport = TCPTransport('localhost', 9999)
    initial_reader = transport._reader_thread

    transport.disconnect()
    fake_connection.lines.append('OK\n')

    transport.connect()
    transport._reader_thread.join(timeout=1)

    assert fake_connection._connected is True
    assert transport._reader_thread is not initial_reader
    assert transport._reader_thread.is_alive() is False
    assert transport._get_reply() == 'OK'


def test_tcp_transport_resize_measurement_log_keeps_existing_records(monkeypatch):
    """Verify growing the log preserves all current measurements."""
    fake_connection = _FakeTelnetConnection()
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )
    transport = TCPTransport('localhost', 9999)
    transport.set_measurement_log_size(2)

    transport._handle_incoming_data(_measurement_payload('0001').strip())
    transport._handle_incoming_data(_measurement_payload('0002').strip())
    transport.set_measurement_log_size(4)

    assert transport.measurement_log.maxlen == 4
    assert [measurement.serial_number for measurement in transport.measurement_log] == [
        '0001',
        '0002',
    ]


def test_tcp_transport_resize_measurement_log_drops_oldest_on_shrink(monkeypatch):
    """Verify shrinking the log keeps the newest records only."""
    fake_connection = _FakeTelnetConnection()
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )
    transport = TCPTransport('localhost', 9999)
    transport.set_measurement_log_size(4)

    transport._handle_incoming_data(_measurement_payload('0001').strip())
    transport._handle_incoming_data(_measurement_payload('0002').strip())
    transport._handle_incoming_data(_measurement_payload('0003').strip())
    transport.set_measurement_log_size(2)

    assert transport.measurement_log.maxlen == 2
    assert [measurement.serial_number for measurement in transport.measurement_log] == [
        '0002',
        '0003',
    ]


def test_tcp_transport_resize_measurement_log_rejects_invalid_size(monkeypatch):
    """Verify resizing rejects non-positive log sizes."""
    fake_connection = _FakeTelnetConnection()
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )
    transport = TCPTransport('localhost', 9999)

    try:
        transport.set_measurement_log_size(0)
    except ValueError as exc:
        assert 'size' in str(exc)
    else:
        err_msg = 'Expected ValueError for size=0'
        raise AssertionError(err_msg)


def test_tcp_transport_str_includes_host_and_port(monkeypatch):
    """Verify __str__ includes host and port."""
    fake_connection = _FakeTelnetConnection()
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )

    transport = TCPTransport('example.com', 2323)

    assert str(transport) == 'TCPTransport (example.com:2323)'


def _utc_dt(year: int, month: int, day: int, hour: int, minute: int, second: int):
    return datetime.datetime(year, month, day, hour, minute, second, tzinfo=UTC)


def test_tcp_transport_persists_valid_and_invalid_lines(monkeypatch, tmp_path):
    fake_connection = _FakeTelnetConnection()
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )

    transport = TCPTransport('localhost', 9999, data_root_dir=tmp_path, max_file_size_kb=32)
    timestamps = iter(
        [
            _utc_dt(2024, 6, 1, 12, 0, 0),
            _utc_dt(2024, 6, 1, 12, 0, 1),
        ]
    )
    transport._utc_now = lambda: next(timestamps)

    valid_line = _measurement_payload('0001').strip()
    invalid_line = 'not,a,measurement'

    transport._handle_incoming_data(valid_line)
    transport._handle_incoming_data(invalid_line)

    day_dir = tmp_path / '20240601'
    raw_files = list(day_dir.glob('*.raw'))
    error_files = list(day_dir.glob('*.error'))

    assert len(transport.measurement_log) == 1
    assert transport._get_reply() == invalid_line
    assert len(raw_files) == 1
    assert len(error_files) == 1
    assert raw_files[0].name.startswith('DALEC_20240601T120000.000000Z')
    assert error_files[0].name.startswith('DALEC_20240601T120001.000000Z')
    assert raw_files[0].read_text(encoding='utf-8').startswith('2024-06-01T12:00:00.000000Z ')
    assert error_files[0].read_text(encoding='utf-8').startswith('2024-06-01T12:00:01.000000Z ')


def test_tcp_transport_rolls_over_raw_stream_at_midnight(monkeypatch, tmp_path):
    fake_connection = _FakeTelnetConnection()
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )

    transport = TCPTransport('localhost', 9999, data_root_dir=tmp_path, max_file_size_kb=32)
    timestamps = iter(
        [
            _utc_dt(2024, 6, 1, 23, 59, 59),
            _utc_dt(2024, 6, 2, 0, 0, 1),
        ]
    )
    transport._utc_now = lambda: next(timestamps)

    transport._handle_incoming_data(_measurement_payload('0001').strip())
    transport._handle_incoming_data(_measurement_payload('0002').strip())

    day1_files = list((tmp_path / '20240601').glob('*.raw'))
    day2_files = list((tmp_path / '20240602').glob('*.raw'))

    assert len(day1_files) == 1
    assert len(day2_files) == 1
    assert day1_files[0].name.startswith('DALEC_20240601T235959.000000Z')
    assert day2_files[0].name.startswith('DALEC_20240602T000001.000000Z')


def test_tcp_transport_rotates_error_stream_independently(monkeypatch, tmp_path):
    fake_connection = _FakeTelnetConnection()
    monkeypatch.setattr(
        'pydalec.transport.tcp.TelnetConnection',
        lambda _host, _port, **_kwargs: fake_connection,
    )

    transport = TCPTransport('localhost', 9999, data_root_dir=tmp_path, max_file_size_kb=2)
    timestamps = iter(
        [
            _utc_dt(2024, 6, 1, 12, 0, 0),
            _utc_dt(2024, 6, 1, 12, 0, 1),
            _utc_dt(2024, 6, 1, 12, 0, 2),
        ]
    )
    transport._utc_now = lambda: next(timestamps)

    transport._handle_incoming_data(_measurement_payload('0001').strip())
    transport._handle_incoming_data('X' * 1600)
    transport._handle_incoming_data('Y' * 1600)

    day_dir = tmp_path / '20240601'
    raw_files = list(day_dir.glob('*.raw'))
    error_files = list(day_dir.glob('*.error'))

    assert len(raw_files) == 1
    assert len(error_files) == 2
    assert transport._get_reply() == 'X' * 1600
    assert transport._get_reply() == 'Y' * 1600
