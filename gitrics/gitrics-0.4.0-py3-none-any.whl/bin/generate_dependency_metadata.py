#!/usr/bin/env python3

import argparse
import json
import os

from importlib.metadata import files, metadata, version

from gitrics import configuration
from gitrics.bin.parameters import param_api, param_gitrics_user, param_token

from glapi.user.user import GitlabUser

def main():
    """
    Generate metadata for dependencies.
    """

    # parse arguments
    opt = parse_args()

    # get package info
    package_name = "gitrics"
    package_path = str(files(package_name)[0].locate()).split("/")
    package_path.pop()
    package_directory_path = "/".join([d for d in package_path])
    package_version = version(package_name)
    package_url = metadata(package_name)["Home-page"]

    # get authors
    author_usernames = list()
    gitrics_authors = list()
    gitrics_maintainers = list()

    # open authors file from package
    if os.path.exists(os.path.join(package_directory_path, "AUTHORS")):
        with open(os.path.join(package_directory_path, "AUTHORS"), "r") as f:
            author_usernames = [d.strip() for d in f.readlines()]

    # if api provided query for data
    if opt.api and opt.token:

        # query api for user data
        for username in author_usernames:

            # initialize user
            gu = GitlabUser(
                token=opt.token,
                username=username,
                version=opt.api
            )

            # add to list
            gitrics_authors.append({
                "id": gu.user["id"],
                "name": gu.user["name"],
                "web_url": gu.user["web_url"],
            })

        # get project id
        project_id = gu.connection.query("projects", params={ "search": "gitrics", "simple": "true" })["data"][0]["id"]

        # format data
        gitrics_maintainers = [
            {
                "id": d["id"],
                "name": d["name"],
                "web_url": d["web_url"]
            }
            for d in gu.connection.query("projects/%s/members" % project_id)["data"]
            if d["access_level"] >= 40
        ]

    # open gitrics user file
    gitrics_user = dict()
    if opt.gitrics_user and os.path.exists(opt.gitrics_user):
        with open(opt.gitrics_user, "r") as f:
            gitrics_user = json.loads(f.read())

    # write metadata to file
    with open("dependencies.json", "w") as f:
        f.write(json.dumps({
            "gitrics": {
                "authors": gitrics_authors,
                "maintainers": gitrics_maintainers,
                "repo_url": package_url,
                "version_label": package_version,
                "version_url": "%s/-/tags/%s" % (
                    package_url,
                    package_version
                )
            },
            "gitrics_user": {
                "authors": gitrics_user["authors"] if gitrics_user else None,
                "maintainers": gitrics_user["maintainers"] if gitrics_user else None,
                "repo_url": gitrics_user["repo_url"] if gitrics_user else None,
                "version_label": gitrics_user["version_label"] if gitrics_user else None,
                "version_url": gitrics_user["version_url"] if gitrics_user else None
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

    # define optional values
    param_api(parser)
    param_gitrics_user(parser)
    param_token(parser)

    # parse user input
    args, unknown = parser.parse_known_args()

    return args

if __name__ == "__main__":
    main()
