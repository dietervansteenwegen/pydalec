"""Synchronous Telnet transport used by the DALEC client."""

import threading
from collections import deque
from typing import Union

from pydantic import ValidationError
from telnetlib3.sync import TelnetConnection

from pydalec.errors import PyDalecConnectionError
from pydalec.measurement import Measurement
from pydalec.transport.base import BaseTransport


class TCPTransport(BaseTransport):
    """Telnet-based synchronous transport for DALEC commands."""

    def __init__(self, host: str, port: int = 23):
        """Connect to a DALEC endpoint over Telnet."""
        super().__init__()
        self._connected = False
        self._connection = TelnetConnection(host, port, connect_minwait=0.0, encoding='utf8')
        self._host: str = host
        self._port: int = port
        try:
            self.connect()
        except ConnectionRefusedError as e:
            self._connected = False
            err_msg = f'Unable to connect to DALEC at {host}:{port}'
            raise PyDalecConnectionError(err_msg) from e
        else:
            self._connected = True
            self._setup_background_reader()

    def _setup_background_reader(self) -> None:
        self._measurement_log_lock = threading.Lock()
        self._responses: deque[str | None] = deque()
        self._responses_lock = threading.Lock()
        self._reader_thread = threading.Thread(target=self._read_incoming_data, daemon=True)
        self._reader_thread.start()

    def set_measurement_log_size(self, size: int) -> None:
        """Resize measurement log while holding the measurement lock."""
        with self._measurement_log_lock:
            super().set_measurement_log_size(size)

    def send(self, data: str) -> None:
        """Send a single command line to the instrument."""
        with self._responses_lock:
            self._responses.clear()
        self._connection.write(data + '\r\n')
        self._connection.flush()

    def _get_reply(self) -> Union[str, None]:
        """Return the oldest response from the instrument."""
        with self._responses_lock:
            return self._responses.popleft() if self._responses else None

    def disconnect(self) -> None:
        """Close the telnet connection and stop the background reader."""
        if not self._connected:
            return

        self._connection.close()
        self._connected = False
        self._reader_thread.join(timeout=1)

    def connect(self) -> None:
        """Reconnect to the DALEC endpoint if currently disconnected."""
        if self._connected:
            return
        else:
            try:
                self._connection.connect()
            except ConnectionRefusedError:
                err_msg = (
                    f'Unable to connect to DALEC at {self._host}:{self._port}. '
                    'Check instrument power/connection and that DALECview is not connected.'
                )
                raise PyDalecConnectionError(err_msg) from None
            else:
                self._connected = True

    def _read_incoming_data(self) -> None:
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
                self._handle_incoming_data(message)

        # self._responses.append(None)

    def _handle_incoming_data(self, message: str) -> None:
        try:
            measurement = Measurement.from_raw_data(message)
        except (ValidationError, ValueError):
            with self._responses_lock:
                self._responses.append(message)
            return

        with self._measurement_log_lock:
            self.measurement_log.append(measurement)

    def start_measurements(self) -> None:
        """Send command to start making measurements."""
        with self._measurement_log_lock:
            self.measurement_log.clear()
        self._connection.write('START\r\n')
        self._connection.flush()

    def stop_measurements(self) -> None:
        """Send command to stop making measurements."""
        self._connection.write('STOP\r\n')
        self._connection.flush()

    def __repr__(self) -> str:
        """Representation of TCPTransport instance.

        Returns:
            str: formatted string showing the host and port of the TCPTransport instance.
        """
        return self.__str__()

    def __str__(self) -> str:
        """String representation of TCPTransport instance.

        Returns:
            str: formatted string showing the host and port of the TCPTransport instance.
        """
        return f'TCPTransport ({self._host}:{self._port})'
