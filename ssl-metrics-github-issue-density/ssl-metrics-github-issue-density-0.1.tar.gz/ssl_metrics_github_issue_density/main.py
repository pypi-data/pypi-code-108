from argparse import ArgumentParser, Namespace
from datetime import datetime

import numpy as np
import pandas as pd
from dateutil.parser import parse
from intervaltree import IntervalTree
from pandas import DataFrame


def getArgs():
    parser: ArgumentParser = ArgumentParser(
        prog="SSL Metrics Issue Density",
        usage="Generate Issue Density metrics",
    )
    parser.add_argument(
        "-c",
        "--commits",
        required=True,
        type=open,
        help="Commits JSON file",
    )
    parser.add_argument(
        "-i",
        "--issues",
        required=True,
        type=open,
        help="Issues JSON file",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output JSON file",
        type=str,
        required=True,
    )
    return parser.parse_args()


def get_timestamp():
    """returns relevant timestamp information

    :return first: the first day of the repo
    :return last: the last day of the repo (todays date)
    :return days: list of days the repo has existed
    """

    first: datetime = parse(pd.read_json(getArgs().commits)["commit_date"][0]).replace(
        tzinfo=None
    )
    last: datetime = datetime.now().replace(tzinfo=None)
    days = [i for i in range((last - first).days)]
    return first, last, days


def get_intervals(*, issues, commits) -> list[tuple()]:
    """return start and end intervals of each issue in a repo

    :param commits: DataFrame
    :param issues: DataFrame

    :return intervals: list
    """

    first, last, days = get_timestamp()

    # # replaces null start values with first day of repo
    issues["created_at"] = issues["created_at"].fillna(first)

    # replaces null close values with todays date
    issues["closed_at"] = issues["closed_at"].fillna(last)

    # for each issue calculate its interval and append to list
    intervals = []
    for start, end in zip(issues["created_at"], issues["closed_at"]):
        start = (start.replace(tzinfo=None) - first).days
        end = (end.replace(tzinfo=None) - first).days

        interval = (start, end)
        intervals.append(interval)

    return intervals


def build_tree(*, issues, commits, intervals) -> IntervalTree:
    """builds interval tree

    :param commits: DataFrame
    :param issues: DataFrame
    :param intervals: list

    :return tree: IntervalTree
    """

    tree = IntervalTree()

    # add all items to interval tree
    for interval in intervals:
        tree.addi(interval[0], interval[1] + 1, 1)

    return tree


def get_daily_kloc(commits):
    """returns a list of average kloc per day"""

    first, last, days = get_timestamp()

    daily_kloc = []
    prev = 0
    for day in days:
        avg_kloc = commits[commits["days_since_0"] == day]["kloc"].mean()
        daily_kloc.append(avg_kloc if not avg_kloc is np.nan else prev)
        prev = avg_kloc if not avg_kloc is np.nan else prev

    return daily_kloc


def get_daily_defects(tree):
    """returns a list of number of defects per day"""

    first, last, days = get_timestamp()

    defects = []
    for day in days:
        defects.append(len(tree[day]))

    return defects


def main():
    args: Namespace = getArgs()

    print()

    commits: DataFrame = pd.read_json(args.commits)
    issues: DataFrame = pd.read_json(args.issues)

    intervals = get_intervals(issues=issues, commits=commits)
    tree = build_tree(issues=issues, commits=commits, intervals=intervals)

    first, last, days = get_timestamp()

    kloc = get_daily_kloc(commits)
    defects = get_daily_defects(tree)
    ddensity = [nd / k for nd, k in zip(defects, kloc)]

    d = {
        "days_since_0": days,
        "defect_density": ddensity,
    }

    out = pd.DataFrame(data=d)
    out.to_json(args.output)


if __name__ == "__main__":
    main()
