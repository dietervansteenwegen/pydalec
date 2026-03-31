"""Class for measurement data for the pydalec mock instrument."""

from __future__ import annotations

import datetime
import enum
from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _has_max_decimals(value: float, decimals: int) -> bool:
    """Check if a float value has at most a specified number of decimal places."""
    decimal_value = Decimal(str(value))
    quantized_value: Decimal = decimal_value.quantize(Decimal(1).scaleb(-decimals))
    return decimal_value == quantized_value


class StatusFlag(enum.IntEnum):
    """Status indicator used in telemetry data.

    0 means stationary during integration, 1 means moving during integration.
    """

    STATIONARY = 0
    MOVING = 1


class Coordinates(BaseModel):
    """Position (lat/lon) in decimal degrees."""

    model_config = ConfigDict(extra='forbid')

    lat: float = Field(ge=-90.0, le=90.0)
    lon: float = Field(ge=-180.0, le=180.0)

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
    status_flag: StatusFlag  # 0 = stationary, 1 = moving during integration

    @field_validator('voltage_volts')
    @classmethod
    def _validate_voltage_precision(cls, value: float) -> float:
        if not _has_max_decimals(value, 1):
            err_msg: str = f'voltage_volts must have at most 1 decimal place (value: {value})'
            raise ValueError(err_msg)
        return value

    @field_validator('humidity_mm_hg')
    @classmethod
    def _validate_humidity_precision(cls, value: float) -> float:
        if not _has_max_decimals(value, 1):
            err_msg: str = f'Humidity_mm_hg must have at most 1 decimal place (value: {value})'
            raise ValueError(err_msg)
        return value

    @field_validator('temperature_diode_celsius')
    @classmethod
    def _validate_temp_precision(cls, value: float) -> float:
        if not _has_max_decimals(value, decimals=3):
            err_msg: str = 'temperature_diode_celsius must have at most 3 decimal '
            f'places (value: {value})'
            raise ValueError(err_msg)
        return value

    def __str__(self) -> str:
        """String representation of the telemetry data.

        Returns a string in the format:
        "Voltage:XXXX.X;Humidity:XX.X;Temperature:XX.XXX;Status flag:X"
        """
        return (
            f'Voltage:{self.voltage_volts:04.1f};Humidity:{self.humidity_mm_hg:04.1f};Temperature:'
            f'{self.temperature_diode_celsius:06.3f};Status flag:{self.status_flag.name}'
        )


class Measurement(BaseModel):
    """Container for measurement data from the mock instrument."""

    model_config = ConfigDict(extra='forbid')

    device_id: Literal['DALEC']
    serial_number: str = Field(pattern=r'^\d{4}$')  # four digits, e.g. '0010'
    channel_type: Literal['Ed', 'Lu', 'Lsky']
    utc_time: datetime.datetime
    location: Coordinates
    sat_compass_heading: float = Field(ge=0.0, le=359.9)
    solar_azimuth_deg: float = Field(ge=0.0, le=359.9)
    solar_zenith_deg: float = Field(ge=0.0, le=359.9)
    gear_position_deg: float = Field(ge=-179.9, le=180.0)
    azimuth_deg: float = Field(ge=0.0, le=359.9)
    relative_azimuth_deg: float = Field(ge=-179.9, le=180.0)
    pitch_start_measurement_deg: float = Field(ge=-90.0, le=90.0)
    roll_start_measurement_deg: float = Field(ge=-179.9, le=180.0)
    telemetry: Telemetry
    int_time: int = Field(ge=1, le=6000)
    signal_percentage: float = Field(ge=0.0, le=100.0)
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
        if v.tzinfo is None or v.utcoffset() != datetime.timedelta(0):
            err_msg = 'utc_time must be timezone-aware UTC'
            raise ValueError(err_msg)
        return v

    @field_validator('spectrum')
    @classmethod
    def _validate_spectrum_values(cls, value: list[int]) -> list[int]:
        if any((x < 0 or x > 65535) for x in value):
            err_msg = 'All spectrum values must be in range 0..65535'
            raise ValueError(err_msg)
        return value

    @classmethod
    def from_raw_data(cls, raw_data: str) -> Self:
        """Factory method from string to Measurement model."""
        return cls.model_validate_json(raw_data)
