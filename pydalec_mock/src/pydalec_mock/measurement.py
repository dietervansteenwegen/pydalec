"""Class for measurement data for the pydalec mock instrument."""

import datetime
from dataclasses import dataclass
from typing import Self


@dataclass
class Coordinates:
    """Position (lat/lon) in decimal degrees."""

    lat: float
    lon: float

    def __str__(self):
        """String represenation of the coordinates in the format 'lat,lon' with N/S and E/W."""
        latitude: str = f'{self.lat:02.7f}N' if self.lat >= 0 else f'{self.lat:02.7f}S'
        longitude: str = f'{self.lon:02.7f}E' if self.lon >= 0 else f'{self.lon:02.7f}W'
        return f'{latitude},{longitude}'


@dataclass
class Telemetry:
    """Container for telemetry data from the mock instrument."""

    voltage_volts: float  # voltage, one decimal point
    humidity_mm_hg: float  # humidity, one decimal point
    temperature_diode_celsius: float  # temperature, three decimal point
    status_flag: int  # 0 = motor stationary, 1 = moving during integration

    def __str__(self):
        """String representation of the telemetry data.

        Format: 'V:xx.x;H:xx.x;T:xx.xxx;S:x' where V is voltage, H is humidity (mmHg),
                    T is temperature and S is status flag.
        """
        # Todo: check values from instrument (e.g. range for humidity)
        return (
            f'Voltage:{self.voltage_volts:04.1f};Humidity:{self.humidity_mm_hg:02.1f};Temperature:'
            f'{self.temperature_diode_celsius:06.3f};Status flag:{self.status_flag:d}'
        )


@dataclass
class Measurement:
    """Container for measurement data from the mock instrument."""

    # todo: migrate to Pydantic model for validation
    device_id: str  # 'DALEC'
    serial_number: str  # '0010'
    channel_type: str  # 'Ed', 'Lu' or 'Lsky'
    utc_time: datetime.datetime
    location: Coordinates
    sat_compass_heading: float  # rel to North, 0.0 to 359.9
    solar_azimuth_deg: float  # 0.0 to 359.9
    solar_zenith_deg: float  # 0.0 to 359.9
    gear_position_deg: float  # -179,9 to 180,0
    azimuth_deg: float  # Compass heading + GearPos, 0.0 to 359.9
    relative_azimuth_deg: float  # rel. to the Solar Azimuth, -179.9 to 180.0
    pitch_start_measurement_deg: float  # angle at the start of integration time, -90.0 to 90.0
    roll_start_measurement_deg: float  # angle at the start of integration time, -179.9 to 180.0
    telemetry: Telemetry
    int_time: int  # integration time in ms, 1 to 6000
    signal_percentage: float  # peak count signal within the spectrometers dynamic range
    dark_counts: int  # avg counts of blackened NIR pixels, 0 - 65535
    max_counts: int  # Max counts of the spectrum
    spectrum: list[int]  # raw ADC counts, 190 values, each 0 - 65535

    @classmethod
    def from_raw_data(cls, raw_data: str) -> Self:
        """Factory method from string as received from instrument to Measurment dataclass."""
        # Todo: finish parsing from raw data to Measurement, including validation(?)
        return cls
