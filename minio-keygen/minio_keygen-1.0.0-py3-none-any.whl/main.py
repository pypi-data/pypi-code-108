""" main function for minio_keygen"""

import sys
from . import functions


def main():
    """main function
    """

    # parse args
    parsed_args = functions.parse_args(sys.argv[1:])

    key_length = 14
    secret_length = 30

    if parsed_args.verbose > 0:
        print('Generating key and secret')
    key, secret = functions.compute_keys(key_length, secret_length)

    print(F'Key: {key}')
    print(F'Secret: {secret}')


if __name__ == "__main__":
    sys.exit(main())
