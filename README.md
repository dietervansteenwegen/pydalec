# pydalec

>Library for the `D`ynamic `A`bove-water radiance(`L`) and irradiance(`E`) `C`ollector (`DALEC`)
>from [In-situ Marine Optics].

![GitHub last commit (master)](https://img.shields.io/github/last-commit/dietervansteenwegen/pydalec/develop?style=plastic)
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
device_id='DALEC',
serial_number='0011',
channel_type='Ed'
utc_time=datetime.datetime(
 2026, 5, 12, 10, 48, 0, 925000, tzinfo=datetime.timezone.utc
),
location=Coordinates(lat=51.2352524, lon=2.931144),
sat_compass_heading=141.43,
solar_azimuth_deg=156.026, solar_zenith_deg=34.893,
gear_position_deg=-76.47,
azimuth_deg=64.96, relative_azimuth_deg=-91.07,
pitch_start_measurement_deg=-3.9, roll_start_measurement_deg=1.8,
telemetry=Telemetry(
    voltage_volts=12.5,
    humidity_mm_hg=17.5,
    temperature_diode_celsius=20.855,
    status_flag=0,
),
int_time=22,
signal_percentage=41.8,
dark_counts=864,
max_counts=27871
spectrum=[3724, 4050, 4455, # Rest of spectrum
```

## CLI connection testing

Useful to quickly validate TCP connectivity and get live measurements from the command line.

```bash
>>> pip install pydalec  # or uv, or ...
>>> # Replace with correct IP, and/or add --port xxx to override port
>>> pydalec-test 192.168.2.11
Connected to DALEC at 192.168.2.11:23
Current location: Location(lat=51.2352524°N, lon=2.931144°E)
Current sun zenith: 34.892 deg
Press Enter to start streaming measurements...
Started measurements. Press Ctrl+C to stop.
device_id='DALEC',
serial_number='0011',
channel_type='Ed'
utc_time=datetime.datetime(
 2026, 5, 12, 10, 48, 0, 925000, tzinfo=datetime.timezone.utc
),
location=Coordinates(lat=51.2352524, lon=2.931144),
sat_compass_heading=141.43,
solar_azimuth_deg=156.026, solar_zenith_deg=34.893,
gear_position_deg=-76.47,
azimuth_deg=64.96, relative_azimuth_deg=-91.07,
pitch_start_measurement_deg=-3.9, roll_start_measurement_deg=1.8,
telemetry=Telemetry(
    voltage_volts=12.5,
    humidity_mm_hg=17.5,
    temperature_diode_celsius=20.855,
    status_flag=0,
),
int_time=22,
signal_percentage=41.8,
dark_counts=864,
max_counts=27871
spectrum=[3724, 4050, 4455, # Rest of spectrum
```

This will:

* print a "successful connection" message
* print the current instrument location, if available
* print the current sun zenith, if available
* start measurements and streams them to stdout
* keep running until you stop with `Ctrl+C`

## Release History

See [CHANGELOG.md](https://github.com/dietervansteenwegen/pydalec/blob/master/CHANGELOG.md)

[In-situ Marine Optics]: https://insitumarineoptics.com/dalec/
