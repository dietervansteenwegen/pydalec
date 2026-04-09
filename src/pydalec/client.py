"""Synchronous client for communicating with a DALEC instrument."""

from pydalec.transport.mock import MockTransport
from pydalec.transport.tcp import TCPTransport


class DALEC:
    """Client API for synchronous DALEC commands."""

    def __init__(self, transport):
        """Initialize the client with a transport implementation."""
        self.transport = transport

    @classmethod
    def connect_tcp(cls, host='127.0.0.1', port=23):
        """Create a client connected to a DALEC TCP endpoint."""
        return cls(TCPTransport(host, port))

    @classmethod
    def connect_mock(cls, delay=0.0, error_rate=0.0):
        """Create a client using the in-memory mock transport."""
        return cls(MockTransport(delay, error_rate))

    @property
    def measurment_log(self):
        """Return a list of recent measurements from the instrument."""
        return list(self.transport.measurement_log)

    def __str__(self) -> str:
        """Return string representation of the class.

        Returns:
            str: representation of the class, including transport information.
        """
        return f'DALEC at {self.transport}'

    def get_temperature(self) -> float:
        """Read and return the current instrument temperature."""
        self.transport.send('READ:TEMP?')
        return float(self.transport.receive())
