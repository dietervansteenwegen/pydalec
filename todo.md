# TODO

* [ ] MockTransport to MockInstrument
* [ ] Check README.md for correct usage/naming
* [X] `pyproject.toml` project name
* [ ] Add serial commands (get from PDF page 6). Add (and check) expected responses.

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