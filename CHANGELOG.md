# pydalec CHANGELOG

## Not released yet

### Added

- feat: Add `pydalec-test` TCP CLI
- feat: Add method to fetch current GNSS location
- feat: add acquiring location to CLI test script
- feat: Add method to fetch current sun zenith
- feat: Add diskwriter for incoming (TCP) data

### Changed

- fix: `Transport.connected` is single source of truth for connection state
- refactor: rewrite measurement buffer handling
- refactor: Track measurements by object reference for efficient polling
- feat: CLI also reports current sun zenith
- feat: Add multiline `Measurement.__str__` format
- refactor: Move position/solar-zenith validity checks to Measurement properties

### Fixed

- fix: restart TCP reader on reconnect

### Removed
