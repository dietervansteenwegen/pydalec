"""Class for measurement data for the pydalec mock instrument."""

from __future__ import annotations

import datetime
import enum
import math
from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

RAW_DATA_FIXED_FIELD_COUNT = 22
SPECTRUM_LENGTH = 190
RAW_DATA_FIELD_COUNT: Literal[212] = RAW_DATA_FIXED_FIELD_COUNT + SPECTRUM_LENGTH


def _has_max_decimals(value: float, decimals: int) -> bool:
    """Check if a float value has at most a specified number of decimal places."""
    if math.isnan(value):
        return True
    decimal_value = Decimal(value=str(object=value))
    quantized_value: Decimal = decimal_value.quantize(exp=Decimal(value=1).scaleb(other=-decimals))
    return decimal_value == quantized_value


def _parse_utc_timestamp(value: str) -> datetime.datetime:
    """Parse a UTC timestamp emitted by the instrument."""
    return datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))


def _normalize_serial_number(value: str) -> str:
    """Normalize instrument serial numbers to the model's four-digit format."""
    return value.zfill(4) if value.isdigit() and len(value) < 4 else value


def _validate_range_or_nan(value: float, minimum: float, maximum: float, field_name: str) -> float:
    """Accept NaN for unavailable readings; otherwise enforce the numeric range."""
    if math.isnan(value):
        return value
    if value < minimum or value > maximum:
        err_msg = f'{field_name} must be in range {minimum}..{maximum}'
        raise ValueError(err_msg)
    return value


class StatusFlag(enum.IntEnum):
    """Status indicator used in telemetry data.

    0 means stationary during integration, 1 means moving during integration.
    """

    STATIONARY = 0
    MOVING = 1


class GearCalibrationStatus(enum.IntEnum):
    """Gear calibration state encoded in status flag bits 7..5."""

    CALIBRATION_OK = 0
    MOVE_LEFT = 1
    MOVE_RIGHT = 2
    MOVE_CENTRE = 3
    MANUAL_ENDSTOPS = 4
    MOVE_RIGHT_MAGNET_NOT_YET_DETECTED = 5
    RESERVED = 6
    NOT_CALIBRATED = 7


class Coordinates(BaseModel):
    """Position (lat/lon) in decimal degrees."""

    model_config = ConfigDict(extra='forbid')

    lat: float
    lon: float

    @field_validator('lat')
    @classmethod
    def _validate_lat(cls, value: float) -> float:
        """Validate latitude range.

        Args:
            value: Latitude in decimal degrees.

        Returns:
            The validated latitude value.
        """
        return _validate_range_or_nan(value, minimum=-90.0, maximum=90.0, field_name='lat')

    @field_validator('lon')
    @classmethod
    def _validate_lon(cls, value: float) -> float:
        """Validate longitude range.

        Args:
            value: Longitude in decimal degrees.

        Returns:
            The validated longitude value.
        """
        return _validate_range_or_nan(value, minimum=-180.0, maximum=180.0, field_name='lon')

    def __str__(self) -> str:
        """String representation in the format 'lat,lon' with N/S and E/W."""
        latitude: str = f'{abs(self.lat):010.7f}N' if self.lat >= 0 else f'{abs(self.lat):010.7f}S'
        longitude: str = f'{abs(self.lon):010.7f}E' if self.lon >= 0 else f'{abs(self.lon):010.7f}W'
        return f'{latitude},{longitude}'


class Telemetry(BaseModel):
    """Container for telemetry data part of the measurement data.

    Attributes:
        voltage_volts (float): Voltage reading in volts.
        humidity_mm_hg (float): Humidity reading in mmHg.
        temperature_diode_celsius (float): Temperature reading from diode in degrees Celsius.
        status_flag (StatusFlag): Status indicator where 0 = stationary and 1 = moving
            during integration.

    Validation:
        - voltage_volts: Must have at most 1 decimal place
        - humidity_mm_hg: Must have at most 1 decimal place
        - temperature_diode_celsius: Must have at most 3 decimal places
        - Extra fields are forbidden (model_config sets extra='forbid')

    String Representation:
        Returns a formatted string with all telemetry values in the format:
        "Voltage:XXXX.X;Humidity:XX.X;Temperature:XX.XXX;Status flag:[STATIONARY|MOVING]"
    """

    model_config = ConfigDict(extra='forbid')

    voltage_volts: float
    humidity_mm_hg: float
    temperature_diode_celsius: float
    status_flag: int = Field(ge=0, le=255)  # 8-bit quality flag from instrument Qflag field

    @field_validator('voltage_volts')
    @classmethod
    def _validate_voltage_precision(cls, value: float) -> float:
        """Validate voltage precision.

        Args:
            value: Voltage in volts.

        Returns:
            The validated voltage value.
        """
        if not _has_max_decimals(value, decimals=1):
            err_msg: str = f'voltage_volts must have at most 1 decimal place (value: {value})'
            raise ValueError(err_msg)
        return value

    @field_validator('humidity_mm_hg')
    @classmethod
    def _validate_humidity_precision(cls, value: float) -> float:
        """Validate humidity precision.

        Args:
            value: Humidity in mmHg.

        Returns:
            The validated humidity value.
        """
        if not _has_max_decimals(value, decimals=1):
            err_msg: str = f'Humidity_mm_hg must have at most 1 decimal place (value: {value})'
            raise ValueError(err_msg)
        return value

    @field_validator('temperature_diode_celsius')
    @classmethod
    def _validate_temp_precision(cls, value: float) -> float:
        """Validate temperature precision.

        Args:
            value: Diode temperature in Celsius.

        Returns:
            The validated temperature value.
        """
        if not _has_max_decimals(value, decimals=3):
            err_msg: str = (
                f'temperature_diode_celsius must have at most 3 decimal places (value: {value})'
            )
            raise ValueError(err_msg)
        return value

    def __str__(self) -> str:
        """String representation of the telemetry data.

        Returns a string in the format:
        "Voltage:XXXX.X;Humidity:XX.X;Temperature:XX.XXX;Status flag:X"
        """
        return (
            f'Voltage:{self.voltage_volts:04.1f};Humidity:{self.humidity_mm_hg:04.1f};Temperature:'
            f'{self.temperature_diode_celsius:06.3f};Status flag:{self.status_flag}'
        )

    @property
    def servo_moved_during_integration(self) -> bool:
        """Bit 0: DALEC moved during last integration."""
        return bool(self.status_flag & (1 << 0))

    @property
    def n2k_epoch_valid(self) -> bool:
        """Bit 1: True when GPS epoch age is within 1500 ms."""
        return not bool(self.status_flag & (1 << 1))

    @property
    def n2k_heading_valid(self) -> bool:
        """Bit 2: True when GPS heading age is within 1000 ms."""
        return not bool(self.status_flag & (1 << 2))

    @property
    def n2k_gps_valid(self) -> bool:
        """Bit 3: True when GPS lat/lon age is within 1000 ms."""
        return not bool(self.status_flag & (1 << 3))

    @property
    def require_configuration(self) -> bool:
        """Bit 4: Compass controller requires configuration."""
        return bool(self.status_flag & (1 << 4))

    @property
    def gear_calibration_status(self) -> GearCalibrationStatus:
        """Bits 7..5: gear calibration state."""
        return GearCalibrationStatus((self.status_flag >> 5) & 0b111)

    @property
    def status_bits_normal(self) -> bool:
        """True when all status bits are clear."""
        return self.status_flag == 0


class Measurement(BaseModel):
    """Container for measurement data from the mock instrument."""

    model_config = ConfigDict(extra='forbid')

    device_id: Literal['DALEC']
    serial_number: str = Field(pattern=r'^\d{4}$')  # four digits, e.g. '0010'
    channel_type: Literal['Ed', 'Lu', 'Lsky']
    utc_time: datetime.datetime
    location: Coordinates
    sat_compass_heading: float
    solar_azimuth_deg: float
    solar_zenith_deg: float
    gear_position_deg: float
    azimuth_deg: float
    relative_azimuth_deg: float
    pitch_start_measurement_deg: float
    roll_start_measurement_deg: float
    telemetry: Telemetry
    int_time: int = Field(ge=1, le=6000)
    signal_percentage: float
    dark_counts: int = Field(ge=0, le=65535)
    max_counts: int = Field(ge=0, le=65535)
    spectrum: list[int] = Field(
        min_length=190,
        max_length=190,
        description='List of 190 integer values representing the spectrum, each in range 0..65535',
    )  # Validation in _validate_spectrum_values

    @field_validator('utc_time')
    @classmethod
    def _validate_utc_time(cls, v: datetime.datetime) -> datetime.datetime:
        """Validate UTC timestamp semantics.

        Args:
            v: Timestamp to validate.

        Returns:
            The validated UTC timestamp.
        """
        if v.tzinfo is None or v.utcoffset() != datetime.timedelta(days=0):
            err_msg = 'utc_time must be timezone-aware UTC'
            raise ValueError(err_msg)
        return v

    @field_validator('spectrum')
    @classmethod
    def _validate_spectrum_values(cls, value: list[int]) -> list[int]:
        """Validate spectral sample range.

        Args:
            value: Spectrum values from the instrument.

        Returns:
            The validated spectrum values.
        """
        if any((x < 0 or x > 65535) for x in value):
            err_msg = 'All spectrum values must be in range 0..65535'
            raise ValueError(err_msg)
        return value

    @field_validator(
        'sat_compass_heading',
        'solar_azimuth_deg',
        'solar_zenith_deg',
        'azimuth_deg',
    )
    @classmethod
    def _validate_bearing_fields(cls, value: float, info: ValidationInfo) -> float:
        """Validate 0..359.9 degree bearing fields.

        Args:
            value: Field value to validate.
            info: Pydantic validation metadata for current field.

        Returns:
            The validated bearing value.
        """
        return _validate_range_or_nan(value, minimum=0.0, maximum=359.9, field_name=info.field_name)

    @field_validator('gear_position_deg', 'relative_azimuth_deg', 'roll_start_measurement_deg')
    @classmethod
    def _validate_signed_heading_fields(cls, value: float, info: ValidationInfo) -> float:
        """Validate signed heading fields.

        Args:
            value: Field value to validate.
            info: Pydantic validation metadata for current field.

        Returns:
            The validated signed heading value.
        """
        return _validate_range_or_nan(
            value, minimum=-179.9, maximum=180.0, field_name=info.field_name
        )

    @field_validator('pitch_start_measurement_deg')
    @classmethod
    def _validate_pitch_field(cls, value: float) -> float:
        """Validate pitch range.

        Args:
            value: Pitch value in degrees.

        Returns:
            The validated pitch value.
        """
        return _validate_range_or_nan(
            value, minimum=-90.0, maximum=90.0, field_name='pitch_start_measurement_deg'
        )

    @field_validator('signal_percentage')
    @classmethod
    def _validate_signal_percentage(cls, value: float) -> float:
        """Validate signal percentage range.

        Args:
            value: Signal percentage value.

        Returns:
            The validated signal percentage.
        """
        return _validate_range_or_nan(
            value, minimum=0.0, maximum=100.0, field_name='signal_percentage'
        )

    def __str__(self) -> str:
        """Human-readable multiline string representation of a measurement."""
        spectrum_values = ', '.join(str(value) for value in self.spectrum)
        return (
            f'device_id={self.device_id!r},\n'
            f'serial_number={self.serial_number!r},\n'
            f'channel_type={self.channel_type!r},\n'
            f'utc_time={self.utc_time!r},\n'
            f'location={self.location!r},\n'
            f'sat_compass_heading={self.sat_compass_heading},\n'
            f'solar_azimuth_deg={self.solar_azimuth_deg}, '
            f'solar_zenith_deg={self.solar_zenith_deg},\n'
            f'gear_position_deg={self.gear_position_deg},\n'
            f'azimuth_deg={self.azimuth_deg}, relative_azimuth_deg={self.relative_azimuth_deg},\n'
            'pitch_start_measurement_deg='
            f'{self.pitch_start_measurement_deg}, '
            f'roll_start_measurement_deg={self.roll_start_measurement_deg},\n'
            'telemetry=Telemetry(\n'
            f'\tvoltage_volts={self.telemetry.voltage_volts},\n'
            f'\thumidity_mm_hg={self.telemetry.humidity_mm_hg},\n'
            f'\ttemperature_diode_celsius={self.telemetry.temperature_diode_celsius},\n'
            f'\tstatus_flag={self.telemetry.status_flag},\n'
            '),\n'
            f'int_time={self.int_time},\n'
            f'signal_percentage={self.signal_percentage},\n'
            f'dark_counts={self.dark_counts},\n'
            f'max_counts={self.max_counts},\n'
            f'spectrum=[{spectrum_values}]'
        )

    @property
    def has_valid_position_fix(self) -> bool:
        """Return True if location has non-NaN latitude and longitude.

        This property checks whether the GNSS position fix is available.
        A valid fix requires both lat and lon to be non-NaN values.
        """
        lat = getattr(self.location, 'lat', float('nan'))
        lon = getattr(self.location, 'lon', float('nan'))
        return not (math.isnan(lat) or math.isnan(lon))

    @property
    def has_valid_solar_zenith(self) -> bool:
        """Return True if solar_zenith_deg is non-NaN.

        This property checks whether the solar zenith angle measurement
        is available.
        """
        return not math.isnan(self.solar_zenith_deg)

    @property
    def servo_moved_during_integration(self) -> bool:
        """Pass-through for telemetry status flag bit 0."""
        return self.telemetry.servo_moved_during_integration

    @property
    def n2k_epoch_valid(self) -> bool:
        """Pass-through for telemetry status flag bit 1 validity."""
        return self.telemetry.n2k_epoch_valid

    @property
    def n2k_heading_valid(self) -> bool:
        """Pass-through for telemetry status flag bit 2 validity."""
        return self.telemetry.n2k_heading_valid

    @property
    def n2k_gnss_valid(self) -> bool:
        """Pass-through for telemetry status flag bit 3 GNSS validity."""
        return self.telemetry.n2k_gps_valid

    @property
    def n2k_gnss_require_configuration(self) -> bool:
        """Pass-through for telemetry status flag bit 4."""
        return self.telemetry.require_configuration

    @property
    def gear_calibration_status(self) -> GearCalibrationStatus:
        """Pass-through for telemetry status flag bits 7..5."""
        return self.telemetry.gear_calibration_status

    @classmethod
    def from_raw_data(cls, raw_data: str) -> Self:
        """Factory method from string to Measurement model."""
        fields = [field.strip() for field in raw_data.strip().split(sep=',')]
        if len(fields) != RAW_DATA_FIELD_COUNT:
            err_msg = f'raw_data must contain {RAW_DATA_FIELD_COUNT} comma-separated fields'
            raise ValueError(err_msg)

        payload = {
            'device_id': fields[0],
            'serial_number': _normalize_serial_number(fields[1]),
            'channel_type': fields[2],
            'utc_time': _parse_utc_timestamp(fields[3]),
            'location': {
                'lat': float(fields[4]),
                'lon': float(fields[5]),
            },
            'sat_compass_heading': float(fields[6]),
            'solar_azimuth_deg': float(fields[7]),
            'solar_zenith_deg': float(fields[8]),
            'gear_position_deg': float(fields[9]),
            'azimuth_deg': float(fields[10]),
            'relative_azimuth_deg': float(fields[11]),
            'pitch_start_measurement_deg': float(fields[12]),
            'roll_start_measurement_deg': float(fields[13]),
            'telemetry': {
                'voltage_volts': float(fields[14]),
                'humidity_mm_hg': float(fields[15]),
                'temperature_diode_celsius': float(fields[16]),
                'status_flag': int(fields[17], 2),
            },
            'int_time': int(fields[18]),
            'signal_percentage': float(fields[19]),
            'dark_counts': int(fields[20]),
            'max_counts': int(fields[21]),
            'spectrum': [int(value) for value in fields[RAW_DATA_FIXED_FIELD_COUNT:]],
        }
        return cls.model_validate(obj=payload)
