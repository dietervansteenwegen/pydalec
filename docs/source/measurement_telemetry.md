# Measurement Data and Telemetry

This page describes the structure of measurement data returned by `pydalec`. For connection
and acquisition instructions, see [Usage](usage.md).

## Measurement Data Structure

The library represents each valid instrument reading as a `Measurement` instance containing
optical readings, geometry, position, and telemetry.

### Core Fields

* `device_id`: Identifier string, always `'DALEC'`.
* `serial_number`: Four-digit serial number string (for example `'0011'`).
* `channel_type`: Channel type (`'Ed'`, `'Lu'`, or `'Lsky'`).
* `utc_time`: Timezone-aware UTC `datetime.datetime` object.
* `location`: `Coordinates` instance containing `lat` and `lon` in decimal degrees.
* `telemetry`: `Telemetry` instance containing voltage, humidity, temperature, and status flags (see [Telemetry and Status Flags](status_field.md)).

### Geometry and Orientation Fields

* `sat_compass_heading`: Heading from satellite compass in degrees (0.0 to 359.9).
* `solar_azimuth_deg`: Calculated solar azimuth angle in degrees (0.0 to 359.9).
* `solar_zenith_deg`: Calculated solar zenith angle in degrees (0.0 to 359.9).
* `gear_position_deg`: Gear position angle in degrees (-179.9 to 180.0).
* `azimuth_deg`: Instrument azimuth angle in degrees (0.0 to 359.9).
* `relative_azimuth_deg`: Relative azimuth angle in degrees (-179.9 to 180.0).
* `pitch_start_measurement_deg`: Pitch angle at start of measurement (-179.9 to 180.0).
* `roll_start_measurement_deg`: Roll angle at start of measurement (-179.9 to 180.0).

### Optical Spectrum Fields

* `int_time`: Integration time in milliseconds (1 to 6000).
* `signal_percentage`: Signal level percentage relative to full scale.
* `dark_counts`: Dark count integer value (0 to 65535).
* `max_counts`: Maximum count integer value (0 to 65535).
* `spectrum`: List of 190 integer values (0 to 65535) for spectral bands.

## Telemetry Field

Every `Measurement` object includes a `telemetry` attribute. For full details on voltage, humidity, temperature, status flag bit decoding, and helper properties, please refer to the dedicated [Telemetry and Status Flags](status_field.md) page.
