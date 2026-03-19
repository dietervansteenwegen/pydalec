"""Asynchronous TCP transport used by the DALEC async client."""

import asyncio


class AsyncTCPTransport:
    """Asyncio TCP transport for newline-delimited DALEC commands."""

    def __init__(self, reader, writer):
        """Initialize the transport with an asyncio reader/writer pair."""
        self.reader = reader
        self.writer = writer

    @classmethod
    async def connect(cls, host: str, port: int):
        """Open a TCP connection and return a configured transport."""
        reader, writer = await asyncio.open_connection(host, port)
        return cls(reader, writer)

    async def send(self, data: str):
        """Send a single command line to the remote endpoint."""
        self.writer.write((data + '\n').encode())
        await self.writer.drain()

    async def receive(self) -> str:
        """Read and return one response line from the remote endpoint."""
        data = await self.reader.readline()
        return data.decode().strip()

    async def close(self):
        """Close the TCP connection cleanly."""
        self.writer.close()
        await self.writer.wait_closed()
