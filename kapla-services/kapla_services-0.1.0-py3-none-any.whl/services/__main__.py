import argparse
import os
import sys

from loguru import logger

from kapla.services.application import BrokerApp
from kapla.services.utils import import_string


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FastNATS Command Line Tool")

    parser.add_argument(
        "app", metavar="app", type=str, help="application to run", nargs="?"
    )
    parser.add_argument(
        "-s",
        "--server",
        metavar="URI",
        dest="servers",
        nargs="+",
        default=[...],
        help="NATS servers to connect to",
    )
    parser.add_argument(
        "--log-level", metavar="LEVEL", help="Logging level", default="INFO"
    )
    parser.add_argument(
        "--connect-timeout",
        metavar="DELAY",
        type=int,
        help="Maximum number of seconds to wait before establishing connection",
        default=...,
    )
    parser.add_argument(
        "--reconnect-timeout",
        metavar="DELAY",
        type=int,
        help="Maximum number of seconds to wait between each reconnect attempt",
        default=...,
    )
    parser.add_argument(
        "--max-reconnect",
        type=int,
        help="Maximum number of reconnect attemps before closing the client",
        default=...,
    )
    parser.add_argument(
        "--ping-interval",
        type=int,
        help="Number of seconds between each ping request to server",
        default=...,
    )
    parser.add_argument(
        "--max-outstanding-pings",
        type=int,
        help="Number of pings that can be sent without receiving response before closing the connection",
        default=...,
    )
    parser.add_argument(
        "--flusher-queue-size",
        type=int,
        help="Maximum size of flusher queue (messages to publish)",
        default=...,
    )
    parser.add_argument(
        "--default-concurrency",
        type=int,
        help="Maximum size of pending buffer (messages to process)",
        default=...,
    )
    parser.add_argument(
        "--default-pending-bytes-limit",
        type=int,
        help="Maximum size of pending buffer (messages to process)",
        default=...,
    )
    parser.add_argument(
        "--default-pending-requests-limit",
        type=int,
        help="Maximum number of requests in pending buffer (messages to process)",
        default=...,
    )
    parser.add_argument(
        "--default-drop-headers",
        type=int,
        help="Headers to drop when sending responses",
        default=...,
    )
    parser.add_argument(
        "--default-status-code",
        type=int,
        help="Default status code to use when sending responses",
        default=...,
    )
    parser.add_argument(
        "--watch",
        help="Watch for changes",
        action="store_true",
    )
    parser.add_argument(
        "--watch-src",
        metavar="PATH",
        nargs="+",
        default=[],
        help="Directories where to look for changes",
    )
    parser.add_argument(
        "--version",
        help="Display the version",
        action="store_true",
    )
    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if args.version:
        print("0.1.0")
        sys.exit(0)

    if not args.app:
        print(
            "Error: Application must be specified as positional argument using an import string."
        )
        print("Usage: cli.py [-h|--help] [OPTIONS] APP")
        sys.exit(1)

    try:
        app: BrokerApp = import_string(args.app)
    except ValueError:
        print(
            "Error: Bad application argument. Application should be given as import string: 'module:app'"
        )
        sys.exit(1)
    except ModuleNotFoundError:
        print(f"Error: Cannot find module {args.app.split(':')[0]}")
        sys.exit(1)

    if args.watch:
        import subprocess

        opts = []

        if args.servers not in ([...], (...), {...}):
            opts += ["--server", *args.servers]
        if args.log_level is not ...:
            opts += ["--log-level", str(args.log_level)]
            os.environ["LOGURU_LEVEL"] = str(args.log_level).upper()
        if args.connect_timeout is not ...:
            opts += ["--connect-timeout", str(args.connect_timeout)]
        if args.reconnect_timeout is not ...:
            opts += ["--reconnect-timeout", str(args.reconnect_timeout)]
        if args.max_reconnect is not ...:
            opts += ["--max-reconnect", str(args.max_reconnect)]
        if args.ping_interval is not ...:
            opts += ["--ping-interval", str(args.ping_interval)]
        if args.max_outstanding_pings is not ...:
            opts += ["--max-outstanding-pings", str(args.max_outstanding_pings)]
        if args.flusher_queue_size is not ...:
            opts += ["--flusher-queue-size", str(args.flusher_queue_size)]
        if args.default_concurrency is not ...:
            opts += ["--default-concurrency", str(args.default_concurrency)]
        if args.default_pending_requests_limit is not ...:
            opts += [
                "--default-pending-requests-limit",
                str(args.default_pending_requests_limit),
            ]
        if args.default_pending_bytes_limit is not ...:
            opts += [
                "--default-pending-bytes-limit",
                str(args.default_pending_bytes_limit),
            ]
        if args.default_drop_headers is not ...:
            opts += ["--default-drop-headers", str(args.default_drop_headers)]
        if args.default_status_code is not ...:
            opts += ["--default-status-code", str(args.default_status_code)]

        cmd = [
            "watchgod",
            "kapla.services.__main__.main",
            *args.watch_src,
            "-a",
            args.app,
        ]
        logger.warning(f"Running watchgod with command: {cmd}")
        if opts:
            cmd += opts
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
            )
            for c in iter(lambda: process.stdout.read(1), b""):  # type: ignore[union-attr]
                sys.stdout.buffer.write(c)
        except KeyboardInterrupt:
            return

    app.update_config(
        default_concurrency=args.default_concurrency,
        default_pending_requests_limit=args.default_pending_requests_limit,
        default_pending_bytes_limit=args.default_pending_bytes_limit,
        default_drop_headers=args.default_drop_headers,
        default_status_code=args.default_status_code,
        servers=args.servers,
        connect_timeout=args.connect_timeout,
        reconnect_timeout=args.reconnect_timeout,
        max_reconnect_attempts=args.max_reconnect,
        ping_interval=args.ping_interval,
        max_outstanding_pings=args.max_outstanding_pings,
        flusher_queue_size=args.flusher_queue_size,
    )

    try:
        app()
    except Exception as err:
        logger.error(err)


if __name__ == "__main__":
    main()
