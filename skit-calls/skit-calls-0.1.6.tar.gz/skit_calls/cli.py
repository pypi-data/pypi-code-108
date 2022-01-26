import argparse
import asyncio
import os
import sys
from datetime import datetime
from typing import Tuple

import pytz
import toml
from loguru import logger

from skit_calls import calls, __version__
from skit_calls import constants as const
from skit_calls import utils


def to_datetime(date_string: str) -> datetime:
    """
    Check if date_string is in YYYY-MM-DD format.

    :param date_string: A string representing a date in YYYY-MM-DD format.
    :type date_string: [type]
    """
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"Invalid date format: expected YYYY-MM-DD for {date_string} instead, {e}"
        )


def validate_date_ranges(start_date: datetime, end_date: datetime) -> None:
    """
    Check if start_date is before end_date.

    :param start_date: A datetime object representing a former date.
    :type start_date: datetime
    :param end_date: A datetime object representing a latter date.
    :type end_date: datetime
    """
    if start_date > end_date:
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
        raise ValueError(f"{start_date=} shouldn't be later than {end_date=}.")


def process_date_filters(
    start_date: datetime, end_date: datetime, timezone: str = const.DEFAULT_TIMEZONE
) -> Tuple[str, str]:
    """
    Process the date filters.

    Make timestamps timezone aware and provide their ISO-8601 representation.

    :param start_date: A datetime object representing a former date.
    :type start_date: datetime
    :param end_date: A datetime object representing a latter date.
    :type end_date: datetime
    :param timezone: The timezone to use for the start and end dates.
    :type timezone: str
    """
    start_date = start_date.replace(tzinfo=pytz.timezone(timezone)).isoformat()
    end_date = end_date.replace(
        hour=23, minute=59, tzinfo=pytz.timezone(timezone)
    ).isoformat()
    return start_date, end_date


def get_version():
    return __version__


def build_cli():
    version = get_version()
    parser = argparse.ArgumentParser(
        description=const.DESCRIPTION.format(version={version})
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity"
    )
    parser.add_argument(
        "--start-date",
        type=to_datetime,
        required=True,
        help="Search calls made after the given date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--lang",
        type=str,
        help="Search calls made in the given language.",
        required=True,
    )
    parser.add_argument(
        "--url",
        type=str,
        default=const.DEFAULT_API_GATEWAY_URL,
        help="The url of the skit.ai's api gateway.",
    )
    parser.add_argument(
        "--token",
        type=str,
        help="The auth token from https://github.com/skit-ai/skit-auth.",
        default=utils.read_session(),
    )
    parser.add_argument(
        "--end-date",
        type=to_datetime,
        help="Search calls made before the given date.",
        default=datetime.now(),
    )
    parser.add_argument(
        "--timezone",
        type=str,
        help="The timezone to use for the start and end dates.",
        default=const.DEFAULT_TIMEZONE,
    )
    parser.add_argument(
        "--call-quantity",
        type=int,
        help="The number of calls to filter.",
        default=const.DEFAULT_CALL_QUANTITY,
    )
    parser.add_argument(
        "--call-type",
        type=str,
        help='The type of call to filter. One of ("live", "subtesting")',
        default=const.LIVE,
        choices=[const.LIVE, const.SUBTESTING],
    )
    parser.add_argument(
        "--ignore-callers",
        type=str,
        nargs="*",
        help="A comma separated list of callers to ignore.",
        default=const.DEFAULT_IGNORE_CALLERS_LIST,
    )
    parser.add_argument(
        "--reported", action="store_true", help="Search only reported calls."
    )
    parser.add_argument(
        "--resolved", action="store_true", help="Search only resolved calls."
    )
    custom_search_command = parser.add_subparsers(dest="commands")
    custom_search_parser = custom_search_command.add_parser(
        "custom-search", help="Calls API custom search options."
    )
    custom_search_parser.add_argument(
        "--key",
        help="Search custom fields using the `custom_search_key` var.",
        required=True,
    )
    custom_search_parser.add_argument(
        "--value",
        help="Search custom fields using the `custom_search_value` var.",
        required=True,
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Choose to inflate calls in memory or in files. Recommended to use files if data points are over 1M.",
        choices=[const.FILES, const.IN_MEMORY],
        default=const.IN_MEMORY,
    )
    return parser


def get_calls_df_path(url, token, start_date, end_date, lang,
    call_type=const.LIVE, call_quantity=const.DEFAULT_CALL_QUANTITY,
    ignore_callers=const.DEFAULT_IGNORE_CALLERS_LIST, 
    reported=False, resolved=False, key=None, value=None, save=const.IN_MEMORY):
    data_path = asyncio.run(
        calls.sample(
            url,
            token,
            start_date,
            end_date,
            lang,
            call_quantity=call_quantity,
            call_type=call_type,
            ignore_callers=ignore_callers,
            reported=reported,
            resolved=resolved,
            custom_search_key=key,
            custom_search_value=value,
            save=save,
        )
    )
    logger.info(f"Data is saved in {data_path}")
    return data_path


def cmd_to_str(args: argparse.Namespace) -> str:
    utils.configure_logger(args.verbose)
    validate_date_ranges(args.start_date, args.end_date)
    args.start_date, args.end_date = process_date_filters(
        args.start_date, args.end_date
    )
    if args.token is None:
        is_pipe = not os.isatty(sys.stdin.fileno())
        if is_pipe:
            args.token = sys.stdin.readline().strip()
        else:
            raise argparse.ArgumentTypeError(
                "Expected to receive --token=<token> or its valued piped in."
            )
    return get_calls_df_path(
        args.url,
        args.token,
        args.start_date,
        args.end_date,
        args.lang,
        call_quantity=args.call_quantity,
        call_type=args.call_type,
        ignore_callers=args.ignore_callers,
        reported=args.reported,
        resolved=args.resolved,
        custom_search_key=args.key, 
        custom_search_value=args.value, 
        save=args.save
    )


def main() -> None:
    """
    Main entry point for the CLI.

    - We try to read token from the pipes if not passed as an arguments.
    - Process the request for sampling calls.
    - Collect the results:
        - In a single file if save is set to IN_MEMORY.
            - Print the file path to stdout.
        - In multiple files if save is set to FILES.
            - Print the directory path to stdout.
    """
    cli = build_cli()
    args = cli.parse_args()
    data_path = cmd_to_str(args)
    print(data_path)
