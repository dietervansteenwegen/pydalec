"""Unit tests for `pydalec.measurement`."""

import datetime
import math

import pytest
from pydantic import ValidationError

from pydalec.measurement import Coordinates, Measurement, Telemetry, _has_max_decimals

UTC = datetime.timezone.utc

# ---------------------------------------------------------------------------
# _has_max_decimals
# ---------------------------------------------------------------------------


class TestHasMaxDecimals:
    def test_integer_value_zero_decimals(self):
        assert _has_max_decimals(1.0, 0) is True

    def test_one_decimal_fails_zero_decimals(self):
        assert _has_max_decimals(1.1, 0) is False

    def test_one_decimal_passes_one_decimal(self):
        assert _has_max_decimals(1.1, 1) is True

    def test_two_decimals_fails_one_decimal(self):
        assert _has_max_decimals(1.12, 1) is False

    def test_three_decimals_passes_three_decimals(self):
        assert _has_max_decimals(1.123, 3) is True

    def test_four_decimals_fails_three_decimals(self):
        assert _has_max_decimals(1.1234, 3) is False

    def test_zero_value(self):
        assert _has_max_decimals(0.0, 0) is True

    def test_negative_value(self):
        assert _has_max_decimals(-1.1, 1) is True

    def test_negative_value_fails(self):
        assert _has_max_decimals(-1.12, 1) is False

    def test_nan_value_passes(self):
        assert _has_max_decimals(float('nan'), 3) is True


# ---------------------------------------------------------------------------
# Coordinates
# ---------------------------------------------------------------------------


class TestCoordinates:
    def test_valid_coordinates(self):
        c = Coordinates(lat=51.5, lon=4.3)
        assert c.lat == 51.5
        assert c.lon == 4.3

    def test_lat_too_low(self):
        with pytest.raises(ValidationError):
            Coordinates(lat=-90.1, lon=0.0)

    def test_lat_too_high(self):
        with pytest.raises(ValidationError):
            Coordinates(lat=90.1, lon=0.0)

    def test_lon_too_low(self):
        with pytest.raises(ValidationError):
            Coordinates(lat=0.0, lon=-180.1)

    def test_lon_too_high(self):
        with pytest.raises(ValidationError):
            Coordinates(lat=0.0, lon=180.1)

    def test_nan_coordinates_allowed(self):
        c = Coordinates(lat=float('nan'), lon=float('nan'))

        assert math.isnan(c.lat)
        assert math.isnan(c.lon)

    def test_extra_field_forbidden(self):
        with pytest.raises(ValidationError):
            Coordinates(lat=0.0, lon=0.0, altitude=100.0)  # ty:ignore[unknown-argument]

    def test_str_north_east(self):
        c = Coordinates(lat=51.5074000, lon=0.1278000)
        result = str(c)
        assert 'N' in result
        assert 'E' in result

    def test_str_south_west(self):
        c = Coordinates(lat=-33.8688, lon=-70.6693)
        result = str(c)
        assert 'S' in result
        assert 'W' in result

    def test_str_format(self):
        c = Coordinates(lat=51.5074000, lon=0.1278000)
        result = str(c)
        parts = result.split(',')
        assert len(parts) == 2


# ---------------------------------------------------------------------------
# Telemetry
# ---------------------------------------------------------------------------


class TestTelemetry:
    def _valid_telemetry(self, **overrides):
        data = {
            'voltage_volts': 12.1,
            'humidity_mm_hg': 55.3,
            'temperature_diode_celsius': 23.456,
            'status_flag': 0,
        }
        data.update(overrides)
        return Telemetry(**data)

    def test_valid_telemetry(self):
        t = self._valid_telemetry()
        assert t.voltage_volts == 12.1

    def test_voltage_too_many_decimals(self):
        with pytest.raises(ValidationError, match='voltage_volts'):
            self._valid_telemetry(voltage_volts=12.12)

    def test_humidity_too_many_decimals(self):
        with pytest.raises(ValidationError, match='[Hh]umidity'):
            self._valid_telemetry(humidity_mm_hg=55.34)

    def test_temperature_too_many_decimals(self):
        with pytest.raises(ValidationError, match='temperature_diode_celsius'):
            self._valid_telemetry(temperature_diode_celsius=23.4567)

    def test_temperature_exactly_three_decimals(self):
        t = self._valid_telemetry(temperature_diode_celsius=23.456)
        assert t.temperature_diode_celsius == 23.456

    def test_nan_telemetry_values_allowed(self):
        t = self._valid_telemetry(
            voltage_volts=float('nan'),
            humidity_mm_hg=float('nan'),
            temperature_diode_celsius=float('nan'),
        )

        assert math.isnan(t.voltage_volts)
        assert math.isnan(t.humidity_mm_hg)
        assert math.isnan(t.temperature_diode_celsius)

    def test_status_flag_zero(self):
        t = self._valid_telemetry(status_flag=0)
        assert t.status_flag == 0

    def test_status_flag_one(self):
        t = self._valid_telemetry(status_flag=1)
        assert t.status_flag == 1

    def test_invalid_status_flag(self):
        with pytest.raises(ValidationError):
            self._valid_telemetry(status_flag=-1)

    def test_extra_field_forbidden(self):
        with pytest.raises(ValidationError):
            self._valid_telemetry(extra_field='bad')

    def test_str_format(self):
        t = self._valid_telemetry()
        result = str(t)
        assert result.startswith('Voltage:')
        assert 'Humidity:' in result
        assert 'Temperature:' in result
        assert 'Status flag:' in result

    def test_str_contains_values(self):
        t = self._valid_telemetry(
            voltage_volts=12.1, humidity_mm_hg=55.3, temperature_diode_celsius=23.456, status_flag=0
        )
        result = str(t)
        assert '12.1' in result
        assert '55.3' in result
        assert '23.456' in result
        assert 'flag:0' in result

    def test_status_flag_accepts_enum_directly(self):
        from pydalec.measurement import StatusFlag

        t = self._valid_telemetry(status_flag=StatusFlag.MOVING)
        assert t.status_flag == StatusFlag.MOVING


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------


def _valid_measurement(**overrides) -> dict:
    base = {
        'device_id': 'DALEC',
        'serial_number': '0010',
        'channel_type': 'Ed',
        'utc_time': datetime.datetime(2024, 6, 1, 12, 0, 0, tzinfo=UTC),
        'location': Coordinates(lat=51.5, lon=4.3),
        'sat_compass_heading': 180.0,
        'solar_azimuth_deg': 90.0,
        'solar_zenith_deg': 45.0,
        'gear_position_deg': 0.0,
        'azimuth_deg': 270.0,
        'relative_azimuth_deg': -90.0,
        'pitch_start_measurement_deg': 0.0,
        'roll_start_measurement_deg': 0.0,
        'telemetry': Telemetry(
            voltage_volts=12.1,
            humidity_mm_hg=55.3,
            temperature_diode_celsius=23.456,
            status_flag=0,
        ),
        'int_time': 100,
        'signal_percentage': 75.0,
        'dark_counts': 100,
        'max_counts': 60000,
        'spectrum': [1000] * 190,
    }
    base.update(overrides)
    return base


def _measurement_to_raw_data(**overrides) -> str:
    measurement = Measurement(**_valid_measurement(**overrides))
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
    return ','.join(fields)


class TestMeasurement:
    def test_valid_measurement(self):
        m = Measurement(**_valid_measurement())
        assert m.device_id == 'DALEC'

    def test_invalid_device_id(self):
        with pytest.raises(ValidationError):
            Measurement(**_valid_measurement(device_id='OTHER'))

    def test_serial_number_valid(self):
        m = Measurement(**_valid_measurement(serial_number='0001'))
        assert m.serial_number == '0001'

    def test_serial_number_too_short(self):
        with pytest.raises(ValidationError):
            Measurement(**_valid_measurement(serial_number='001'))

    def test_serial_number_too_long(self):
        with pytest.raises(ValidationError):
            Measurement(**_valid_measurement(serial_number='00001'))

    def test_serial_number_non_digits(self):
        with pytest.raises(ValidationError):
            Measurement(**_valid_measurement(serial_number='00AB'))

    def test_invalid_channel_type(self):
        with pytest.raises(ValidationError):
            Measurement(**_valid_measurement(channel_type='Invalid'))

    @pytest.mark.parametrize('channel_type', ['Ed', 'Lu', 'Lsky'])
    def test_valid_channel_types(self, channel_type: str):
        m = Measurement(**_valid_measurement(channel_type=channel_type))
        assert m.channel_type == channel_type

    def test_utc_time_naive_rejected(self):
        with pytest.raises(ValidationError, match='UTC'):
            Measurement(**_valid_measurement(utc_time=datetime.datetime(2024, 6, 1, 12, 0, 0)))  # noqa: DTZ001

    def test_utc_time_non_utc_rejected(self):
        tz_plus2 = datetime.timezone(datetime.timedelta(hours=2))
        with pytest.raises(ValidationError, match='UTC'):
            Measurement(
                **_valid_measurement(
                    utc_time=datetime.datetime(2024, 6, 1, 12, 0, 0, tzinfo=tz_plus2)
                )
            )

    def test_sat_compass_heading_out_of_range(self):
        with pytest.raises(ValidationError):
            Measurement(**_valid_measurement(sat_compass_heading=360.0))

    def test_int_time_below_minimum(self):
        with pytest.raises(ValidationError):
            Measurement(**_valid_measurement(int_time=0))

    def test_int_time_above_maximum(self):
        with pytest.raises(ValidationError):
            Measurement(**_valid_measurement(int_time=6001))

    def test_signal_percentage_out_of_range(self):
        with pytest.raises(ValidationError):
            Measurement(**_valid_measurement(signal_percentage=100.1))

    def test_nan_measurement_floats_allowed(self):
        measurement = Measurement(
            **_valid_measurement(
                sat_compass_heading=float('nan'),
                solar_azimuth_deg=float('nan'),
                solar_zenith_deg=float('nan'),
                gear_position_deg=float('nan'),
                azimuth_deg=float('nan'),
                relative_azimuth_deg=float('nan'),
                pitch_start_measurement_deg=float('nan'),
                roll_start_measurement_deg=float('nan'),
                signal_percentage=float('nan'),
            )
        )

        assert math.isnan(measurement.sat_compass_heading)
        assert math.isnan(measurement.signal_percentage)

    def test_dark_counts_out_of_range(self):
        with pytest.raises(ValidationError):
            Measurement(**_valid_measurement(dark_counts=65536))

    def test_max_counts_out_of_range(self):
        with pytest.raises(ValidationError):
            Measurement(**_valid_measurement(max_counts=65536))

    def test_spectrum_wrong_length(self):
        with pytest.raises(ValidationError):
            Measurement(**_valid_measurement(spectrum=[1000] * 189))

    def test_spectrum_value_out_of_range(self):
        spectrum = [1000] * 190
        spectrum[42] = 65536
        with pytest.raises(ValidationError, match='spectrum'):
            Measurement(**_valid_measurement(spectrum=spectrum))

    def test_spectrum_negative_value(self):
        spectrum = [1000] * 190
        spectrum[0] = -1
        with pytest.raises(ValidationError, match='spectrum'):
            Measurement(**_valid_measurement(spectrum=spectrum))

    def test_extra_field_forbidden(self):
        with pytest.raises(ValidationError):
            Measurement(**_valid_measurement(unknown_field='bad'))

    def test_from_raw_data(self):
        restored = Measurement.from_raw_data(_measurement_to_raw_data(serial_number='0010'))

        assert restored == Measurement(**_valid_measurement())

    def test_from_raw_data_zero_pads_serial_number(self):
        restored = Measurement.from_raw_data(_measurement_to_raw_data(serial_number='0011'))

        assert restored.serial_number == '0011'

    def test_from_raw_data_accepts_instrument_style_serial_field(self):
        raw_data = _measurement_to_raw_data(serial_number='0011').replace(',11,', ',11,', 1)

        restored = Measurement.from_raw_data(raw_data)

        assert restored.serial_number == '0011'

    def test_from_raw_data_accepts_nan_values(self):
        raw_data = _measurement_to_raw_data(serial_number='0011').replace(',180.0,', ',nan,', 1)

        restored = Measurement.from_raw_data(raw_data)

        assert math.isnan(restored.sat_compass_heading)

    def test_measurement_str_is_multiline_and_includes_core_fields(self):
        measurement = Measurement(**_valid_measurement(serial_number='0011'))

        rendered = str(measurement)

        assert "device_id='DALEC'," in rendered
        assert "serial_number='0011'," in rendered
        assert "channel_type='Ed'," in rendered
        assert 'utc_time=datetime.datetime(' in rendered
        assert 'location=Coordinates(' in rendered
        assert 'solar_azimuth_deg=90.0, solar_zenith_deg=45.0,' in rendered
        assert 'telemetry=Telemetry(' in rendered
        assert rendered.endswith('spectrum=[' + ', '.join(['1000'] * 190) + ']')
