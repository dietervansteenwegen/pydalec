# TODO

* [ ] MockTransport to MockInstrument
* [ ] Check README.md for correct usage/naming
* [X] `pyproject.toml` project name

## Bugs

> `MockTransport.start_measurements()` never produces measurements — `transport/mock.py`

`_making_measurements = True` is set, but `measurement_log` is never populated. The mock is
non-functional for any test that expects measurements.

> `start_measurements()` and `stop_measurements()` bypass `send()` — `transport/tcp.py`

Both write directly via `self._connection.write()`, skipping the `_responses.clear()` call in
`send()`. Stale responses can linger after a START/STOP command.

---

## Poor Design Decisions

> `set_measurement_log_size()` is not on `BaseTransport` or `MockTransport` — `transport/tcp.py`

TCP-only method makes the transport API inconsistent.

> `Dalec.connect_tcp()` does not expose `measurement_log_size` — `instrument.py`

`TCPTransport` accepts the parameter; the factory silently hardcodes the default.

> `pydalec_mock` server does not handle `START`/`STOP` — `pydalec_mock/protocol.py`

`handle_command` only recognizes `READ:TEMP?`. Any command sent through `start_measurements()` /
`stop_measurements()` returns `ERROR`. Useless for measurement integration testing.

> `pydalec_mock` creates fresh `InstrumentState` per connection — `async_server.py`

Reconnecting clients lose all state. Not documented.

## Test Issues

> `_DummyTransport.receive()` is dead code — `test_client.py`

`Dalec` never calls `receive()` on the transport. The method is never invoked in any test.

## Add status/flag bit values

| Bit |            Value            |
| :-: | :-------------------------: |
|  7  |    GearCalibrationStatus    |
|  6  |    GearCalibrationStatus    |
|  5  |    GearCalibrationStatus    |
|  4  |    requireConfiguration     |
|  3  |        n2kGpsInvalid        |
|  2  |      n2kHeadingInvalid      |
|  1  |       n2kEpochInvalid       |
|  0  | servoMovedDuringIntegration |

> Status bits of 0 (zero) indicate normal operation.

* **servoMovedDuringIntegration**: `1` if the DALEC relative azimuth during the last integration reading
* **n2kEpochInvalid**: 1 if the GPS epoch is older than 1500ms
* **n2kHeadingInvalid**: 1 if the GPS heading is older than 1000ms
* **n2kGpsInvalid**: 1 if the GPS lat/long is older than 1000ms
* **requireConfiguration**: 1 if the compass controller has not been configured

* **gearCalibrationStatus**:  
000: Calibration OK, using magnetic endstops  
001: 'MOVE_LEFT', Locating left magnetic endstop  
010: 'MOVE_RIGHT', Locating right magnetic endstop  
011: 'MOVE_CENTRE', Moving to centrepoint
100: Manual endstops  
101: MOVE_RIGHT_MAGNET_NOT_YET_DETECTED', Moving right, left magnetic endstop detected. Likely between physical limit and left magnetic endstop
110: n/a
111: Gear NOT calibrated (default)
