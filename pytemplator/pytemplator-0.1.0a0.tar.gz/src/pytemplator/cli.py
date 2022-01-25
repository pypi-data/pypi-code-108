"""Console script for pytemplator."""

import argparse
import sys
from distutils.util import strtobool

from loguru import logger

from pytemplator.pytemplator import Templator


def main():
    """Console script for pytemplator."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b",
        "--base-dir",
        default=None,
        help=(
            "The directory which pytemplator can use to store its config files "
            "and downloaded templates (defaults to $HOME/.pytemplator)"
        ),
    )
    parser.add_argument(
        "-c",
        "--checkout-branch",
        default="main",
        help="Which ref to checkout if using a repo-based template",
    )
    parser.add_argument(
        "-d",
        "--destination-dir",
        default=None,
        help=(
            "The directory where the templated files will be written,"
            "defaults to the current working directory"
        ),
    )
    parser.add_argument(
        "--no-input",
        type=strtobool,
        nargs="?",
        const=True,
        default=False,
        help=(
            "If this flag is present, the templating is purely programmatic with no "
            "prompt for user input. This requires the template to be compatible, i.e."
            "all the variables have default values set."
        ),
    )
    parser.add_argument(
        "template_location",
        help=(
            "The location of the template to use, can be either a repo url or "
            "its path on the filesystem."
        ),
    )
    args = parser.parse_args()
    templator = Templator(**vars(args))
    templator.generate_context()
    templator.render()
    logger.info("\nSuccess!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
