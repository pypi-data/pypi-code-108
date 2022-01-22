#!/usr/bin/env python3

import argparse
import json
import os

from gitrics import configuration
from gitrics.bin.generate_user_project_membership import main as ProjectMembership
from gitrics.bin.parameters import param_api, param_date_end, param_date_start, param_token, param_user
from gitrics.user.issues import gitricsUserIssues
from gitrics.user.merge_requests import gitricsUserMergeRequests
from gitrics.utilities import configure_date_range

def main(user: dict = None, date_start: str = None, date_end: str = None, projects: list = None):
    """
    Generate complete data profile for user from GitLab usage.

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

    # initialie issues
    user_issues = gitricsUserIssues(
        date_end=dt_end.strftime("%Y-%m-%d"),
        date_start=dt_start.strftime("%Y-%m-%d"),
        token=opt.token,
        user_id=opt.user,
        version=opt.api
    )

    # pull user data from class
    user = user if user else user_issues.user

    # prune to remove created by and assigned to same user
    issues = user_issues.prune(user_issues.items)

    # format as key/value map of user id to related user object
    issues_formatted = user_issues.format(issues)

    # initialie merge requests
    user_merge_requests = gitricsUserMergeRequests(
        date_end=dt_end.strftime("%Y-%m-%d"),
        date_start=dt_start.strftime("%Y-%m-%d"),
        token=opt.token,
        user_id=opt.user,
        version=opt.api
    )

    # prune to remove created by and assigned to same user
    merge_requests = user_merge_requests.prune(user_merge_requests.items)

    # format as key/value map of user id to related user object
    merge_request_formatted = user_merge_requests.format(merge_requests)

    # combine totals for issues/merge requests
    count_issues_mergerequests = dict()

    # loop through user ids from issues
    for user_id in issues_formatted:

        # check for key in combined
        if user_id not in count_issues_mergerequests:

            # add key/update attributes
            count_issues_mergerequests[user_id] = issues_formatted[user_id]
            count_issues_mergerequests[user_id]["member_only"] = False

    # loop through user ids from merge requests
    for user_id in merge_request_formatted:

        # check for key in combined
        if user_id not in count_issues_mergerequests:

            # add key/update attributes
            count_issues_mergerequests[user_id] = { "count": 0, "member_only": False }

        # now that key exists sum values not yet captured
        count_issues_mergerequests[user_id]["count"] += merge_request_formatted[user_id]["count"]

    # get user project membership if necessary
    if not projects:
        projects, projects_binned_by_access, count_projects_private = ProjectMembership(
            date_end=dt_end.strftime("%Y-%m-%d"),
            date_start=dt_start.strftime("%Y-%m-%d"),
            return_data=True,
            user=user
        )

    # extract and format active project memebers
    # filtering out users which match self
    level1_connections = [
        {
            "id": d["id"],
            "members": [
                {
                    "id": m["id"],
                    "name": m["name"],
                    "avatar_url": m["avatar_url"],
                    "web_url": m["web_url"]
                } for m in d["members"]
                if m["state"] == "active" and m["id"] != user["id"]
            ]
        } for d in projects
    ]

    # flatten
    level1_connections_flat = [x for y in [d["members"] for d in level1_connections] for x in y]

    # remove duplicates
    level1_connections = [dict(t) for t in {tuple(d.items()) for d in level1_connections_flat}]

    # loop through first level connections
    for user in level1_connections:

        # check if captured in combined connection counts
        if user["id"] not in count_issues_mergerequests:

            # add user and update attribute for membership
            count_issues_mergerequests[user["id"]] = {
                "user": user,
                "count": 0,
                "member_only": True
            }

            # add value to existing
            count_issues_mergerequests[user["id"]]["count"] += 1

    # write languages to file
    with open("connections.json", "w") as f:
        f.write(json.dumps({
            "stats": dict(),
            "data": count_issues_mergerequests
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
