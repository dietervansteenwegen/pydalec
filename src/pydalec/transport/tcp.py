"""Synchronous Telnet transport used by the DALEC client."""

import queue
import threading
from collections import deque
from typing import Union

from pydantic import ValidationError
from telnetlib3.sync import TelnetConnection

from pydalec.errors import DalecConnectionError
from pydalec.measurement import Measurement
from pydalec.transport.base import BaseTransport


class TCPTransport(BaseTransport):
    """Telnet-based synchronous transport for DALEC commands."""

    def __init__(self, host: str, port: int = 23, measurement_log_size: int = 20):
        """Connect to a DALEC endpoint over Telnet."""
        if measurement_log_size < 1:
            err_msg = 'measurement_log_size must be at least 1'
            raise ValueError(err_msg)
        self._connected = False
        self._connection = TelnetConnection(host, port, connect_minwait=0.0, encoding='utf8')
        try:
            self.connect()
        except ConnectionRefusedError as e:
            self._connected = False
            err_msg = f'Unable to connect to DALEC at {host}:{port}'
            raise DalecConnectionError(err_msg) from e
        else:
            self._connected = True
            self._host: str = host
            self._port: int = port
            self._measurement_log_size: int = measurement_log_size
            self._setup_background_reader()

    def _setup_background_reader(self) -> None:
        self.measurement_log: deque[Measurement] = deque(maxlen=self._measurement_log_size)
        self._measurement_log_lock = threading.Lock()
        self._responses: queue.Queue[str | None] = queue.Queue()
        self._reader_thread = threading.Thread(target=self._read_incoming_data, daemon=True)
        self._reader_thread.start()

    def set_measurement_log_size(self, size: int) -> None:
        """Resize the measurement log while preserving existing records.

        When increasing the size, all current records are retained. When
        decreasing, the oldest records are discarded first.
        """
        if size < 1:
            err_msg = 'size must be at least 1'
            raise ValueError(err_msg)
        self._measurement_log_size = size
        with self._measurement_log_lock:
            self.measurement_log = deque(self.measurement_log, maxlen=size)

    def send(self, data: str) -> None:
        """Send a single command line to the instrument."""
        self._responses.empty()
        self._connection.write(data + '\r\n')
        self._connection.flush()

    def _get_reply(self) -> Union[str, None]:
        """Return the oldest response from the instrument."""
        return self._responses.get() if self._responses.qsize() > 0 else None

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
                raise DalecConnectionError(err_msg) from None
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
            self._responses.put(message)
            return

        with self._measurement_log_lock:
            self.measurement_log.append(measurement)

    def start_measurements(self) -> None:
        """Send command to start making measurements."""
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
