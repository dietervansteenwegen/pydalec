"""In-memory synchronous mock transport for DALEC testing."""

from collections import deque

from pydalec.measurement import Measurement
from pydalec.transport.base import BaseTransport


class MockTransport(BaseTransport):
    """Mock synchronous transport that simulates DALEC responses."""

    def __init__(self, delay: float = 0.0, error_rate: float = 0.0):
        """Initialize mock behavior options for delay and error simulation."""
        self.delay = delay
        self.error_rate = error_rate
        self.measurement_log: deque[Measurement] = deque()
        self._making_measurements = False
        self._connected = True

    def start_measurements(self) -> None:
        """Start the background process for making and receiving measurements."""
        self._making_measurements = True

    def stop_measurements(self) -> None:
        """Stop the background process for making and receiving measurements."""
        self._making_measurements = False

    def send(self, data: str) -> None:
        """Store the latest command so a response can be generated."""
        self._last_cmd: str = data.strip()

    def disconnect(self) -> None:
        """Release mock transport resources."""
        self._connected = False

    def connect(self) -> None:
        """Reconnect the mock transport."""
        self._connected = True

    def __repr__(self) -> str:
        """Representation of Mock instance.

        Returns:
            str: formatted string showing the host and port of the Mock instance.
        """
        return self.__str__()

    def __str__(self) -> str:
        """String representation of Mock instance.

        Returns:
            str: formatted string showing the host and port of the Mock instance.
        """
        return f'MockTransport with delay={self.delay}s and error_rate={self.error_rate:.2%}'
