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
* `location`: `Coordinates` instance containing latitude and longitude in decimal degrees,
  accurate to at most 7 decimal places; latitude is in the range -90.0 to 90.0 and longitude
  is in the range -180.0 to 180.0.
* `telemetry`: `Telemetry` instance containing voltage, humidity, temperature, and status flags (see [Telemetry and Status Flags](status_field.md)).

### Geometry and Orientation Fields

* `sat_compass_heading`: Satellite compass heading relative to North in degrees (0.0 to 359.9).
* `solar_azimuth_deg`: Calculated solar azimuth relative to North in degrees (0.0 to 359.9).
* `solar_zenith_deg`: Calculated solar zenith angle in degrees (0.0 to 180.0). A value of
 0 degrees means the sun is directly overhead (zenith), 90 degrees means it is on the
 horizon, and values above 90 degrees mean it is below the horizon.
* `gear_position_deg`: Gear position angle in degrees (-179.9 to 180.0); positive is clockwise.
* `azimuth_deg`: DALEC azimuth, calculated as compass heading plus gear position, in degrees (0.0 to 359.9).
* `relative_azimuth_deg`: DALEC azimuth relative to the solar azimuth in degrees (-179.9 to 180.0).
* `pitch_start_measurement_deg`: Pitch angle at the start of integration in degrees (-90.0 to 90.0).
* `roll_start_measurement_deg`: Roll angle at the start of integration in degrees (-179.9 to 180.0).

### Optical Spectrum Fields

* `int_time`: Integration time in milliseconds (1 to 6000).
* `signal_percentage`: Percentage of peak count signal within the spectrometers' dynamic range.
* `dark_counts`: Average counts of the blackened NIR pixels (0 to 65535).
* `max_counts`: Maximum count of the spectrum (0 to 65535).
* `spectrum`: List of 190 raw ADC count values for the spectral bands (0 to 65535).

### Raw File Format

The raw file contains fixed-position columns: columns 0 to 3 are device ID, serial number,
channel type, and UTC timestamp; columns 4 and 5 are latitude and longitude; columns 6 to 13
are the geometry fields in the order listed above; columns 14 to 21 are telemetry and summary
values; and columns 22 to 211 are `spectrum[0]` through `spectrum[189]`. Angles are emitted
to one decimal place, temperature to three decimal places, and coordinates to seven decimal
places. Unavailable instrument readings may be represented as `NaN`.

## Telemetry Field

Every `Measurement` object includes a `telemetry` attribute. For full details on voltage, humidity, temperature, status flag bit decoding, and helper properties, please refer to the dedicated [Telemetry and Status Flags](status_field.md) page.
