"""End-to-end tests for `pydalec.client`."""

import asyncio
import queue
import sys
import threading
from pathlib import Path

import pytest
import telnetlib3

from pydalec.client import DALEC

MOCK_SRC = Path(__file__).resolve().parents[1] / 'pydalec_mock' / 'src'
if str(MOCK_SRC) not in sys.path:
    sys.path.insert(0, str(MOCK_SRC))

from pydalec_mock.async_server import handle_client  # noqa: E402


@pytest.fixture
def mock_telnet_server():
    """Start the telnet mock server in a background thread and yield its port."""
    started: queue.Queue[tuple[asyncio.AbstractEventLoop, asyncio.Event, int]] = queue.Queue()

    def run_server() -> None:
        async def server_main() -> None:
            stop_event = asyncio.Event()
            server = await telnetlib3.create_server(
                host='127.0.0.1',
                port=0,
                shell=handle_client,
                connect_maxwait=0.0,
            )
            port = server.sockets[0].getsockname()[1]
            started.put((asyncio.get_running_loop(), stop_event, port))
            await stop_event.wait()
            server.close()
            await server.wait_closed()

        asyncio.run(server_main())

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    loop, stop_event, port = started.get(timeout=5)

    try:
        yield port
    finally:
        loop.call_soon_threadsafe(stop_event.set)
        thread.join(timeout=5)
        assert thread.is_alive() is False


def test_dalec_connect_tcp_end_to_end_with_mock_server(mock_telnet_server):
    """Verify the client can talk to the telnet mock server end to end."""
    client = DALEC.connect_tcp('127.0.0.1', mock_telnet_server)

    try:
        assert client.get_temperature() == 25.0
    finally:
        client.transport.close()
