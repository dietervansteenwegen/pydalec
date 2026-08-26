# Telemetry and Status Flags

The `Telemetry` model inside `Measurement.telemetry` captures environmental housekeeping readings and diagnostic status flags from the DALEC instrument.

## Telemetry Attributes

* `voltage_volts`: Input supply voltage in volts (at most 1 decimal place).
* `humidity_mm_hg`: Internal sensor housing humidity in mmHg (at most 1 decimal place).
* `temperature_diode_celsius`: Diode temperature reading in °C (at most 3 decimal places).
* `status_flag`: Raw 8-bit integer (0 to 255) encoding quality flags and calibration state.

## Status Flag Bit Values

The instrument outputs the 8-bit `status_flag` as part of its telemetry stream. Unset bits (value 0) indicate normal operation, while set bits (value 1) indicate warnings, motion during integration, or stale GPS data.

### Bit Layout Table

| Bit | Hardware Flag | Python Helper Property | Description |
| :-: | --- | --- | --- |
| 7 | `gearCalibrationStatus` | `gear_calibration_status` | Gear calibration state (MSB) |
| 6 | `gearCalibrationStatus` | `gear_calibration_status` | Gear calibration state |
| 5 | `gearCalibrationStatus` | `gear_calibration_status` | Gear calibration state (LSB) |
| 4 | `requireConfiguration` | `require_configuration` | Compass controller requires configuration |
| 3 | `n2kGpsInvalid` | `n2k_gps_valid` | GPS lat/lon age status |
| 2 | `n2kHeadingInvalid` | `n2k_heading_valid` | GPS heading age status |
| 1 | `n2kEpochInvalid` | `n2k_epoch_valid` | GPS epoch age status |
| 0 | `servoMovedDuringIntegration` | `servo_moved_during_integration` | Servo movement during integration |

### Bit Field Descriptions

* **servoMovedDuringIntegration** (`Bit 0`): Set to 1 if the instrument moved during the last integration reading.
  * In Python: `telemetry.servo_moved_during_integration` is `True` when set.
* **n2kEpochInvalid** (`Bit 1`): Set to 1 if the N2K GPS epoch timestamp is older than 1500 ms.
  * In Python: `telemetry.n2k_epoch_valid` is `True` when clear (epoch is valid).
* **n2kHeadingInvalid** (`Bit 2`): Set to 1 if the N2K GPS heading is older than 1000 ms.
  * In Python: `telemetry.n2k_heading_valid` is `True` when clear (heading is valid).
* **n2kGpsInvalid** (`Bit 3`): Set to 1 if the N2K GPS position (lat/lon) is older than 1000 ms.
  * In Python: `telemetry.n2k_gps_valid` is `True` when clear (position is valid).
* **requireConfiguration** (`Bit 4`): Set to 1 if the compass controller requires configuration.
  * In Python: `telemetry.require_configuration` is `True` when set.

## Gear Calibration Status (Bits 5 to 7)

Bits 5, 6, and 7 encode the gear calibration state as a 3-bit integer value (0 to 7), mapped to the `GearCalibrationStatus` enum in `pydalec`:

* **000 (0) - CALIBRATION_OK**: Calibration OK, using magnetic endstops.
* **001 (1) - MOVE_LEFT**: Locating left magnetic endstop.
* **010 (2) - MOVE_RIGHT**: Locating right magnetic endstop.
* **011 (3) - MOVE_CENTRE**: Moving to centrepoint.
* **100 (4) - MANUAL_ENDSTOPS**: Manual endstops.
* **101 (5) - MOVE_RIGHT_MAGNET_NOT_YET_DETECTED**: Moving right, left magnetic endstop detected.
* **110 (6) - RESERVED**: Reserved.
* **111 (7) - NOT_CALIBRATED**: Gear NOT calibrated (default).

## Overall Status Normal Check

When all status bits are clear (`status_flag == 0`), the `telemetry.status_bits_normal` property returns `True`.
