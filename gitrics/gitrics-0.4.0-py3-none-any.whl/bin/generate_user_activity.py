#!/usr/bin/env python3

import argparse
import json
import math
import os

from collections import Counter

from gitrics import configuration
from gitrics.bin.parameters import param_api, param_date_end, param_date_start, param_token, param_user
from gitrics.user.events import gitricsUserEvents
from gitrics.utilities import configure_date_range

def main(user: dict = None, date_start: str = None, date_end: str = None, projects: list = None):
    """
    Generate activity for user from GitLab usage.

    Args:
        date_end (string): iso 8601 date value
        date_start (string): iso 8601 date value
        projects (list): dictionaries where each represents a GitLab Project
        user (dictionary): GitLab User
    """

    # parse arguments
    opt = parse_args()

    # convert time
    dt_start, dt_end = configure_date_range(
        date_end=date_end if date_end else opt.date_end,
        date_start=date_start if date_start else opt.date_start
    )

    # convert time
    count_days = (dt_end - dt_start).days

    # initialize events
    user_events = gitricsUserEvents(
        date_end=dt_end.strftime("%Y-%m-%d"),
        date_start=dt_start.strftime("%Y-%m-%d"),
        token=opt.token,
        user_id=opt.user,
        version=opt.api
    )

    # flatten all events into single list
    events = [item for sublist in [user_events.events[k] for k in user_events.events] for item in sublist]

    events_coding = user_events.events["pushed"] + user_events.events["merged"]

    events_collaboration = user_events.events["approved"] + user_events.events["closed"] + user_events.events["commented"] + user_events.events["created"] + user_events.events["updated"]

    # totals
    total_events_coding = len(events_coding)
    total_events_collaboration = len(events_collaboration)
    total_projects_with_events = len(list(set([d["project_id"] for d in events])))

    # get common factor
    event_type_common_factor = math.gcd(total_events_coding, total_events_collaboration) if math.gcd(total_events_coding, total_events_collaboration) > 0 else 1

    # get activity stats
    count_activity_types = count_activity_types = { k: sum([len(user_events.events[a]) for a in configuration.ACTIVITY_TYPES[k]]) for k in configuration.ACTIVITY_TYPES }

    # count date occurances in events
    date_occurances_in_events = [d["created_at"].split("T")[0] for d in events]
    date_occurance_count = Counter(date_occurances_in_events)
    
    # write to file
    with open("activity.json", "w") as f:
        f.write(json.dumps({
            "stats": {
                "average_coding_per_day": int(round(count_activity_types["coding"] / count_days)),
                "average_coding_per_project": int(round(count_activity_types["coding"] / total_projects_with_events)) if total_projects_with_events > 0 else 0,
                "average_collaboration_per_day": int(round(count_activity_types["collaboration"] / count_days)),
                "average_collaboration_per_project": int(round(count_activity_types["collaboration"] / total_projects_with_events)) if total_projects_with_events > 0 else 0,
                "max_activity_date_count": date_occurance_count.most_common(1)[0][1] if len(date_occurance_count) > 0 else None,
                "max_activity_date": date_occurance_count.most_common(1)[0][0] if len(date_occurance_count) > 0 else None,
                "rate_collaboration_per_code": "%s:%s" % (
                    int(round(total_events_collaboration / event_type_common_factor)),
                    int(round(total_events_coding / event_type_common_factor))
                )
            },
            "data": {
                "coding": [
                    {
                        "date": d["created_at"],
                        "value": 1,
                        "type": "coding"
                    } for d in events_coding
                ],
                "collaboration": [
                    {
                        "date": d["created_at"],
                        "value": 1,
                        "type": "collaboration"
                    } for d in events_collaboration
                ]
            }
        }))

def parse_args():
    """
    Parse user input.

    Returns:
        A Namespace with attributes for each provided argument.
    """

    # create arguments
    parser = argparse.ArgumentParser()

    # define required values
    param_user(parser)

    # define optional values
    param_api(parser)
    param_date_end(parser)
    param_date_start(parser)
    param_token(parser)

    # parse user input
    args, unknown = parser.parse_known_args()

    return args

if __name__ == "__main__":
    main()
