"""Command-line interface for connecting to a DALEC instrument over TCP."""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence

from pydalec.errors import DalecConnectionError
from pydalec.instrument import Dalec


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for TCP connection and stream polling settings."""
    parser = argparse.ArgumentParser(
        prog='pydalec-test',
        description='Connect to a DALEC instrument over TCP and stream measurements.',
    )
    parser.add_argument('ip', help='Instrument IP address')
    parser.add_argument('--port', type=int, default=23, help='TCP port (default: 23)')
    parser.add_argument(
        '--poll-interval',
        type=float,
        default=0.2,
        help='Polling interval in seconds for new measurements (default: 0.2)',
    )
    return parser.parse_args(argv)


def _print_new_measurements(client: Dalec, last_measurement) -> object | None:
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


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI workflow and return a shell-style exit code."""
    args = _parse_args(argv)

    try:
        client = Dalec.connect_tcp(args.ip, args.port)
    except DalecConnectionError as exc:
        print(f'Connection failed: {exc}', file=sys.stderr)
        return 1

    print(f'Connected to DALEC at {args.ip}:{args.port}')

    measurements_started = False
    exit_code = 0
    last_measurement = None

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


if __name__ == '__main__':
    raise SystemExit(main())
