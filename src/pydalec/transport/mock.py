"""In-memory synchronous mock transport for DALEC testing."""

import random
import time
from typing import Union

from pydalec.transport.base import BaseTransport


class MockTransport(BaseTransport):
    """Mock synchronous transport that simulates DALEC responses."""

    def __init__(self, delay: float = 0.0, error_rate: float = 0.0):
        """Initialize mock behavior options for delay and error simulation."""
        self.delay = delay
        self.error_rate = error_rate
        self._last_cmd: Union[str | None] = None
        self.measurement_log: list[str] = []
        self._state = None

    def send(self, data: str) -> None:
        """Store the latest command so a response can be generated."""
        self._last_cmd: str = data.strip()

    def receive(self) -> str:
        """Return a simulated response for the last received command."""
        if self.delay:
            time.sleep(self.delay)

        if random.random() < self.error_rate:  # noqa: S311 # This isn´t cryptography
            return 'ERROR'

        return 'ERROR'

    def close(self) -> None:
        """Release mock transport resources."""
        return None
