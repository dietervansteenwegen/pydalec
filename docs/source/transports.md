# Transports

`Dalec` uses a transport to communicate with an instrument. The transport handles connection, data and commands. Select a
transport through the `Dalec` factory methods:

- `Dalec.connect_tcp()` uses `TCPTransport` to connect to a physical DALEC over TCP/Telnet.
- `Dalec.connect_mock()` uses `MockTransport` for development and testing.

## TCP Transport

`connect_tcp()` connects to the instrument at the defined host. The default TCP port is 23.
For a physical instrument, the DALEC network configuration must route the client to the
instrument's address.

The TCP transport sends acquisition commands to the instrument and uses a background thread to read incoming data. Valid lines containing measurement data are returned as `Measurement` instances; invalid or non-measurement
lines are retained in a separate error stream.

### Persisting Incoming Data

Pass `data_root_dir` to `connect_tcp()` to write incoming data (line per line) to disk:

```python
dalec = Dalec.connect_tcp(
    host='192.168.2.11',
    data_root_dir='./data',
    max_file_size_kb=10240,
)
```

Valid lines are written inside UTC-date folders in files with the `.raw` extention. Error or
non-measurement lines are written to separate files with the `.error` extention. Both files roll over and flush to disk when they grow beyond `max_file_size_kb` or the client disconnects.

For example, files under `data_root_dir= '/data'` could look like this:

```text
data/20260827/DALEC_20260827T143012.123456Z.raw
data/20260827/DALEC_20260827T143015.654321Z.error

The timestamps in the directory and filename are in UTC. The timstamp in the filename is the
time when the first line for that file was received; subsequent lines are appended until rollover.

## Mock Transport

`MockTransport` is intended for development and testing only. It does not yet provide the
full functionality of a physical DALEC instrument and should not be used to assess hardware
communication or acquisition behavior. It currently accepts the same connection-related
arguments for API compatibility, but it does not persist files or generate measurements.

The mock transport is useful for exercising client lifecycle code and interfaces that do not
require live instrument data. Its behavior is a work in progress and may change as additional
instrument functionality is implemented.

## API Reference

Detailed transport classes and their public methods are available in the generated API
reference:

- [Transport package](pydalec.transport.rst)
- [Base transport](pydalec.transport.base.rst)
- [Mock transport](pydalec.transport.mock.rst)
- [TCP transport](pydalec.transport.tcp.rst)
