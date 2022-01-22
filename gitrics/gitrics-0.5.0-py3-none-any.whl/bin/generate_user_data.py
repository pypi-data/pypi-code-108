#!/usr/bin/env python3

import argparse
import json
import os

from gitrics import configuration
from gitrics.bin.parameters import param_api, param_return_data, param_token, param_user

from glapi.user.user import GitlabUser

def main(return_data: bool = False) -> dict:
    """
    Generate user data from GitLab usage.

    Args:
        return_data (bool): TRUE if data should be returned

    Returns:
        A dictionary representing a GitLab User.
    """

    # parse arguments
    opt = parse_args()

    # initialize user
    gu = GitlabUser(
        id=opt.user,
        token=opt.token,
        version=opt.api
    )

    # write user to file
    with open("user.json", "w") as f:
        f.write(json.dumps({
            "id": gu.user["id"],
            "name": gu.user["name"],
            "avatar_url": gu.user["avatar_url"],
            "web_url": gu.user["web_url"],
            "email": gu.user["public_email"]
        }))

    # only return data when requested
    # this ensures console scripts do not break when output is evaluated as error 1 code
    if opt.return_data or return_data:
        return gu.user

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
    param_return_data(parser)
    param_token(parser)

    # parse user input
    args, unknown = parser.parse_known_args()

    return args

if __name__ == "__main__":
    main()
