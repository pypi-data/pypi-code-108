#!/usr/bin/env python3

import argparse
import json
import os

from collections import Counter

from gitrics import configuration
from gitrics.bin.generate_user_data import main as UserMain
from gitrics.bin.generate_user_project_membership import main as ProjectMembership
from gitrics.bin.parameters import param_api, param_date_end, param_date_start, param_token, param_user
from gitrics.project.events import gitricsProjectEvents
from gitrics.utilities import configure_date_range

def enrich_projects(projects: list, date_start: str, date_end: str, token: str, api: str) -> dict:
    """
    Add events and membership which are filtered by each other and added to each project as attributes.

    Args:
        api (string): GitLab api url
        date_end (string): iso 8601 date value
        date_start (string): iso 8501 date value
        projects (list): dictionaries where each is a GitLab Project
        token (string): GitLab access token

    Returns:
        A list of dictionaries where each represents an enriched GitLab Project.
    """

    result = list()

    # loop through projects
    for project in projects:

        # only get events for projects with a focus tag
        if len(project["foci"]) > 0:

            # get events
            events = gitricsProjectEvents(
                date_end=date_end,
                date_start=date_start,
                project=project,
                token=token,
                version=api
            ).events

            # simplify for just the attributes needed
            events = [
                {
                    "id": d["id"],
                    "project_id": d["project_id"],
                    "author_id": d["author_id"],
                    "created_at": d["created_at"]
                } for d in events
            ]

        else:
            events = list()

        # filter by membership this way we remove events from service accounts
        events = [d for d in events if d["author_id"] in [d["id"] for d in project["members"]]]

        # ids
        member_ids_with_events = list(set([
            d["author_id"] for d in events
        ]))
        member_ids_by_focus = {
            f: [d["id"] for d in project["members"]]
            for f in project["foci"]
        }

        # counts
        foci_event_counts = {
            f: len(events) / len(project["foci"])
            for f in project["foci"]
        }

        result.append({
            "effort": project["effort"],
            "events": events,
            "foci": project["foci"],
            "foci_event_counts": foci_event_counts,
            "forks_count": project["forks_count"],
            "id": project["id"],
            "languages": project["languages"],
            "members": project["members"],
            "member_ids_by_focus": member_ids_by_focus,
            "member_ids_with_events": member_ids_with_events,
            "name": project["name"],
            "star_count": project["star_count"],
            "topics": project["topics"],
            "web_url": project["web_url"]
        })

    return result

def extract_efforts(projects: list) -> dict:
    """
    Organize projects into efforts and aggregate/organize data across projects.

    Args:
        projects (list): dictionaries where each is a GitLab Project

    Returns:
        A dictionary of key/value pairs where the key is an effort label and corresponding value is a dictionary of values representing the effort.
    """

    # the x for y in [] for x in y sytnax is flattening a 2D array into 1D
    result = {
        k: {
            "events": [
                x for y in [
                    p["events"] for p in projects if p["effort"] == k
                ] for x in y
            ],
            "foci": list(set([
                x for y in [
                    p["foci"] for p in projects if p["effort"] == k
                ] for x in y
            ])),
            "foci_event_counts": {
                f: sum([
                    p["foci_event_counts"][f] for p in projects
                        if p["effort"] == k
                        and len(p["foci"]) > 0
                        and f in p["foci"]
                ])
                for f in list(set([
                    x for y in [
                        p["foci"] for p in projects if p["effort"] == k and len(p["events"]) > 0
                    ] for x in y
                ]))
            },
            "foci_with_events": list(set([
                x for y in [
                    p["foci"] for p in projects if p["effort"] == k and len(p["events"]) > 0
                ] for x in y
            ])),
            "members": [
                dict(t) for t in
                {
                    tuple(d.items()) for d in [
                        {
                            "avatar_url": d["avatar_url"],
                            "id": d["id"],
                            "name": d["name"]
                        } for d in [
                            x for y in [
                                p["members"] for p in projects if p["effort"] == k
                            ] for x in y
                        ]
                    ]
                }
            ],
            "member_ids": list(set([
                x for y in [
                    [
                        m["id"] for m in p["members"]
                    ] for p in projects if p["effort"] == k
                ] for x in y
            ])),
            "member_ids_by_focus": {
                f: list(set([
                    x for y in [
                        p["member_ids_by_focus"][f] for p in projects
                            if p["effort"] == k
                            and len(p["member_ids_by_focus"]) > 0
                            and f in p["member_ids_by_focus"]
                    ] for x in y
                ]))
                for f in list(set([
                    x for y in [
                        p["foci"] for p in projects if p["effort"] == k
                    ] for x in y
                ]))
            },
            "member_ids_with_events": list(set([
                x for y in [
                    p["member_ids_with_events"] for p in projects if p["effort"] == k
                ] for x in y
            ])),
            "member_ids_with_foci": list(set([
                x["id"] for y in [
                    p["members"] for p in projects if p["effort"] == k and len(p["foci"]) > 0
                ] for x in y
            ])),
            "project_ids": list(set([
                p["id"] for p in projects if p["effort"] == k
            ])),
            "project_ids_with_events": list(set([
                x["project_id"] for y in [
                    p["events"] for p in projects if p["effort"] == k
                ] for x in y
            ])),
            "project_ids_by_foci": {
                f: [
                    p["id"] for p in projects if p["effort"] == k and f in p["foci"]
                ]
                for f in list(set([
                    x for y in [
                        p["foci"] for p in projects if p["effort"] == k
                    ] for x in y
                ]))
            },
            "project_ids_with_foci": list(set([
                p["id"] for p in projects if p["effort"] == k and len(p["foci"]) > 0
            ]))
        }
        for k in list(set([d["effort"] for d in projects]))
    }

    # only keep efforts with events and foci
    result = { k: result[k] for k in result if len(result[k]["events"]) > 0 and len(result[k]["foci"]) > 0 }

    return result

def main(user: dict = None, date_start: str = None, date_end: str = None, projects: list = None):
    """
    Generate effort contribution for user from GitLab usage.

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

    # dates
    date_start = dt_start.strftime("%Y-%m-%d")
    date_end = dt_end.strftime("%Y-%m-%d")

    # generate user data if necessary
    if not user:
        user = UserMain()

    # get user project membership if necessary
    if not projects:
        projects, projects_binned_by_access, count_projects_private = ProjectMembership(
            date_end=date_end,
            date_start=date_start,
            return_data=True,
            user=user
        )

    # enrich projects with events/filter by membership
    projects = enrich_projects(projects, date_start, date_end, opt.token, opt.api)

    # organize projects into efforts
    efforts = extract_efforts(projects)

    # get across all efforts
    all_events = [
        x for y in [
            efforts[k]["events"] for k in efforts
        ] for x in y
    ]
    all_foci = list(set([
        x for y in [
            efforts[k]["foci"] for k in efforts
        ] for x in y
    ]))
    all_project_ids_with_events = list(set([
        x for y in [
            efforts[k]["project_ids_with_events"] for k in efforts
        ] for x in y
    ]))
    all_member_ids_with_events = list(set([
        x for y in [
            efforts[k]["member_ids_with_events"] for k in efforts
        ] for x in y
    ]))

    # generate reference objects across all efforts
    connections = {
        f: {
            e: [
                m for m in efforts[e]["member_ids_with_events"]
                if m in efforts[e]["member_ids_with_foci"]
            ]
            for e in efforts
            if f in efforts[e]["foci"]
        }
        for f in all_foci
    }
    foci_reference_project_ids = {
        f: list(set([
            x for y in [
                efforts[k]["project_ids_by_foci"][f] for k in efforts if f in efforts[k]["project_ids_by_foci"]
            ] for x in y
        ]))
        for f in all_foci
    }
    member_ids_with_events_by_focus = {
        f: list(set([
            x for y in [
                [
                    u for u in efforts[k]["member_ids_by_focus"][f]
                        if u in efforts[k]["member_ids_with_events"]
                ] for k in efforts
                    if f in efforts[k]["member_ids_by_focus"]
            ] for x in y
        ]))
        for f in all_foci
    }
    member_reference = {
        u: [
            x for y in [
                efforts[k]["members"] for k in efforts
            ] for x in y if x["id"] == u
        ][0]
        for u in all_member_ids_with_events
    }
    project_ids_by_effort = {
        k: efforts[k]["project_ids"]
        for k in efforts
    }
    project_ids_with_foci_and_events = list(set([
        x for y in [
            [
                p for p in efforts[k]["project_ids_with_events"]
                    if p in efforts[k]["project_ids_with_foci"]
            ]
            for k in efforts
        ] for x in y
    ]))
    project_ids_with_foci_and_events_by_effort = {
        k: [
            p for p in efforts[k]["project_ids_with_events"]
                if p in efforts[k]["project_ids_with_foci"]
        ]
        for k in efforts
    }

    # count events
    effort_event_counts = {
        k: len([
            e for e in efforts[k]["events"]
        ])
        for k in efforts
    }
    effort_event_counts_with_foci = {
        k: len([
            e for e in efforts[k]["events"]
                if e["author_id"] in efforts[k]["member_ids_with_foci"]
                and e["project_id"] in efforts[k]["project_ids_with_foci"]
        ])
        for k in efforts
    }
    foci_event_counts = {
        f: sum([
            efforts[k]["foci_event_counts"][f]
            for k in efforts
                if f in efforts[k]["foci_event_counts"]
        ])
        for f in all_foci
    }
    member_event_counts_with_foci = {
        m: sum([
            len([
                    e for e in efforts[k]["events"]
                        if e["author_id"] == m
                        and e["project_id"] in efforts[k]["project_ids_with_foci"]
                ]) for k in efforts
                    if m in efforts[k]["member_ids_with_foci"]
        ])
        for m in all_member_ids_with_events
    }
    member_project_counts_with_foci_and_events = {
        m: sum([
            len(list(set([
                    e["project_id"] for e in efforts[k]["events"]
                        if e["author_id"] == m
                        and e["project_id"] in all_project_ids_with_events
                ]) for k in efforts
                    if m in efforts[k]["member_ids_with_foci"]
                    and m in efforts[k]["member_ids_with_events"]
        ))])
        for m in all_member_ids_with_events
    }
    total_events_with_foci = sum([foci_event_counts[k] for k in foci_event_counts])

    # get events specific to user
    user_events = [
        d["id"] for d in all_events
            if d["author_id"] == user["id"]
            and d["project_id"] in project_ids_with_foci_and_events
    ]

    # stats

    # averages
    average_activity_per_effort = int(round(total_events_with_foci / len(effort_event_counts_with_foci))) if len(effort_event_counts_with_foci) > 0 else None
    average_activity_per_focus = int(round(total_events_with_foci / len(all_foci))) if len(all_foci) > 0 else None

    # extract the project id of the most events
    max_event_count = Counter(user_events)
    max_event_project_id = max_event_count.most_common(1)[0][0] if len(max_event_count) > 0 else None
    max_event_project_count = max_event_count.most_common(1)[0][1] if len(max_event_count) > 0 else None

    # calculate percentile rank of activity count
    user_occurance_counts = Counter([
        d["author_id"] for d in all_events
    ])
    values_below_user_count = len([
        k for k in user_occurance_counts
        if user_occurance_counts[k] < user_occurance_counts[user["id"]
    ]])
    percentile = (values_below_user_count / len(user_occurance_counts)) * 100 if len(user_occurance_counts) > 0 else None
    percentile_rank = percentile / (100 * (len(user_occurance_counts) + 1)) if percentile else None

    # generate ordinal number format
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

    percentile_for_activity_contribution = ordinal(int(round(percentile))) if percentile else None

    # write to file
    with open("contribution.json", "w") as f:
        f.write(json.dumps({
            "stats": {
                "average_activity_per_effort": average_activity_per_effort,
                "average_activity_per_focus": average_activity_per_focus,
                "member_event_counts_with_foci": member_event_counts_with_foci,
                "member_project_counts_with_foci_and_events": member_project_counts_with_foci_and_events,
                "percentile_for_activity_contribution": percentile_for_activity_contribution
            },
            "data": {
                "efforts": effort_event_counts_with_foci,
                "foci": foci_event_counts,
                "members": member_event_counts_with_foci
            },
            "reference": {
                "connections": connections,
                "member_ids_with_events_by_focus": member_ids_with_events_by_focus,
                "members": member_reference,
                "project_ids_by_effort": project_ids_by_effort,
                "project_ids_with_foci_and_events_by_effort": project_ids_with_foci_and_events_by_effort
            }
        })
    )

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
