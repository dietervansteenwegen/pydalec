"""Async TCP server that simulates a DALEC instrument."""

import asyncio

import telnetlib3

from .protocol import handle_command
from .state import InstrumentState


async def handle_client(reader, writer):
    """Handle one client connection and serve line-based commands."""
    instrument_state = InstrumentState()
    while True:
        data = await reader.readline()
        if not data:
            break
        cmd: str = data.strip()
        response: str = handle_command(state=instrument_state, cmd=cmd)
        writer.write(response + '\n')
        await writer.drain()
    writer.close()


async def run():
    """Start the mock server and serve indefinitely."""
    server = await telnetlib3.create_server(
        host='127.0.0.1',
        port=9999,
        shell=handle_client,
        connect_maxwait=0.0,
    )
    await server.wait_closed()


def main():
    """Run the async mock server entry point."""
    asyncio.run(run())
