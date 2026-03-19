"""Synchronous TCP transport used by the DALEC client."""

import socket

from .base import BaseTransport


class TCPTransport(BaseTransport):
    """Socket-based synchronous transport for DALEC commands."""

    def __init__(self, host: str, port: int):
        """Connect to a DALEC endpoint over TCP."""
        self.sock = socket.create_connection((host, port))

    def send(self, data: str) -> None:
        """Send a single command line to the remote endpoint."""
        self.sock.sendall((data + '\n').encode())

    def receive(self) -> str:
        """Receive and decode a response from the remote endpoint."""
        return self.sock.recv(4096).decode().strip()
