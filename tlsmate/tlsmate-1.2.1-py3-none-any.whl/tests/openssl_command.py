#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract the openssl s_server command line from a given pickle file
"""
# import basic stuff
import argparse

# import own stuff

# import other stuff
import pickle


def main():
    parser = argparse.ArgumentParser(description="openssl_command")
    parser.add_argument(
        "pickle_file", metavar="pickle-file", help="The pickle file to inspect"
    )
    args = parser.parse_args()

    with open(args.pickle_file, "rb") as fh:
        obj = pickle.load(fh)
    if hasattr(obj, "openssl_command"):
        if obj.openssl_command is not None:
            cmd = obj.openssl_command
            if isinstance(cmd, list):
                cmd = cmd[0]
            print("openssl_command: " + cmd)
            return
    print("No openssl command found.")


if __name__ == "__main__":
    main()
