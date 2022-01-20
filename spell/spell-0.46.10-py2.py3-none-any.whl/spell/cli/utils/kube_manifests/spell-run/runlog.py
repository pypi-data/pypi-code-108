#!/usr/bin/env python

import fileinput
import os
import requests
import sys
import warnings

run_id = os.environ["spell_run_id"]
status = os.environ["spell_status"]


class SpellRunlogsWarning(Warning):
    """A warning issued if there is an unexpected condition processing a runlog"""

    pass


def send(text):
    r = requests.post(
        "http://localhost/user-run-logs",
        json={
            "run_id": run_id,
            "status": status,
            "log": text,
        },
    )
    if r.status_code == requests.codes.bad_request:
        # TODO: add logging for throttled log events
        warnings.warn("runlog discarded: {}".format(r.text), SpellRunlogsWarning)


def main():
    for line in fileinput.input():
        text = line.rstrip("\n")
        sys.stdout.write(text)
        send(text)


if __name__ == "__main__":
    main()
