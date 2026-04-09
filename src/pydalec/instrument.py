"""Synchronous client for communicating with a DALEC instrument."""

from pydalec.transport.mock import MockTransport
from pydalec.transport.tcp import TCPTransport


class DalecStatus:
    """Instrument status."""

    def __init__(self):
        """Initialize the status with default values."""
        self.measuring: bool = False
        self._connected: bool = True


class DALEC:
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
        self.status._connected = False

    @property
    def connected(self) -> bool:
        """Return True if the client is currently connected to the instrument."""
        return self.status._connected

    def connect(self) -> None:
        """Reconnect to the instrument if currently disconnected."""
        if not self.connected:
            self.transport.connect()
            self.status._connected = True

    @property
    def measurement_log(self):
        """Return a list of recent measurements from the instrument."""
        return list(self.transport.measurement_log)

    def ___repr__(self) -> str:
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
