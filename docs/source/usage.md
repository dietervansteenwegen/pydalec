# Usage

This page describes how to connect to a DALEC instrument, control acquisition, retrieve
measurements, and manage the in-memory and persisted data buffers.

## Connect to a TCP Instrument

`connect_tcp()` creates a client and connects immediately. The default TCP port is 23.

```python
from pydalec import Dalec

dalec = Dalec.connect_tcp(host='192.168.2.11')
print(dalec.connected)
```

The client raises `PyDalecConnectionError` when the connection cannot be established. Call
`dalec.connect()` to reconnect after a disconnect.

## Start and Stop Measurements

```python
dalec.start_measurements()
print(dalec.status.measuring)

dalec.stop_measurements()
print(dalec.status.measuring)
```

For TCP, `start_measurements()` sends the `START` command and clears the in-memory
measurement buffer before acquisition begins. `stop_measurements()` sends the `STOP`
command and preserves measurements already received. Stopping does not disconnect the client.

## Read Measurements

The TCP transport reads incoming lines in a background thread. Valid lines are parsed into
`Measurement` instances and appended to the measurement buffer.

`measurement_log` returns a list snapshot of the measurements currently in the buffer. It
does not return the internal deque, so changing the returned list does not change the buffer.

```python
dalec.start_measurements()

measurements = dalec.measurement_log
if measurements:
    latest = measurements[-1]
    print(latest.channel_type)
    print(latest.spectrum)

dalec.stop_measurements()
```

There is no blocking `read()` call or callback API. Poll `measurement_log` periodically and
track which records the application has already processed.

## In-Memory Buffering

The default in-memory buffer is a `collections.deque` with a maximum length of 40. When it
is full, a new measurement removes the oldest record. It is intended for recent readings,
not archival storage.

Resize it through the transport:

```python
dalec.transport.set_measurement_log_size(100)
```

The size must be at least 1. Increasing the size preserves existing records; reducing it
retains only the newest records that fit.

## Persist Raw TCP Data

Pass `data_root_dir` to `connect_tcp()` to persist incoming TCP lines:

```python
dalec = Dalec.connect_tcp(
    host='192.168.2.11',
    data_root_dir='./data',
    max_file_size_kb=51200,
)
```

Valid raw lines are written beneath UTC-date folders. Error or non-measurement lines are
written to a separate error stream. Files roll over when they exceed `max_file_size_kb` and
are finalized when the stream closes or the client disconnects.

The mock transport accepts these arguments for API compatibility but does not currently
persist files or generate measurements.

## Convenience Queries

`get_location()` and `get_solar_zenith()` wait for the first suitable measurement and return
the requested value. If acquisition is not already running, each method starts it
temporarily, stops it when finished, and restores the previous measurement buffer.

```python
location = dalec.get_location(timeout_secs=10.0)
solar_zenith = dalec.get_solar_zenith(timeout_secs=10.0)
```

Both methods raise a specific `pydalec` error if no valid value arrives before the timeout.
The timeout must be greater than 0 seconds.

## Disconnect

Stop acquisition before disconnecting:

```python
dalec.stop_measurements()
dalec.disconnect()
```

`disconnect()` closes the TCP connection, stops the background reader, and finalizes enabled
raw and error files. In-memory measurements remain available until a later
`start_measurements()` clears them.
