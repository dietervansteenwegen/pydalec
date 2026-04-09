# pydalec

>Library for the In-situ Marine Optics Dynamic Above-water radiance(L) and irradiance(E) Collector (DALEC).

![GitHub last commit (master)](https://img.shields.io/github/last-commit/dietervansteenwegen/pydalec/develop?style=plastic)
![GitHub commit activity (master)](https://img.shields.io/github/commit-activity/w/dietervansteenwegen/pydalec/develop?style=plastic)
![GitHub](https://img.shields.io/github/license/dietervansteenwegen/pydalec?style=plastic)

## Usage example

```python
>>> from pydalec import DALEC

>>> IP:str = '192.168.2.11'  # Replace with your correct IP

>>> dalec = DALEC.connect_tcp(host= IP)
>>> dalec
DALEC at TCPTransport (192.168.2.11:23)

>>> dalec.start_measurements()
>>> dalec.measurement_log[0]
```

## Release History

See [CHANGELOG.md](https://github.com/dietervansteenwegen/pydalec/blob/master/CHANGELOG.md)
