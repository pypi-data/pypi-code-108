#!/usr/bin/env python3

import argparse
import json
import os
import time

from gitrics import configuration
from gitrics.bin.generate_dependency_metadata import main as Dependency
from gitrics.bin.generate_metadata import main as Metadata
from gitrics.bin.generate_user_activity import main as Activity
from gitrics.bin.generate_user_color import main as Color
from gitrics.bin.generate_user_contribution import main as Contribution
from gitrics.bin.generate_user_connection import main as Connection
from gitrics.bin.generate_user_data import main as UserMain
from gitrics.bin.generate_user_data_coverage import main as Coverage
from gitrics.bin.generate_user_languages import main as Languages
from gitrics.bin.generate_user_project_membership import main as ProjectMembership
from gitrics.bin.generate_user_topics import main as Topics
from gitrics.bin.parameters import param_access, param_api, param_date_end, param_date_start, param_filter_group_namespaces, param_filter_project_ids, param_filter_project_names, param_filter_project_names_starts_with, param_member_only, param_personal_only, param_simple, param_token, param_user, param_visibility
from gitrics.utilities import configure_date_range

def main():
    """
    Generate complete data profile for user from GitLab usage.
    """

    # parse arguments
    opt = parse_args()

    # convert time
    dt_start, dt_end = configure_date_range(opt.date_start, opt.date_end)

    # generate metadata
    Dependency()
    Metadata(
        date_end=dt_end.strftime("%Y-%m-%d"),
        date_start=dt_start.strftime("%Y-%m-%d")
    )

    # generate user data
    user = UserMain(return_data=True)

    # rate imit on api
    time.sleep(10)

    # generate projects data
    projects, projects_binned_by_access, count_projects_private = ProjectMembership(
        date_end=dt_end.strftime("%Y-%m-%d"),
        date_start=dt_start.strftime("%Y-%m-%d"),
        return_data=True,
        user=user
    )

    # rate imit on api
    time.sleep(5)

    # generate color palette
    Color(user=user)

    # generate user connections
    Connection(
        date_end=dt_end.strftime("%Y-%m-%d"),
        date_start=dt_start.strftime("%Y-%m-%d"),
        projects=projects,
        user=user
    )

    # generate data coverage
    Coverage(
        count_projects_private=count_projects_private,
        projects=projects,
        projects_binned_by_access=projects_binned_by_access,
        user=user
    )

    # generate languages
    Languages(
        date_end=dt_end.strftime("%Y-%m-%d"),
        date_start=dt_start.strftime("%Y-%m-%d"),
        projects=projects,
        user=user
    )

    # generate topics
    Topics(
        date_end=dt_end.strftime("%Y-%m-%d"),
        date_start=dt_start.strftime("%Y-%m-%d"),
        projects=projects,
        user=user
    )

    # generate events
    Activity(
        date_end=dt_end.strftime("%Y-%m-%d"),
        date_start=dt_start.strftime("%Y-%m-%d"),
        projects=projects,
        user=user
    )

    # generate effort contribution
    Contribution(
        date_end=dt_end.strftime("%Y-%m-%d"),
        date_start=dt_start.strftime("%Y-%m-%d"),
        projects=projects,
        user=user
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
