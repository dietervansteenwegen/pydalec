"""Synchronous Telnet transport used by the DALEC client."""

import queue
import threading
from collections import deque

from pydantic import ValidationError
from telnetlib3.sync import TelnetConnection

from pydalec.measurement import Measurement
from pydalec.transport.base import BaseTransport


class TCPTransport(BaseTransport):
    """Telnet-based synchronous transport for DALEC commands."""

    def __init__(self, host: str, port: int = 23, measurement_log_size: int = 20):
        """Connect to a DALEC endpoint over Telnet."""
        if measurement_log_size < 1:
            err_msg = 'measurement_log_size must be at least 1'
            raise ValueError(err_msg)

        self._connection = TelnetConnection(host, port, connect_minwait=0.0, encoding='utf8')
        self._connection.connect()
        self.measurement_log: deque[Measurement] = deque(maxlen=measurement_log_size)
        self._measurement_log_lock = threading.Lock()
        self._responses: queue.Queue[str | None] = queue.Queue()
        self._closed = False
        self._reader_thread = threading.Thread(target=self._read_connection, daemon=True)
        self._reader_thread.start()
        self._host = host
        self._port = port

    def set_measurement_log_size(self, size: int) -> None:
        """Resize the measurement log while preserving existing records.

        When increasing the size, all current records are retained. When
        decreasing, the oldest records are discarded first.
        """
        if size < 1:
            err_msg = 'size must be at least 1'
            raise ValueError(err_msg)

        with self._measurement_log_lock:
            self.measurement_log = deque(self.measurement_log, maxlen=size)

    def send(self, data: str) -> None:
        """Send a single command line to the remote endpoint."""
        self._connection.write(data + '\n')
        self._connection.flush()

    def receive(self) -> str:
        """Receive and decode a response from the remote endpoint."""
        message: str | None = self._responses.get()
        if message is None:
            self._responses.put(None)
            return ''
        return message

    def close(self) -> None:
        """Close the telnet connection and stop the background reader."""
        if self._closed:
            return

        self._closed = True
        self._connection.close()
        self._reader_thread.join(timeout=1)

    def _read_connection(self) -> None:
        while True:
            try:
                raw_message = self._connection.readline()
            except (EOFError, RuntimeError):
                break
            if not raw_message:
                break

            if isinstance(raw_message, bytes):
                raw_message = raw_message.decode()

            message = raw_message.strip()
            if message:
                self._record_message(message)

        self._responses.put(None)

    def _record_message(self, message: str) -> None:
        try:
            measurement = Measurement.from_raw_data(message)
        except ValidationError:
            self._responses.put(message)
            return

        with self._measurement_log_lock:
            self.measurement_log.append(measurement)

    def __str__(self) -> str:
        """String representation of TCPTransport instance.

        Returns:
            str: formatted string showing the host and port of the TCPTransport instance.
        """
        return f'TCPTransport at {self._host}:{self._port}'
