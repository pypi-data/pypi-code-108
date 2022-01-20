#!/usr/bin/env python3
"""
share/tools/iam-policy-patcher.py - See DESC constant below

Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
Created: Tue Jun 15 08:06:56 2021
"""
import argparse
import json

DESC = r"""Script to patch an IAM policy by overwriting the principal """


def main():
    """ Entry point into this program. """
    parser = create_arg_parser()
    args = parser.parse_args()
    policy = json.loads(args.policy.read())
    for stmt in policy["Statement"]:
        stmt["Principal"] = { "AWS" : "*" }
    print(json.dumps(policy, indent=2))
    return 0


def create_arg_parser():
    """ Create the command line options parser object for this script. """
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("policy", type=argparse.FileType('r'))
    return parser


if __name__ == "__main__":
    import sys, traceback
    try:
        sys.exit(main())
    except Exception as e:
        print(e, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

