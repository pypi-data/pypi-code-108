#!/usr/bin/env python3

import argparse
import json
import os

from gitrics import configuration
from gitrics.bin.generate_user_project_membership import main as ProjectMembership
from gitrics.bin.parameters import param_access, param_api, param_date_end, param_date_start, param_member_only, param_personal_only, param_simple, param_token, param_user, param_visibility
from gitrics.user.projects import gitricsUserProjects
from gitrics.utilities import configure_date_range

from glapi.user.user import GitlabUser

def main(user: dict = None, date_start: str = None, date_end: str = None, projects: list = None, projects_binned_by_access: dict = None, count_projects_private: int = None):
    """
    Generate user data coverage from GitLab usage.

    Args:
        count_projects_private (integer): number of private projects
        date_end (string): iso 8601 date value
        date_start (string): iso 8601 date value
        projects (list): dictionaries where each represents a GitLab Project
        projects_binned_by_access (dict): key/value pairs of access to GitLab Projects
        user (str): GitLab user id

    """

    # parse arguments
    opt = parse_args()

    # convert time
    dt_start, dt_end = configure_date_range(
        date_end=date_end if date_end else opt.date_end,
        date_start=date_start if date_start else opt.date_start
    )

    # initialize user if necessary
    if not user:
        user = GitlabUser(
            id=opt.user,
            token=opt.token,
            version=opt.api
        ).user

    # get user project membership if necessary
    if not projects:
        projects, projects_binned_by_access, count_projects_private = ProjectMembership(
            date_end=dt_end.strftime("%Y-%m-%d"),
            date_start=dt_start.strftime("%Y-%m-%d"),
            return_data=True,
            user=user
        )

    # calculate totals
    total_projects = len(projects)

    total_projects_personal = len([d for d in projects_binned_by_access["maintainer"] if user["username"] in d["path_with_namespace"]]) if projects_binned_by_access and user else 0
    total_projects_public = total_projects - total_projects_personal

    # write user to file
    with open("coverage.json", "w") as f:
        f.write(json.dumps({
            "stats": {
                "percent_projects_coverage": int(round(total_projects_public / (total_projects + count_projects_private) * 100))
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
    param_access(parser)
    param_api(parser)
    param_date_end(parser)
    param_date_start(parser)
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
