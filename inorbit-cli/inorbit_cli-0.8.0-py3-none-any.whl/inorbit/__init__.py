# Copyright (c) 2021, InOrbit, Inc.
# All rights reserved.

import os
import click
import sys
from inorbit.client import InOrbit
from inorbit.constants import DEFAULT_URL

# The `INORBIT_CLI_API_KEY` is the only mandatory configuration
if "INORBIT_CLI_API_KEY" not in os.environ or \
    not os.environ["INORBIT_CLI_API_KEY"]:
    click.echo(("Environment variable `INORBIT_CLI_API_KEY` is not defined or it\n"
                "is invalid. Please check your configuration and try again."), err=True)
    sys.exit(1)

# (lean) this makes unittesting a little bit difficult given that the `INORBIT_CLI_API_KEY`
# needs to be mocked before importing the `inorbit` module. See `tox.ini` and `pytest-env`.
client = InOrbit(
    url=os.environ.get("INORBIT_CLI_URL", DEFAULT_URL),
    api_key=os.environ["INORBIT_CLI_API_KEY"])

from inorbit.exceptions import *  # noqa: F401,F403
