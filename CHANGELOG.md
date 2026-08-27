# CHANGELOG

## Not released yet

### Changed

- feat: use `writing.ext` as temporary filenames while writing
- feat: Extend status flag decoding

### Added

- docs: Many improvements in the documentation configuration/content
- docs: Document measurement acquisition lifecycle
- docs: Separate telemetry and measurement documentation
- docs: Prepare for Read the docs automated builds
- docs: Add additional information for measurement fields

## Fixed

- fix: Sun zenith cannot be >180 degrees

<!-- start-docs -->
## v0.1.0 (20260603)

### Added

- feat: Add `pydalec-test` TCP CLI
- feat: Add method to fetch current GNSS location
- feat: add acquiring location to CLI test script
- feat: Add method to fetch current sun zenith
- feat: Add diskwriter for incoming (TCP) data
- build: Add tox to pre-commit hooks
- feat: Add opt-in package debug logging

### Changed

- build: improve __version__ tracking
- fix: `Transport.connected` is single source of truth for connection state
- refactor: rewrite measurement buffer handling
- refactor: Track measurements by object reference for efficient polling
- feat: CLI also reports current sun zenith
- feat: Add multiline `Measurement.__str__` format
- refactor: Move position/solar-zenith validity checks to Measurement properties
- build: Add Python 3.14 as tested and supported

### Fixed

- fix: restart TCP reader on reconnect
- fix: use Windows-compliant filenames without colons
