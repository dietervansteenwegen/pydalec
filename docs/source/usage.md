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

## Instrument Readiness

After power-up, the GNSS can take up to 90 seconds to establish a valid fix.
During this period, position and compass-derived fields may return `NaN`. Use
`get_location()` when a valid position is required; it waits for a valid fix or raises
`PyDalecNoPositionDataError` if the timeout expires.

Gear calibration must also be completed before the instrument can provide a reliable DALEC
azimuth based on relative solar azimuth tracking. When gear position or DALEC azimuth is
unavailable, the instrument reports `NaN`. Use `Measurement.has_valid_solar_zenith` and
the existing measurement validity properties before consuming any retrieved geometry.

## In-Memory Buffering

The default in-memory buffer is a `collections.deque` with a maximum length of 40. When it
is full, new measurements replace the oldest records. It is intended as a received data buffer, not long-term storage. If that is needed, write to disc providing a `data_root_dir` when setting up the connection. See below.

Resize it through the transport:

```python
dalec.transport.set_measurement_log_size(100)
```

The size must be > 1. Increasing the size preserves existing records; reducing
retains only the most recent records.

## Transports and Disk Persistence

The TCP and mock transports, including TCP data persistence and the mock transport's current
limitations, are described in [Transports](transports.md).

## Convenience Queries

`get_location()` and `get_solar_zenith()` wait for the first suitable measurement and return
the requested value. If acquisition is not already running, each method starts it
temporarily, stops it when finished, and restores the previous measurement buffer.

```python
location = dalec.get_location(timeout_secs=10.0)
solar_zenith = dalec.get_solar_zenith(timeout_secs=10.0)
```

`get_location()` raises `PyDalecNoPositionDataError` if no valid position arrives before the
timeout. `get_solar_zenith()` raises `PyDalecNoSolarZenithDataError` if no valid solar zenith
arrives before the timeout.

## Disconnecting

Stop acquisition before closing the connection:

```python
dalec.stop_measurements()
dalec.disconnect()
```

`disconnect()` closes the TCP connection, stops the background reader, and finalizes enabled
raw and error files. In-memory measurements remain available until a later
`start_measurements()` clears them.
