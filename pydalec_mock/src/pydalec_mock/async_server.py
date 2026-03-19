"""Async TCP server that simulates a DALEC instrument."""

import asyncio

from .protocol import handle_command
from .state import InstrumentState


async def handle_client(reader, writer):
    """Handle one client connection and serve line-based commands."""
    state = InstrumentState()
    while True:
        data = await reader.readline()
        if not data:
            break
        cmd = data.decode().strip()
        response = handle_command(state, cmd)
        writer.write((response + '\n').encode())
        await writer.drain()
    writer.close()
    await writer.wait_closed()


async def run():
    """Start the mock server and serve indefinitely."""
    server = await asyncio.start_server(handle_client, '127.0.0.1', 9999)
    async with server:
        await server.serve_forever()


def main():
    """Run the async mock server entry point."""
    asyncio.run(run())
