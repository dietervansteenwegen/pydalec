"""Command-line interface for connecting to a DALEC instrument over TCP."""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence

from pydalec.errors import (
    PyDalecConnectionError,
    PyDalecNoPositionDataError,
    PyDalecNoSolarZenithDataError,
)
from pydalec.instrument import Dalec, Location
from pydalec.logging_utils import enable_debug_logging


class _CliArgumentError(ValueError):
    """Raised when parsed CLI arguments violate local validation rules."""


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for TCP connection and stream polling settings."""
    parser = argparse.ArgumentParser(
        prog='pydalec-test',
        description='Connect to a DALEC instrument over TCP and stream measurements.',
    )
    parser.add_argument('ip', help='Instrument IP address')
    parser.add_argument('--port', type=int, default=23, help='TCP port (default: 23)')
    parser.add_argument(
        '--data-root-dir',
        type=str,
        default=None,
        help='Root directory where incoming data files are stored',
    )
    parser.add_argument(
        '--max-file-size-kb',
        type=int,
        default=51200,
        help='Maximum size in kB for each output file (default: 51200, i.e. 50 MB)',
    )
    parser.add_argument(
        '--poll-interval',
        type=float,
        default=0.2,
        help='Polling interval in seconds for new measurements (default: 0.2)',
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable pydalec debug logging (without configuring the root logger)',
    )
    return parser.parse_args(argv)


def _print_new_measurements(client: Dalec, last_measurement: object | None) -> object | None:
    """Print newly received measurements and return the latest seen record."""
    measurements = client.measurement_log
    if not measurements:
        return last_measurement

    start_index = 0
    if last_measurement is not None:
        for index, measurement in enumerate(measurements):
            if measurement == last_measurement:
                start_index = index + 1

    new_measurements = measurements[start_index:]
    for measurement in new_measurements:
        print(measurement)

    return measurements[-1]


def print_header(client: Dalec) -> None:
    """Print the current location and sun zenith before streaming."""
    try:
        location: Location = client.get_location()
        solar_zenith_deg: float = client.get_solar_zenith()
        print(f'Current location: {location}')
        print(f'Current sun zenith: {solar_zenith_deg} deg')
    except PyDalecNoPositionDataError:
        print('ERROR: No location data available')
    except PyDalecNoSolarZenithDataError:
        print('ERROR: No sun zenith data available')
    else:
        _ = input('Press Enter to start streaming measurements...')


def _get_and_check_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments and check for required dependencies."""
    args = _parse_args(argv)
    raw_argv = list(argv) if argv is not None else sys.argv[1:]

    if args.data_root_dir is None and '--max-file-size-kb' in raw_argv:
        err_msg = '--max-file-size-kb requires --data-root-dir.'
        raise _CliArgumentError(err_msg)

    return args


def _get_args_or_exit_code(argv: Sequence[str] | None = None) -> argparse.Namespace | int:
    """Return parsed CLI arguments or an exit code for invalid invocation."""
    try:
        return _get_and_check_args(argv)
    except _CliArgumentError as exc:
        print(exc, file=sys.stderr)
        return 2
    except SystemExit as exc:
        if exc.code in (None, 0):
            return 0
        if isinstance(exc.code, int):
            return exc.code
        print(exc.code, file=sys.stderr)
        return 2


def run(argv: Sequence[str] | None = None) -> int:
    """Run the CLI workflow and return a shell-style exit code."""
    args = _get_args_or_exit_code(argv)
    if isinstance(args, int):
        return args

    if args.debug:
        enable_debug_logging()

    try:
        client = Dalec.connect_tcp(
            args.ip,
            args.port,
            data_root_dir=args.data_root_dir,
            max_file_size_kb=args.max_file_size_kb,
        )
    except PyDalecConnectionError as exc:
        print(f'Connection failed: {exc}', file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f'Invalid configuration: {exc}', file=sys.stderr)
        return 2

    print(f'Connected to DALEC at {args.ip}:{args.port}')
    print_header(client)

    exit_code = make_measurements(args, client)

    return exit_code


def make_measurements(args: argparse.Namespace, client: Dalec) -> int:
    """Stream measurements until interrupted and return an exit code."""
    last_measurement = None
    exit_code = 0
    measurements_started = False
    try:
        client.start_measurements()
        measurements_started = True
        print('Started measurements. Press Ctrl+C to stop.')

        while True:
            last_measurement = _print_new_measurements(client, last_measurement)
            time.sleep(args.poll_interval)
    except KeyboardInterrupt:
        print('\nStopping measurement stream...')
    except Exception as exc:  # pragma: no cover
        print(f'Runtime error: {exc}', file=sys.stderr)
        exit_code = 1
    finally:
        if measurements_started:
            try:
                client.stop_measurements()
            except Exception as exc:  # pragma: no cover
                print(f'Failed to stop measurements cleanly: {exc}', file=sys.stderr)
                exit_code = 1

        try:
            client.disconnect()
        except Exception as exc:  # pragma: no cover
            print(f'Failed to disconnect cleanly: {exc}', file=sys.stderr)
            exit_code = 1

        print('Disconnected.')
    return exit_code


def main(argv: Sequence[str] | None = None) -> None:
    """Run the CLI and exit the process with the returned status code."""
    raise SystemExit(run(argv))


if __name__ == '__main__':
    main()
