"""Abstract transport interface used by DALEC clients."""

from abc import ABC, abstractmethod
from collections import deque

from pydalec.measurement import Measurement


class BaseTransport(ABC):
    """Abstract interface for synchronous DALEC transports."""

    measurement_log: deque[Measurement]
    _connected: bool

    def __init__(self) -> None:
        """Initialize shared transport state."""
        self.measurement_log = deque(maxlen=40)

    def set_measurement_log_size(self, size: int) -> None:
        """Resize measurement log while preserving the newest possible records."""
        if size < 1:
            err_msg = 'size must be at least 1'
            raise ValueError(err_msg)
        self.measurement_log = deque(self.measurement_log, maxlen=size)

    @property
    def connected(self) -> bool:
        """Return True if the transport is currently connected.

        This is the single source of truth for connection state.
        """
        return self._connected

    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the transport backend."""
        pass

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
