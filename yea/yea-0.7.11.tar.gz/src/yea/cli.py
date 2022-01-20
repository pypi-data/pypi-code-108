"""Command line entrypoint."""

import argparse
import sys

from yea import context, runner


def cli_list(yc):
    print("Tests:")
    yc._args.action = "list"
    tr = runner.TestRunner(yc=yc)
    tests = tr.get_tests()
    test_ids = [len(t.test_id) for t in tests]
    tlen = max(test_ids) if test_ids else 0
    for t in tests:
        print("  {:<{}s}: {}".format(t.test_id, tlen, t.name))
    tr.clean()


def cli_run(yc):
    yc._args.action = "run"
    tr = runner.TestRunner(yc=yc)
    tr.run()


def cli():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="action", title="action", description="Action to perform")
    parser.add_argument("--dryrun", action="store_true", help="Dont do anything")
    parser.add_argument("--live", action="store_true", help="Run against real server")
    parser.add_argument("--debug", action="store_true", help="Print out extra debug info")
    parser.add_argument("--shard", help="Specify testing shard")
    parser.add_argument("--suite", help="Specify testing suite")
    parser.add_argument("--docs-only", help="Read tests from docstrings only.", action="store_true")

    parse_list = subparsers.add_parser("list", aliases=["l"])
    parse_list.set_defaults(func=cli_list)
    parse_list.add_argument("tests", nargs="*")

    parse_run = subparsers.add_parser("run", aliases=["r"])
    parse_run.add_argument("-a", "--all", action="store_true", help="Run all")
    parse_run.add_argument("tests", nargs="*")
    parse_run.set_defaults(func=cli_run)
    args = parser.parse_args()
    if not args.action:
        parser.print_help()
        sys.exit(1)

    yc = context.YeaContext(args=args)
    args.func(yc)
