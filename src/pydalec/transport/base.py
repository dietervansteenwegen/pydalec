"""Abstract transport interface used by DALEC clients."""

from abc import ABC, abstractmethod
from collections import deque

from pydalec.measurement import Measurement


class BaseTransport(ABC):
    """Abstract interface for synchronous DALEC transports."""

    measurement_log: deque[Measurement]
    _connected: bool

    @abstractmethod
    def send(self, data: str) -> None:
        """Send a command string to the transport backend."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Release any transport resources held by the backend."""
        pass

    @abstractmethod
    def start_measurements(self) -> None:
        """Start the background process for making and receiving measurements."""
        pass

    @abstractmethod
    def stop_measurements(self) -> None:
        """Stop the background process for making and receiving measurements."""
        pass
