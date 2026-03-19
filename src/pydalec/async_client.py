"""Asynchronous client for communicating with a DALEC instrument."""

import asyncio

from .transport.async_tcp import AsyncTCPTransport


class AsyncDALEC:
    """Client API for asynchronous DALEC commands."""

    def __init__(self, transport):
        """Initialize the async client with a transport implementation."""
        self.transport = transport
        self._lock = asyncio.Lock()

    @classmethod
    async def connect_tcp(cls, host='127.0.0.1', port=9999):
        """Create a client connected to a DALEC TCP endpoint."""
        transport = await AsyncTCPTransport.connect(host, port)
        return cls(transport)

    async def get_temperature(self) -> float:
        """Read and return the current instrument temperature."""
        async with self._lock:
            await self.transport.send('READ:TEMP?')
            resp = await self.transport.receive()
            return float(resp)

    async def close(self):
        """Close the underlying transport."""
        await self.transport.close()
