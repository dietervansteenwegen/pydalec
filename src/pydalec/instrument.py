"""Synchronous client for communicating with a DALEC instrument."""

from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import dataclass

from pydalec.errors import PyDalecNoPositionDataError
from pydalec.transport.mock import MockTransport
from pydalec.transport.tcp import TCPTransport


class DalecStatus:
    """Instrument status."""

    def __init__(self):
        """Initialize the status with default values."""
        self.measuring: bool = False


@dataclass(frozen=True)
class Location:
    """Simple latitude/longitude position fix."""

    lat: float
    lon: float

    def __str__(self) -> str:
        """Return string representation of the class.

        Returns:
            str: representation of the class, including lat and lon values.
        """
        lat: str = (
            f'{self.lat}\N{DEGREE SIGN}N' if self.lat >= 0 else f'{-self.lat}\N{DEGREE SIGN}S'
        )
        lon: str = (
            f'{self.lon}\N{DEGREE SIGN}E' if self.lon >= 0 else f'{-self.lon}\N{DEGREE SIGN}W'
        )
        return f'Location(lat={lat}, lon={lon})'


class Dalec:
    """Client API for synchronous DALEC commands."""

    def __init__(self, transport):
        """Initialize the client with a transport implementation."""
        self.transport = transport
        self.status = DalecStatus()

    @classmethod
    def connect_tcp(cls, host='127.0.0.1', port=23):
        """Create a client connected to a DALEC TCP endpoint."""
        return cls(transport=TCPTransport(host, port))

    @classmethod
    def connect_mock(cls, delay=0.0, error_rate=0.0):
        """Create a client using the in-memory mock transport."""
        return cls(MockTransport(delay, error_rate))

    def disconnect(self) -> None:
        """Close the transport connection."""
        self.transport.disconnect()

    @property
    def connected(self) -> bool:
        """Return True if the client is currently connected to the instrument."""
        return self.transport.connected

    def connect(self) -> None:
        """Reconnect to the instrument if currently disconnected."""
        if not self.connected:
            self.transport.connect()

    @property
    def measurement_log(self):
        """Return a list of recent measurements from the instrument."""
        return list(self.transport.measurement_log)

    def __repr__(self) -> str:
        """Representation of DALEC instance.

        Returns:
            str: formatted string showing the transport information of the DALEC instance.
        """
        return self.__str__()

    def __str__(self) -> str:
        """Return string representation of the class.

        Returns:
            str: representation of the class, including transport information.
        """
        return f'DALEC at {self.transport}'

    def start_measurements(self) -> None:
        """Start the background process for making and receiving measurements."""
        self.transport.start_measurements()
        self.status.measuring = True

    def stop_measurements(self) -> None:
        """Stop the background process for making and receiving measurements."""
        self.transport.stop_measurements()
        self.status.measuring = False

    @staticmethod
    def _has_valid_position_fix(measurement) -> bool:
        """Return True if measurement carries a non-NaN GNSS position."""
        location = getattr(measurement, 'location', None)
        if location is None:
            return False

        lat = getattr(location, 'lat', float('nan'))
        lon = getattr(location, 'lon', float('nan'))
        return not (math.isnan(lat) or math.isnan(lon))

    def get_location(self, timeout_secs: float = 10.0) -> Location:
        """Return the first valid GNSS position fix received within timeout."""
        if timeout_secs <= 0:
            err_msg = 'timeout must be greater than 0 seconds'
            raise ValueError(err_msg)

        was_measuring: bool = self.status.measuring
        saved_log = deque(
            self.transport.measurement_log, maxlen=self.transport.measurement_log.maxlen
        )
        last_seen_measurement = None

        if not was_measuring:
            self.start_measurements()

        deadline = time.monotonic() + timeout_secs
        try:
            while time.monotonic() < deadline:
                measurements = list(self.transport.measurement_log)

                if last_seen_measurement is None:
                    new_measurements = measurements
                else:
                    try:
                        last_index = measurements.index(last_seen_measurement)
                        new_measurements = measurements[last_index + 1 :]
                    except ValueError:
                        new_measurements = measurements

                for measurement in new_measurements:
                    if self._has_valid_position_fix(measurement):
                        return Location(lat=measurement.location.lat, lon=measurement.location.lon)
                    last_seen_measurement = measurement

                time.sleep(0.05)
        finally:
            if not was_measuring:
                try:
                    self.stop_measurements()
                finally:
                    self.transport.measurement_log = deque(saved_log, maxlen=saved_log.maxlen)

        err_msg = f'No valid GNSS position fix received within {timeout_secs:.1f}s'
        raise PyDalecNoPositionDataError(err_msg)
