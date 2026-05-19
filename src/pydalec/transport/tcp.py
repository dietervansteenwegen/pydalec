"""Synchronous Telnet transport used by the DALEC client."""

import datetime
import io
import logging
import threading
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Union

from pydantic import ValidationError
from telnetlib3.sync import TelnetConnection

from pydalec.errors import PyDalecConnectionError
from pydalec.measurement import Measurement
from pydalec.transport.base import BaseTransport

_LINE_STREAM_OPTIONS = Literal['raw', 'error']
_LOGGER = logging.getLogger(__name__)


@dataclass
class StreamState:
    """Track the current file handle and rollover state for one stream."""

    handle: io.TextIOBase | None = None
    path: Path | None = None
    size_bytes: int = 0
    day_key: str | None = None


class DataSink:
    """Persist incoming DALEC lines to per-day stream files."""

    def __init__(
        self,
        data_root_dir: str | Path | None,
        max_file_size_kb: int,
    ):
        """Configure data sink and prepare directories when enabled."""
        self._enabled = data_root_dir is not None
        self._data_root_dir: Path | None = None
        self._max_file_size_bytes = 0
        self._stream_states: dict[_LINE_STREAM_OPTIONS, StreamState] = {
            'raw': StreamState(),
            'error': StreamState(),
        }
        self._lock = threading.Lock()

        if data_root_dir is None:
            return

        if max_file_size_kb <= 0:
            err_msg = 'max_file_size_kb must be greater than 0'
            raise ValueError(err_msg)

        self._max_file_size_bytes = max_file_size_kb * 1024
        self._data_root_dir = Path(data_root_dir).expanduser().resolve()
        self._data_root_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _format_iso8601_utc(timestamp: datetime.datetime) -> str:
        utc_timestamp = timestamp.astimezone(datetime.timezone.utc)
        return utc_timestamp.isoformat(timespec='microseconds').replace('+00:00', 'Z')

    def store_line(
        self,
        stream: _LINE_STREAM_OPTIONS,
        message: str,
        timestamp: datetime.datetime,
    ) -> None:
        """Store a single incoming line to the matching stream file."""
        if not self._enabled:
            return

        iso_timestamp = self._format_iso8601_utc(timestamp)
        line = f'{iso_timestamp} {message}\n'
        line_size = len(line.encode('utf-8'))

        with self._lock:
            try:
                self._ensure_stream_ready(
                    stream=stream,
                    timestamp=timestamp,
                    incoming_line_size=line_size,
                )
                state = self._stream_states[stream]
                handle = state.handle
                if handle is None:
                    return
                handle.write(line)
                handle.flush()
                state.size_bytes += line_size
            except OSError:
                _LOGGER.exception('Failed to persist incoming %s line', stream)

    def _ensure_stream_ready(
        self,
        stream: _LINE_STREAM_OPTIONS,
        timestamp: datetime.datetime,
        incoming_line_size: int,
    ) -> None:
        if self._data_root_dir is None:
            return

        state = self._stream_states[stream]
        day_key = timestamp.astimezone(datetime.timezone.utc).strftime('%Y%m%d')
        if state.day_key is not None and state.day_key != day_key:
            self._close_stream(stream)
            state = self._stream_states[stream]

        if state.handle is not None:
            next_size = state.size_bytes + incoming_line_size
            if next_size > self._max_file_size_bytes:
                self._close_stream(stream)
                state = self._stream_states[stream]

        if state.handle is not None:
            return

        day_dir = self._data_root_dir / day_key
        day_dir.mkdir(parents=True, exist_ok=True)
        timestamp_label = self._format_iso8601_utc(timestamp)
        file_name = f'DALEC_{timestamp_label}.{stream}'
        path = day_dir / file_name
        handle = path.open('a', encoding='utf-8', newline='')

        state.handle = handle
        state.path = path
        state.size_bytes = path.stat().st_size
        state.day_key = day_key

    def _close_stream(self, stream: _LINE_STREAM_OPTIONS) -> None:
        state = self._stream_states[stream]
        if state.handle is not None:
            state.handle.close()
        self._stream_states[stream] = StreamState()

    def close_all_streams(self) -> None:
        """Close any open stream file handles."""
        if not self._enabled:
            return
        with self._lock:
            self._close_stream('raw')
            self._close_stream('error')


class TCPTransport(BaseTransport):
    """Telnet-based synchronous transport for DALEC commands."""

    def __init__(
        self,
        host: str,
        port: int = 23,
        data_root_dir: str | Path | None = None,
        max_file_size_kb: int = 10240,
    ):
        """Connect to a DALEC endpoint over Telnet."""
        super().__init__()
        self._connected = False
        self._data_sink = DataSink(data_root_dir=data_root_dir, max_file_size_kb=max_file_size_kb)
        self._connection = TelnetConnection(host, port, connect_minwait=0.0, encoding='utf8')
        self._host: str = host
        self._port: int = port
        try:
            self.connect()
        except ConnectionRefusedError as e:
            self._connected = False
            err_msg = f'Unable to connect to DALEC at {host}:{port}'
            raise PyDalecConnectionError(err_msg) from e

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
        self._data_sink.close_all_streams()

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
                self._setup_background_reader()

    def _read_incoming_data(self) -> None:
        while True:
            try:
                raw_message = self._connection.readline()
            except (EOFError, RuntimeError):
                break
            if not raw_message:
                break

            if isinstance(raw_message, str):
                message = raw_message.strip()
            elif isinstance(raw_message, bytes):
                message = raw_message.decode('utf-8').strip()
            else:
                message = bytes(raw_message).decode('utf-8').strip()

            if message:
                self._handle_incoming_data(message)

    def _handle_incoming_data(self, message: str) -> None:
        received_at = self._utc_now()
        try:
            measurement = Measurement.from_raw_data(message)
        except (ValidationError, ValueError):
            self._data_sink.store_line(
                stream='error',
                message=message,
                timestamp=received_at,
            )
            with self._responses_lock:
                self._responses.append(message)
            return

        self._data_sink.store_line(
            stream='raw',
            message=message,
            timestamp=received_at,
        )

        with self._measurement_log_lock:
            self.measurement_log.append(measurement)

    @staticmethod
    def _utc_now() -> datetime.datetime:
        return datetime.datetime.now(datetime.timezone.utc)

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
