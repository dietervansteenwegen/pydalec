# pydalec

>Library for the In-situ Marine Optics Dynamic Above-water radiance(L) and irradiance(E) Collector (DALEC).

![GitHub last commit (master)](https://img.shields.io/github/last-commit/dietervansteenwegen/pydalec/develop?style=plastic)
![GitHub commit activity (master)](https://img.shields.io/github/commit-activity/w/dietervansteenwegen/pydalec/develop?style=plastic)
![GitHub](https://img.shields.io/github/license/dietervansteenwegen/pydalec?style=plastic)

## Usage example

\#TODO

Replace `MockTransport` with your connection/correct IP to connect to a real instrument.

```python
from pydalec.client import DALECClient
from pydalec.transport.mock import MockTransport

client = DALECClient(MockTransport())
print(client.do_something())
```

## Features

- Sync + async (planned) client
- Built-in mock instrument
- Optional simulator package ([mock] extra)

### Testing options

| Option        | Use case                                                          |
| ------------- | ----------------------------------------------------------------- |
| MockTransport | Lightweight option for unit testing                               |
| PyDalecMock   | Mock instrument for local testing over IP for integration testing |

#### MockTransport

- No network connection required
- Fast
- Deterministic behaviour

Example:

```python
from pydalec.client import DALECClient
from pydalec.transport.mock import MockTransport

client = DALECClient(MockTransport())
assert client.get_temperature() == 25.0
```

#### Integration tests

Using `pydalec-mock`:

- Simulates a real instrument through a TCP server
- Run pydalec-mock (optional dependency) as a local server
- Real network connection via TCP or AsyncTCPTransport to simulator

## Release History

See [CHANGELOG.md](https://github.com/dietervansteenwegen/pydalec/blob/master/CHANGELOG.md)
