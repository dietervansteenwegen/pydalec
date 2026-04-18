"""Unit tests for `pydalec.cli`."""

import datetime

from pydalec.cli import main
from pydalec.errors import DalecConnectionError
from pydalec.measurement import Coordinates, Measurement, StatusFlag, Telemetry

UTC = datetime.timezone.utc


def _make_measurement(serial_number: str = '0001') -> Measurement:
    return Measurement(
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


class _FakeClient:
    def __init__(self, measurement):
        self._measurement = measurement
        self.started = False
        self.stopped = False
        self.disconnected = False

    @property
    def measurement_log(self):
        if self.started and not self.stopped:
            return [self._measurement]
        return []

    def start_measurements(self):
        self.started = True

    def stop_measurements(self):
        self.stopped = True

    def disconnect(self):
        self.disconnected = True


def test_cli_connects_starts_streams_and_stops(monkeypatch, capsys):
    measurement = _make_measurement()
    fake_client = _FakeClient(measurement)
    recorded = {}

    def fake_connect_tcp(ip, port):
        recorded['ip'] = ip
        recorded['port'] = port
        return fake_client

    def fake_sleep(_seconds):
        raise KeyboardInterrupt

    monkeypatch.setattr('pydalec.cli.Dalec.connect_tcp', fake_connect_tcp)
    monkeypatch.setattr('pydalec.cli.time.sleep', fake_sleep)

    exit_code = main(['10.0.0.5', '--port', '9999'])

    stdout = capsys.readouterr().out

    assert exit_code == 0
    assert recorded == {'ip': '10.0.0.5', 'port': 9999}
    assert 'Connected to DALEC at 10.0.0.5:9999' in stdout
    assert 'Started measurements. Press Ctrl+C to stop.' in stdout
    assert str(measurement) in stdout
    assert 'Stopping measurement stream...' in stdout
    assert 'Disconnected.' in stdout
    assert fake_client.started is True
    assert fake_client.stopped is True
    assert fake_client.disconnected is True


def test_cli_returns_non_zero_on_connection_error(monkeypatch, capsys):
    def fake_connect_tcp(_ip, _port):
        raise DalecConnectionError

    monkeypatch.setattr('pydalec.cli.Dalec.connect_tcp', fake_connect_tcp)

    exit_code = main(['192.168.0.100'])

    stderr = capsys.readouterr().err

    assert exit_code == 1
    assert 'Connection failed:' in stderr
