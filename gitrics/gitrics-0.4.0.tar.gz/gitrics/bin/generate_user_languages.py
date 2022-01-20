#!/usr/bin/env python3

import argparse
import json
import os

from gitrics import configuration
from gitrics.bin.generate_user_project_membership import main as ProjectMembership
from gitrics.bin.parameters import param_access, param_api, param_date_end, param_date_start, param_filter_group_namespaces, param_filter_project_ids, param_filter_project_names, param_filter_project_names_starts_with, param_member_only, param_personal_only, param_simple, param_token, param_user, param_visibility
from gitrics.utilities import configure_date_range

def main(user: dict = None, date_start: str = None, date_end: str = None, projects: list = None):
    """
    Generate languages for user from GitLab usage.

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

    # get user project membership if necessary
    if not projects:
        projects, projects_binned_by_access, count_projects_private = ProjectMembership(
            date_end=dt_end.strftime("%Y-%m-%d"),
            date_start=dt_start.strftime("%Y-%m-%d"),
            return_data=True,
            user=user
        )

    languages = dict()

    # loop through projects
    for project in projects:

        # loop through languages
        for language in project["languages"]:

            # check if tracked already
            if language not in languages:

                # add it
                languages[language] = { "percent": 0 }

            # sum percents
            languages[language]["percent"] += project["languages"][language]
            languages[language]["percent_aggregate"] = languages[language]["percent"] / (len(projects) * 100)

    # write to file
    with open("languages.json", "w") as f:
        f.write(json.dumps({
            "stats": {
                "count_projects": len(projects)
            },
            "data": {k: (languages[k]["percent_aggregate"] * 100) for k in languages}
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
    param_access(parser)
    param_api(parser)
    param_date_end(parser)
    param_date_start(parser)
    param_filter_group_namespaces(parser)
    param_filter_project_ids(parser)
    param_filter_project_names(parser)
    param_filter_project_names_starts_with(parser)
    param_member_only(parser)
    param_personal_only(parser)
    param_simple(parser)
    param_token(parser)
    param_visibility(parser)

    # parse user input
    args, unknown = parser.parse_known_args()

    return args

if __name__ == "__main__":
    main()
