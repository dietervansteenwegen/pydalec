"""Async TCP server that simulates a DALEC instrument."""

import asyncio

from .protocol import handle_command
from .state import InstrumentState


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Handle one client connection and serve line-based commands."""
    instrument_state = InstrumentState()
    while True:
        data: bytes = await reader.readline()
        if not data:
            break
        cmd: str = data.decode().strip()
        response: str = handle_command(state=instrument_state, cmd=cmd)
        writer.write((response + '\n').encode())
        await writer.drain()
    writer.close()
    await writer.wait_closed()


async def run():
    """Start the mock server and serve indefinitely."""
    server = await asyncio.start_server(
        client_connected_cb=handle_client, host='127.0.0.1', port=9999
    )
    async with server:
        await server.serve_forever()


def main():
    """Run the async mock server entry point."""
    asyncio.run(run())
