""" helper functions"""

import argparse
import secrets
from typing import Tuple
from . import version


def compute_keys(key_l: int, secret_l: int) -> Tuple[str, str]:
    """compute access key and token value

    Args:
        key_l (int): byte length for the key value
        secret_l (int): byte length for the secret value

    Returns:
        Tuple[str, str]: key and secret value
    """

    if not isinstance(key_l, int):
        try:
            key_l = int(key_l)
        except ValueError as value_error:
            print('Invalid input for key length')
            raise SystemExit(1) from value_error

    if not isinstance(secret_l, int):
        try:
            secret_l = int(secret_l)
        except ValueError as value_error:
            print('Invalid input for secret length')
            raise SystemExit(1) from value_error

    key = secrets.token_urlsafe(nbytes=key_l)
    secret = secrets.token_urlsafe(nbytes=secret_l)

    return(key, secret)


def parse_args(args: list) -> argparse.Namespace:
    """parse command line arguments

    Args:
        args (list): command line arguments sys.argv[1:]

    Returns:
        argparse.Namespace: parsed arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
                        action='count',
                        default=0,
                        help="Verbosity (-v, -vv, etc)"
                        )
    parser.add_argument('--version',
                        action='version',
                        version=F"%(prog)s (version {version.__version__ })"
                        )

    return parser.parse_args(args)
