#!/usr/bin/env python3

import argparse
import json
import os

from collections import Counter

from gitrics import configuration
from gitrics.bin.parameters import param_user, param_access, param_api, param_filter_group_namespaces, param_filter_project_ids, param_filter_project_names, param_filter_project_names_starts_with, param_member_only, param_personal_only, param_return_data, param_simple, param_token, param_visibility
from gitrics.user.projects import gitricsUserProjects
from gitrics.utilities import parse_multi_parameters

def main(user: dict = None, date_start: str = None, date_end: str = None, return_data: bool = False):
    """
    Generate complete data profile for user from GitLab usage.

    Args:
        date_end (string): iso 8601 date value
        date_start (string): iso 8601 date value
        return_data (bool): TRUE if data should be returned
        user (dictionary): GitLab User

    Return:
        A tuple of (list, dict, int) where list of dictionaries where each represents a GitLab Project, dict is a key/pair value sets of project visibility to projects, and int is the count of private projects.
    """

    # parse arguments
    opt = parse_args()

    # initialize projects
    user_projects = gitricsUserProjects(
        access=opt.access,
        membership=opt.member_only,
        personal=opt.personal_only,
        simple=opt.simple,
        user=user,
        user_id=opt.user,
        token=opt.token,
        version=opt.api,
        visibility=opt.visibility
    )

    # depending on how user data is passed to script or
    # as function argument we can still pull the user object
    # from the initialized class without needing to requery the API
    user = user_projects.user

    # prune projects based on specified items
    projects = user_projects.prune(
        user_projects.projects,
        filter_group_namespaces=parse_multi_parameters(opt.filter_group_namespaces),
        filter_project_ids=parse_multi_parameters(opt.filter_project_ids),
        filter_project_names=parse_multi_parameters(opt.filter_project_names),
        filter_project_names_startswith=parse_multi_parameters(opt.filter_project_names_startswith)
    )

    # bin projects by user access level
    projects_binned_by_access = user_projects.bin("access")

    # enrich projects with langauges/topics/foci/effort/membership
    projects = user_projects.enrich(projects)

    # find out how many private projects the user has
    # regardless of namespace or public
    count_projects_private = len(user_projects.connection.paginate("projects", { "visibility": "private"}))

    # calculate simple project totals
    total_projects = len(user_projects.projects)
    total_projects_developer = len(projects_binned_by_access["developer"])
    total_projects_maintainer = len([d for d in projects_binned_by_access["maintainer"] if user["username"] not in d["path_with_namespace"]])
    total_projects_personal = len([d for d in projects_binned_by_access["maintainer"] if user["username"] in d["path_with_namespace"]])
    total_projects_public = total_projects - total_projects_personal
    total_projects_owner = len(projects_binned_by_access["owner"])

    # calculate public to personal
    public_personal_difference = total_projects_public -  total_projects_personal;
    public_personal_average = total_projects / 2;
    ratio_of_public_personal_difference_average = public_personal_difference / public_personal_average;
    public_private_percent_difference = ratio_of_public_personal_difference_average * 100

    # generate dictionary of role values
    d = {
        "developer": total_projects_developer,
        "maintainer": total_projects_maintainer,
        "owner": total_projects_owner
    }

    # find largest role percent
    count_role_percent = Counter(d)
    greatest_percent_role = max(count_role_percent, key=count_role_percent.get)

    # add project types to roles
    d["personal"] = total_projects_personal
    d["private"] = count_projects_private
    d["public"] = total_projects_public

    # write stats to file
    with open("membership.json", "w") as f:
        f.write(json.dumps({
            "stats": {
                "difference_public_to_personal": public_personal_difference,
                "greatest_percent_role": greatest_percent_role,
                "percent_developer": int(round(total_projects_developer / total_projects_public) * 100) if total_projects_public > 0 else None,
                "percent_difference_public_to_personal": int(round(public_private_percent_difference)),
                "percent_maintainer": int(round(total_projects_maintainer / total_projects_public) * 100) if total_projects_public > 0 else None,
                "percent_owner": int(round(total_projects_owner / total_projects_public) * 100) if total_projects_public > 0 else None,
                "percent_personal": int(round((total_projects_personal / total_projects) * 100)) if total_projects_public > 0 else None,
                "percent_public": int(round((total_projects_public / total_projects) * 100)) if total_projects > 0 else None,
                "count_projects": total_projects
            },
            "data": d
        }))

    # only return data when requested 
    # this ensures console scripts do not break when output is evaluated as error 1 code
    if opt.return_data or return_data:
        return (projects, projects_binned_by_access, count_projects_private)

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
    param_filter_group_namespaces(parser)
    param_filter_project_ids(parser)
    param_filter_project_names(parser)
    param_filter_project_names_starts_with(parser)
    param_member_only(parser)
    param_personal_only(parser)
    param_return_data(parser)
    param_simple(parser)
    param_token(parser)
    param_visibility(parser)

    # parse user input
    args, unknown = parser.parse_known_args()

    return args

if __name__ == "__main__":
    main()
