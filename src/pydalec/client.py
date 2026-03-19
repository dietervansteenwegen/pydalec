"""Synchronous client for communicating with a DALEC instrument."""

from .transport.tcp import TCPTransport


class DALEC:
    """Client API for synchronous DALEC commands."""

    def __init__(self, transport):
        """Initialize the client with a transport implementation."""
        self.transport = transport

    @classmethod
    def connect_tcp(cls, host='127.0.0.1', port=9999):
        """Create a client connected to a DALEC TCP endpoint."""
        return cls(TCPTransport(host, port))

    def get_temperature(self) -> float:
        """Read and return the current instrument temperature."""
        self.transport.send('READ:TEMP?')
        return float(self.transport.receive())
