#!/usr/bin/env python3

import argparse
import json
import os

import colorgram
import requests

from PIL import Image

from gitrics import configuration
from gitrics.bin.parameters import param_accent_color, param_api, param_token, param_user

from glapi.user.user import GitlabUser

CERT_IS_PRESENT = "REQUESTS_CLIENT_CERT" in os.environ and os.environ["REQUESTS_CLIENT_CERT"] and os.environ["REQUESTS_CLIENT_CERT"] != ""
KEY_IS_PRESENT = "REQUESTS_CLIENT_KEY" in os.environ and os.environ["REQUESTS_CLIENT_KEY"] and os.environ["REQUESTS_CLIENT_KEY"] != ""

def main(user: dict = None):
    """
    Generate user color data from GitLab avatar.

    Args:
        user (dictionary): GitLab User
    """

    # parse arguments
    opt = parse_args()

    # initialize user if necessary
    if not user:
        user = GitlabUser(
            id=opt.user,
            token=opt.token,
            version=opt.api
        ).user

    # attempt to extract color based on user avatar
    try:

        # http request for avatar
        avatar = requests.get(user["avatar_url"], cert=(os.environ["REQUESTS_CLIENT_CERT"], os.environ["REQUESTS_CLIENT_KEY"]), stream=True) if (CERT_IS_PRESENT and KEY_IS_PRESENT) else requests.get(user["avatar_url"], stream=True)

        # pull colors
        colors = colorgram.extract(Image.open(avatar.raw), 6)

    except Exception as e:
        raise e

    # generate css
    with open("visualization.scss", "w") as f:
        f.write("%s" % "\n".join([
        "$visualization%s: %s;" % (
            i + 1,
            "rgb(%s, %s, %s)" % (
                d.rgb.r,
                d.rgb.g,
                d.rgb.b
            )
        ) for i, d in enumerate(colors)
        ]))

        # if accent color provided add it last
        # to overwrite auto generated color
        if opt.accent_color:
            f.write("$visualization%s: %s;" % (
                len(colors),
                opt.accent_color
            ))

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
    param_accent_color(parser)
    param_api(parser)
    param_token(parser)

    # parse user input
    args, unknown = parser.parse_known_args()

    return args

if __name__ == "__main__":
    main()
