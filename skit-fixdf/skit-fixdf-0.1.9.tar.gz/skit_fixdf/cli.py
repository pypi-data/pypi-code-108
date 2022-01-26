"""
CLI for formatting dataframes.
"""
import argparse
import os
import sys

from skit_fixdf import constants as const
from skit_fixdf import utils
from skit_fixdf.fix import calls_df, labels_df


def build_calls_cmd(parser: argparse.ArgumentParser):
    parser.add_argument("--input", "-i", help="Input csv file.")
    parser.add_argument("--output", "-o", help="Output csv file.")


def build_labels_cmd(parser: argparse.ArgumentParser):
    parser.add_argument("--input", "-i", help="Input csv file.")
    parser.add_argument("--output", "-o", help="Output csv file.")
    parser.add_argument(
        "--dataset-type",
        "-dt",
        required=True,
        help="Dataset type.",
        choices=const.SUPPORTED_DATASET_TYPES,
    )
    parser.add_argument("--duckling-url", help="Duckling host for entity parsing.")


def build_parser():
    parser = argparse.ArgumentParser(
        "Formatting/Patching dataframes obtained via skit-calls and skit-df."
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity."
    )
    source = parser.add_subparsers(dest="source", help="Source of dataframe.")
    calls_cmd = source.add_parser(
        "calls", help="Untagged Dataframe obtained via skit-calls."
    )
    build_calls_cmd(calls_cmd)
    labels_cmd = source.add_parser(
        "labels", help="Tagged Dataframe obtained via skit-df."
    )
    build_labels_cmd(labels_cmd)
    return parser


def main():
    args = build_parser().parse_args()
    utils.configure_logger(args.verbose)

    if args.input is None:
        is_pipe = not os.isatty(sys.stdin.fileno())
        if is_pipe:
            args.input = sys.stdin.readline().strip()
        else:
            raise argparse.ArgumentTypeError(
                "Expected to receive --input=<file> or its valued piped in."
            )

    if args.source == const.CALLS:
        output = calls_df.prepare_call_df_for_tagging(args.input, args.output)
        print(output)
    elif args.source == const.LABELS:
        output = labels_df.prepare_tagged_df_for_training(
            args.input, args.dataset_type, args.output, duckling_url=args.duckling_url
        )
        print(output)
    else:
        raise ValueError(f"Unknown source {args.source=}.")
