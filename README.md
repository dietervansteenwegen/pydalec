# pydalec

>Library for the `D`ynamic `A`bove-water radiance(`L`) and irradiance(`E`) `C`ollector (`DALEC`)
>from [In-situ Marine Optics].

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

## CLI connection testing

Useful to quickly validate TCP connectivity and get live measurements from the command line.

```bash
pip install pydalec  # or uv, or ...
# Replace with correct IP, and/or add --port xxx to override port
pydalec-test 192.168.2.11
```

This will:

* print a "successful connection" message
* start measurements and streams them to stdout
* keep running until you stop with `Ctrl+C`

## Release History

See [CHANGELOG.md](https://github.com/dietervansteenwegen/pydalec/blob/master/CHANGELOG.md)

[In-situ Marine Optics]: https://insitumarineoptics.com/dalec/
