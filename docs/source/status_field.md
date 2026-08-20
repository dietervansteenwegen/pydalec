# Status/flag bit values

The status/flag

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

> Unset status bits (value of zero) indicate normal operation.  
> Set status bits (value of one) indicate issues.

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
