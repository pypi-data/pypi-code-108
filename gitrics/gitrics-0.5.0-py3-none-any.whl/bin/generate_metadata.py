#!/usr/bin/env python3

import argparse
import datetime
import json

from gitrics import configuration
from gitrics.bin.parameters import param_date_end, param_date_start, param_gitlab_name, param_gitlab_url, param_visibility
from gitrics.utilities import configure_date_range

def main(date_start: str = None, date_end: str = None):
    """
    Generate metadata for report.

    Args:
        date_end (string): iso 8601 date value
        date_start (string): iso 8601 date value
    """

    # parse arguments
    opt = parse_args()

    # convert time
    dt_start, dt_end = configure_date_range(
        date_end=date_end if date_end else opt.date_end,
        date_start=date_start if date_start else opt.date_start
    )

    # write metadata to file
    with open("metadata.json", "w") as f:
        f.write(json.dumps({
            "date_end": dt_end.strftime("%Y-%m-%d"),
            "date_publish": datetime.datetime.now().isoformat(),
            "date_start": dt_start.strftime("%Y-%m-%d"),
            "gitlab_name": opt.gitlab_name,
            "gitlab_url": opt.gitlab_url,
            "public_or_private": "public" if opt.visibility.lower() == "internal" or opt.visibility.lower() == "public" else "private",
            "visibility": opt.visibility
        }))

def parse_args():
    """
    Parse user input.

    Returns:
        A Namespace with attributes for each provided argument.
    """

    # create arguments
    parser = argparse.ArgumentParser()

    # define optional values
    param_date_end(parser)
    param_date_start(parser)
    param_gitlab_name(parser)
    param_gitlab_url(parser)
    param_visibility(parser)

    # parse user input
    args, unknown = parser.parse_known_args()

    return args

if __name__ == "__main__":
    main()
